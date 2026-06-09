---
{
  "schemaVersion": 1,
  "operationType": "application.execute",
  "executorClass": "aivane.core.executor.ApplicationExecuteExecutor",
  "displayName": "Execute application",
  "description": "Execute the main process (__main__.json) of other applications, supporting parameter passing, version selection and return value collection",
  "category": "process_control",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "applicationId",
      "type": "string",
      "required": true,
      "description": "Target application ID."
    },
    {
      "name": "applicationVersion",
      "type": "string",
      "required": false,
      "description": "Target application version. If not passed, the default version will be used."
    },
    {
      "name": "parameters",
      "type": "object",
      "required": false,
      "description": "Input parameters passed to the target application's main template."
    },
    {
      "name": "timeout",
      "type": "integer",
      "allowedTypes": [
        "integer",
        "string"
      ],
      "required": false,
      "description": "Execution timeout, in milliseconds."
    },
    {
      "name": "continueOnFailure",
      "type": "boolean",
      "required": false,
      "defaultValue": false,
      "description": "Whether to continue the current template when the target application fails to execute."
    }
  ]
}
---

# application.execute
