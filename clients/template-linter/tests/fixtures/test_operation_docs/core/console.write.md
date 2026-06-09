---
{
  "operationType": "console.write",
  "displayName": "Console write",
  "category": "DEBUG",
  "platforms": ["core"],
  "parameters": [
    {
      "name": "message",
      "type": "string",
      "required": true,
      "allowEmpty": true,
      "description": "Message content"
    },
    {
      "name": "level",
      "type": "enum",
      "defaultValue": "INFO",
      "enumValues": ["DEBUG", "INFO", "WARN", "ERROR"],
      "description": "Log level"
    }
  ],
  "constraints": {
    "requiresLoopContext": false
  }
}
---
