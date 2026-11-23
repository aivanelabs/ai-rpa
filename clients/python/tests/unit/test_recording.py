import json
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

from agent_android import cli, repl
from agent_android.client import AgentAndroidClient
from agent_android.recording import ActionSession


URL = "http://127.0.0.1:8080"


@pytest.fixture(autouse=True)
def local_state(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    monkeypatch.setattr(repl, "_HAS_READLINE", False)


def run_cli(monkeypatch, *args, url=URL, session="demo"):
    monkeypatch.setattr(sys, "argv", ["agent-android", *args, "--url", url, "--session", session])
    try:
        return cli.main()
    except SystemExit as exc:
        return exc.code


def test_recording_requires_a_confirmed_mutation(monkeypatch):
    monkeypatch.setattr(AgentAndroidClient, "_api_call", lambda *args, **kwargs: {"success": True})
    monkeypatch.setattr(AgentAndroidClient, "get_health", lambda self: {"status": "running"})
    assert run_cli(monkeypatch, "--health") == 0
    assert not ActionSession(URL, "demo").path.exists()

    for response in (None, {}, {"success": False}, {"success": "true"}):
        monkeypatch.setattr(AgentAndroidClient, "_api_call", lambda *args, **kwargs: response)
        run_cli(monkeypatch, "--back")
        assert not ActionSession(URL, "demo").path.exists()


def test_chooser_response_is_not_a_launch(monkeypatch):
    response = {"success": True, "data": {"outputs": {"launchResult": {
        "status": "selection_required", "launched": False,
    }}}}
    monkeypatch.setattr(AgentAndroidClient, "_api_call", lambda *args, **kwargs: response)
    assert run_cli(monkeypatch, "--launch", "com.example") == 2
    assert not ActionSession(URL, "demo").path.exists()

    response["data"]["outputs"]["launchResult"] = {"status": "launched", "launched": True}
    assert run_cli(monkeypatch, "--launch", "com.example", "--launch-choice", "2") == 0
    record = json.loads(ActionSession(URL, "demo").path.read_text(encoding="utf-8"))
    assert record["operationType"] == "android.app.launch"
    assert record["parameters"] == {
        "packageName": "com.example", "choiceIndex": 2, "timeoutMs": 8000, "selectionHandling": "fail",
    }


def test_cli_and_repl_save_one_application_with_inputs(monkeypatch, tmp_path):
    monkeypatch.setattr(AgentAndroidClient, "_api_call", lambda *args, **kwargs: {"success": True})
    monkeypatch.setattr(AgentAndroidClient, "_resolve_xpath_input_target", lambda *args: ({}, {}, None))
    assert run_cli(monkeypatch, "--tap-xpath", "//Button") == 0

    commands = iter(["p home", "ix //EditText -- practice text", "ix //EditText --", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(commands))
    assert run_cli(monkeypatch, "--repl", url=URL + "/") == 0

    record = ActionSession(URL, "demo").path
    recorded = record.read_text(encoding="utf-8")
    assert "practice text" not in recorded
    assert len(recorded.splitlines()) == 4
    assert not ActionSession(URL, "other").path.exists()
    assert not ActionSession("http://127.0.0.1:8081", "demo").path.exists()

    def fail_if_contacted(*args, **kwargs):
        pytest.fail("Save must not construct a phone client")

    monkeypatch.setattr(cli, "AgentAndroidClient", fail_if_contacted)
    destination = tmp_path / "application.v1"
    assert run_cli(monkeypatch, "save", str(destination)) == 0
    with ZipFile(tmp_path / "application.v1.zip") as bundle:
        assert set(bundle.namelist()) == {"app.json", "__main__.json"}
        for name in bundle.namelist():
            assert bundle.read(name) == (destination / name).read_bytes()
    app = json.loads((destination / "app.json").read_text(encoding="utf-8"))
    main = json.loads((destination / "__main__.json").read_text(encoding="utf-8"))
    assert app["mainTemplateId"] == main["templateId"] == "__main__"
    assert main["parameters"] == [{"name": "input_1", "type": "STRING", "direction": "INPUT", "required": True}]
    assert [op["operationType"] for op in main["operations"]] == [
        "android.touch.tap", "android.press.home", "android.element.input", "android.element.input",
    ]
    assert main["operations"][2]["parameters"]["value"] == "${input_1}"
    assert main["operations"][3]["parameters"]["value"] == ""


def test_empty_save_does_not_create_output(monkeypatch, tmp_path):
    destination = tmp_path / "empty"
    assert run_cli(monkeypatch, "save", str(destination)) == 1
    assert not destination.exists()
    assert not destination.with_suffix(".zip").exists()


def test_lint_error_exits_nonzero_and_removes_invalid_output(monkeypatch, tmp_path, capfd):
    ActionSession(URL, "demo").append("android.touch.tap", {"mode": "coordinate"})
    destination = tmp_path / "invalid"
    assert run_cli(monkeypatch, "save", str(destination)) == 1
    assert "T004" in capfd.readouterr().out
    assert not destination.exists()
    assert not destination.with_suffix(".zip").exists()


def test_save_preserves_existing_zip(monkeypatch, tmp_path):
    ActionSession(URL, "demo").append("android.press.back", {})
    destination = tmp_path / "application"
    archive = destination.with_suffix(".zip")
    archive.write_bytes(b"existing archive")
    assert run_cli(monkeypatch, "save", str(destination)) == 1
    assert not destination.exists()
    assert archive.read_bytes() == b"existing archive"
