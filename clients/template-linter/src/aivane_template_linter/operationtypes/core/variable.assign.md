---
{
  "schemaVersion": 1,
  "operationType": "variable.assign",
  "executorClass": "aivane.core.executor.VariableAssignmentExecutor",
  "displayName": "variable assignment executor",
  "description": "Variable assignment executor - supports simple assignments and arithmetic expressions",
  "category": "variable_manipulation",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "variableName",
      "type": "string",
      "required": true,
      "description": "variable name to write"
    },
    {
      "name": "value",
      "type": "any",
      "required": true,
      "allowEmpty": true,
      "description": "The value assigned to the variable can be written directly as a fixed value, or you can use ${...} expressions."
    }
  ]
}
---

# variable.assign
