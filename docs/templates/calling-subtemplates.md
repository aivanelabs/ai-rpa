# Calling Child Templates

Use `template.execute` when one template needs to call another template in the same application bundle.

Example:

```json
{
  "operationType": "template.execute",
  "parameters": {
    "templateId": "open-user-profile",
    "parameters": {
      "targetId": "${targetId}"
    },
    "continueOnFailure": false
  }
}
```

Best practices:

- Reference child templates by `templateId`.
- Keep `templateId` stable and unique within the application.
- Declare child template inputs in the child template `parameters` array.
- Pass all required input parameters from the caller.
- Do not pass extra parameters unless the child template intentionally accepts them.

Application-level lint checks catch:

- missing child templates
- ambiguous template IDs or file aliases
- missing required child inputs
- extra parameters passed to a child template

Extra parameters are warnings because some older templates relied on ambient variable behavior. For new templates, treat them as contract drift and either declare the parameter on the child template or stop passing it.
