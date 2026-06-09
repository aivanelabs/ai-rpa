# Template Schema

A template is a JSON file with metadata, optional parameter declarations, optional variables, and an operation list.

Minimal template:

```json
{
  "templateId": "hello-world",
  "templateName": "Hello world",
  "description": "Write a message",
  "parameters": [],
  "variables": [],
  "operations": [
    {
      "operationType": "console.write",
      "parameters": {
        "message": "Hello, AIVane"
      }
    }
  ]
}
```

Recommended top-level fields:

- `templateId`: stable machine identifier used by `template.execute`
- `templateName`: human-readable display name
- `description`: short purpose statement
- `parameters`: explicit input and output contract
- `variables`: local variables that are expected before operations run
- `operations`: ordered operation list

Use `templateId` for references and `templateName` for display text. Keeping them separate avoids confusing stable IDs with localized or user-facing labels.
