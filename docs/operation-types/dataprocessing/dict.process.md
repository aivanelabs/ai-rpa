---
{
  "schemaVersion": 1,
  "operationType": "dict.process",
  "executorClass": "aivane.dataprocessing.executor.DictProcessExecutor",
  "displayName": "Dictionary processing",
  "description": "Dictionary processing operations - supports getting, setting, deleting, traversing, merging, etc.",
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
      "description": "The dictionary processing operation to perform.",
      "enumValues": [
        "create",
        "get",
        "set",
        "put",
        "putAll",
        "remove",
        "clear",
        "containsKey",
        "containsValue",
        "keys",
        "values",
        "entries",
        "size",
        "isEmpty",
        "merge",
        "copy",
        "clone",
        "renameKey",
        "getOrDefault",
        "computeIfAbsent",
        "filter",
        "pick",
        "omit",
        "has"
      ]
    },
    {
      "name": "output",
      "type": "string",
      "required": true,
      "description": "The name of the output variable that holds the processing results."
    },
    {
      "name": "dict",
      "type": [
        "object",
        "string"
      ],
      "description": "The target dictionary, or a string referencing a dictionary variable."
    },
    {
      "name": "initialCapacity",
      "type": [
        "integer",
        "string"
      ],
      "default": 16,
      "description": "The initial capacity for the create operation."
    },
    {
      "name": "key",
      "type": "string",
      "description": "Dictionary key name."
    },
    {
      "name": "value",
      "type": "any",
      "description": "The value to write or compare."
    },
    {
      "name": "entries",
      "type": [
        "object",
        "string"
      ],
      "description": "The key-value pair object used by putAll can also be passed as a JSON string."
    },
    {
      "name": "otherDict",
      "type": [
        "object",
        "string"
      ],
      "description": "Another dictionary used by the merge operation."
    },
    {
      "name": "oldKey",
      "type": "string",
      "description": "renameKey The old key name used."
    },
    {
      "name": "newKey",
      "type": "string",
      "description": "renameKey The new key name to use."
    },
    {
      "name": "defaultValue",
      "type": "any",
      "description": "The default value used by getOrDefault or computeIfAbsent."
    },
    {
      "name": "filterKey",
      "type": "string",
      "description": "The key name filter condition used by filter."
    },
    {
      "name": "filterValue",
      "type": "any",
      "description": "filter The value filter to use."
    },
    {
      "name": "keys",
      "type": [
        "array",
        "string"
      ],
      "description": "The set of keys used by pick or omit."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---
# dict.process
