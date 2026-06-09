---
{
  "schemaVersion": 1,
  "operationType": "datetime.process",
  "executorClass": "aivane.dataprocessing.executor.DatetimeProcessExecutor",
  "displayName": "Date and time processing",
  "description": "Date and time processing operations - supports parsing, formatting, calculation, comparison, obtaining time components, etc.",
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
      "description": "The datetime processing operation to perform.",
      "enumValues": [
        "now",
        "today",
        "timestamp",
        "parse",
        "format",
        "toTimestamp",
        "fromTimestamp",
        "add",
        "subtract",
        "isBefore",
        "isAfter",
        "isSameDay",
        "equals",
        "compareTo",
        "get",
        "set",
        "startOfDay",
        "endOfDay",
        "startOfWeek",
        "startOfMonth",
        "startOfYear",
        "diff",
        "between",
        "isWeekend"
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
      "description": "Enter a date, timestamp, or date string."
    },
    {
      "name": "format",
      "type": "string",
      "default": "yyyy-MM-dd HH:mm:ss",
      "description": "The date format used by parse or format."
    },
    {
      "name": "amount",
      "type": [
        "integer",
        "string"
      ],
      "default": 0,
      "description": "The amount of add or subtract added or subtracted."
    },
    {
      "name": "unit",
      "type": "string",
      "description": "The time unit used by add, subtract, diff, and between.",
      "enumValues": [
        "years",
        "year",
        "months",
        "month",
        "days",
        "day",
        "hours",
        "hour",
        "minutes",
        "minute",
        "seconds",
        "second",
        "millis",
        "millisecond"
      ]
    },
    {
      "name": "otherDate",
      "type": "any",
      "description": "Another time value used by comparison, diff, and between operations."
    },
    {
      "name": "field",
      "type": "string",
      "default": "day",
      "description": "Time field used by get or set operations.",
      "enumValues": [
        "year",
        "month",
        "day",
        "hour",
        "minute",
        "second",
        "millisecond",
        "dayofweek",
        "dayOfWeek",
        "dayofyear",
        "dayOfYear"
      ]
    },
    {
      "name": "value",
      "type": [
        "integer",
        "string"
      ],
      "default": 0,
      "description": "The field value written by the set operation."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---
# datetime.process
