---
{
  "schemaVersion": 1,
  "operationType": "android.touch.longPress",
  "executorClass": "aivane.android.executor.AndroidTouchLongPressExecutor",
  "displayName": "Android Long Press",
  "description": "Presses and holds a point, an element object, a located element's center, or an element defined in elements.json.",
  "category": "android_automation",
  "platforms": [
    "android"
  ],
  "parameters": [
    {
      "name": "mode",
      "type": "string",
      "required": true,
      "enumValues": [
        "coordinate",
        "element",
        "locator"
      ],
      "description": "Target mode: coordinate, element, or locator."
    },
    {
      "name": "x",
      "type": [
        "integer",
        "double",
        "string"
      ],
      "description": "Press X coordinate in coordinate mode."
    },
    {
      "name": "y",
      "type": [
        "integer",
        "double",
        "string"
      ],
      "description": "Press Y coordinate in coordinate mode."
    },
    {
      "name": "coordinateSpace",
      "type": "string",
      "default": "pixel",
      "enumValues": [
        "pixel",
        "normalized"
      ],
      "description": "Unit of x/y coordinates: pixel (whole screen pixels) or normalized (fractions 0..1 of the screen width and height, so a recorded point survives a different resolution)."
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
    },
    {
      "name": "duration",
      "type": [
        "integer",
        "string"
      ],
      "default": 800,
      "minimum": 500,
      "maximum": 10000,
      "description": "How long to hold the press, in milliseconds."
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
  },
  "display": {
    "summary": {
      "template": "Long press Android {target}{x}{y}{duration}",
      "tokens": {
        "target": {
          "firstOf": [
            "element",
            "xpath",
            "id",
            "text",
            "contentDescription",
            "className",
            "elementName"
          ],
          "kind": "locator"
        },
        "x": {
          "param": "x",
          "kind": "number",
          "prefix": " at x="
        },
        "y": {
          "param": "y",
          "kind": "number",
          "prefix": ", y="
        },
        "duration": {
          "param": "duration",
          "kind": "number",
          "prefix": ", hold ",
          "suffix": " ms",
          "whenNonDefault": true
        }
      }
    }
  }
}
---

# android.touch.longPress

Runtime schema source of truth for Android long press. The press is a dispatched gesture at the target's center, the same gesture the screen-mirror recorder injects.
