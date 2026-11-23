---
{
  "schemaVersion": 1,
  "operationType": "android.touch.drag",
  "executorClass": "aivane.android.executor.AndroidTouchDragExecutor",
  "displayName": "Android Drag",
  "description": "Presses and holds the start point (a point, an element object or a located element's center), then moves to the end point without lifting. Use it for drag and drop, sliders and reordering; use android.touch.swipe for scrolling.",
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
      "description": "Start mode: coordinate, element, or locator."
    },
    {
      "name": "x",
      "type": [
        "integer",
        "double",
        "string"
      ],
      "description": "Start X coordinate in coordinate mode."
    },
    {
      "name": "y",
      "type": [
        "integer",
        "double",
        "string"
      ],
      "description": "Start Y coordinate in coordinate mode."
    },
    {
      "name": "endX",
      "type": [
        "integer",
        "double",
        "string"
      ],
      "required": true,
      "description": "End X coordinate on the screen."
    },
    {
      "name": "endY",
      "type": [
        "integer",
        "double",
        "string"
      ],
      "required": true,
      "description": "End Y coordinate on the screen."
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
      "name": "holdDuration",
      "type": [
        "integer",
        "string"
      ],
      "default": 600,
      "minimum": 0,
      "maximum": 10000,
      "description": "How long to hold the start point before moving, in milliseconds. 0 moves at once."
    },
    {
      "name": "duration",
      "type": [
        "integer",
        "string"
      ],
      "default": 500,
      "minimum": 50,
      "maximum": 10000,
      "description": "How long the move to the end point takes, in milliseconds."
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
      "template": "Drag Android {target}{x}{y} to {endX}, {endY}",
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
          "prefix": " from x="
        },
        "y": {
          "param": "y",
          "kind": "number",
          "prefix": ", y="
        },
        "endX": {
          "param": "endX",
          "kind": "number"
        },
        "endY": {
          "param": "endY",
          "kind": "number"
        }
      }
    }
  }
}
---

# android.touch.drag

Runtime schema source of truth for Android drag. The hold and the move are one continued stroke, so the app sees a single press that moves.
