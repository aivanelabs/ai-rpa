---
{
  "schemaVersion": 1,
  "operationType": "continue",
  "executorClass": "aivane.core.executor.ContinueExecutor",
  "displayName": "Continueexecutor",
  "description": "Continue executor - skips the current iteration of the current loop and continues with the next iteration",
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
      "description": "Number of loop levels to continue, defaults to 1."
    }
  ],
  "constraints": {
    "requiresLoopContext": true
  }
}
---

# continue
