---
{
  "schemaVersion": 1,
  "operationType": "jump",
  "executorClass": "aivane.core.executor.JumpExecutor",
  "displayName": "Jump executor",
  "description": "Jump to the specified operation position to implement loop control flow",
  "category": "process_control",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "condition",
      "type": "string",
      "required": false,
      "description": "Jump conditional expression, using ${expr} format. Execute the jump when the condition is true."
    },
    {
      "name": "targetIndex",
      "type": "integer",
      "required": false,
      "description": "Target operation index (0-based)."
    },
    {
      "name": "targetLabel",
      "type": "string",
      "required": false,
      "description": "Target operation label, used to identify the jump target location."
    }
  ],
  "constraints": {
    "oneOfRequired": [
      "targetIndex",
      "targetLabel",
      "condition"
    ]
  }
}
---

# jump
