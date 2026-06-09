---
{
  "schemaVersion": 1,
  "operationType": "ifelse",
  "executorClass": "aivane.core.executor.IfElseExecutor",
  "displayName": "If/Else conditional executor",
  "description": "Perform different branch operations based on conditional expressions",
  "category": "process_control",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "condition",
      "type": "string",
      "required": true,
      "description": "A conditional expression of the form ${...} must be used."
    },
    {
      "name": "ifBranch",
      "type": "object",
      "allowedTypes": [
        "object",
        "array"
      ],
      "required": false,
      "description": "A single operation or array of operations that is performed when the condition is true."
    },
    {
      "name": "elseBranch",
      "type": "object",
      "allowedTypes": [
        "object",
        "array"
      ],
      "required": false,
      "description": "A single operation or array of operations that is performed when the condition is false."
    }
  ],
  "constraints": {
    "nestedOperations": [
      "ifBranch",
      "elseBranch"
    ]
  }
}
---

# ifelse
