# Release Checklist

Use this checklist before publishing a tagged PyPI release from this repository.

## Agent Android CLI

Package:

1. Confirm the PyPI package name in `clients/python/pyproject.toml` is `aivane-agent-android`.
2. Confirm the package version in `clients/python/src/agent_android/__init__.py`.
3. From `clients/python/`, run:
   - `python -m build`
4. Verify both `dist/*.tar.gz` and `dist/*.whl` were created.
5. Test a fresh local install from `dist/`.

Docs and skill:

1. Confirm README install instructions still use `agent-android`.
2. Confirm `skills/agent-android/SKILL.md` does not depend on local-only script paths.
3. Confirm the GitHub skill install command is still:
   - `npx skills add aivanelabs/ai-rpa --skill agent-android`

GitHub Actions and PyPI:

1. Confirm `.github/workflows/python-publish.yml` is present.
2. Confirm the workflow triggers on pushed tags matching `agent-android-v*`.
3. Confirm the publish job has `id-token: write` permission for Trusted Publishing.
4. Confirm the PyPI Trusted Publisher points at:
   - owner: `aivanelabs`
   - repo: `ai-rpa`
   - workflow: `python-publish.yml`
   - environment: `pypi`

Tag release:

1. Merge the release-ready changes to `main`.
2. Create and push a tag such as `agent-android-v0.1.4`.
3. Watch the GitHub Actions release workflow.
4. Verify the package appears on PyPI.
5. Verify `uv tool install aivane-agent-android` on a clean machine.

## Template Linter CLI

Package:

1. Confirm the PyPI package name in `clients/template-linter/pyproject.toml` is `aivane-template-linter`.
2. Confirm the package version in `clients/template-linter/src/aivane_template_linter/__init__.py`.
3. From `clients/template-linter/`, run:
   - `python -m build`
4. Verify both `dist/*.tar.gz` and `dist/*.whl` were created.
5. Test a fresh local install from `dist/`.

Docs:

1. Confirm README install instructions use `aivane-template-linter`.
2. Confirm the console command is `aivane-template-lint`.
3. Confirm `docs/templates/` describes application structure and lint workflow.
4. Confirm `docs/operation-types/` contains the public OperationType reference.
5. Confirm the bundled schema snapshot under `clients/template-linter/src/aivane_template_linter/operationtypes/` matches the published docs when intended.

GitHub Actions and PyPI:

1. Confirm `.github/workflows/template-linter-tests.yml` is present.
2. Confirm `.github/workflows/template-linter-publish.yml` is present.
3. Confirm the publish workflow triggers on pushed tags matching `template-linter-v*`.
4. Confirm the publish job has `id-token: write` permission for Trusted Publishing.
5. Confirm the PyPI Trusted Publisher points at:
   - owner: `aivanelabs`
   - repo: `ai-rpa`
   - workflow: `template-linter-publish.yml`
   - environment: `pypi`

Tag release:

1. Merge the release-ready changes to `main`.
2. Create and push a tag such as `template-linter-v0.1.0`.
3. Watch the GitHub Actions release workflow.
4. Verify the package appears on PyPI.
5. Verify `uv tool install aivane-template-linter` on a clean machine.
