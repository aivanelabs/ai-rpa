---
{
  "schemaVersion": 1,
  "operationType": "json.format",
  "executorClass": "aivane.core.executor.JsonFormatExecutor",
  "displayName": "JSON formatting",
  "description": "Convert compressed JSON string to indented prettified format",
  "category": "data_processing",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "json",
      "type": "any",
      "required": true,
      "description": "JSON data or JSON string to be formatted."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "required": false,
      "description": "The variable name that holds the formatted result."
    },
    {
      "name": "indent",
      "type": "integer",
      "allowedTypes": [
        "integer",
        "string"
      ],
      "required": false,
      "defaultValue": 2,
      "description": "The number of spaces to indent."
    }
  ]
}
---

# json.format
