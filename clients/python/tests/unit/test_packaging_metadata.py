from __future__ import annotations

from pathlib import Path
import tomllib

from agent_android import __version__


def test_pyproject_uses_runtime_version_as_single_source_of_truth():
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    config = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    assert "version" not in config["project"]
    assert config["project"]["dynamic"] == ["version"]
    assert config["tool"]["setuptools"]["dynamic"]["version"]["attr"] == "agent_android.__version__"
    assert __version__.count(".") == 2
