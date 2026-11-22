"""Copy public skills into the Claude Code plugin directories that bundle them.

Claude Code plugins cannot reference files outside their own directory, so
plugins/<plugin>/skills/<skill>/ holds a generated copy of skills/<skill>/.
Edit the source under skills/, then run this script. Use --check in CI.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# (source skill directory, generated copy inside a plugin)
COPIES = [
    (REPO_ROOT / "skills" / "aivane", REPO_ROOT / "plugins" / "aivane" / "skills" / "aivane"),
]


def _differences(source: Path, target: Path) -> list[str]:
    if not target.is_dir():
        return [f"{target.relative_to(REPO_ROOT)} is missing"]
    problems: list[str] = []
    stack = [filecmp.dircmp(source, target)]
    while stack:
        cmp = stack.pop()
        for name in cmp.left_only:
            problems.append(f"missing in copy: {Path(cmp.right, name).relative_to(REPO_ROOT)}")
        for name in cmp.right_only:
            problems.append(f"extra in copy: {Path(cmp.right, name).relative_to(REPO_ROOT)}")
        _, mismatch, errors = filecmp.cmpfiles(cmp.left, cmp.right, cmp.common_files, shallow=False)
        for name in mismatch + errors:
            problems.append(f"differs: {Path(cmp.right, name).relative_to(REPO_ROOT)}")
        stack.extend(cmp.subdirs.values())
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if a plugin copy is out of date")
    args = parser.parse_args()

    stale: list[str] = []
    for source, target in COPIES:
        problems = _differences(source, target)
        if not problems:
            continue
        if args.check:
            stale.extend(problems)
        else:
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)
            print(f"updated {target.relative_to(REPO_ROOT)}")

    if stale:
        print("Plugin skill copies are out of date; run python scripts/sync_plugin_skills.py", file=sys.stderr)
        for problem in stale:
            print(f"  {problem}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
