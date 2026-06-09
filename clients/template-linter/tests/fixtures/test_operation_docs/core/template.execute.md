---
{
  "operationType": "template.execute",
  "displayName": "Execute subtemplate",
  "category": "process_control",
  "platforms": ["core"],
  "parameters": [
    {
      "name": "templateId",
      "type": "string",
      "required": true
    },
    {
      "name": "parameters",
      "type": "object",
      "required": false
    },
    {
      "name": "continueOnFailure",
      "type": "boolean",
      "required": false
    }
  ],
  "constraints": {
    "requiresLoopContext": false
  }
}
---
