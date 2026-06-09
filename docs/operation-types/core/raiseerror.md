---
{
  "schemaVersion": 1,
  "operationType": "raiseerror",
  "executorClass": "aivane.core.executor.RaiseErrorExecutor",
  "displayName": "RaiseError executor",
  "description": "Proactively throw error executor - for custom error conditions and error messages",
  "category": "error_handling",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "message",
      "type": "string",
      "required": true,
      "description": "error message."
    },
    {
      "name": "errorCode",
      "type": "string",
      "required": false,
      "defaultValue": "6002",
      "description": "error code."
    },
    {
      "name": "context",
      "type": "object",
      "required": false,
      "description": "Attach error context."
    },
    {
      "name": "propagate",
      "type": "boolean",
      "required": false,
      "defaultValue": true,
      "description": "Whether to continue propagating this error to the upper layer."
    }
  ]
}
---

# raiseerror
