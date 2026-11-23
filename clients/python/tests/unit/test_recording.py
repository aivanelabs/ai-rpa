import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile

import pytest

from agent_android import cli, repl, snapshot
from agent_android.client import AgentAndroidClient
from agent_android.recording import ActionSession


URL = "http://127.0.0.1:8080"


@pytest.fixture(autouse=True)
def local_state(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    monkeypatch.setattr(repl, "_HAS_READLINE", False)


def run_cli(monkeypatch, *args, url=URL, session="demo"):
    argv = ["agent-android", *args]
    if url is not None:
        argv.extend(["--url", url])
    if session is not None:
        argv.extend(["--session", session])
    monkeypatch.setattr(sys, "argv", argv)
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


def test_recording_failure_keeps_successful_command_successful(monkeypatch, capsys):
    monkeypatch.setattr(AgentAndroidClient, "_api_call", lambda *args, **kwargs: {"success": True})

    def fail_to_record(*args):
        raise OSError("append failed") from PermissionError("read-only session")

    monkeypatch.setattr(ActionSession, "append", fail_to_record)
    assert run_cli(monkeypatch, "--back") == 0
    output = capsys.readouterr()
    assert "Warning: phone action succeeded but could not be recorded locally." in output.err
    assert "OSError: append failed" in output.err
    assert "PermissionError: read-only session" in output.err
    assert "Pressed back" in output.out


@pytest.mark.parametrize("operation_type", ["android.clipboard.set", "android.keyboard.type", "android.keyboard.paste"])
def test_unrecognized_text_operations_are_never_recorded(monkeypatch, capsys, operation_type):
    client = AgentAndroidClient(URL)
    client.action_session = ActionSession(URL, "demo")
    entered = {"text": "example text", "clipboard": {"contents": "example contents"}}
    monkeypatch.setattr(client, "_execute_single_operation", lambda *args: {"success": True})
    assert client._run_single_operation("test-text-action", operation_type, entered, "Action succeeded", "Failed")
    output = capsys.readouterr()
    assert "unsupported by the action recorder" in output.err
    assert "example text" not in output.out + output.err
    assert not client.action_session.path.exists()


def test_recorder_omits_unrecognized_parameter_values(monkeypatch, tmp_path):
    session = ActionSession(URL, "demo")
    session.append("android.element.input", {
        "id": "example:id/input", "value": "typed sample", "clipboardText": "clipboard sample",
    })
    session.append("android.touch.tap", {
        "mode": "locator", "xpath": "//*[@text='Visible label']", "textToType": "tap parameter sample",
    })
    destination = tmp_path / "application"
    assert run_cli(monkeypatch, "save", str(destination)) == 0
    template = (destination / "__main__.json").read_text(encoding="utf-8")
    assert all("sample" not in data for data in (template, session.path.read_text(encoding="utf-8")))
    assert "${input_1}" in template
    assert "Visible label" in template and "Visible label" in session.path.read_text(encoding="utf-8")


def test_chooser_response_is_not_a_launch(monkeypatch, tmp_path):
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
    destination = tmp_path / "chooser"
    assert run_cli(monkeypatch, "save", str(destination)) == 0
    main = json.loads((destination / "__main__.json").read_text(encoding="utf-8"))
    assert main["operations"] == [{
        **record,
        "description": "Unstable chooser index. Replay depends on the current chooser order.",
    }]


@pytest.mark.parametrize(
    ("attributes", "locator"),
    [
        ({"resourceId": "example:id/port", "contentDesc": "Port", "text": "8080"}, {"id": "example:id/port"}),
        ({"contentDesc": "Port", "text": "8080"}, {"xpath": "//*[@content-desc='Port']"}),
        ({"text": "Setup"}, {"xpath": "//*[@text='Setup']"}),
    ],
)
def test_recording_prefers_element_locators(monkeypatch, attributes, locator):
    client = AgentAndroidClient(URL)
    client.action_session = ActionSession(URL, "demo")
    bounds = "[0,5][50,15]"
    target = {"refId": 1, "x": 25, "y": 10, "bounds": bounds, **attributes}
    client._local_tree = [target]
    root = ET.Element("hierarchy")
    key_to_xml = {"resourceId": "resource-id", "contentDesc": "content-desc", "text": "text"}
    ET.SubElement(root, "node", {"bounds": bounds, **{key_to_xml[k]: v for k, v in attributes.items()}})
    monkeypatch.setattr(client, "_get_ui_tree_root", lambda *, visible_only: root if not visible_only else None)
    sent = []

    def execute(template_id, operation_type, parameters):
        sent.append({"operationType": operation_type, "parameters": parameters})
        return {"success": True}

    monkeypatch.setattr(client, "_execute_single_operation", execute)
    assert client.tap_element(1)
    expected = {"operationType": "android.touch.tap", "parameters": {"mode": "locator", **locator}}
    assert sent == [expected]
    assert client.action_session._read_actions() == [expected]


@pytest.mark.parametrize("refresh", ["unavailable", "unrelated", "first-row"])
def test_one_off_tap_uses_saved_rows_even_if_refresh_replaces_snapshot(monkeypatch, tmp_path, refresh):
    monkeypatch.setattr(snapshot, "SNAPSHOT_FILE_PATH", tmp_path / "snapshot.json")
    first = {
        "refId": 7, "resourceId": "example:id/row", "simpleClassName": "TextView",
        "text": "Shared", "bounds": "[0,0][50,10]", "x": 25, "y": 5,
    }
    second = {**first, "refId": 8, "bounds": "[0,20][50,30]", "y": 25}
    snapshot.save_snapshot(URL, "example", [first, second])
    monkeypatch.setattr(AgentAndroidClient, "get_current_package_name", lambda self: "example")
    refreshed = {"unavailable": None, "unrelated": [{"refId": 1}], "first-row": [first]}[refresh]
    monkeypatch.setattr(AgentAndroidClient, "_fetch_ui_elements_impl", lambda *args, **kwargs: refreshed)
    root = ET.fromstring("""
        <hierarchy><node class="android.widget.LinearLayout">
            <node class="android.widget.TextView" bounds="[0,0][50,10]" resource-id="example:id/row" text="Shared"/>
            <node class="android.widget.TextView" bounds="[0,20][50,30]" resource-id="example:id/row" text="Shared"/>
        </node></hierarchy>
    """)
    monkeypatch.setattr(AgentAndroidClient, "_get_ui_tree_root", lambda self, *, visible_only: root if not visible_only else None)
    submitted = []

    def execute(self, template_id, operation_type, parameters):
        submitted.append({"operationType": operation_type, "parameters": parameters})
        return {"success": True}

    monkeypatch.setattr(AgentAndroidClient, "_execute_single_operation", execute)
    assert run_cli(monkeypatch, "--tap", "8") == 0
    expected = {
        "operationType": "android.touch.tap",
        "parameters": {"mode": "locator", "xpath": "/hierarchy/LinearLayout[1]/TextView[2]"},
    }
    assert submitted == [expected]
    assert ActionSession(URL, "demo")._read_actions() == [expected]


@pytest.mark.parametrize(
    ("key", "attribute", "duplicate_attribute"),
    [
        ("resourceId", "resource-id", "resource-id"),
        ("contentDesc", "content-desc", "content-desc"),
        ("text", "text", "content-desc"),
    ],
)
def test_offscreen_duplicate_disqualifies_unindexed_locator(monkeypatch, key, attribute, duplicate_attribute):
    client = AgentAndroidClient(URL)
    bounds = "[0,0][50,10]"
    target = {"refId": 1, "simpleClassName": "Button", "bounds": bounds, key: "shared"}
    client._local_tree = [target]
    root = ET.Element("hierarchy")
    ET.SubElement(root, "node", {"class": "android.widget.Button", "bounds": bounds, attribute: "shared"})
    ET.SubElement(root, "node", {
        "class": "android.widget.Button", "bounds": "[0,2000][50,2010]", duplicate_attribute: "shared",
    })
    monkeypatch.setattr(client, "_get_ui_tree_root", lambda *, visible_only: root if not visible_only else None)

    assert client._target_locator(target) == {"xpath": "/hierarchy/Button[1]"}


def test_unique_full_hierarchy_match_requires_target_bounds(monkeypatch):
    client = AgentAndroidClient(URL)
    target = {"refId": 1, "resourceId": "example:id/row", "simpleClassName": "Button", "bounds": "[0,0][50,10]"}
    client._local_tree = [target]
    root = ET.fromstring('<hierarchy><node class="Button" resource-id="example:id/row" bounds="[0,20][50,30]"/></hierarchy>')
    monkeypatch.setattr(client, "_get_ui_tree_root", lambda *, visible_only: root)
    assert client._target_locator(target) == {}


def test_input_records_indexed_field_locator_when_id_is_shared(monkeypatch, tmp_path):
    client = AgentAndroidClient(URL)
    client.action_session = ActionSession(URL, "demo")
    first = {
        "refId": 1, "resourceId": "example:id/field", "simpleClassName": "EditText",
        "text": "8080", "bounds": "[0,0][50,10]",
    }
    second = {
        **first, "refId": 2, "text": "existing field value", "bounds": "[0,20][50,30]", "x": 25, "y": 25,
    }
    # The ARIA list is in visual order. XPath positions come from the full tree.
    client._local_tree = [second, first]
    monkeypatch.setattr(client, "get_ui_tree_xml", lambda *, force_refresh, visible_only: """
        <hierarchy><node class="android.widget.LinearLayout">
            <node class="android.widget.EditText" bounds="[0,0][50,10]" resource-id="example:id/field" text="8080"/>
            <node class="android.widget.TextView" bounds="[0,10][50,20]"/>
            <node class="android.widget.EditText" bounds="[0,20][50,30]" resource-id="example:id/field"
                  text="existing field value"/>
        </node></hierarchy>
    """ if force_refresh and not visible_only else None)
    sent = []

    def execute(template_id, operation_type, parameters):
        sent.append(parameters)
        return {"success": True}

    monkeypatch.setattr(client, "_execute_single_operation", execute)
    assert client.input_to_element(2, "replacement")
    locator = {"xpath": "/hierarchy/LinearLayout[1]/EditText[2]"}
    assert sent == [{**locator, "clearFirst": True, "value": "replacement"}]
    assert client.action_session._read_actions() == [{
        "operationType": "android.element.input", "parameters": {**locator, "clearFirst": True},
        "textInput": True,
    }]
    destination = tmp_path / "application"
    assert run_cli(monkeypatch, "save", str(destination)) == 0
    main = json.loads((destination / "__main__.json").read_text(encoding="utf-8"))
    assert main["operations"] == [{
        "operationType": "android.element.input",
        "parameters": {**locator, "clearFirst": True, "value": "${input_1}"},
    }]


def test_save_marks_coordinate_fallback_and_legacy_input(monkeypatch, tmp_path):
    client = AgentAndroidClient(URL)
    client.action_session = ActionSession(URL, "demo")
    target = {"refId": 1, "resourceId": "example:id/button", "bounds": "[530,1119][550,1139]", "x": 540, "y": 1129}
    monkeypatch.setattr(client, "_resolve_action_target", lambda ref_id: target)
    monkeypatch.setattr(client, "_get_ui_tree_root", lambda **kwargs: pytest.fail("No peer list is available"))
    monkeypatch.setattr(client, "_execute_single_operation", lambda *args: {"success": True})
    assert client.tap_element(1)
    # Previously recorded sessions only have x/y for a refId input.
    client.action_session.append("android.element.input", {"x": 540, "y": 1129, "value": "1234"})
    destination = tmp_path / "application"
    assert run_cli(monkeypatch, "save", str(destination)) == 0
    with ZipFile(destination.with_suffix(".zip")) as bundle:
        main = json.loads(bundle.read("__main__.json"))
    tap, field = main["operations"]
    assert tap["parameters"] == {"mode": "coordinate", "x": 540, "y": 1129}
    assert field["parameters"] == {"x": 540, "y": 1129, "value": "${input_1}"}
    assert all(op["description"].startswith("Coordinate-only") for op in main["operations"])


def test_input_requires_a_field_locator(monkeypatch):
    client = AgentAndroidClient(URL)
    client.action_session = ActionSession(URL, "demo")
    client._local_tree = [{"refId": 1, "simpleClassName": "EditText", "text": "8080", "x": 540, "y": 1129}]
    monkeypatch.setattr(client, "_execute_single_operation", lambda *args: pytest.fail("Input needs a locator"))
    assert not client.input_to_element(1, "8083")
    assert not client.action_session.path.exists()


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


def test_save_after_global_options_skips_torn_tail_and_slugifies_id(monkeypatch, tmp_path, capsys):
    session = ActionSession(URL, "demo")
    session.append("android.press.back", {})
    with session.path.open("ab") as handle:
        handle.write(b'{"operationType":')
    destination = tmp_path / "Café Setup"
    assert run_cli(monkeypatch, "--url", "127.0.0.1:8080", "save", str(destination), url=None) == 0
    assert "Warning: skipping a torn trailing line" in capsys.readouterr().err
    app = json.loads((destination / "app.json").read_text(encoding="utf-8"))
    assert app["applicationId"] == "cafe-setup"
    assert app["applicationName"] == destination.name
    assert destination.with_suffix(".zip").is_file()


@pytest.mark.parametrize(
    ("tail", "tail_is_valid"),
    [(b'{"operationType":', False), (b'{"operationType":"android.press.home","parameters":{}}', True)],
)
def test_append_can_continue_after_an_unterminated_line(capsys, tail, tail_is_valid):
    session = ActionSession(URL, "demo")
    session.append("android.press.back", {})
    with session.path.open("ab") as handle:
        handle.write(tail)
    session.append("android.press.menu", {})
    action_types = [action["operationType"] for action in session._read_actions()]
    expected = ["android.press.back"]
    if tail_is_valid:
        expected.append("android.press.home")
    assert action_types == [*expected, "android.press.menu"]
    assert ("Warning: skipping a torn trailing line" in capsys.readouterr().err) == (not tail_is_valid)


@pytest.mark.parametrize(
    ("lines", "message"),
    [
        ('{"operationType":"android.press.back"}\n', "Expected a parameters object"),
        ('broken\n{"operationType":"android.press.back","parameters":{}}\n', "Invalid JSON"),
    ],
)
def test_save_reports_invalid_session_records(monkeypatch, tmp_path, capsys, lines, message):
    session = ActionSession(URL, "demo")
    session.append("android.press.back", {})
    session.path.write_text(lines, encoding="utf-8")
    destination = tmp_path / "invalid"
    assert run_cli(monkeypatch, "save", str(destination)) == 1
    assert message in capsys.readouterr().err
    assert not destination.exists()
    assert not destination.with_suffix(".zip").exists()


def test_clear_is_local_and_scoped_to_one_endpoint_and_session(monkeypatch, tmp_path):
    selected = ActionSession(URL, "demo")
    other_session = ActionSession(URL, "other")
    other_endpoint = ActionSession("http://127.0.0.1:8081", "demo")
    for session in (selected, other_session, other_endpoint):
        session.append("android.press.back", {})
    monkeypatch.setattr(cli, "AgentAndroidClient", lambda *args, **kwargs: pytest.fail("Clear is local"))
    assert run_cli(monkeypatch, "--session=demo", "session", "clear", url="127.0.0.1:8080", session=None) == 0
    assert selected.path.read_bytes() == b""
    assert other_session.path.stat().st_size > 0
    assert other_endpoint.path.stat().st_size > 0
    assert run_cli(monkeypatch, "save", str(tmp_path / "empty")) == 1
    selected.append("android.press.menu", {})
    assert [action["operationType"] for action in selected._read_actions()] == ["android.press.menu"]


def test_repl_bad_url_keeps_current_client_and_session(monkeypatch, capsys):
    client = AgentAndroidClient(URL)
    client.action_session = ActionSession(URL, "demo")
    session = repl.AriaReplSession.from_client(client)
    persisted = []
    monkeypatch.setattr(repl, "save_url_to_config", persisted.append)
    assert not session._execute_line("set url http://127.0.0.1:bad")
    assert "Invalid URL: ValueError:" in capsys.readouterr().err
    assert session.client is client
    assert persisted == []
    assert session._execute_line("set url 127.0.0.1:8080")
    assert session.client.base_url == URL
    assert session.client.action_session.path == client.action_session.path
    assert persisted == [URL]


def test_repl_does_not_keep_text_input_in_history(monkeypatch):
    commands = iter(["i 2 example", "input 2 example", "ix //EditText -- example", "inputx //EditText -- example", "p home"])
    history = ["l"]
    readline = SimpleNamespace(get_current_history_length=lambda: len(history), remove_history_item=history.pop)
    monkeypatch.setattr(repl, "_HAS_READLINE", True)
    monkeypatch.setattr(repl, "readline", readline, raising=False)

    def fake_input(_prompt):
        line = next(commands)
        history.append(line)
        return line

    monkeypatch.setattr("builtins.input", fake_input)
    session = repl.AriaReplSession.from_client(AgentAndroidClient(URL))
    assert [session._readline().split()[0] for _ in range(5)] == ["i", "input", "ix", "inputx", "p"]
    assert history == ["l", "p home"]


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
