from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from typing import Iterable, List, Optional

import pytest

from agent_android.client import AgentAndroidClient


pytestmark = pytest.mark.device

APP_PACKAGE = os.environ.get("AIVANE_E2E_APP_PACKAGE", "aivane.apprepl")
APP_COMPONENT = os.environ.get("AIVANE_E2E_APP_COMPONENT", f"{APP_PACKAGE}/.ui.ReplMainActivity")
SERVICE_COMPONENT = os.environ.get("AIVANE_E2E_SERVICE_COMPONENT", f"{APP_PACKAGE}/.api.ApiService")
HEALTHY_STATUSES = {"running", "up"}
ACCESSIBILITY_SERVICE = os.environ.get(
    "AIVANE_E2E_ACCESSIBILITY_SERVICE",
    "aivane.apprepl/aivane.android.accessibility.AIVaneAccessibilityService:0",
)


@dataclass
class DeviceContext:
    adb_serial: Optional[str]
    base_url: str
    client: AgentAndroidClient


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _run(command: List[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=check, capture_output=True, text=True)


def _discover_adb_serial() -> Optional[str]:
    forced = os.environ.get("AIVANE_E2E_ADB_SERIAL")
    if forced:
        return forced.strip()

    try:
        result = _run(["adb", "devices"], check=True)
    except FileNotFoundError:
        return None
    except subprocess.CalledProcessError:
        return None

    devices = []
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("List of devices attached"):
            continue
        parts = stripped.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])

    return devices[0] if len(devices) == 1 else None


def _derive_base_url(adb_serial: Optional[str]) -> Optional[str]:
    explicit = os.environ.get("AIVANE_E2E_URL")
    if explicit:
        return explicit.strip().rstrip("/")
    if adb_serial and ":" in adb_serial:
        host, _port = adb_serial.rsplit(":", 1)
        return f"http://{host}:8080"
    return None


def _adb(command: Iterable[str], adb_serial: Optional[str]) -> subprocess.CompletedProcess[str]:
    base = ["adb"]
    if adb_serial:
        base.extend(["-s", adb_serial])
    base.extend(command)
    return _run(base, check=False)


def _is_adb_serial_healthy(adb_serial: Optional[str]) -> bool:
    if not adb_serial:
        return False
    result = _adb(["get-state"], adb_serial)
    return result.returncode == 0 and result.stdout.strip() == "device"


def _wait_for_health(base_url: str, timeout_seconds: int = 20) -> dict:
    deadline = time.time() + timeout_seconds
    last_error: Optional[Exception] = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{base_url}/health", timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - exercised against live device
            last_error = exc
            time.sleep(1)
    pytest.fail(f"Timed out waiting for {base_url}/health: {last_error}")


def _assert_healthy_status(health: dict) -> None:
    assert health["status"] in HEALTHY_STATUSES


def _bring_apprepl_to_front(ctx: DeviceContext) -> None:
    if ctx.adb_serial and _is_adb_serial_healthy(ctx.adb_serial):
        _adb(["shell", "am", "start", "-n", APP_COMPONENT], ctx.adb_serial)
        _adb(["shell", "am", "start-foreground-service", "-n", SERVICE_COMPONENT], ctx.adb_serial)
        time.sleep(2)
        return

    ctx.client.launch_app(APP_PACKAGE)
    time.sleep(2)


def _fetch_tree_with_retries(client: AgentAndroidClient, attempts: int = 3) -> list[dict]:
    last_elements: Optional[list[dict]] = None
    for _attempt in range(attempts):
        elements = client.get_ui_elements(wait=1, force_refresh=True)
        if elements:
            return elements
        last_elements = elements
        time.sleep(1)
    pytest.fail(f"Failed to fetch UI tree from device after {attempts} attempts: {last_elements}")


def _find_first_ref_id(elements: list[dict], *, contains_text: str) -> Optional[int]:
    needle = contains_text.lower()
    for elem in elements:
        text = str(elem.get("text", "") or elem.get("contentDesc", "") or "")
        if needle in text.lower():
            ref_id = elem.get("refId")
            if isinstance(ref_id, int):
                return ref_id
    return None


def _find_ref_id_by_resource_id(elements: list[dict], resource_id: str) -> Optional[int]:
    for elem in elements:
        if elem.get("resourceId") == resource_id and isinstance(elem.get("refId"), int):
            return elem["refId"]
    return None


def _find_first_ref_id_by_text_any(elements: list[dict], *, candidates: Iterable[str]) -> Optional[int]:
    lowered = [entry.lower() for entry in candidates]
    for elem in elements:
        ref_id = elem.get("refId")
        if not isinstance(ref_id, int):
            continue
        text = str(elem.get("text", "") or elem.get("contentDesc", "") or "").lower()
        if any(token in text for token in lowered):
            return ref_id
    return None


def _is_setup_screen(elements: list[dict]) -> bool:
    if any(elem.get("resourceId") == "aivane.apprepl:id/tokenEdit" for elem in elements):
        return True

    active_label = next(
        (str(elem.get("text", "")) for elem in elements if elem.get("resourceId") == "aivane.apprepl:id/activeScreenLabel"),
        "",
    )
    return active_label.lower() == "setup"


def _pick_safe_tap_target_ref_id(elements: list[dict]) -> Optional[int]:
    for resource_id in (
        "aivane.apprepl:id/copyBaseButton",
        "aivane.apprepl:id/tabSetup",
        "aivane.apprepl:id/tabRun",
        "aivane.apprepl:id/tabConsole",
        "aivane.apprepl:id/startButton",
    ):
        ref_id = _find_ref_id_by_resource_id(elements, resource_id)
        if ref_id is not None:
            return ref_id

    by_text = _find_first_ref_id_by_text_any(
        elements,
        candidates=("base url", "setup", "run", "console"),
    )
    if by_text is not None:
        return by_text

    for elem in elements:
        ref_id = elem.get("refId")
        if not isinstance(ref_id, int):
            continue
        if not elem.get("clickable"):
            continue
        text = str(elem.get("text", "") or elem.get("contentDesc", "") or "")
        resource_id = str(elem.get("resourceId", "") or "").lower()
        if "stop" in text.lower() or "stop" in resource_id:
            continue
        return ref_id

    return None


def _ensure_setup_screen(ctx: DeviceContext) -> list[dict]:
    elements = _fetch_tree_with_retries(ctx.client)
    if _is_setup_screen(elements):
        return elements

    setup_tab_ref_id = _find_ref_id_by_resource_id(elements, "aivane.apprepl:id/tabSetup")
    if setup_tab_ref_id is None:
        setup_tab_ref_id = _find_first_ref_id_by_text_any(elements, candidates=("setup",))
    if setup_tab_ref_id is None:
        pytest.fail("Could not find the setup tab in the current apprepl UI tree.")

    assert ctx.client.tap_element(setup_tab_ref_id) is True
    time.sleep(1)
    return _fetch_tree_with_retries(ctx.client)


@pytest.fixture(scope="session")
def device_context() -> DeviceContext:
    adb_serial = _discover_adb_serial()
    base_url = _derive_base_url(adb_serial)

    if not base_url:
        pytest.skip("No device test target found. Set AIVANE_E2E_URL or connect exactly one ADB-over-LAN device.")

    if adb_serial and not _is_adb_serial_healthy(adb_serial):
        adb_serial = None

    if adb_serial and not _env_flag("AIVANE_E2E_SKIP_ADB_PREP"):
        _adb(
            [
                "shell",
                "settings",
                "put",
                "secure",
                "enabled_accessibility_services",
                ACCESSIBILITY_SERVICE,
            ],
            adb_serial,
        )
        _adb(["shell", "settings", "put", "secure", "accessibility_enabled", "1"], adb_serial)
        _adb(["shell", "am", "start", "-n", APP_COMPONENT], adb_serial)
        _adb(["shell", "am", "start-foreground-service", "-n", SERVICE_COMPONENT], adb_serial)

    health = _wait_for_health(base_url)
    _assert_healthy_status(health)

    return DeviceContext(adb_serial=adb_serial, base_url=base_url, client=AgentAndroidClient(base_url))


def test_health_endpoint_reports_running(device_context: DeviceContext):
    health = _wait_for_health(device_context.base_url, timeout_seconds=5)

    assert health["service"] == "aivane-repl"
    _assert_healthy_status(health)


def test_launcher_apps_contains_aivane_entry(device_context: DeviceContext):
    apps = device_context.client.list_launcher_apps()

    assert apps
    assert any(app.get("package") == APP_PACKAGE for app in apps)


def test_apprepl_ui_tree_is_fetchable(device_context: DeviceContext):
    _bring_apprepl_to_front(device_context)
    elements = _fetch_tree_with_retries(device_context.client)

    assert device_context.client.get_current_package_name() == APP_PACKAGE
    assert any("AIVane" in str(elem.get("text", "")) for elem in elements)
    assert _pick_safe_tap_target_ref_id(elements) is not None


def test_apprepl_safe_tap_and_relaunch(device_context: DeviceContext):
    _bring_apprepl_to_front(device_context)
    elements = _fetch_tree_with_retries(device_context.client)
    target_ref_id = _pick_safe_tap_target_ref_id(elements)

    assert target_ref_id is not None
    assert device_context.client.tap_element(target_ref_id) is True
    assert device_context.client.press_key("home") is True
    assert device_context.client.launch_app(APP_PACKAGE) is True


@pytest.mark.skipif(
    not _env_flag("AIVANE_E2E_ENABLE_MUTATIONS"),
    reason="Set AIVANE_E2E_ENABLE_MUTATIONS=1 to exercise input actions on a real device.",
)
def test_apprepl_token_field_accepts_input(device_context: DeviceContext):
    _bring_apprepl_to_front(device_context)
    elements = _ensure_setup_screen(device_context)
    edit_ref_id = next(
        (
            elem.get("refId")
            for elem in elements
            if elem.get("resourceId") == "aivane.apprepl:id/tokenEdit" and isinstance(elem.get("refId"), int)
        ),
        None,
    )
    if edit_ref_id is None:
        edit_ref_id = next(
            (
                elem.get("refId")
                for elem in elements
                if elem.get("simpleClassName") == "EditText" and isinstance(elem.get("refId"), int)
            ),
            None,
        )

    assert edit_ref_id is not None
    assert device_context.client.input_to_element(edit_ref_id, "codex-device-smoke") is True


@pytest.mark.skipif(
    not _env_flag("AIVANE_E2E_ENABLE_SCREENSHOT"),
    reason="Set AIVANE_E2E_ENABLE_SCREENSHOT=1 after granting screenshot permission on the device.",
)
def test_screenshot_capture_succeeds(device_context: DeviceContext, tmp_path):
    output_path = tmp_path / "device-smoke.png"

    saved_path = device_context.client.screenshot(output_path=str(output_path))
    assert saved_path == str(output_path)
    assert output_path.exists()
    assert output_path.stat().st_size > 0
