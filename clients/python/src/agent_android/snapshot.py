from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


SNAPSHOT_FILE_PATH = Path(os.path.expanduser("~/.agent-android-snapshot.json"))


def load_snapshot(base_url: str) -> Optional[Dict[str, Any]]:
    if not SNAPSHOT_FILE_PATH.exists():
        return None
    try:
        data = json.loads(SNAPSHOT_FILE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    if data.get("baseUrl") != base_url:
        return None
    if not isinstance(data.get("elements"), list):
        return None
    return data


def save_snapshot(base_url: str, package_name: Optional[str], elements: List[Dict[str, Any]]) -> None:
    payload = {
        "baseUrl": base_url,
        "packageName": package_name,
        "savedAt": int(time.time()),
        "elements": elements,
    }
    SNAPSHOT_FILE_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def find_snapshot_element(snapshot: Dict[str, Any], ref_id: int) -> Optional[Dict[str, Any]]:
    elements = snapshot.get("elements")
    if not isinstance(elements, list):
        return None
    for elem in elements:
        if isinstance(elem, dict) and elem.get("refId") == ref_id:
            return elem
    return None
