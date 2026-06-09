# AIVane Template Linter

`aivane-template-linter` is a Python CLI for validating AIVane template JSON files and application bundles before they are sent to the Android REPL runtime.

It checks single templates, recursive template directories, and application directories that contain `app.json`, `__main__.json`, and child templates.

## Install

```bash
uv tool install aivane-template-linter
```

Or with pipx:

```bash
pipx install aivane-template-linter
```

## Run

Lint one template:

```bash
aivane-template-lint template.json
```

Lint an application bundle directory:

```bash
aivane-template-lint path/to/my-app -r
```

Emit machine-readable JSON:

```bash
aivane-template-lint path/to/my-app -r --json
```

Treat warnings as failures:

```bash
aivane-template-lint path/to/my-app -r --strict
```

Use a custom OperationType schema directory:

```bash
aivane-template-lint path/to/my-app -r --docs-dir path/to/operation-types
```

By default, the package uses the OperationType schema snapshot bundled with the installed wheel.

## What It Checks

- JSON parse errors
- Required template and operation fields
- Unknown OperationTypes
- Missing, unknown, deprecated, mistyped, or invalid enum parameters
- Variable references that are not declared in the current template scope
- `break` and `continue` outside loop context
- Nested operation structure
- Application-level relationships when `app.json` is present
- `template.execute` targets and parameter contracts across templates

## Application Checks

When a directory contains `app.json`, the linter also checks the template graph:

- `app.mainTemplateId` resolves to exactly one template
- template IDs and file aliases are not duplicated
- every `template.execute.templateId` target exists
- required child template input parameters are passed
- extra parameters passed to child templates are reported as warnings

## Exit Codes

- `0`: no errors
- `1`: one or more errors, or warnings when `--strict` is used

The same exit-code behavior applies to `--json`.

## Development

From this directory:

```bash
python -m pip install -e . pytest
python -m pytest tests
```

Build a local distribution:

```bash
python -m pip install build
python -m build
```

## Related Docs

- [Template linting guide](../../docs/templates/linting.md)
- [Template structure guide](../../docs/templates/application-structure.md)
- [OperationType reference](../../docs/operation-types/README.md)
