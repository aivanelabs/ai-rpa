from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

CONFIG_FILE_PATH = Path(os.path.expanduser("~/.agent-android.json"))
CONFIG_URL_KEY = "url"
CONFIG_TOKEN_KEY = "token"
TOKEN_ENV_VAR = "AIVANE_API_TOKEN"

def _load_saved_config() -> Dict[str, Any]:
    if not CONFIG_FILE_PATH.exists():
        return {}
    try:
        raw = CONFIG_FILE_PATH.read_text(encoding="utf-8")
    except OSError:
        return {}
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    return {}


def load_saved_url() -> Optional[str]:
    config = _load_saved_config()
    url = config.get(CONFIG_URL_KEY)
    if isinstance(url, str):
        stripped = url.strip()
        if stripped:
            return stripped
    return None


def load_saved_token() -> Optional[str]:
    config = _load_saved_config()
    token = config.get(CONFIG_TOKEN_KEY)
    if isinstance(token, str):
        stripped = token.strip()
        if stripped:
            return stripped
    return None


def _write_partial_config(key: str, value: Optional[str]) -> None:
    CONFIG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = _load_saved_config()
    if value is None:
        payload.pop(key, None)
    else:
        payload[key] = value.strip()
    CONFIG_FILE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_url_to_config(url: str) -> None:
    _write_partial_config(CONFIG_URL_KEY, url)


def save_token_to_config(token: Optional[str]) -> None:
    normalized = token.strip() if isinstance(token, str) and token.strip() else None
    _write_partial_config(CONFIG_TOKEN_KEY, normalized)


def resolve_base_url(cmdline_url: Optional[str]) -> Optional[str]:
    if cmdline_url:
        trimmed = cmdline_url.strip()
        if trimmed:
            return trimmed
    return load_saved_url()


def resolve_api_token(cmdline_token: Optional[str]) -> Optional[str]:
    if cmdline_token:
        trimmed = cmdline_token.strip()
        if trimmed:
            return trimmed
    env_token = os.environ.get(TOKEN_ENV_VAR)
    if env_token:
        trimmed = env_token.strip()
        if trimmed:
            return trimmed
    return load_saved_token()


def require_base_url(cmdline_url: Optional[str]) -> str:
    url = resolve_base_url(cmdline_url)
    if url:
        return url
    print(
        "AIVane server URL is required. Provide it via `--url` or run "
        "`agent-android --repl` and `set url <url>` to persist it under "
        f"{CONFIG_FILE_PATH}.",
        file=sys.stderr,
    )
    sys.exit(2)
