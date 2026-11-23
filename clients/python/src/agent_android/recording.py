from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile
from contextlib import ExitStack
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlsplit


DEFAULT_SESSION = "default"
MAIN_TEMPLATE = "__main__"


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
        endpoint = urlsplit(base_url.strip())
        port = endpoint.port or {"http": 80, "https": 443}.get(endpoint.scheme)
        identity = (endpoint.scheme, endpoint.hostname, port, endpoint.path.rstrip("/"))
        device = hashlib.sha256(json.dumps(identity).encode("utf-8")).hexdigest()
        self.name = name
        self.path = Path.home() / ".aivane" / "agent-android" / "sessions" / device / f"{name}.jsonl"

    def append(self, operation_type: str, parameters: Dict[str, Any]) -> None:
        parameters = dict(parameters)
        action: Dict[str, Any] = {"operationType": operation_type, "parameters": parameters}
        if operation_type == "android.element.input" and parameters.get("value"):
            del parameters["value"]
            action["textInput"] = True
        line = (json.dumps(action, ensure_ascii=False) + "\n").encode("utf-8")
        try:
            self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            with self.path.open("ab") as handle:
                _lock_record(handle)
                handle.write(line)
        except OSError as exc:
            raise OSError("Phone action succeeded but could not be recorded locally") from exc

    def _read_actions(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            raise ValueError(f"No successful actions recorded in session {self.name!r}")
        with self.path.open("rb") as handle:
            _lock_record(handle)
            actions = [json.loads(line) for line in handle]
        if not actions:
            raise ValueError(f"No successful actions recorded in session {self.name!r}")
        return actions

    def save(self, directory: Path) -> Path:
        actions = self._read_actions()
        directory = directory.expanduser().resolve()
        zip_path = directory.with_name(directory.name + ".zip")
        linter = shutil.which("aivane-template-lint")
        if not linter:
            raise FileNotFoundError("Install aivane-template-linter and put aivane-template-lint on PATH")

        inputs = []
        for action in actions:
            if action.pop("textInput", False):
                name = f"input_{len(inputs) + 1}"
                inputs.append({"name": name, "type": "STRING", "direction": "INPUT", "required": True})
                action["parameters"]["value"] = "${" + name + "}"

        documents = {
            "app.json": {
                "applicationId": directory.name,
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
