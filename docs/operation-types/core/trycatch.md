---
{
  "schemaVersion": 1,
  "operationType": "trycatch",
  "executorClass": "aivane.core.executor.TryCatchExecutor",
  "displayName": "Try-Catch-Finally executor",
  "description": "Try-Catch-Finally executor - provides structured error handling",
  "category": "error_handling",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "tryBranch",
      "type": "array",
      "required": true,
      "description": "try branches to operate on arrays."
    },
    {
      "name": "catchBranch",
      "type": "array",
      "required": false,
      "description": "catch branch operates on an array."
    },
    {
      "name": "finallyBranch",
      "type": "array",
      "required": false,
      "description": "finally branch operates on the array."
    },
    {
      "name": "catchFilter",
      "type": "string",
      "required": false,
      "description": "Only capture specified error codes."
    }
  ],
  "constraints": {
    "nestedOperations": [
      "tryBranch",
      "catchBranch",
      "finallyBranch"
    ]
  }
}
---

# trycatch
