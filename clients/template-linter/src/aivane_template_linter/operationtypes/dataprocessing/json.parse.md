---
{
  "schemaVersion": 1,
  "operationType": "json.parse",
  "executorClass": "aivane.dataprocessing.executor.JsonParseExecutor",
  "displayName": "JSON parsing",
  "description": "JSON parsing operation - supports parsing, generation, path query, formatting, etc.",
  "category": "DATA_PROCESSING",
  "platforms": [
    "core"
  ],
  "aliases": [],
  "parameters": [
    {
      "name": "operation",
      "type": "string",
      "required": true,
      "description": "The JSON operation to perform.",
      "enumValues": [
        "parse",
        "parseArray",
        "stringify",
        "pretty",
        "get",
        "set",
        "has",
        "keys",
        "values",
        "length",
        "merge",
        "validate",
        "flatten"
      ]
    },
    {
      "name": "output",
      "type": "string",
      "required": true,
      "description": "The name of the output variable that holds the processing results."
    },
    {
      "name": "input",
      "type": "any",
      "description": "Enter a JSON string, object, or array."
    },
    {
      "name": "indent",
      "type": [
        "integer",
        "string"
      ],
      "default": 2,
      "description": "The number of indent spaces for pretty operations."
    },
    {
      "name": "path",
      "type": "string",
      "description": "The path used by get, set, and has operations."
    },
    {
      "name": "defaultValue",
      "type": "any",
      "description": "The default value returned by the get operation when the path does not exist."
    },
    {
      "name": "value",
      "type": "any",
      "description": "The value written by the set operation."
    },
    {
      "name": "otherJson",
      "type": "any",
      "description": "Another JSON object used by the merge operation."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---
# json.parse
