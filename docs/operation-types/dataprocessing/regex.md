---
{
  "schemaVersion": 1,
  "operationType": "regex",
  "executorClass": "aivane.dataprocessing.executor.RegexExecutor",
  "displayName": "regular expression",
  "description": "Regular expression operations - supports matching, search, replacement, extraction, etc.",
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
      "description": "Regular operation to perform.",
      "enumValues": [
        "match",
        "matches",
        "find",
        "findFirst",
        "replace",
        "replaceAll",
        "split",
        "extract",
        "extractAll",
        "extractGroups",
        "count",
        "containsPattern",
        "test",
        "findIndexes",
        "replaceWithCallback"
      ]
    },
    {
      "name": "pattern",
      "type": "string",
      "required": true,
      "description": "Regular expression pattern."
    },
    {
      "name": "output",
      "type": "string",
      "required": true,
      "description": "The name of the output variable that holds the processing results."
    },
    {
      "name": "input",
      "type": "string",
      "default": "",
      "description": "The input string to process."
    },
    {
      "name": "flags",
      "type": "string",
      "default": "",
      "description": "Regular flag string, which can be combined with i, m, s, d, u, x."
    },
    {
      "name": "replacement",
      "type": "string",
      "default": "",
      "description": "The replacement string used by replace, replaceAll, and replaceWithCallback."
    },
    {
      "name": "limit",
      "type": [
        "integer",
        "string"
      ],
      "default": 0,
      "description": "The maximum number of splits for the split operation, 0 means no limit."
    },
    {
      "name": "groupIndex",
      "type": [
        "integer",
        "string"
      ],
      "default": 0,
      "description": "Capture group index used by extract or extractAll."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---
# regex
