from __future__ import annotations

import base64
import urllib.error

import pytest

from agent_android import client as client_module


class _UnexpectedNetworkOpener:
    def open(self, *_args, **_kwargs):
        raise AssertionError("Unexpected network access in unit test")


class _FakeClock:
    def __init__(self):
        self.now = 0.0

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(client_module, "_build_http_opener", lambda _base_url: _UnexpectedNetworkOpener())
    return client_module.AgentAndroidClient("http://device:8080")


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (
            {"success": True, "apps": {"label": "Calculator", "package": "pkg.calc"}},
            [{"label": "Calculator", "package": "pkg.calc"}],
        ),
        (
            {"success": True, "data": {"apps": [{"label": "Maps", "package": "pkg.maps"}]}},
            [{"label": "Maps", "package": "pkg.maps"}],
        ),
        (
            {"success": True, "data": {"appList": [{"label": "Camera", "package": "pkg.camera"}]}},
            [{"label": "Camera", "package": "pkg.camera"}],
        ),
        (
            {"success": True, "data": [{"label": "Clock", "package": "pkg.clock"}]},
            [{"label": "Clock", "package": "pkg.clock"}],
        ),
    ],
)
def test_list_launcher_apps_normalizes_compatible_shapes(client, monkeypatch, payload, expected):
    monkeypatch.setattr(client, "_get_raw", lambda _path: payload)

    assert client.list_launcher_apps() == expected


def test_list_launcher_apps_returns_none_on_explicit_failure(client, monkeypatch):
    monkeypatch.setattr(client, "_get_raw", lambda _path: {"success": False})

    assert client.list_launcher_apps() is None


def test_get_health_returns_payload_dict(client, monkeypatch):
    payload = {"service": "aivane-repl", "status": "running"}
    monkeypatch.setattr(client, "_get_raw", lambda _path: payload)

    assert client.get_health() == payload


def test_get_health_connection_error_prints_actionable_hint(client, capsys):
    class _BrokenOpener:
        def open(self, *_args, **_kwargs):
            raise urllib.error.URLError("connection refused")

    client._opener = _BrokenOpener()

    assert client.get_health() is None

    captured = capsys.readouterr()
    assert "GET http://device:8080/health failed: connection refused" in captured.err
    assert "Confirm the AIVane app is still open on the phone" in captured.err
    assert "curl http://device:8080/health" in captured.err


def test_api_call_connection_error_prints_actionable_hint(client, capsys):
    class _BrokenOpener:
        def open(self, *_args, **_kwargs):
            raise urllib.error.URLError("connection refused")

    client._opener = _BrokenOpener()

    assert client._api_call({"templateId": "smoke", "operations": []}) is None

    captured = capsys.readouterr()
    assert "POST http://device:8080/execute failed: connection refused" in captured.err
    assert "Confirm the AIVane app is still open on the phone" in captured.err
    assert "same LAN" in captured.err


def test_api_call_sends_token_header(monkeypatch):
    captured = {}

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"success": true}'

    class _RecordingOpener:
        def open(self, request, *_args, **_kwargs):
            headers = {key.lower(): value for key, value in request.header_items()}
            captured["token"] = headers.get("x-api-token")
            captured["url"] = request.full_url
            return _FakeResponse()

    monkeypatch.setattr(client_module, "_build_http_opener", lambda _base_url: _RecordingOpener())
    token_client = client_module.AgentAndroidClient("http://device:8080", token="shared-secret")

    assert token_client._api_call({"templateId": "smoke", "operations": []}) == {"success": True}
    assert captured == {
        "token": "shared-secret",
        "url": "http://device:8080/execute",
    }


def test_get_ui_elements_caches_results_and_saves_snapshot(client, monkeypatch):
    elements = [{"refId": 1, "text": "Search"}]
    calls = {"fetch": 0, "save": 0}

    def fake_fetch(visible_only=True):
        calls["fetch"] += 1
        assert visible_only is True
        return elements

    def fake_save(base_url, package_name, saved_elements):
        calls["save"] += 1
        assert base_url == "http://device:8080"
        assert package_name == "pkg.example"
        assert saved_elements == elements

    monkeypatch.setattr(client, "_fetch_ui_elements_impl", fake_fetch)
    monkeypatch.setattr(client, "get_current_package_name", lambda: "pkg.example")
    monkeypatch.setattr(client_module, "save_snapshot", fake_save)

    first = client.get_ui_elements()
    second = client.get_ui_elements()

    assert first == elements
    assert second == elements
    assert calls == {"fetch": 1, "save": 1}
    assert client._snapshot == {
        "baseUrl": "http://device:8080",
        "packageName": "pkg.example",
        "elements": elements,
    }


def test_get_ui_elements_keeps_visible_only_cache_separate(client, monkeypatch):
    calls = []

    def fake_fetch(visible_only=True):
        calls.append(visible_only)
        return [{"refId": 1 if visible_only else 2}]

    monkeypatch.setattr(client, "_fetch_ui_elements_impl", fake_fetch)
    monkeypatch.setattr(client, "get_current_package_name", lambda: "pkg.example")
    monkeypatch.setattr(client_module, "save_snapshot", lambda *_args: None)

    visible = client.get_ui_elements(visible_only=True)
    all_nodes = client.get_ui_elements(visible_only=False)

    assert visible == [{"refId": 1}]
    assert all_nodes == [{"refId": 2}]
    assert calls == [True, False]


def test_resolve_action_target_rejects_snapshot_from_other_package(client, monkeypatch, capsys):
    client._snapshot = {
        "baseUrl": "http://device:8080",
        "packageName": "pkg.old",
        "elements": [{"refId": 7, "text": "Search"}],
    }
    monkeypatch.setattr(client, "get_current_package_name", lambda: "pkg.new")
    monkeypatch.setattr(
        client,
        "get_ui_elements",
        lambda *args, **kwargs: pytest.fail("get_ui_elements should not run for mismatched packages"),
    )

    assert client._resolve_action_target(7) is None
    assert "snapshot package=pkg.old, current package=pkg.new" in capsys.readouterr().err


def test_resolve_action_target_prefers_matching_element_from_current_tree(client, monkeypatch):
    snapshot_elem = {
        "refId": 7,
        "resourceId": "pkg:id/search",
        "text": "Search",
        "contentDesc": "",
        "simpleClassName": "EditText",
        "xpath": "//EditText[1]",
    }
    current_elem = {
        "refId": 99,
        "resourceId": "pkg:id/search",
        "text": "Search",
        "contentDesc": "",
        "simpleClassName": "EditText",
        "xpath": "//EditText[1]",
    }
    client._snapshot = {
        "baseUrl": "http://device:8080",
        "packageName": "pkg.example",
        "elements": [snapshot_elem],
    }
    monkeypatch.setattr(client, "get_current_package_name", lambda: "pkg.example")
    monkeypatch.setattr(client, "get_ui_elements", lambda *args, **kwargs: [current_elem])

    assert client._resolve_action_target(7) == current_elem


def test_wait_for_element_retries_until_text_match_is_found(client, monkeypatch):
    responses = [
        [],
        [{"refId": 2, "text": "Search", "contentDesc": "", "simpleClassName": "EditText"}],
    ]
    clock = _FakeClock()

    def fake_get_ui_elements(*args, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(client, "get_ui_elements", fake_get_ui_elements)
    monkeypatch.setattr(client_module.time, "time", clock.time)
    monkeypatch.setattr(client_module.time, "sleep", clock.sleep)

    found = client.wait_for_element(text="search", timeout=2, interval=0.5)

    assert found is not None
    assert found["refId"] == 2


def test_find_by_text_matches_text_and_content_description_fields(client):
    elements = [
        {"refId": 1, "text": "Search", "contentDesc": "", "contentDescription": ""},
        {"refId": 2, "text": "", "contentDesc": "Search icon", "contentDescription": ""},
        {"refId": 3, "text": "", "contentDesc": "", "contentDescription": "Search hint"},
        {"refId": 4, "text": "Other", "contentDesc": "", "contentDescription": ""},
    ]

    matches = client.find_by_text(elements, "search")

    assert [elem["refId"] for elem in matches] == [1, 2, 3]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, 1),
        (False, 0),
        (5, 5),
        (3.9, 3),
        (" 7 ", 7),
        ("not-a-number", -1),
        (None, -1),
    ],
)
def test_parse_match_count_handles_common_runtime_shapes(client, value, expected):
    assert client._parse_match_count(value) == expected


def test_describe_xpath_match_returns_selected_match_details(client, monkeypatch):
    tree = [
        {
            "refId": 7,
            "text": "Search",
            "contentDesc": "Search box",
            "simpleClassName": "EditText",
            "bounds": "[0,0][100,50]",
            "x": 50,
            "y": 25,
            "resourceId": "pkg:id/search",
            "editable": True,
            "xpath": "//EditText[@text='Search']",
        }
    ]
    monkeypatch.setattr(client, "get_ui_elements", lambda *args, **kwargs: tree)

    detail = client.describe_xpath_match("//EditText[@text='Search']", 0)

    assert detail == {
        "index": 0,
        "count": 1,
        "refId": 7,
        "text": "Search",
        "contentDescription": "Search box",
        "className": "EditText",
        "bounds": "[0,0][100,50]",
        "x": 50,
        "y": 25,
        "resourceId": "pkg:id/search",
        "isInput": True,
    }


def test_input_by_xpath_rejects_non_input_match(client, monkeypatch, capsys):
    tree = [
        {
            "refId": 9,
            "text": "Search",
            "contentDesc": "",
            "simpleClassName": "TextView",
            "bounds": "[0,0][100,50]",
            "x": 50,
            "y": 25,
            "xpath": "//TextView[@text='Search']",
        }
    ]
    monkeypatch.setattr(client, "get_ui_elements", lambda *args, **kwargs: tree)
    monkeypatch.setattr(client, "_run_single_operation", lambda *args, **kwargs: pytest.fail("should not submit input"))

    assert client.input_by_xpath("//TextView[@text='Search']", "hello") is False
    assert "Refusing to guess a nearby input field" in capsys.readouterr().err


def test_input_by_xpath_rejects_ambiguous_matches(client, monkeypatch, capsys):
    tree = [
        {
            "refId": 1,
            "text": "Search",
            "contentDesc": "",
            "simpleClassName": "EditText",
            "editable": True,
            "xpath": "//EditText[@text='Search']",
        },
        {
            "refId": 2,
            "text": "Search",
            "contentDesc": "",
            "simpleClassName": "EditText",
            "editable": True,
            "xpath": "//EditText[@text='Search']",
        },
    ]
    monkeypatch.setattr(client, "get_ui_elements", lambda *args, **kwargs: tree)
    monkeypatch.setattr(client, "_get_xpath_match_count", lambda _xpath: 2)
    monkeypatch.setattr(client, "_run_single_operation", lambda *args, **kwargs: pytest.fail("should not submit input"))

    assert client.input_by_xpath("//EditText[@text='Search']", "hello") is False
    assert "matched 2 elements" in capsys.readouterr().err


def test_input_to_element_rejects_non_input_refid(client, monkeypatch, capsys):
    monkeypatch.setattr(
        client,
        "_resolve_action_target",
        lambda _ref_id: {"refId": 4, "simpleClassName": "Button", "x": 1, "y": 2},
    )
    monkeypatch.setattr(client, "_run_single_operation", lambda *args, **kwargs: pytest.fail("should not submit input"))

    assert client.input_to_element(4, "hello") is False
    assert "resolved to non-input element" in capsys.readouterr().err


def test_input_by_xpath_allows_clearing_input(client, monkeypatch):
    tree = [
        {
            "refId": 1,
            "text": "Search",
            "contentDesc": "",
            "simpleClassName": "EditText",
            "editable": True,
            "bounds": "[0,0][100,50]",
            "x": 50,
            "y": 25,
            "xpath": "//EditText[@text='Search']",
        }
    ]
    monkeypatch.setattr(client, "get_ui_elements", lambda *args, **kwargs: tree)
    calls = []

    def fake_run_single_operation(*_args, **kwargs):
        calls.append(kwargs)
        return True

    monkeypatch.setattr(client, "_run_single_operation", fake_run_single_operation)

    assert client.input_by_xpath("//EditText[@text='Search']", "") is True
    assert calls[0]["parameters"]["value"] == ""
    assert calls[0]["success_message"] == "Cleared XPath [//EditText[@text='Search']]"


def test_press_key_supports_menu(client, monkeypatch):
    templates = []

    def fake_api_call(template):
        templates.append(template)
        return {"success": True}

    monkeypatch.setattr(client, "_api_call", fake_api_call)

    assert client.press_key("menu") is True
    assert templates == [
        {
            "templateId": "press-menu",
            "operations": [{"operationType": "android.press.menu", "parameters": {}}],
        }
    ]


def test_screenshot_writes_output_file_from_base64_payload(client, monkeypatch, tmp_path):
    image_bytes = b"fake-image-bytes"
    monkeypatch.setattr(
        client,
        "_get_raw",
        lambda _path, _params=None: {"success": True, "base64": base64.b64encode(image_bytes).decode("ascii")},
    )

    output_path = tmp_path / "smoke.jpg"
    saved_path = client.screenshot(output_path=str(output_path))

    assert saved_path == str(output_path)
    assert output_path.read_bytes() == image_bytes
