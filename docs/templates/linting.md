# Linting Templates

Install the linter:

```bash
uv tool install aivane-template-linter
```

Validate one template:

```bash
aivane-template-lint template.json
```

Validate an application bundle directory recursively:

```bash
aivane-template-lint my-app -r
```

Output JSON for scripts or CI:

```bash
aivane-template-lint my-app -r --json
```

Treat warnings as failures:

```bash
aivane-template-lint my-app -r --strict
```

Use a local OperationType schema directory:

```bash
aivane-template-lint my-app -r --docs-dir docs/operation-types
```

Exit codes:

- `0`: no errors
- `1`: errors found, or warnings found with `--strict`

The bundled schema snapshot is good for normal use. Use `--docs-dir` when you are developing against a newer runtime schema or reviewing a local checkout of this repository.
