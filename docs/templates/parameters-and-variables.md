# Parameters And Variables

Parameters describe the external contract of a template. Variables describe local state used inside the template.

Input parameter example:

```json
{
  "name": "targetId",
  "type": "STRING",
  "direction": "INPUT",
  "required": true,
  "description": "Target user or note ID"
}
```

Output parameter example:

```json
{
  "name": "result",
  "type": "STRING",
  "direction": "OUTPUT"
}
```

The linter warns when a template references a variable that is not declared, not assigned by a previous operation, or not introduced by a known control-flow scope.

Common fixes:

- Declare template inputs in `parameters`.
- Declare expected local state in `variables`.
- Check spelling for `${variable}` references.
- Prefer passing values explicitly to child templates instead of relying on ambient names.

Some runtime-provided variables may be reported as warnings until their source is modeled in the schema. Treat those warnings as prompts to make the contract explicit.
