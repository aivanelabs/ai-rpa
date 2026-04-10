from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from agent_android import cli as cli_module


def test_main_apps_command_exits_zero_and_prints_app_list(monkeypatch, capsys):
    class FakeClient:
        def __init__(self, url, token=None):
            self.base_url = url
            self.token = token

        def list_launcher_apps(self):
            return [{"label": "Calculator", "package": "pkg.calc", "activity": "MainActivity"}]

    monkeypatch.setattr(cli_module, "AgentAndroidClient", FakeClient)
    monkeypatch.setattr(sys, "argv", ["agent-android.py", "--url", "http://device:8080", "--apps"])

    with pytest.raises(SystemExit) as exc_info:
        cli_module.main()

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert "Launcher apps:" in captured.out
    assert "Calculator - pkg.calc [MainActivity]" in captured.out


def test_main_health_command_exits_zero_and_prints_payload(monkeypatch, capsys):
    class FakeClient:
        def __init__(self, url, token=None):
            self.base_url = url
            self.token = token

        def get_health(self):
            return {"service": "aivane-repl", "status": "running"}

    monkeypatch.setattr(cli_module, "AgentAndroidClient", FakeClient)
    monkeypatch.setattr(sys, "argv", ["agent-android.py", "--url", "http://device:8080", "--health"])

    with pytest.raises(SystemExit) as exc_info:
        cli_module.main()

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert json.loads(captured.out) == {"service": "aivane-repl", "status": "running"}


def test_main_health_command_failure_mentions_connection_hints(monkeypatch, capsys):
    class FakeClient:
        def __init__(self, url, token=None):
            self.base_url = url
            self.token = token

        def get_health(self):
            return None

    monkeypatch.setattr(cli_module, "AgentAndroidClient", FakeClient)
    monkeypatch.setattr(sys, "argv", ["agent-android.py", "--url", "http://device:8080", "--health"])

    with pytest.raises(SystemExit) as exc_info:
        cli_module.main()

    captured = capsys.readouterr()
    assert exc_info.value.code == 1
    assert "Check the connection hints above." in captured.err


def test_main_list_raw_writes_output_file(monkeypatch, tmp_path, capsys):
    elements = [{"refId": 1, "text": "Search"}]

    class FakeClient:
        def __init__(self, url, token=None):
            self.base_url = url
            self.token = token

        def get_ui_elements(self, wait=0, force_refresh=False, visible_only=True):
            assert wait == 0
            assert force_refresh is False
            assert visible_only is True
            return elements

    output_path = tmp_path / "tree.json"
    monkeypatch.setattr(cli_module, "AgentAndroidClient", FakeClient)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "agent-android.py",
            "--url",
            "http://device:8080",
            "--list",
            "--raw",
            "--output",
            str(output_path),
        ],
    )

    assert cli_module.main() == 0

    captured = capsys.readouterr()
    assert json.loads(captured.out) == elements
    assert json.loads(output_path.read_text(encoding="utf-8")) == elements
    assert "ARIA tree saved to:" in captured.err


def test_main_list_include_offscreen_passes_flag(monkeypatch, capsys):
    class FakeClient:
        def __init__(self, url, token=None):
            self.base_url = url
            self.token = token

        def get_ui_elements(self, wait=0, force_refresh=False, visible_only=True):
            assert wait == 0
            assert force_refresh is False
            assert visible_only is False
            return [{"refId": 2, "text": "Offscreen"}]

    monkeypatch.setattr(cli_module, "AgentAndroidClient", FakeClient)
    monkeypatch.setattr(
        sys,
        "argv",
        ["agent-android.py", "--url", "http://device:8080", "--list", "--include-offscreen", "--raw"],
    )

    assert cli_module.main() == 0
    assert json.loads(capsys.readouterr().out) == [{"refId": 2, "text": "Offscreen"}]


def test_main_wait_for_command_reports_match(monkeypatch, capsys):
    class FakeClient:
        def __init__(self, url, token=None):
            self.base_url = url
            self.token = token

        def wait_for_element(self, text=None, timeout=30):
            assert text == "Search"
            assert timeout == 12
            return {"refId": 8, "text": "Search", "simpleClassName": "TextView", "x": 10, "y": 20}

    monkeypatch.setattr(cli_module, "AgentAndroidClient", FakeClient)
    monkeypatch.setattr(
        sys,
        "argv",
        ["agent-android.py", "--url", "http://device:8080", "--wait-for", "Search", "--timeout", "12"],
    )

    with pytest.raises(SystemExit) as exc_info:
        cli_module.main()

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert "Waiting for element 'Search' (timeout=12s)" in captured.err
    assert "refId=8 found: text='Search' class=TextView at (10, 20)" in captured.out


def test_main_health_passes_token_to_client(monkeypatch):
    seen = {}

    class FakeClient:
        def __init__(self, url, token=None):
            seen["url"] = url
            seen["token"] = token
            self.base_url = url

        def get_health(self):
            return {"service": "aivane-repl", "status": "running"}

    monkeypatch.setattr(cli_module, "AgentAndroidClient", FakeClient)
    monkeypatch.setattr(sys, "argv", ["agent-android.py", "--url", "http://device:8080", "--token", "shared-secret", "--health"])

    with pytest.raises(SystemExit) as exc_info:
        cli_module.main()

    assert exc_info.value.code == 0
    assert seen == {"url": "http://device:8080", "token": "shared-secret"}


def test_main_template_executes_payload_and_prints_response(monkeypatch, tmp_path, capsys):
    seen = {}
    template_path = tmp_path / "template.json"
    template_payload = {"templateId": "smoke-template", "operations": []}
    template_path.write_text(json.dumps(template_payload), encoding="utf-8")

    class FakeClient:
        def __init__(self, url, token=None):
            seen["url"] = url
            seen["token"] = token
            self.base_url = url

        def execute_template_payload(self, payload):
            seen["payload"] = payload
            return {"success": True, "data": {"runStatus": "SUCCESS"}}

    monkeypatch.setattr(cli_module, "AgentAndroidClient", FakeClient)
    monkeypatch.setattr(
        sys,
        "argv",
        ["agent-android.py", "--url", "http://device:8080", "--token", "shared-secret", "--template", str(template_path)],
    )

    with pytest.raises(SystemExit) as exc_info:
        cli_module.main()

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert seen == {
        "url": "http://device:8080",
        "token": "shared-secret",
        "payload": template_payload,
    }
    assert json.loads(captured.out) == {"success": True, "data": {"runStatus": "SUCCESS"}}


def test_main_template_reports_missing_file(monkeypatch, capsys):
    class FakeClient:
        def __init__(self, url, token=None):
            self.base_url = url

    monkeypatch.setattr(cli_module, "AgentAndroidClient", FakeClient)
    monkeypatch.setattr(
        sys,
        "argv",
        ["agent-android.py", "--url", "http://device:8080", "--template", str(Path("missing-template.json"))],
    )

    with pytest.raises(SystemExit) as exc_info:
        cli_module.main()

    captured = capsys.readouterr()
    assert exc_info.value.code == 1
    assert "Template file not found:" in captured.err


def test_cli_help_mentions_new_repl_commands(capsys):
    parser = cli_module.build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--help"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert "node <N>" in captured.out
    assert "mx <ids>" in captured.out
    assert "vn <xpath>" in captured.out
    assert "ux [path] [--all]" in captured.out
    assert "p <key>                   Press a system key (back/home/recents)" in captured.out
