---
{
  "operationType": "variable.assign",
  "displayName": "Variable assignment",
  "category": "VARIABLE",
  "platforms": ["core"],
  "parameters": [
    {
      "name": "variableName",
      "type": "string",
      "required": true,
      "description": "Variable name"
    },
    {
      "name": "value",
      "type": "any",
      "required": true,
      "allowEmpty": true,
      "description": "Value to assign; ${...} expressions are supported"
    }
  ],
  "constraints": {
    "requiresLoopContext": false
  }
}
---
