---
{
  "schemaVersion": 1,
  "operationType": "android.element.input",
  "executorClass": "aivane.android.executor.AndroidElementInputExecutor",
  "displayName": "element input",
  "description": "Input text to Android UI elements, support element objects, locators, focus input boxes, or focus by coordinates first and then input.",
  "category": "android_automation",
  "platforms": [
    "android"
  ],
  "parameters": [
    {
      "name": "value",
      "type": "string",
      "required": true,
      "allowEmpty": true,
      "description": "The text content to be entered."
    },
    {
      "name": "x",
      "type": [
        "integer",
        "string"
      ],
      "description": "In coordinate mode, first click on the X coordinate used when focusing."
    },
    {
      "name": "y",
      "type": [
        "integer",
        "string"
      ],
      "description": "In coordinate mode, first click on the Y coordinate used when focusing."
    },
    {
      "name": "element",
      "type": "any",
      "description": "Element objects or variable references passed directly take precedence over positioning parameters."
    },
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
      "description": "Use text content to locate Android elements; when element is not passed, this is the positioning parameter, not the input content."
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
      "name": "waitFor",
      "type": [
        "integer",
        "string"
      ],
      "default": 0,
      "description": "The maximum length of time to wait for an element to appear, in milliseconds."
    },
    {
      "name": "clearFirst",
      "type": [
        "boolean",
        "string"
      ],
      "default": false,
      "description": "Whether to clear the original content before inputting."
    },
    {
      "name": "visibleOnly",
      "type": "boolean",
      "default": true,
      "description": "When true, only visible elements are eligible for single-element lookup when positioning by locator. Set it to false to allow off-screen matches."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---

# android.element.input
