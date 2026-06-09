# OperationType Documentation

Welcome to the AIVane OperationType documentation. This guide explains how to build, validate, and run automation templates.

---

## Overview

AIVane uses a JSON-based template system to define automation tasks.
Each template contains a sequence of OperationTypes that can run across Windows and Android platforms.

## Quick Start

### 1. Create a Template

```json
{
  "templateId": "my-template",
  "templateName": "My Automation Template",
  "description": "A sample automation template",
  "operations": [
    {
      "operationType": "console.write",
      "parameters": {
        "message": "Hello, AIVane!"
      }
    }
  ]
}
```

### 2. Browse Available OperationTypes

See [INDEX.md](INDEX.md) for the full list of available OperationTypes by module.

### 3. Validate Templates

Use `template_linter.py` to validate template structure and operation usage:

```bash
# Validate a template
python tools/template-linter/template_linter.py validate my-template.json

# Check a specific operation usage
python tools/template-linter/template_linter.py check-operation my-template.json "console.write"

# Auto-fix simple issues
python tools/template-linter/template_linter.py fix my-template.json
```

### 4. Run Templates

```bash
# Run a template
python run-template.py my-template.json

# Use timeout to avoid infinite loops
timeout 30 python run-template.py my-template.json
```

---

## Documentation Structure

- `INDEX.md`: index of all OperationTypes
- `<module>/<operation>.md`: detailed docs for each OperationType
- `README.md`: this guide
- `EXAMPLES.json`: sample templates
- `tools/template-linter/`: template validation tooling
