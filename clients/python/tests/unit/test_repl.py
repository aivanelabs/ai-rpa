from __future__ import annotations

import json

import pytest

from agent_android import repl as repl_module


class _DummyClient:
    def __init__(self, url, token=None):
        self.base_url = url
        self.token = token
        self._local_tree = None
        self.input_calls = []
        self.input_xpath_calls = []
        self.pressed_keys = []

    def get_ui_elements(self, force_refresh=False):
        return [
            {
                "refId": 5,
                "text": "Search",
                "contentDesc": "Search box",
                "simpleClassName": "EditText",
                "x": 120,
                "y": 240,
            }
        ]

    def get_current_package_name(self):
        return "pkg.example"

    def get_health(self):
        return {"service": "aivane-repl", "status": "running"}

    def find_by_refId(self, elements, ref_id):
        for elem in elements:
            if elem.get("refId") == ref_id:
                return elem
        return None

    def generate_xpath_candidates(self, _elem, _tree):
        return [("//EditText[@text='Search']", 1, "text")]

    def validate_xpath_runtime(self, xpath):
        return {
            "xpath": xpath,
            "count": 2 if xpath == "//many" else 1,
            "text": "Search",
            "contentDescription": "Search box",
            "className": "EditText",
            "bounds": "[0,0][100,50]",
        }

    def build_ui_tree_absolute_xpath(self, _tree, _elem):
        return "/FrameLayout[1]/EditText[@text='Search']"

    def build_runtime_absolute_xpath(self, _tree, _elem):
        return "/hierarchy/FrameLayout[1]/EditText[@text='Search']"

    def describe_xpath_match(self, xpath, index=0):
        matches = [
            {"refId": 5, "className": "EditText", "text": "Search", "contentDescription": "Search box", "bounds": "[0,0][100,50]", "x": 120, "y": 240, "isInput": True},
            {"refId": 8, "className": "EditText", "text": "Other", "contentDescription": "", "bounds": "[0,50][100,100]", "x": 120, "y": 320, "isInput": True},
        ]
        if xpath == "//many" and 0 <= index < len(matches):
            return matches[index]
        if xpath != "//many" and index == 0:
            return matches[0]
        return None

    def input_to_element(self, ref_id, text):
        self.input_calls.append((ref_id, text))
        return True

    def input_by_xpath(self, xpath, text):
        self.input_xpath_calls.append((xpath, text))
        return True

    def press_key(self, key):
        self.pressed_keys.append(key)
        return True


@pytest.fixture
def session(monkeypatch):
    monkeypatch.setattr(repl_module, "AgentAndroidClient", _DummyClient)
    return repl_module.AriaReplSession(url="http://device:8080")


def test_parse_line_keeps_xpath_remainder_intact(session):
    command, args = session._parse_line("tx //node[@text='Hello world']")

    assert command == "tx"
    assert args == ["//node[@text='Hello world']"]


def test_parse_line_supports_inputx_delimiter_for_text_with_spaces(session):
    command, args = session._parse_line("ix //node[@resource-id='pkg:id/search'] -- hello world")

    assert command == "ix"
    assert args == ["//node[@resource-id='pkg:id/search']", "hello world"]


def test_parse_line_supports_inputx_clear_with_trailing_delimiter(session):
    command, args = session._parse_line("ix //node[@resource-id='pkg:id/search'] --")

    assert command == "ix"
    assert args == ["//node[@resource-id='pkg:id/search']", ""]


def test_parse_line_keeps_input_text_with_spaces_for_refid_commands(session):
    command, args = session._parse_line("i 5 hello world")

    assert command == "i"
    assert args == ["5", "hello world"]


def test_parse_line_supports_validatex_optional_index(session):
    command, args = session._parse_line("vx //node[@text='Hello world'] 1")

    assert command == "vx"
    assert args == ["//node[@text='Hello world']", "1"]


def test_parse_line_uses_shell_style_splitting_for_regular_commands(session):
    command, args = session._parse_line("set timeout 45")

    assert command == "set"
    assert args == ["timeout", "45"]


def test_execute_line_reports_unknown_command(session, capsys):
    assert session._execute_line("unknown-command") is False

    assert "Unknown command" in capsys.readouterr().err


def test_cmd_set_url_replaces_client_and_persists_value(session, monkeypatch, capsys):
    saved_urls = []
    monkeypatch.setattr(repl_module, "save_url_to_config", lambda url: saved_urls.append(url))
    session.client.token = "saved-token"

    assert session._cmd_set(["url", " http://new-device:8080 "]) is True

    captured = capsys.readouterr()
    assert session.client.base_url == "http://new-device:8080"
    assert session.client.token == "saved-token"
    assert saved_urls == ["http://new-device:8080"]
    assert "URL set to: http://new-device:8080" in captured.out


def test_cmd_set_timeout_updates_session_timeout(session, capsys):
    assert session._cmd_set(["timeout", "45"]) is True

    captured = capsys.readouterr()
    assert session._timeout == 45
    assert "Timeout set to: 45s" in captured.out


def test_cmd_set_rejects_empty_url(session, capsys):
    assert session._cmd_set(["url", "   "]) is False

    assert "URL cannot be empty" in capsys.readouterr().err


def test_cmd_set_token_updates_client_and_persists_value(session, monkeypatch, capsys):
    saved_tokens = []
    monkeypatch.setattr(repl_module, "save_token_to_config", lambda token: saved_tokens.append(token))

    assert session._cmd_set(["token", " shared-secret "]) is True

    captured = capsys.readouterr()
    assert session.client.token == "shared-secret"
    assert saved_tokens == ["shared-secret"]
    assert "Token set for protected API access" in captured.out


def test_cmd_set_token_clear_removes_saved_token(session, monkeypatch, capsys):
    saved_tokens = []
    monkeypatch.setattr(repl_module, "save_token_to_config", lambda token: saved_tokens.append(token))
    session.client.token = "old-token"

    assert session._cmd_set(["token", "--clear"]) is True

    captured = capsys.readouterr()
    assert session.client.token is None
    assert saved_tokens == [None]
    assert "Token cleared" in captured.out


def test_cmd_health_prints_health_payload(session, capsys):
    assert session._cmd_health([]) is True

    captured = capsys.readouterr()
    assert "Health:" in captured.out
    assert "service: aivane-repl" in captured.out
    assert "status: running" in captured.out


def test_cmd_health_respects_raw_output(session, capsys):
    session._raw_output = True

    assert session._cmd_health([]) is True

    captured = capsys.readouterr()
    assert json.loads(captured.out) == {"service": "aivane-repl", "status": "running"}


def test_cmd_input_supports_clear_flag(session):
    assert session._cmd_input(["5", "--clear"]) is True

    assert session.client.input_calls == [(5, "")]


def test_cmd_input_supports_quoted_empty_string(session):
    assert session._cmd_input(["5", '""']) is True

    assert session.client.input_calls == [(5, "")]


def test_cmd_inputx_supports_empty_text_via_delimiter(session):
    assert session._cmd_inputx(["//EditText[@text='Search']", ""]) is True

    assert session.client.input_xpath_calls == [("//EditText[@text='Search']", "")]


def test_cmd_validatex_prints_requested_match_detail(session, capsys):
    assert session._cmd_validatex(["//many", "1"]) is True

    captured = capsys.readouterr()
    assert "Runtime match count: 2" in captured.out
    assert "Match[1] refId: 8" in captured.out
    assert "Center: (120, 320)" in captured.out


def test_cmd_xpath_does_not_store_last_xpath_dead_state(session):
    session.variables["LAST_XPATH"] = "//stale"

    assert session._cmd_xpath(["5"]) is True

    assert "LAST_XPATH" not in session.variables
    assert session.variables["LAST_UI_TREE_ABSOLUTE_XPATH"] == "/FrameLayout[1]/EditText[@text='Search']"
    assert session.variables["LAST_RUNTIME_ABSOLUTE_XPATH"] == "/hierarchy/FrameLayout[1]/EditText[@text='Search']"


def test_cmd_xpath_rejects_extra_arguments_with_usage(session, capsys):
    assert session._cmd_xpath(["5", "1"]) is False

    captured = capsys.readouterr()
    assert "Usage: x <refId>" in captured.err


def test_help_text_matches_current_xpath_and_press_usage(session, capsys):
    assert session._cmd_help([]) is True

    captured = capsys.readouterr()
    assert "x <refId>" in captured.out
    assert "x <N>" not in captured.out
    assert "p <key>           Press a key (back/home/menu/enter/delete/power)" in captured.out
    assert "Press a key (back/home/menu)" not in captured.out
    assert "set token <value>  Save the shared token (--clear to remove it)" in captured.out
