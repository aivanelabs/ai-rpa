---
{
  "schemaVersion": 1,
  "operationType": "android.touch.tap",
  "executorClass": "aivane.android.executor.AndroidTouchTapExecutor",
  "displayName": "Android Tap",
  "description": "Performs the Android tap gesture, supporting coordinates, element objects, locators, or element names defined in elements.json.",
  "category": "android_automation",
  "platforms": [
    "android"
  ],
  "parameters": [
    {
      "name": "mode",
      "type": "string",
      "required": true,
      "description": "Click mode: coordinate, element, or locator.",
      "enumValues": [
        "coordinate",
        "element",
        "locator"
      ]
    },
    {
      "name": "x",
      "type": [
        "integer",
        "string"
      ],
      "description": "X coordinate in coordinate mode."
    },
    {
      "name": "y",
      "type": [
        "integer",
        "string"
      ],
      "description": "Y coordinate in coordinate mode."
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
      "description": "Position Android elements using text content."
    },
    {
      "name": "contentDescription",
      "type": "string",
      "description": "Use contentDescription to locate Android elements."
    },
    {
      "name": "className",
      "type": "string",
      "description": "Locate Android elements using class names."
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
      "description": "The maximum length of time to wait for an element to appear, in milliseconds.",
      "default": 0
    },
    {
      "name": "visibleOnly",
      "type": "boolean",
      "default": true,
      "description": "When true, only visible elements are eligible for locator-based single-element lookup. Set it to false to allow off-screen matches."
    }
  ],
  "constraints": {
    "conditionalRequired": [
      {
        "conditionParam": "mode",
        "conditionValue": "coordinate",
        "requiredParams": [
          "x",
          "y"
        ]
      },
      {
        "conditionParam": "mode",
        "conditionValue": "element",
        "requiredParams": [
          "element"
        ]
      }
    ],
    "conditionalOneOfRequired": [
      {
        "conditionParam": "mode",
        "conditionValue": "locator",
        "requiredParams": [
          "xpath",
          "id",
          "text",
          "contentDescription",
          "className",
          "elementName"
        ]
      }
    ],
    "rejectUnknownParams": true
  }
}
---

# android.touch.tap

Runtime schema source of truth for Android tap.
