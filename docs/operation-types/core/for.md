---
{
  "schemaVersion": 1,
  "operationType": "for",
  "executorClass": "aivane.core.executor.ForExecutor",
  "displayName": "For loop executor",
  "description": "For loop executor that supports multiple loop modes such as numeric range loop, array traversal, string traverse, etc.",
  "category": "process_control",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "type",
      "type": "enum",
      "required": false,
      "defaultValue": "range",
      "enumValues": [
        "range",
        "array",
        "string"
      ],
      "description": "Loop mode."
    },
    {
      "name": "variable",
      "type": "string",
      "required": false,
      "defaultValue": "i",
      "description": "Loop variable name."
    },
    {
      "name": "start",
      "type": "double",
      "allowedTypes": [
        "double",
        "string"
      ],
      "required": false,
      "description": "The starting value of the range pattern."
    },
    {
      "name": "end",
      "type": "double",
      "allowedTypes": [
        "double",
        "string"
      ],
      "required": false,
      "description": "The end value of the range pattern."
    },
    {
      "name": "step",
      "type": "double",
      "allowedTypes": [
        "double",
        "string"
      ],
      "required": false,
      "description": "The step size of range mode."
    },
    {
      "name": "array",
      "type": "array",
      "required": false,
      "description": "The array to be traversed in array mode."
    },
    {
      "name": "text",
      "type": "string",
      "required": false,
      "description": "The string to be traversed in string mode."
    },
    {
      "name": "indexVariable",
      "type": "string",
      "required": false,
      "description": "The variable name that holds the current index."
    },
    {
      "name": "maxIterations",
      "type": "integer",
      "allowedTypes": [
        "integer",
        "string"
      ],
      "required": false,
      "defaultValue": 10000,
      "description": "Maximum number of iterations."
    },
    {
      "name": "operations",
      "type": "array",
      "required": true,
      "description": "The loop body operates on the array."
    }
  ],
  "constraints": {
    "nestedOperations": [
      "operations"
    ]
  }
}
---

# for
