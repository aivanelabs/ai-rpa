# Application Structure

An AIVane application bundle is a directory or zip that keeps one main template and its child templates together.

Typical layout:

```text
my-app/
  app.json
  __main__.json
  templates/
    child-template.json
    another-child.json
```

`app.json` identifies the application and its entry template:

```json
{
  "app": {
    "applicationId": "my-app",
    "applicationName": "My App",
    "mainTemplateId": "__main__"
  }
}
```

The main template should usually use the same stable ID as the entry file:

```json
{
  "templateId": "__main__",
  "templateName": "Main workflow",
  "operations": []
}
```

Child templates live under `templates/` and should use stable, unique `templateId` values. Parent templates call them with `template.execute`.

The linter resolves template references by `templateId` first. File-name aliases are supported for compatibility, but relying on mismatched file names and template IDs makes applications harder to review.
