---
{
  "schemaVersion": 1,
  "operationType": "template.execute",
  "executorClass": "aivane.core.executor.TemplateExecuteExecutor",
  "displayName": "Execute subtemplate",
  "description": "Call and execute subtemplates, support parameter passing and OUTPUT collection, and configure timeout and failure handling strategies",
  "category": "process_control",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "templateId",
      "type": "string",
      "required": true,
      "description": "Target subtemplate ID."
    },
    {
      "name": "parameters",
      "type": "object",
      "required": false,
      "description": "Input parameters passed to the child template."
    },
    {
      "name": "outputPrefix",
      "type": "string",
      "required": false,
      "description": "The prefix used when recycling subtemplate output variables."
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
      "description": "Whether to continue the current template when the subtemplate fails to execute."
    }
  ]
}
---

# template.execute
