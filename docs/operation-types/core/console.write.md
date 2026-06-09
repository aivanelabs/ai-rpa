---
{
  "schemaVersion": 1,
  "operationType": "console.write",
  "executorClass": "aivane.core.executor.ConsoleExecutor",
  "displayName": "Console output (cross-platform)",
  "description": "Cross-platform console outputs log information, using a unified log system to support color output and variable replacement",
  "category": "debugging_tools",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "message",
      "type": "string",
      "required": true,
      "allowEmpty": true,
      "defaultValue": "",
      "description": "The content of the message to be output to the console"
    },
    {
      "name": "level",
      "type": "enum",
      "required": false,
      "defaultValue": "INFO",
      "enumValues": [
        "DEBUG",
        "INFO",
        "WARN",
        "ERROR"
      ],
      "description": "Log level"
    },
    {
      "name": "newline",
      "type": "boolean",
      "required": false,
      "defaultValue": true,
      "description": "Whether to wrap the line, the default is true"
    }
  ]
}
---

# console.write
