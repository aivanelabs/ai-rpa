# OperationType Reference

This directory is the public OperationType reference used by AIVane templates.

Each OperationType page contains machine-readable front matter plus human-readable notes. The `aivane-template-linter` package uses the same schema shape to validate template JSON files and application bundles.

## Browse

- [INDEX.md](INDEX.md): all OperationTypes grouped by module
- `android/`: Android UI, input, app, screenshot, and device operations
- `browser/`: browser automation operations
- `core/`: template control flow, variables, logging, and application execution
- `dataprocessing/`: JSON, JSONata, list, dict, date/time, and string helpers
- `file/`: file operations
- `network/`: HTTP and upload/download operations
- `testing/`: assertion-style operations
- `windows/`: Windows-oriented operations

## Validate Templates

Install the public linter:

```bash
uv tool install aivane-template-linter
```

Validate an application bundle directory:

```bash
aivane-template-lint path/to/my-app -r
```

Validate against a local schema checkout instead of the bundled schema snapshot:

```bash
aivane-template-lint path/to/my-app -r --docs-dir docs/operation-types
```

## Runtime Compatibility

These docs describe the OperationType schema snapshot published with this repository. Runtime support depends on the installed AIVane Android REPL version and the template executor bundled in that release.

For template structure and linting workflow guidance, see [Template docs](../templates/README.md).
