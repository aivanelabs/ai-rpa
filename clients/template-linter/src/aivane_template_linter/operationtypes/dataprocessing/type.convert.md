---
{
  "schemaVersion": 1,
  "operationType": "type.convert",
  "executorClass": "aivane.dataprocessing.executor.TypeConvertExecutor",
  "displayName": "type conversion",
  "description": "Data type conversion operation - supports string, number, Boolean and other type conversions",
  "category": "DATA_PROCESSING",
  "platforms": [
    "core"
  ],
  "aliases": [],
  "parameters": [
    {
      "name": "input",
      "type": "any",
      "description": "The input value to be converted."
    },
    {
      "name": "targetType",
      "type": "string",
      "required": true,
      "description": "Target data type.",
      "enumValues": [
        "string",
        "int",
        "integer",
        "long",
        "double",
        "float",
        "boolean",
        "number",
        "date"
      ]
    },
    {
      "name": "output",
      "type": "string",
      "required": true,
      "description": "The name of the output variable that holds the processing results."
    },
    {
      "name": "format",
      "type": "string",
      "description": "The format used when converting dates or numbers to strings."
    },
    {
      "name": "defaultValue",
      "type": "any",
      "description": "The fallback value when conversion fails."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---
# type.convert
