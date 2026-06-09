---
{
  "schemaVersion": 1,
  "operationType": "break",
  "executorClass": "aivane.core.executor.BreakExecutor",
  "displayName": "Break executor",
  "description": "Break executor - Break out of the current loop or a loop at a specified level",
  "category": "process_control",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "levels",
      "type": "integer",
      "allowedTypes": [
        "integer",
        "string"
      ],
      "required": false,
      "defaultValue": 1,
      "description": "The number of loop levels to jump out of, defaults to 1."
    }
  ],
  "constraints": {
    "requiresLoopContext": true
  }
}
---

# break
