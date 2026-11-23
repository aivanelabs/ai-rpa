from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
from contextlib import ExitStack
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlsplit

from .config import normalize_base_url

DEFAULT_SESSION = "default"
MAIN_TEMPLATE = "__main__"

# Only the replay parameters of supported interactive commands may be stored.
# Text-entry payloads are handled separately from locator strings.
REPLAY_PARAMETERS = {
    "android.app.launch": ("packageName", "choiceIndex", "choiceText", "timeoutMs", "selectionHandling"),
    "android.element.input": ("id", "xpath", "x", "y", "clearFirst"),
    "android.touch.tap": ("mode", "x", "y", "id", "xpath"),
    "android.touch.swipe": ("mode", "area", "type", "direction", "duration", "distance", "xpath"),
    "android.press.back": (),
    "android.press.home": (),
    "android.press.recents": (),
    "android.press.menu": (),
}


def _lock_record(handle) -> None:
    # Keep concurrent CLI writes and save reads from observing partial lines.
    # Closing the file releases the lock on both platforms.
    if os.name == "nt":
        import msvcrt

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
    else:
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)


class ActionSession:
    """Local record of successful interactive operations for one phone endpoint."""

    def __init__(self, base_url: str, name: str):
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", name):
            raise ValueError("Session name must use lowercase letters, digits, hyphens or underscores (1-80 characters).")
        if re.fullmatch(r"con|prn|aux|nul|com[1-9]|lpt[1-9]", name):
            raise ValueError(f"Reserved session name: {name}")
        endpoint = urlsplit(normalize_base_url(base_url))
        port = endpoint.port or {"http": 80, "https": 443}.get(endpoint.scheme)
        identity = (endpoint.scheme, endpoint.hostname, port, endpoint.path.rstrip("/"))
        device = hashlib.sha256(json.dumps(identity).encode("utf-8")).hexdigest()
        self.name = name
        self.path = Path.home() / ".aivane" / "agent-android" / "sessions" / device / f"{name}.jsonl"

    def append(self, operation_type: str, parameters: Dict[str, Any]) -> None:
        action = self._replay_action(operation_type, parameters)
        line = (json.dumps(action, ensure_ascii=False) + "\n").encode("utf-8")
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with self.path.open("a+b") as handle:
            _lock_record(handle)
            handle.seek(0, os.SEEK_END)
            if handle.tell():
                handle.seek(-1, os.SEEK_END)
                if handle.read(1) != b"\n":
                    handle.seek(0)
                    complete, separator, tail = handle.read().rpartition(b"\n")
                    try:
                        json.loads(tail)
                    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                        self._warn_torn_line(exc)
                        handle.truncate(len(complete) + len(separator))
                    else:
                        handle.write(b"\n")
            handle.write(line)

    @staticmethod
    def _replay_action(operation_type: str, parameters: Dict[str, Any], *, text_input: bool = False) -> Dict[str, Any]:
        allowed = REPLAY_PARAMETERS.get(operation_type)
        if allowed is None:
            raise ValueError("Operation is unsupported by the action recorder")
        replay = {
            key: parameters[key] for key in allowed
            if isinstance(parameters.get(key), (str, bool, int, float))
        }
        action: Dict[str, Any] = {"operationType": operation_type, "parameters": replay}
        if operation_type == "android.element.input":
            if text_input or ("value" in parameters and parameters["value"] != ""):
                action["textInput"] = True
            elif "value" in parameters:
                replay["value"] = ""
        return action

    def _warn_torn_line(self, exc: Exception) -> None:
        print(
            f"Warning: skipping a torn trailing line in session {self.name!r}: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )

    def clear(self) -> None:
        try:
            handle = self.path.open("r+b")
        except FileNotFoundError:
            return
        with handle:
            _lock_record(handle)
            # Keep the file in place so concurrent readers and writers share its lock.
            handle.truncate(0)

    def _read_actions(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            raise ValueError(f"No successful actions recorded in session {self.name!r}")
        actions = []
        with self.path.open("rb") as handle:
            _lock_record(handle)
            for line_number, line in enumerate(handle, start=1):
                try:
                    action = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    if handle.peek(1):
                        raise ValueError(f"Invalid JSON in session {self.name!r}, line {line_number}") from exc
                    self._warn_torn_line(exc)
                    break
                if not isinstance(action, dict) or not isinstance(action.get("parameters"), dict):
                    raise ValueError(f"Expected a parameters object in session {self.name!r}, line {line_number}")
                operation_type = action.get("operationType")
                if not isinstance(operation_type, str):
                    raise ValueError(f"Expected an operationType in session {self.name!r}, line {line_number}")
                actions.append(self._replay_action(operation_type, action["parameters"], text_input=action.get("textInput") is True))
        if not actions:
            raise ValueError(f"No successful actions recorded in session {self.name!r}")
        return actions

    def save(self, directory: Path) -> Path:
        actions = self._read_actions()
        directory = directory.expanduser().resolve()
        zip_path = directory.with_name(directory.name + ".zip")
        ascii_name = unicodedata.normalize("NFKD", directory.name).encode("ascii", "ignore").decode("ascii").lower()
        application_id = re.sub(r"[^a-z0-9_.-]+", "-", ascii_name)[:120].strip("_.-")
        if not application_id:
            application_id = "app-" + hashlib.sha256(directory.name.encode("utf-8")).hexdigest()[:12]
        linter = shutil.which("aivane-template-lint")
        if not linter:
            raise FileNotFoundError("Install aivane-template-linter and put aivane-template-lint on PATH")

        inputs = []
        for action in actions:
            parameters = action["parameters"]
            if (
                parameters.get("mode") == "coordinate"
                or action["operationType"] == "android.element.input" and "x" in parameters and "y" in parameters
            ):
                action["description"] = "Coordinate-only target. Replay depends on the screen layout."
            if action["operationType"] == "android.app.launch" and "choiceIndex" in parameters:
                action["description"] = "Unstable chooser index. Replay depends on the current chooser order."
            if action.pop("textInput", False):
                name = f"input_{len(inputs) + 1}"
                inputs.append({"name": name, "type": "STRING", "direction": "INPUT", "required": True})
                parameters["value"] = "${" + name + "}"

        documents = {
            "app.json": {
                "applicationId": application_id,
                "applicationName": directory.name,
                "version": "1.0.0",
                "mainTemplateId": MAIN_TEMPLATE,
            },
            f"{MAIN_TEMPLATE}.json": {
                "templateId": MAIN_TEMPLATE,
                "templateName": directory.name,
                "parameters": inputs,
                "operations": actions,
            },
        }

        directory.parent.mkdir(parents=True, exist_ok=True)
        with ExitStack() as rollback:
            directory.mkdir()
            rollback.callback(directory.rmdir)
            for name, document in documents.items():
                path = directory / name
                with path.open("x", encoding="utf-8") as handle:
                    rollback.callback(path.unlink)
                    json.dump(document, handle, ensure_ascii=False, indent=2)
                    handle.write("\n")
            with zip_path.open("xb") as handle:
                rollback.callback(zip_path.unlink)
                with zipfile.ZipFile(handle, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
                    for name in documents:
                        bundle.write(directory / name, arcname=name)
            subprocess.run([linter, str(directory), "-r", "--platform", "android"], check=True)
            rollback.pop_all()
        return zip_path
