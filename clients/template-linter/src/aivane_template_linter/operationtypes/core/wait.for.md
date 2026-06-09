---
{
  "schemaVersion": 1,
  "operationType": "wait.for",
  "executorClass": "aivane.core.executor.WaitForExecutor",
  "displayName": "Wait condition",
  "description": "Polling waits for conditions to be met, supports timeout and polling interval configuration, and can poll up to 10,000 times.",
  "category": "process_control",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "condition",
      "type": "string",
      "required": true,
      "description": "A wait condition expression of the form ${...} must be used."
    },
    {
      "name": "timeout",
      "type": "integer",
      "allowedTypes": [
        "integer",
        "string"
      ],
      "required": false,
      "defaultValue": 60000,
      "description": "Maximum waiting time, in milliseconds."
    },
    {
      "name": "pollInterval",
      "type": "integer",
      "allowedTypes": [
        "integer",
        "string"
      ],
      "required": false,
      "defaultValue": 500,
      "description": "Polling interval, in milliseconds."
    }
  ]
}
---

# wait.for
