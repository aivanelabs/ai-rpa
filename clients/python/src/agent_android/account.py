"""Native account sign-in and restricted account API requests."""
from __future__ import annotations

import base64
import hashlib
import hmac
import http.client
import json
import re
import secrets
import time
import webbrowser
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
from uuid import UUID

from . import account_credentials
from .config import normalize_base_url
from .recording import _lock_record

BINDING_HEADERS = {
    "accountUserId": "X-AIVane-Sync-Account",
    "tenantId": "X-AIVane-Sync-Tenant",
    "workspaceId": "X-AIVane-Sync-Workspace",
    "deviceSessionId": "X-AIVane-Sync-Session",
}
_SIGN_IN_AGAIN = "Account sign-in has expired or was rejected. Run `agent-android sign-in` again."
_INVALID_RESPONSE = "The account server returned an unexpected response."
_REFRESH_PATH = "/api/auth/device/refresh"
_LOOPBACK = {"127.0.0.1", "localhost", "::1"}
_BROWSER_TIMEOUT = 300
_JSON_LIMIT = 1024 * 1024
_SERVER_ERRORS = {
    "SYNC_BINDING_CHANGED": "The account, tenant, workspace or session binding changed.",
    "SYNC_CONFLICT": "The library head changed (SYNC_CONFLICT).",
    "SYNC_HEAD_CHANGED": "The library head changed (SYNC_HEAD_CHANGED).",
    "SYNC_DELETED": "The library automation was moved or deleted (SYNC_DELETED).",
    "LIBRARY_DAILY_LIMIT": "The library's daily upload limit was reached (LIBRARY_DAILY_LIMIT).",
    "SAVED_APP_LIMIT_REACHED": "The account's saved Application limit was reached (SAVED_APP_LIMIT_REACHED).",
    "CLOUD_EXPANSION_LIMIT": "The library's workspace storage limit was reached (CLOUD_EXPANSION_LIMIT).",
    "LIBRARY_STORAGE_FULL": "The library's storage limit was reached (LIBRARY_STORAGE_FULL).",
    "LIBRARY_INVALID_UPLOAD": "The server rejected the ZIP or its upload descriptor (LIBRARY_INVALID_UPLOAD).",
    "SYNC_PACKAGE_INTEGRITY": "The library package failed its integrity check (SYNC_PACKAGE_INTEGRITY).",
    "SYNC_REVISION_MISMATCH": "The library revision or its digest did not match (SYNC_REVISION_MISMATCH).",
    "SYNC_SAFE_REVISION_REQUIRED": "The server requires a sync-safe Application (SYNC_SAFE_REVISION_REQUIRED).",
    "SECRET_LITERAL": "The server rejected a literal secret in the Application (SECRET_LITERAL).",
    "SYNC_OUTCOME_UNKNOWN": "The server could not confirm the upload outcome.",
}


class AccountError(Exception):
    pass


class _SessionRejected(AccountError):
    pass


def valid_id(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return str(UUID(value)) == value
    except ValueError:
        return False


def binding_from(value: dict) -> dict[str, str]:
    if not isinstance(value, dict) or not all(valid_id(value.get(key)) for key in BINDING_HEADERS):
        raise AccountError(_INVALID_RESPONSE)
    return {key: value[key] for key in BINDING_HEADERS}


def account_server(url: str) -> str:
    try:
        url = normalize_base_url(url)
        parts = urlsplit(url)
        if parts.username is not None or parts.path or any(char in url for char in "?#"):
            raise ValueError
        if any(char.isspace() or ord(char) < 32 for char in url):
            raise ValueError
        hostname = parts.hostname
        if parts.scheme == "http" and hostname not in _LOOPBACK:
            raise ValueError
        authority = f"[{hostname}]" if ":" in hostname else hostname
        default_port = 443 if parts.scheme == "https" else 80
        if parts.port is not None and parts.port != default_port:
            authority += f":{parts.port}"
    except ValueError:
        raise AccountError("Use an HTTPS account server origin, or HTTP on loopback for local testing.") from None
    return f"{parts.scheme}://{authority}"


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class AccountAPI:
    def __init__(self, server: str, token: str | None = None, binding: dict | None = None):
        self.server = account_server(server)
        self.headers = {"Accept": "application/json"}
        if token is not None:
            self.headers["Authorization"] = f"Bearer {token}"
        if binding is not None:
            self.headers.update({header: binding[key] for key, header in BINDING_HEADERS.items()})
        handlers = [_NoRedirect()]
        if urlsplit(self.server).hostname in _LOOPBACK:
            handlers.append(ProxyHandler({}))
        self.opener = build_opener(*handlers)

    def request(self, method: str, path: str, body: dict | bytes | None = None, *, sha256: str | None = None) -> dict:
        headers = dict(self.headers)
        if isinstance(body, dict):
            body = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif body is not None:
            headers.update({"Content-Type": "application/zip", "X-AIVane-Sha256": sha256})
        request = Request(self.server + path, data=body, method=method, headers=headers)
        try:
            with self.opener.open(request, timeout=30) as response:
                payload = response.read(_JSON_LIMIT + 1)
        except HTTPError as error:
            with error:
                if error.code == 401 and "Authorization" in headers:
                    raise _SessionRejected(_SIGN_IN_AGAIN) from None
                try:
                    failure = json.loads(error.read(_JSON_LIMIT + 1))
                    code = failure["error"]["code"]
                    if path == _REFRESH_PATH and code == "invalid_grant":
                        raise _SessionRejected(_SIGN_IN_AGAIN) from None
                    if isinstance(code, str) and code in _SERVER_ERRORS:
                        raise AccountError(_SERVER_ERRORS[code]) from None
                except (ValueError, TypeError, KeyError, OSError, http.client.HTTPException):
                    pass
                raise AccountError(f"The account server rejected the request (HTTP {error.code}).") from None
        except (URLError, OSError, http.client.HTTPException):
            raise AccountError("The account server is offline or the connection was lost.") from None
        try:
            if len(payload) <= _JSON_LIMIT:
                envelope = json.loads(payload)
                if envelope["success"] is True and isinstance(envelope["data"], dict):
                    return envelope["data"]
        except (ValueError, TypeError, KeyError):
            pass
        raise AccountError(_INVALID_RESPONSE)


@dataclass(frozen=True)
class AccountSession:
    server: str
    token: str = field(repr=False)
    expires_at: float
    binding: dict[str, str]
    refresh_token: str | None = field(default=None, repr=False)

    @classmethod
    def load(cls) -> AccountSession | None:
        try:
            saved = account_credentials.load()
            if saved is None:
                return None
            refresh_token = saved.get("refresh_token")
            return cls(
                account_server(saved["server"]), _credential_token(saved["token"]),
                float(saved["expires_at"]), binding_from(saved["binding"]),
                None if refresh_token is None else _credential_token(refresh_token),
            )
        except (ValueError, OSError, KeyError, TypeError, AccountError):
            raise AccountError("Could not read the stored account sign-in. Sign in again with the account server URL.") from None

    def renew(self) -> AccountSession:
        if self.expires_at > time.time():
            return self
        with _session_lock():
            current = self.load()
            if current is None or current.server != self.server or current.binding != self.binding:
                raise _SessionRejected(_SIGN_IN_AGAIN)
            return current._refresh_if_expired()

    def _refresh_if_expired(self) -> AccountSession:
        start = time.time()
        if self.expires_at > start:
            return self
        if self.refresh_token is None:
            raise _SessionRejected(_SIGN_IN_AGAIN)
        result = AccountAPI(self.server).request("POST", _REFRESH_PATH, {"refresh_token": self.refresh_token})
        renewed = _session_from_grant(self.server, result, start, self.binding)
        renewed._store()
        return renewed

    def _store(self) -> None:
        try:
            account_credentials.save({
                "server": self.server, "token": self.token, "expires_at": self.expires_at,
                "binding": self.binding, "refresh_token": self.refresh_token,
            })
        except OSError:
            raise AccountError("Could not store the account credential in user-only storage.") from None

    def api(self) -> AccountAPI:
        return AccountAPI(self.server, self.token, self.binding)


def _credential_token(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[!-~]+", value):
        raise AccountError(_INVALID_RESPONSE)
    return value


@contextmanager
def _session_lock():
    # Keep concurrent commands from replaying a rotated refresh token or restoring a signed-out credential.
    path = account_credentials.state_directory() / "account.lock"
    try:
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with path.open("a+b") as lock:
            _lock_record(lock)
            yield
    except OSError:
        raise AccountError("Could not update the stored account sign-in.") from None


def _session_from_grant(server: str, result: dict, start: float, binding: dict | None = None) -> AccountSession:
    token = _credential_token(result.get("access_token"))
    refresh_token = _credential_token(result.get("refresh_token"))
    expires_in = result.get("expires_in")
    scope = result.get("scope")
    if (
        result.get("token_type") != "Bearer" or type(expires_in) is not int or expires_in <= 0
        or not isinstance(scope, str) or "library:sync" not in scope.split()
        or not valid_id(result.get("session_id"))
    ):
        raise AccountError("The account server did not issue a library sync credential.")
    if binding is None:
        binding = binding_from(AccountAPI(server, token).request("POST", "/api/library/bind", {}))
    if binding["deviceSessionId"] != result["session_id"]:
        raise AccountError("The server did not return the expected device session.")
    return AccountSession(server, token, start + expires_in, binding, refresh_token)


class _LoopbackServer(HTTPServer):
    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(2)
        return connection, address

    def handle_error(self, request, client_address):
        # A closed browser socket must not log the callback URL or exception.
        pass


def _browser_code(server: str, verifier: str) -> tuple[str, str]:
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).decode("ascii").rstrip("=")
    state = secrets.token_urlsafe(32)
    path = f"/{secrets.token_urlsafe(24)}/callback"
    result: dict[str, str] = {}

    class Callback(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            target = urlsplit(self.path)
            fields = parse_qs(target.query, keep_blank_values=True)
            states = fields.get("state", [])
            codes = fields.get("code", [])
            valid = (
                target.path == path and self.headers.get("Host") == host
                and len(states) == 1 and states[0].isascii() and hmac.compare_digest(states[0], state)
            )
            if valid and len(codes) == 1 and codes[0] and "error" not in fields:
                result["code"] = codes[0]
                status, message = 200, b"Sign-in confirmed. Return to agent-android."
            elif valid and not codes and fields.get("error") == ["access_denied"]:
                result["error"] = "Browser sign-in was declined."
                status, message = 200, b"Sign-in declined. Return to agent-android."
            else:
                status, message = 400, b"Invalid sign-in callback."
            self.send_response(status)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(message)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(message)

    with _LoopbackServer(("127.0.0.1", 0), Callback) as listener:
        host = f"127.0.0.1:{listener.server_port}"
        redirect = f"http://{host}{path}"
        query = urlencode({
            "client_id": "aivane-desktop", "device_name": "agent-android", "redirect_uri": redirect,
            "state": state, "code_challenge_method": "S256", "code_challenge": challenge,
        })
        try:
            opened = webbrowser.open(f"{server}/account/native/authorize?{query}")
        except (OSError, webbrowser.Error):
            opened = False
        if not opened:
            raise AccountError("Could not open the system browser for account sign-in.")
        deadline = time.monotonic() + _BROWSER_TIMEOUT
        while not result:
            listener.timeout = deadline - time.monotonic()
            if listener.timeout <= 0:
                raise AccountError("Timed out waiting for a valid browser sign-in callback.")
            listener.handle_request()
    if "error" in result:
        raise AccountError(result["error"])
    return result["code"], redirect


def sign_in(url: str | None) -> None:
    if url is None:
        previous = AccountSession.load()
        if previous is None:
            raise AccountError("Provide the account server with `agent-android sign-in --url ACCOUNT_SERVER`.")
        url = previous.server
    server = account_server(url)
    verifier = secrets.token_urlsafe(48)
    try:
        code, redirect = _browser_code(server, verifier)
    except OSError:
        raise AccountError("Could not start the loopback listener for browser sign-in.") from None
    start = time.time()
    result = AccountAPI(server).request("POST", "/api/auth/native/token", {
        "grant_type": "authorization_code", "code": code, "code_verifier": verifier, "redirect_uri": redirect,
    })
    session = _session_from_grant(server, result, start)
    with _session_lock():
        session._store()


def sign_out() -> None:
    with _session_lock():
        session = AccountSession.load()
        if session is None:
            return
        try:
            session = session._refresh_if_expired()
            session_id = session.binding["deviceSessionId"]
            result = AccountAPI(session.server, session.token).request(
                "POST", f"/api/account/sessions/{session_id}/revoke", {},
            )
            if result.get("revoked") is not True:
                raise AccountError("The server did not confirm session revocation.")
        except _SessionRejected:
            if session.refresh_token is None:
                raise AccountError("Revoke this session from your account settings. The stored sign-in cannot renew.") from None
            result = AccountAPI(session.server).request(
                "POST", "/api/auth/device/session-status", {"refresh_token": session.refresh_token},
            )
            if result.get("status") not in ("revoked", "expired"):
                raise AccountError("The server did not confirm session revocation.") from None
        account_credentials.clear()
