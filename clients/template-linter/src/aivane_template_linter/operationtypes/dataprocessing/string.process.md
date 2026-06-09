---
{
  "schemaVersion": 1,
  "operationType": "string.process",
  "executorClass": "aivane.dataprocessing.executor.StringProcessExecutor",
  "displayName": "String processing",
  "description": "String processing operations - supports splitting, replacing, intercepting, case conversion, etc.",
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
      "description": "The string processing operation to perform.",
      "enumValues": [
        "split",
        "replace",
        "replaceAll",
        "replaceFirst",
        "substring",
        "toUpperCase",
        "toLowerCase",
        "trim",
        "ltrim",
        "trimLeft",
        "rtrim",
        "trimRight",
        "length",
        "indexOf",
        "lastIndexOf",
        "contains",
        "startsWith",
        "endsWith",
        "reverse",
        "join",
        "repeat",
        "padLeft",
        "padRight",
        "remove",
        "count",
        "isEmpty",
        "isNotEmpty",
        "isBlank",
        "isNotBlank",
        "toCharArray",
        "compareTo",
        "compareToIgnoreCase",
        "equals"
      ]
    },
    {
      "name": "input",
      "type": [
        "string",
        "array"
      ],
      "description": "Input a string; when operation=join, you can also directly pass in a string array."
    },
    {
      "name": "output",
      "type": "string",
      "required": true,
      "description": "The name of the output variable that holds the processing results."
    },
    {
      "name": "delimiter",
      "type": "string",
      "default": ",",
      "description": "The delimiter used by split or join."
    },
    {
      "name": "oldValue",
      "type": "string",
      "description": "The old value to use when finding, replacing, or deleting."
    },
    {
      "name": "newValue",
      "type": "string",
      "allowEmpty": true,
      "description": "The new value written by the replace operation."
    },
    {
      "name": "startIndex",
      "type": [
        "integer",
        "string"
      ],
      "default": 0,
      "description": "substring starting index."
    },
    {
      "name": "endIndex",
      "type": [
        "integer",
        "string"
      ],
      "description": "substring end index."
    },
    {
      "name": "length",
      "type": [
        "integer",
        "string"
      ],
      "description": "substring length."
    },
    {
      "name": "searchString",
      "type": "string",
      "description": "Find string, alias for oldValue."
    },
    {
      "name": "prefix",
      "type": "string",
      "description": "The prefix used by startsWith."
    },
    {
      "name": "suffix",
      "type": "string",
      "description": "The suffix used by endsWith."
    },
    {
      "name": "count",
      "type": [
        "integer",
        "string"
      ],
      "default": 1,
      "description": "repeat The number of times the operation is repeated."
    },
    {
      "name": "targetLength",
      "type": [
        "integer",
        "string"
      ],
      "description": "The target length of padLeft or padRight."
    },
    {
      "name": "fillChar",
      "type": "string",
      "default": " ",
      "description": "The padding character for padLeft or padRight."
    },
    {
      "name": "removeString",
      "type": "string",
      "description": "The string to be removed in the remove operation, an alias of oldValue."
    },
    {
      "name": "other",
      "type": "string",
      "description": "Another string used by comparison operations such as compareTo and equals."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---
# string.process
