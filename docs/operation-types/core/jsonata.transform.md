---
{
  "schemaVersion": 1,
  "operationType": "jsonata.transform",
  "executorClass": "aivane.core.executor.JsonataTransformExecutor",
  "displayName": "JSONata transform",
  "description": "Query, filter, and transform JSON-compatible data using standard JSONata expressions. String inputs that contain JSON objects or arrays are parsed automatically.",
  "category": "data_processing",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "expression",
      "type": "string",
      "required": true,
      "description": "Standard JSONata expression."
    },
    {
      "name": "data",
      "type": "any",
      "required": true,
      "description": "Enter data."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "required": false,
      "description": "The name of the variable that holds the conversion result."
    }
  ]
}
---

# jsonata.transform
