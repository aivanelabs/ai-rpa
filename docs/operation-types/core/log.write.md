---
{
  "schemaVersion": 1,
  "operationType": "log.write",
  "executorClass": "aivane.core.executor.LogWriteExecutor",
  "displayName": "Log writing (cross-platform)",
  "description": "Export the collected console.write logs to a file, supporting level filtering, append mode and variable replacement",
  "category": "debugging_tools",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "filePath",
      "type": "string",
      "required": true,
      "description": "Log output file path."
    },
    {
      "name": "append",
      "type": "boolean",
      "required": false,
      "defaultValue": false,
      "description": "Whether to write in append mode."
    },
    {
      "name": "filter",
      "type": "enum",
      "required": false,
      "enumValues": [
        "DEBUG",
        "INFO",
        "WARN",
        "ERROR"
      ],
      "description": "Minimum log level filtering."
    }
  ]
}
---

# log.write
