# Release Checklist

Use this checklist before publishing a tagged PyPI release for the `agent-android` CLI.

## Package

1. Confirm the final PyPI package name in `clients/python/pyproject.toml`.
2. Confirm the package version in `clients/python/src/agent_android/__init__.py` and `clients/python/pyproject.toml`.
3. From `clients/python/`, run:
   - `python -m pip install --upgrade build`
   - `python -m build`
4. Verify both `dist/*.tar.gz` and `dist/*.whl` were created.
5. Test a fresh local install from `dist/`.

## Docs And Skill

1. Confirm README install instructions still use `agent-android`.
2. Confirm `skills/agent-android/SKILL.md` does not depend on relative local script paths.
3. Confirm the GitHub skill install command is still:
   - `npx skills add aivanelabs/ai-rpa --skill agent-android -a claude-code -a codex -a openclaw -g -y`

## GitHub Actions

1. Confirm `.github/workflows/python-publish.yml` is present.
2. Confirm the workflow triggers on pushed tags matching `v*`.
3. Confirm the publish job has `id-token: write` permission for Trusted Publishing.

## PyPI Trusted Publishing

1. Create the PyPI project if it does not exist yet.
2. Add a Trusted Publisher for this GitHub repository and workflow.
3. Confirm the trusted publisher points at:
   - owner: `aivanelabs`
   - repo: `ai-rpa`
   - workflow: `python-publish.yml`

## Tag Release

1. Merge the release-ready changes to `main`.
2. Create and push a tag such as `v0.1.0`.
3. Watch the GitHub Actions release workflow.
4. Verify the package appears on PyPI.
5. Verify `python -m pip install aivane-agent-android` on a clean machine.
