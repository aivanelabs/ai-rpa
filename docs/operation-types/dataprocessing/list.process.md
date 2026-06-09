---
{
  "schemaVersion": 1,
  "operationType": "list.process",
  "executorClass": "aivane.dataprocessing.executor.ListProcessExecutor",
  "displayName": "List processing",
  "description": "List processing operations - supports adding, deleting, sorting, filtering, etc.",
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
      "description": "The list processing operation to perform.",
      "enumValues": [
        "create",
        "add",
        "insert",
        "remove",
        "removeAt",
        "removeAll",
        "clear",
        "get",
        "set",
        "indexOf",
        "lastIndexOf",
        "contains",
        "size",
        "isEmpty",
        "sort",
        "reverse",
        "slice",
        "concat",
        "distinct",
        "filter",
        "map",
        "reduce",
        "sum",
        "avg",
        "max",
        "min",
        "join",
        "shuffle",
        "swap",
        "subList",
        "pop",
        "push",
        "peek",
        "anyMatch",
        "allMatch",
        "noneMatch"
      ]
    },
    {
      "name": "output",
      "type": "string",
      "required": true,
      "description": "The name of the output variable that holds the processing results."
    },
    {
      "name": "list",
      "type": [
        "array",
        "string"
      ],
      "description": "A list of targets, or a string referencing a list variable."
    },
    {
      "name": "initialCapacity",
      "type": [
        "integer",
        "string"
      ],
      "default": 10,
      "description": "The initial capacity for the create operation."
    },
    {
      "name": "element",
      "type": "any",
      "description": "Element values ​​used by add, insert, set, push and other operations."
    },
    {
      "name": "elements",
      "type": [
        "array",
        "string"
      ],
      "description": "A list of elements used by the removeAll operation."
    },
    {
      "name": "index",
      "type": [
        "integer",
        "string"
      ],
      "description": "Element index."
    },
    {
      "name": "otherIndex",
      "type": [
        "integer",
        "string"
      ],
      "default": 1,
      "description": "Another index in a swap operation."
    },
    {
      "name": "otherList",
      "type": [
        "array",
        "string"
      ],
      "description": "concat operates another list to be concatenated."
    },
    {
      "name": "ascending",
      "type": [
        "boolean",
        "string"
      ],
      "default": true,
      "description": "sort Whether to sort in ascending order."
    },
    {
      "name": "fromIndex",
      "type": [
        "integer",
        "string"
      ],
      "default": 0,
      "description": "The starting index of the slice."
    },
    {
      "name": "toIndex",
      "type": [
        "integer",
        "string"
      ],
      "description": "The end index of the slice."
    },
    {
      "name": "condition",
      "type": "string",
      "description": "The condition string used by filter."
    },
    {
      "name": "value",
      "type": "any",
      "description": "Comparison values ​​used by operations such as filter."
    },
    {
      "name": "expression",
      "type": "string",
      "description": "The expression used by map."
    },
    {
      "name": "targetType",
      "type": "string",
      "default": "string",
      "description": "The target type of the map operation.",
      "enumValues": [
        "string",
        "int",
        "integer",
        "double",
        "boolean"
      ]
    },
    {
      "name": "reduceOperation",
      "type": "string",
      "default": "sum",
      "description": "The aggregation method used by the reduce operation.",
      "enumValues": [
        "sum",
        "+",
        "product",
        "*",
        "concat"
      ]
    },
    {
      "name": "delimiter",
      "type": "string",
      "default": ",",
      "description": "The delimiter used by join."
    },
    {
      "name": "from",
      "type": [
        "integer",
        "string"
      ],
      "default": 0,
      "description": "The starting index of subList."
    },
    {
      "name": "to",
      "type": [
        "integer",
        "string"
      ],
      "description": "End index of subList."
    },
    {
      "name": "target",
      "type": "string",
      "description": "The target string for anyMatch, allMatch, noneMatch comparison."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---
# list.process
