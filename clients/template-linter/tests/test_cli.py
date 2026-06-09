import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
TEST_CASES = FIXTURES / "test_cases"
TEST_DOCS = FIXTURES / "test_operation_docs"


def run_linter(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "aivane_template_linter.cli", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def test_valid_template_with_fixture_docs_passes() -> None:
    result = run_linter(
        str(TEST_CASES / "valid_template.json"),
        "--docs-dir",
        str(TEST_DOCS),
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_invalid_template_fails() -> None:
    result = run_linter(
        str(TEST_CASES / "invalid_missing_required.json"),
        "--docs-dir",
        str(TEST_DOCS),
    )

    assert result.returncode == 1
    assert "T004" in result.stdout


def test_application_relationship_lint_runs_recursively() -> None:
    result = run_linter(
        str(TEST_CASES / "invalid_application_missing_template"),
        "-r",
        "--docs-dir",
        str(TEST_DOCS),
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert any(error["code"] == "A008" for error in payload["errors"])


def test_bundled_operation_docs_are_default() -> None:
    result = run_linter(
        str(TEST_CASES / "valid_application"),
        "-r",
        "--json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["summary"]["total_errors"] == 0
