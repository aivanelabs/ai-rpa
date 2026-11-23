from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import re
import socket
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen
from uuid import uuid4
from zipfile import ZipFile

import pytest

from agent_android import account, account_credentials, cli, library_upload, recording
from agent_android.library_upload import tree_digest

PHONE_URL = "http://127.0.0.1:1"
PHONE_SECRET = "fake-phone-credential"
RECORDED_TEXT = "fake-entered-secret"
TOKEN = "fake-library-credential"
REFRESH_TOKEN = "fake-refresh-credential"
AUTHORIZATION_CODE = "fake-one-time-code"
BINDING = {
    "accountUserId": "00000000-0000-4000-8000-000000000001",
    "tenantId": "00000000-0000-4000-8000-000000000002",
    "workspaceId": "00000000-0000-4000-8000-000000000003",
    "deviceSessionId": "00000000-0000-4000-8000-000000000004",
}
SYNC_HEADERS = {
    "accountUserId": "X-AIVane-Sync-Account",
    "tenantId": "X-AIVane-Sync-Tenant",
    "workspaceId": "X-AIVane-Sync-Workspace",
    "deviceSessionId": "X-AIVane-Sync-Session",
}
FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "library_exact_v1.json"


class FakeLibrary:
    def __init__(self):
        self.binding = dict(BINDING)
        self.authorizations = []
        self.sessions = {}
        self.refresh_count = 0
        self.events = []
        self.requests = {}
        self.heads = {}
        self.errors = []
        self.redirect_bind = None
        self.reject = None
        self.drop = None
        self.already_synced = False
        self.wrong_head_binding = False
        self.callback_statuses = []
        self.callback_threads = []
        self.callback = "invalid-then-valid"

    def handler(self):
        library = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

            def reply(self, status, data, content_type="application/json"):
                raw = data if isinstance(data, bytes) else json.dumps(data).encode()
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def ok(self, stage, data):
                if library.drop == stage:
                    library.drop = None
                    self.connection.shutdown(socket.SHUT_RDWR)
                    self.close_connection = True
                    return
                self.reply(200, {"success": True, "data": data, "error": None})

            def fail(self, status, code):
                self.reply(status, {"success": False, "data": None, "error": {
                    "code": code, "message": f"Server diagnostics containing {TOKEN} and {AUTHORIZATION_CODE}",
                }})

            def handle_route(self):
                target = urlsplit(self.path)
                data = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                body = data if self.command == "PUT" else json.loads(data) if data else None
                library.events.append((self.command, target.path, body))
                if target.path == "/account/native/authorize":
                    fields = {key: val[0] for key, val in parse_qs(target.query).items()}
                    library.authorizations.append(fields)
                    assert fields["client_id"] == "aivane-desktop"
                    assert fields["device_name"] == "agent-android"
                    assert fields["code_challenge_method"] == "S256"
                    assert re.fullmatch(r"http://127\.0\.0\.1:[0-9]{4,5}/[\w-]{16,64}/callback", fields["redirect_uri"])
                    assert "Authorization" not in self.headers
                    query = {"error": "access_denied"} if library.callback == "declined" else {"code": AUTHORIZATION_CODE}
                    query["state"] = fields["state"]
                    self.send_response(302)
                    self.send_header("Location", fields["redirect_uri"] + "?" + urlencode(query))
                    self.end_headers()
                    return
                if target.path == "/api/auth/native/token":
                    fields = library.authorizations[-1]
                    assert set(body) == {"grant_type", "code", "code_verifier", "redirect_uri"}
                    assert body["grant_type"] == "authorization_code"
                    assert body["code"] == AUTHORIZATION_CODE
                    assert body["redirect_uri"] == fields["redirect_uri"]
                    verifier_hash = hashlib.sha256(body["code_verifier"].encode()).digest()
                    assert base64.urlsafe_b64encode(verifier_hash).decode().rstrip("=") == fields["code_challenge"]
                    assert "Authorization" not in self.headers
                    if sum(not session["revoked"] for session in library.sessions.values()) >= 20:
                        self.fail(400, "session_limit")
                        return
                    session_id = library.binding["deviceSessionId"]
                    assert session_id not in library.sessions
                    session = library.sessions[session_id] = {
                        "access_token": f"{TOKEN}-{len(library.sessions)}",
                        "refresh_token": f"{REFRESH_TOKEN}-{len(library.sessions)}",
                        "expires": False, "revoked": False,
                    }
                    self.send_tokens("token", session_id, session)
                    return

                if target.path in ("/api/auth/device/refresh", "/api/auth/device/session-status"):
                    assert self.command == "POST" and set(body) == {"refresh_token"}
                    assert "Authorization" not in self.headers
                    session_id, session = next(
                        ((key, value) for key, value in library.sessions.items()
                         if value["refresh_token"] == body["refresh_token"]), (None, None),
                    )
                    if target.path.endswith("/session-status"):
                        status = "expired" if session is None else "revoked" if session["revoked"] else "active"
                        self.ok("session-status", {"status": status})
                        return
                    if session is None or session["revoked"]:
                        self.fail(400, "invalid_grant")
                        return
                    library.refresh_count += 1
                    session.update(
                        access_token=f"{TOKEN}-rotated-{library.refresh_count}",
                        refresh_token=f"{REFRESH_TOKEN}-rotated-{library.refresh_count}",
                        expires=False,
                    )
                    self.send_tokens("refresh", session_id, session)
                    return

                session_id, session = next(
                    ((key, value) for key, value in library.sessions.items()
                     if self.headers.get("Authorization") == f"Bearer {value['access_token']}"), (None, None),
                )
                if session is None or session["revoked"] or session["expires"]:
                    self.fail(401, "UNAUTHORIZED")
                    return
                assert "Cookie" not in self.headers and "Origin" not in self.headers
                if target.path == f"/api/account/sessions/{session_id}/revoke":
                    assert self.command == "POST" and body == {}
                    assert all(header not in self.headers for header in SYNC_HEADERS.values())
                    session["revoked"] = True
                    self.ok("revoke", {"revoked": True})
                    return
                if target.path == "/api/library/bind":
                    assert body == {}
                    assert all(header not in self.headers for header in SYNC_HEADERS.values())
                    if library.redirect_bind:
                        self.send_response(302)
                        self.send_header("Location", library.redirect_bind)
                        self.end_headers()
                        return
                    self.ok("bind", library.binding)
                    return

                for field, header in SYNC_HEADERS.items():
                    assert self.headers.get(header) == library.binding[field]

                status_match = re.fullmatch(r"/api/library/upload-requests/([^/]+)", target.path)
                if status_match:
                    assert self.command == "GET"
                    entry = library.requests.get(status_match[1])
                    if entry is None:
                        self.ok("status", {"status": "not-found"})
                    elif "receipt" in entry:
                        self.ok("status", {"status": "committed", "result": entry["receipt"]})
                    else:
                        self.ok("status", {"status": "pending"})
                    return

                route = re.fullmatch(r"/api/library/automations/([^/]+)(.*)", target.path)
                assert route is not None
                automation, suffix = route.groups()
                if suffix == "/revisions":
                    assert self.command == "POST"
                    assert set(body) == {
                        "clientRequestId", "revisionId", "parentRevisionId", "digest", "name", "definitionFormat", "package",
                    }
                    assert body["parentRevisionId"] is None and body["definitionFormat"] == "exact-v1"
                    if self.reject("prepare"):
                        return
                    if library.already_synced:
                        library.heads[automation] = {
                            "revisionId": body["revisionId"], "sequence": 1, "treeDigest": body["digest"],
                            "package": body["package"], "representation": "exact",
                        }
                        self.ok("prepare", {
                            "state": "already_synced", "requiredParts": [], "missingImages": [],
                            "head": library.heads[automation],
                        })
                        return
                    candidate = {"automation": automation, "request": body}
                    entry = library.requests.setdefault(body["clientRequestId"], candidate)
                    assert entry["request"] == body and entry["automation"] == automation
                    self.ok("prepare", {
                        "state": "pending", "requiredParts": [] if "package" in entry else ["package"], "missingImages": [],
                    })
                    return
                if suffix == "/sync-head":
                    assert self.command == "GET"
                    head = library.heads[automation]
                    proof = dict(library.binding)
                    if library.wrong_head_binding:
                        proof["tenantId"] = str(uuid4())
                    self.ok("head", {"head": head, "headRevisionId": head["revisionId"], "state": "active", **proof})
                    return
                part = re.fullmatch(r"/revisions/([^/]+)/(package|commit)", suffix)
                assert part is not None
                revision, stage = part.groups()
                entry, = (item for item in library.requests.values()
                          if item["automation"] == automation and item["request"]["revisionId"] == revision)
                if self.command == "GET":
                    assert stage == "package" and "receipt" in entry
                    self.reply(200, entry["package"], content_type="application/zip")
                    return
                if self.reject(stage):
                    return
                if stage == "package":
                    assert self.command == "PUT"
                    assert self.headers["Content-Type"] == "application/zip"
                    descriptor = entry["request"]["package"]
                    assert descriptor == {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
                    assert self.headers["X-AIVane-Sha256"] == descriptor["sha256"]
                    entry["package"] = data
                    self.ok("package", {})
                    return
                assert self.command == "POST" and body == {} and "package" in entry
                assert "receipt" not in entry, "The client sent a duplicate commit"
                head = {"revisionId": revision, "sequence": 1}
                entry["receipt"] = {"head": head, "changeSeq": 7}
                library.heads[automation] = {
                    **head, "treeDigest": entry["request"]["digest"],
                    "package": entry["request"]["package"], "representation": "exact",
                }
                self.ok("commit", entry["receipt"])

            def send_tokens(self, stage, session_id, session):
                self.ok(stage, {
                    "token_type": "Bearer", "access_token": session["access_token"],
                    "refresh_token": session["refresh_token"],
                    "scope": "account:read library:sync session:revoke", "expires_in": 600,
                    "session_id": session_id,
                })

            def reject(self, stage):
                if library.reject and library.reject[0] == stage:
                    _, status, code = library.reject
                    self.fail(status, code)
                    return True
                return False

            def dispatch(self):
                try:
                    self.handle_route()
                except Exception as error:
                    library.errors.append(error)
                    self.fail(500, "FAKE_SERVER_ASSERTION")

            do_GET = do_POST = do_PUT = dispatch

        return Handler

    def browser_open(self, url):
        def browser():
            from urllib.request import HTTPRedirectHandler, build_opener

            class CaptureRedirect(HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, headers, newurl):
                    return None

            opener = build_opener(CaptureRedirect())
            try:
                with pytest.raises(HTTPError) as redirect:
                    opener.open(url, timeout=5)
                with redirect.value as response:
                    assert response.code == 302
                    destination = response.headers["Location"]
                if self.callback.startswith("invalid"):
                    invalid = destination.split("&state=")[0] + "&state=wrong-state"
                    with pytest.raises(HTTPError) as denied:
                        urlopen(invalid, timeout=5)
                    with denied.value as response:
                        self.callback_statuses.append(response.code)
                if self.callback != "invalid-only":
                    with urlopen(destination, timeout=5) as response:
                        self.callback_statuses.append(response.status)
                        assert AUTHORIZATION_CODE.encode() not in response.read()
            except (Exception, pytest.fail.Exception) as error:
                self.errors.append(error)

        thread = threading.Thread(target=browser)
        self.callback_threads.append(thread)
        thread.start()
        return True

    def get(self, path):
        token = self.sessions[self.binding["deviceSessionId"]]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        headers.update({header: self.binding[key] for key, header in SYNC_HEADERS.items()})
        with urlopen(Request(self.url + path, headers=headers), timeout=5) as response:
            return response.read()


@pytest.fixture(autouse=True)
def isolated_state(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path / "home"))
    monkeypatch.setattr(account_credentials, "CREDENTIAL_TARGET", f"AIVane/agent-android/test/{uuid4()}")
    monkeypatch.setenv("AIVANE_API_TOKEN", PHONE_SECRET)
    yield
    account_credentials.clear()


@pytest.fixture
def library(monkeypatch):
    instance = FakeLibrary()
    with ThreadingHTTPServer(("127.0.0.1", 0), instance.handler()) as server:
        instance.url = f"http://127.0.0.1:{server.server_port}"
        runner = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01})
        runner.start()
        monkeypatch.setattr(account.webbrowser, "open", instance.browser_open)
        monkeypatch.setattr(account, "_BROWSER_TIMEOUT", 5)
        yield instance
        server.shutdown()
        runner.join()
    for thread in instance.callback_threads:
        thread.join()
    assert not instance.errors


def run_cli(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["agent-android", *map(str, args)])
    return cli.main()


def sign_in(monkeypatch, library):
    assert run_cli(monkeypatch, "sign-in", "--url", library.url) == 0


def record(tmp_path):
    session = recording.ActionSession(PHONE_URL, "default")
    session.append("android.element.input", {"xpath": "//EditText", "value": RECORDED_TEXT})
    return tmp_path / "demo-app"


def save(monkeypatch, directory, *extra):
    return run_cli(monkeypatch, "save", directory, "--upload", "--url", PHONE_URL, *extra)


def test_exact_v1_fixture_matches_real_server_bytes_and_digest():
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="ascii"))
    archive = base64.b64decode(fixture["package"]["base64"])
    assert len(archive) == fixture["package"]["size"]
    assert hashlib.sha256(archive).hexdigest() == fixture["package"]["sha256"]
    with ZipFile(io.BytesIO(archive)) as bundle:
        assert {info.filename: {
            "size": info.file_size, "sha256": hashlib.sha256(bundle.read(info)).hexdigest(),
        } for info in bundle.infolist()} == fixture["files"]
        assert tree_digest(bundle) == fixture["treeDigest"]


def test_browser_login_save_download_and_signout(library, monkeypatch, tmp_path, capsys):
    sign_in(monkeypatch, library)
    directory = record(tmp_path)
    assert save(monkeypatch, directory) == 0
    assert library.callback_statuses == [400, 200]
    entry, = library.requests.values()
    automation, revision = entry["automation"], entry["request"]["revisionId"]
    base = f"/api/library/automations/{automation}"
    head = json.loads(library.get(f"{base}/sync-head"))["data"]
    assert head["headRevisionId"] == revision
    assert head["head"]["treeDigest"] == entry["request"]["digest"]
    assert {key: head[key] for key in SYNC_HEADERS} == BINDING
    downloaded = library.get(f"{base}/revisions/{revision}/package")
    assert downloaded == directory.with_suffix(".zip").read_bytes()
    with ZipFile(io.BytesIO(downloaded)) as bundle:
        assert tree_digest(bundle) == head["head"]["treeDigest"]
        assert json.loads(bundle.read("app.json"))["applicationId"] == "demo-app"
        assert automation != revision
        for name in bundle.namelist():
            assert bundle.read(name) == (directory / name).read_bytes()
            assert TOKEN.encode() not in bundle.read(name)
        assert RECORDED_TEXT.encode() not in bundle.read("__main__.json")
    session = account_credentials.load()
    assert set(session) == {"server", "token", "binding", "expires_at", "refresh_token"}
    journals = list((account_credentials.state_directory() / "uploads").glob("*.json"))
    assert len(journals) == 1
    for credential in (TOKEN, REFRESH_TOKEN):
        assert credential not in journals[0].read_text()
    if os.name != "nt":
        assert account_credentials._credential_file().stat().st_mode & 0o777 == 0o600
    assert run_cli(monkeypatch, "sign-out") == 0
    assert library.sessions[BINDING["deviceSessionId"]]["revoked"]
    assert account_credentials.load() is None
    assert run_cli(monkeypatch, "sign-out") == 0
    captured = capsys.readouterr()
    assert f"Library automation {automation}, revision {revision} (change sequence 7)" in captured.out
    assert "Signed out" in captured.out
    for secret in (TOKEN, REFRESH_TOKEN, PHONE_SECRET, AUTHORIZATION_CODE, RECORDED_TEXT):
        assert secret not in captured.out + captured.err


def test_bad_callback_state_never_exchanges_a_code(library, monkeypatch, capsys):
    library.callback = "invalid-only"
    monkeypatch.setattr(account, "_BROWSER_TIMEOUT", 1)
    assert run_cli(monkeypatch, "sign-in", "--url", library.url) == 1
    assert library.callback_statuses == [400]
    assert len(library.events) == 1
    assert account_credentials.load() is None
    assert "waiting for a valid browser sign-in callback" in capsys.readouterr().err


def test_declined_callback_never_exchanges_a_code(library, monkeypatch, capsys):
    library.callback = "declined"
    assert run_cli(monkeypatch, "sign-in", "--url", library.url) == 1
    assert len(library.events) == 1
    assert account_credentials.load() is None
    assert "declined" in capsys.readouterr().err


def test_credential_request_does_not_follow_redirects(library, monkeypatch, capsys):
    library.redirect_bind = f"{library.url}/redirected"
    assert run_cli(monkeypatch, "sign-in", "--url", library.url) == 1
    assert len(library.events) == 3
    assert "HTTP 302" in capsys.readouterr().err
    assert account_credentials.load() is None


def test_signed_out_saves_locally_then_resumes_original_zip(library, monkeypatch, tmp_path, capsys):
    directory = record(tmp_path)
    assert save(monkeypatch, directory) == 1
    assert "Signed out" in capsys.readouterr().err
    assert library.events == []
    original = directory.with_suffix(".zip").read_bytes()
    sign_in(monkeypatch, library)
    assert save(monkeypatch, directory) == 0
    entry, = library.requests.values()
    assert entry["package"] == original


def test_plain_save_and_failed_lint_do_not_contact_library(library, monkeypatch, tmp_path):
    sign_in(monkeypatch, library)
    library.events.clear()
    directory = record(tmp_path)
    assert run_cli(monkeypatch, "save", directory, "--url", PHONE_URL) == 0

    def reject_lint(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "aivane-template-lint")

    monkeypatch.setattr(recording.subprocess, "run", reject_lint)
    invalid = tmp_path / "invalid"
    assert save(monkeypatch, invalid) == 1
    assert not invalid.exists() and not invalid.with_suffix(".zip").exists()
    assert library.events == []


def test_save_accepts_legacy_url_abbreviation(library, monkeypatch, tmp_path):
    directory = record(tmp_path)
    assert run_cli(monkeypatch, "save", directory, "--u", PHONE_URL) == 0
    assert directory.is_dir() and directory.with_suffix(".zip").is_file()
    assert library.events == []


def test_oversize_upload_keeps_local_save(library, monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(library_upload, "_ARCHIVE_LIMIT", 1)
    directory = record(tmp_path)
    assert save(monkeypatch, directory) == 1
    assert "exceeds the 64 MiB library upload limit" in capsys.readouterr().err
    with ZipFile(directory.with_suffix(".zip")) as archive:
        assert archive.read("app.json") == (directory / "app.json").read_bytes()
    assert library.events == []


@pytest.mark.parametrize("existing", ["directory", "zip", "both"])
def test_upload_does_not_take_over_unrelated_output(existing, library, monkeypatch, tmp_path):
    sign_in(monkeypatch, library)
    library.events.clear()
    directory = record(tmp_path)
    archive = directory.with_suffix(".zip")
    if existing in ("directory", "both"):
        directory.mkdir()
        (directory / "app.json").write_bytes(b"unrelated directory")
    if existing in ("zip", "both"):
        archive.write_bytes(b"unrelated ZIP")
    assert save(monkeypatch, directory) == 1
    if existing in ("directory", "both"):
        assert list(directory.iterdir()) == [directory / "app.json"]
        assert (directory / "app.json").read_bytes() == b"unrelated directory"
    else:
        assert not directory.exists()
    if existing in ("zip", "both"):
        assert archive.read_bytes() == b"unrelated ZIP"
    else:
        assert not archive.exists()
    assert library.events == []


def test_interruption_after_local_save_resumes_original_zip(library, monkeypatch, tmp_path):
    sign_in(monkeypatch, library)
    library.events.clear()
    directory = record(tmp_path)
    archive = directory.with_suffix(".zip")
    write_journal = account_credentials.write_private_json

    def interrupt_after_save(path, value):
        if archive.is_file() and archive.stat().st_size:
            raise KeyboardInterrupt
        write_journal(path, value)

    with monkeypatch.context() as interrupted:
        interrupted.setattr(account_credentials, "write_private_json", interrupt_after_save)
        with pytest.raises(KeyboardInterrupt):
            save(monkeypatch, directory)
    assert library.events == []
    original = archive.read_bytes()
    assert (directory / "app.json").is_file()
    assert save(monkeypatch, directory) == 0
    entry, = library.requests.values()
    assert entry["package"] == original == archive.read_bytes()


@pytest.mark.parametrize("stage", ["prepare", "package", "commit"])
def test_lost_reply_resumes_same_request_and_commits_once(stage, library, monkeypatch, tmp_path, capsys):
    sign_in(monkeypatch, library)
    directory = record(tmp_path)
    library.drop = stage
    assert save(monkeypatch, directory) == 1
    assert "connection was lost" in capsys.readouterr().err
    original = directory.with_suffix(".zip").read_bytes()
    assert save(monkeypatch, directory) == 0
    assert save(monkeypatch, directory) == 0
    assert "change sequence 7" in capsys.readouterr().out
    entry, = library.requests.values()
    assert entry["package"] == original and entry["receipt"]["changeSeq"] == 7
    assert sum(method == "PUT" for method, _, _ in library.events) == 1
    assert sum(path.endswith("/commit") for _, path, _ in library.events) == 1
    assert sum("/upload-requests/" in path for _, path, _ in library.events) == 2


@pytest.mark.parametrize(("stage", "status", "code", "message"), [
    ("prepare", 409, "SYNC_CONFLICT", "library head changed"),
    ("commit", 409, "SYNC_HEAD_CHANGED", "library head changed"),
    ("commit", 403, "SAVED_APP_LIMIT_REACHED", "Application limit"),
    ("commit", 413, "LIBRARY_STORAGE_FULL", "storage limit"),
    ("package", 400, "LIBRARY_INVALID_UPLOAD", "rejected the ZIP"),
    ("commit", 409, "SYNC_PACKAGE_INTEGRITY", "integrity check"),
    ("prepare", 401, "UNAUTHORIZED", "sign-in has expired"),
    ("prepare", 403, "SYNC_BINDING_CHANGED", "binding changed"),
    ("prepare", 422, "UNRECOGNIZED", "rejected the request (HTTP 422)"),
])
def test_rejected_upload_keeps_local_output(stage, status, code, message, library, monkeypatch, tmp_path, capsys):
    sign_in(monkeypatch, library)
    directory = record(tmp_path)
    library.reject = (stage, status, code)
    assert save(monkeypatch, directory) == 1
    captured = capsys.readouterr()
    assert message in captured.err
    assert TOKEN not in captured.err and AUTHORIZATION_CODE not in captured.err
    with ZipFile(directory.with_suffix(".zip")) as bundle:
        assert bundle.read("app.json") == (directory / "app.json").read_bytes()


def test_25_access_expiries_reuse_one_session_and_signout_revokes(library, monkeypatch, tmp_path):
    sign_in(monkeypatch, library)
    directory = record(tmp_path)
    session_id = BINDING["deviceSessionId"]
    for _ in range(25):
        saved = account_credentials.load()
        account_credentials.save({**saved, "expires_at": 0})
        library.sessions[session_id]["expires"] = True
        assert save(monkeypatch, directory) == 0
        renewed = account_credentials.load()
        assert renewed["binding"] == BINDING
        assert renewed["expires_at"] > saved["expires_at"]
        assert renewed["token"] != saved["token"]
        assert renewed["refresh_token"] != saved["refresh_token"]
    assert len(library.authorizations) == len(library.sessions) == len(library.requests) == 1
    assert library.refresh_count == 25
    account_credentials.save({**renewed, "expires_at": 0})
    library.sessions[session_id]["expires"] = True
    assert run_cli(monkeypatch, "sign-out") == 0
    assert library.refresh_count == 26
    assert library.sessions[session_id]["revoked"]
    assert account_credentials.load() is None
    assert save(monkeypatch, directory) == 1


def test_signout_retries_after_lost_revocation_reply(library, monkeypatch):
    sign_in(monkeypatch, library)
    library.drop = "revoke"
    assert run_cli(monkeypatch, "sign-out") == 1
    assert account_credentials.load() is not None
    assert library.sessions[BINDING["deviceSessionId"]]["revoked"]
    assert run_cli(monkeypatch, "sign-out") == 0
    assert account_credentials.load() is None


def test_expired_legacy_credential_pins_owner_and_stays_offline(library, monkeypatch, tmp_path, capsys):
    sign_in(monkeypatch, library)
    session = account_credentials.load()
    session.pop("refresh_token")
    account_credentials.save({**session, "expires_at": 0})
    library.events.clear()
    directory = record(tmp_path)
    assert save(monkeypatch, directory) == 1
    assert "sign-in has expired" in capsys.readouterr().err
    assert library.events == []
    assert directory.with_suffix(".zip").is_file()

    library.binding["deviceSessionId"] = str(uuid4())
    assert run_cli(monkeypatch, "sign-in") == 0
    assert library.authorizations[0]["state"] != library.authorizations[1]["state"]
    assert library.authorizations[0]["code_challenge"] != library.authorizations[1]["code_challenge"]
    assert save(monkeypatch, directory) == 0


@pytest.mark.parametrize("field", ["accountUserId", "tenantId", "workspaceId"])
def test_retry_rejects_a_different_library_owner(field, library, monkeypatch, tmp_path, capsys):
    sign_in(monkeypatch, library)
    directory = record(tmp_path)
    library.reject = ("package", 400, "LIBRARY_INVALID_UPLOAD")
    assert save(monkeypatch, directory) == 1
    library.binding.update({field: str(uuid4()), "deviceSessionId": str(uuid4())})
    sign_in(monkeypatch, library)
    library.events.clear()
    assert save(monkeypatch, directory) == 1
    assert "different account server, account, tenant or workspace" in capsys.readouterr().err
    assert library.events == []
    assert directory.with_suffix(".zip").is_file()


def test_retry_rejects_changed_zip_and_recovers_when_restored(library, monkeypatch, tmp_path, capsys):
    sign_in(monkeypatch, library)
    directory = record(tmp_path)
    library.reject = ("package", 400, "LIBRARY_INVALID_UPLOAD")
    assert save(monkeypatch, directory) == 1
    library.events.clear()
    zip_path = directory.with_suffix(".zip")
    original = zip_path.read_bytes()
    zip_path.write_bytes(original + b"changed")
    assert save(monkeypatch, directory) == 1
    assert "saved ZIP changed" in capsys.readouterr().err
    assert library.events == []
    assert zip_path.read_bytes() == original + b"changed"

    zip_path.write_bytes(original)
    library.reject = None
    assert save(monkeypatch, directory) == 0
    entry, = library.requests.values()
    assert entry["package"] == original and entry["receipt"]["changeSeq"] == 7


@pytest.mark.parametrize("wrong_binding", [False, True])
def test_already_synced_requires_exact_head_in_same_workspace(wrong_binding, library, monkeypatch, tmp_path, capsys):
    sign_in(monkeypatch, library)
    directory = record(tmp_path)
    library.already_synced = True
    library.wrong_head_binding = wrong_binding
    assert save(monkeypatch, directory) == int(wrong_binding)
    captured = capsys.readouterr()
    if wrong_binding:
        assert "different account server, account, tenant or workspace" in captured.err
        assert "Library automation" not in captured.out
    else:
        automation, = library.heads
        assert f"Library automation {automation}, revision {library.heads[automation]['revisionId']}" in captured.out
    assert all(method != "PUT" and not path.endswith("/commit") for method, path, _ in library.events)


def test_offline_server_keeps_local_save(library, monkeypatch, tmp_path, capsys):
    sign_in(monkeypatch, library)
    # Keep a loopback TCP port reserved without listening so it cannot be reused by a server.
    with socket.socket(socket.AF_INET) as offline:
        offline.bind(("127.0.0.1", 0))
        session = account_credentials.load()
        session["server"] = f"http://127.0.0.1:{offline.getsockname()[1]}"
        account_credentials.save(session)
        library.events.clear()
        directory = record(tmp_path)
        assert save(monkeypatch, directory) == 1
        assert "server is offline" in capsys.readouterr().err
        assert directory.is_dir() and directory.with_suffix(".zip").is_file()
        assert library.events == []
