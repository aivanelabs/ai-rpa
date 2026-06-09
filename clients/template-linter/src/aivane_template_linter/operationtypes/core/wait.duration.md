---
{
  "schemaVersion": 1,
  "operationType": "wait.duration",
  "executorClass": "aivane.core.executor.WaitDurationExecutor",
  "displayName": "Waiting time",
  "description": "Fixed duration waiting, supporting millisecond-level precision",
  "category": "process_control",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "milliseconds",
      "type": "integer",
      "allowedTypes": [
        "integer",
        "string"
      ],
      "required": true,
      "description": "Waiting time, in milliseconds."
    }
  ]
}
---

# wait.duration
