---
{
  "schemaVersion": 1,
  "operationType": "android.element.count",
  "executorClass": "aivane.android.executor.AndroidElementCountExecutor",
  "displayName": "Count the number of Android elements",
  "description": "Count the number of matching Android UI elements based on the locator and directly return an integer result.",
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
      "defaultValue": "count",
      "description": "Save the matching number of variable names."
    },
    {
      "name": "waitFor",
      "type": [
        "integer",
        "string"
      ],
      "defaultValue": 0,
      "description": "The maximum length of time to wait for an element to appear, in milliseconds."
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

# android.element.count
