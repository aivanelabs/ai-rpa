---
{
  "schemaVersion": 1,
  "operationType": "android.element.getAll",
  "executorClass": "aivane.android.executor.AndroidElementGetAllExecutor",
  "displayName": "Get Android elements in batches",
  "description": "Finds all matching Android UI elements based on the locator and returns a list of elements.",
  "category": "android_automation",
  "platforms": [
    "android"
  ],
  "parameters": [
    {
      "name": "xpath",
      "type": "string",
      "description": "Locate Android elements using XPath."
    },
    {
      "name": "id",
      "type": "string",
      "description": "Locate Android elements using resource IDs."
    },
    {
      "name": "text",
      "type": "string",
      "description": "Position Android elements using text content."
    },
    {
      "name": "className",
      "type": "string",
      "description": "Locate Android elements using class names."
    },
    {
      "name": "contentDescription",
      "type": "string",
      "description": "Use contentDescription to locate Android elements."
    },
    {
      "name": "elementName",
      "type": "string",
      "description": "Element name read from elements.json."
    },
    {
      "name": "variableName",
      "type": "string",
      "default": "elements",
      "description": "The variable name to hold the result list."
    },
    {
      "name": "waitFor",
      "type": [
        "integer",
        "string"
      ],
      "default": 0,
      "description": "The maximum length of time to wait for an element to appear, in milliseconds."
    },
    {
      "name": "minCount",
      "type": [
        "integer",
        "string"
      ],
      "default": 0,
      "description": "The minimum number of matches required; if insufficient, an empty list is returned."
    },
    {
      "name": "maxCount",
      "type": [
        "integer",
        "string"
      ],
      "description": "The maximum number of results returned."
    }
  ],
  "constraints": {
    "oneOfRequired": [
      "xpath",
      "id",
      "text",
      "className",
      "contentDescription",
      "elementName"
    ],
    "rejectUnknownParams": true
  }
}
---

# android.element.getAll
