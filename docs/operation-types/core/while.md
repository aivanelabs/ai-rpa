---
{
  "schemaVersion": 1,
  "operationType": "while",
  "executorClass": "aivane.core.executor.WhileExecutor",
  "displayName": "While loop executor",
  "description": "Loop executor that supports precondition loop (while) and postcondition loop (do-while)",
  "category": "process_control",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "condition",
      "type": "string",
      "required": true,
      "description": "A loop conditional expression of the form ${...} must be used."
    },
    {
      "name": "operations",
      "type": "array",
      "required": true,
      "description": "The loop body operates on the array."
    },
    {
      "name": "loopType",
      "type": "enum",
      "required": false,
      "defaultValue": "while",
      "enumValues": [
        "while",
        "do",
        "dowhile"
      ],
      "description": "Loop type."
    },
    {
      "name": "maxIterations",
      "type": "integer",
      "allowedTypes": [
        "integer",
        "string"
      ],
      "required": false,
      "defaultValue": 10000,
      "description": "The maximum number of iterations, execution will fail after exceeding it."
    }
  ],
  "constraints": {
    "nestedOperations": [
      "operations"
    ]
  }
}
---

# while
