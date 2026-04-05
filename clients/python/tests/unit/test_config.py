from __future__ import annotations

import json

import pytest

from agent_android import config


def test_load_saved_url_returns_stripped_value(tmp_path, monkeypatch):
    config_path = tmp_path / "agent-android.json"
    monkeypatch.setattr(config, "CONFIG_FILE_PATH", config_path)
    config_path.write_text(json.dumps({"url": " http://device:8080/ "}), encoding="utf-8")

    assert config.load_saved_url() == "http://device:8080/"


def test_save_url_to_config_writes_json_payload(tmp_path, monkeypatch):
    config_path = tmp_path / "agent-android.json"
    monkeypatch.setattr(config, "CONFIG_FILE_PATH", config_path)

    config.save_url_to_config("  http://device:8080  ")

    assert json.loads(config_path.read_text(encoding="utf-8")) == {"url": "http://device:8080"}


def test_save_url_to_config_preserves_saved_token(tmp_path, monkeypatch):
    config_path = tmp_path / "agent-android.json"
    monkeypatch.setattr(config, "CONFIG_FILE_PATH", config_path)
    config_path.write_text(json.dumps({"token": "secret-token"}), encoding="utf-8")

    config.save_url_to_config("http://device:8080")

    assert json.loads(config_path.read_text(encoding="utf-8")) == {
        "url": "http://device:8080",
        "token": "secret-token",
    }


def test_load_saved_token_returns_stripped_value(tmp_path, monkeypatch):
    config_path = tmp_path / "agent-android.json"
    monkeypatch.setattr(config, "CONFIG_FILE_PATH", config_path)
    config_path.write_text(json.dumps({"token": " shared-secret "}), encoding="utf-8")

    assert config.load_saved_token() == "shared-secret"


def test_save_token_to_config_writes_and_can_clear_value(tmp_path, monkeypatch):
    config_path = tmp_path / "agent-android.json"
    monkeypatch.setattr(config, "CONFIG_FILE_PATH", config_path)
    config_path.write_text(json.dumps({"url": "http://device:8080"}), encoding="utf-8")

    config.save_token_to_config(" shared-secret ")
    assert json.loads(config_path.read_text(encoding="utf-8")) == {
        "url": "http://device:8080",
        "token": "shared-secret",
    }

    config.save_token_to_config(None)
    assert json.loads(config_path.read_text(encoding="utf-8")) == {"url": "http://device:8080"}


def test_resolve_base_url_prefers_command_line_over_saved_value(tmp_path, monkeypatch):
    config_path = tmp_path / "agent-android.json"
    monkeypatch.setattr(config, "CONFIG_FILE_PATH", config_path)
    config_path.write_text(json.dumps({"url": "http://saved:8080"}), encoding="utf-8")

    assert config.resolve_base_url("http://cli:8080") == "http://cli:8080"


def test_load_saved_url_returns_none_for_invalid_json(tmp_path, monkeypatch):
    config_path = tmp_path / "agent-android.json"
    monkeypatch.setattr(config, "CONFIG_FILE_PATH", config_path)
    config_path.write_text("{invalid json", encoding="utf-8")

    assert config.load_saved_url() is None


def test_resolve_api_token_prefers_command_line_over_env_and_saved(tmp_path, monkeypatch):
    config_path = tmp_path / "agent-android.json"
    monkeypatch.setattr(config, "CONFIG_FILE_PATH", config_path)
    monkeypatch.setenv(config.TOKEN_ENV_VAR, "env-token")
    config_path.write_text(json.dumps({"token": "saved-token"}), encoding="utf-8")

    assert config.resolve_api_token("cli-token") == "cli-token"


def test_resolve_api_token_falls_back_to_env_then_saved(tmp_path, monkeypatch):
    config_path = tmp_path / "agent-android.json"
    monkeypatch.setattr(config, "CONFIG_FILE_PATH", config_path)
    config_path.write_text(json.dumps({"token": "saved-token"}), encoding="utf-8")

    monkeypatch.setenv(config.TOKEN_ENV_VAR, "env-token")
    assert config.resolve_api_token(None) == "env-token"

    monkeypatch.delenv(config.TOKEN_ENV_VAR, raising=False)
    assert config.resolve_api_token(None) == "saved-token"


def test_require_base_url_exits_when_no_value_available(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / "agent-android.json"
    monkeypatch.setattr(config, "CONFIG_FILE_PATH", config_path)

    with pytest.raises(SystemExit) as exc_info:
        config.require_base_url(None)

    captured = capsys.readouterr()
    assert exc_info.value.code == 2
    assert "AIVane server URL is required" in captured.err
