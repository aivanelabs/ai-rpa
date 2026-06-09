---
{
  "schemaVersion": 1,
  "operationType": "android.element.get",
  "executorClass": "aivane.android.executor.AndroidElementGetExecutor",
  "displayName": "Get Android element",
  "description": "Find Android UI elements based on locators or definitions in elements.json.",
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
      "default": "element",
      "description": "The variable name that holds the found element object."
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
      "name": "visibleOnly",
      "type": "boolean",
      "default": true,
      "description": "When true, only visible elements are eligible for single-element lookup. Set it to false to allow matching off-screen elements."
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

# android.element.get
