---
{
  "schemaVersion": 1,
  "operationType": "android.touch.swipe",
  "executorClass": "aivane.android.executor.AndroidElementSwipeExecutor",
  "displayName": "Android Swipe",
  "description": "Performs a swipe gesture on the Android screen or a specified element area.",
  "category": "android_automation",
  "platforms": [
    "android"
  ],
  "parameters": [
    {
      "name": "mode",
      "type": "enum",
      "description": "Sliding mode: coordinate, element, screen. If not specified, it will be automatically inferred based on area/type.",
      "enumValues": [
        "coordinate",
        "element",
        "screen"
      ]
    },
    {
      "name": "area",
      "type": "enum",
      "default": "screen",
      "description": "Sliding area: the entire screen or specified elements.",
      "enumValues": [
        "screen",
        "element"
      ]
    },
    {
      "name": "type",
      "type": "enum",
      "default": "direction",
      "description": "Sliding method: slide by direction or slide by coordinates.",
      "enumValues": [
        "direction",
        "coordinates"
      ]
    },
    {
      "name": "direction",
      "type": "enum",
      "default": "down",
      "description": "The sliding direction in directional mode.",
      "enumValues": [
        "up",
        "down",
        "left",
        "right"
      ]
    },
    {
      "name": "startX",
      "type": [
        "integer",
        "string"
      ],
      "description": "Starting X coordinate in coordinate mode."
    },
    {
      "name": "startY",
      "type": [
        "integer",
        "string"
      ],
      "description": "Starting Y coordinate in coordinate mode."
    },
    {
      "name": "endX",
      "type": [
        "integer",
        "string"
      ],
      "description": "Ending X coordinate in coordinate mode."
    },
    {
      "name": "endY",
      "type": [
        "integer",
        "string"
      ],
      "description": "Ending Y coordinate in coordinate mode."
    },
    {
      "name": "element",
      "type": "any",
      "description": "Element mode directly passes in an Element object or variable reference."
    },
    {
      "name": "xpath",
      "type": "string",
      "description": "Element mode uses XPath to locate Android elements."
    },
    {
      "name": "id",
      "type": "string",
      "description": "Element mode uses resource IDs to locate Android elements."
    },
    {
      "name": "text",
      "type": "string",
      "description": "Element mode uses text content to position Android elements."
    },
    {
      "name": "className",
      "type": "string",
      "description": "Element patterns use class names to locate Android elements."
    },
    {
      "name": "contentDescription",
      "type": "string",
      "description": "Element mode uses contentDescription to locate Android elements."
    },
    {
      "name": "elementName",
      "type": "string",
      "description": "Element pattern The element name read from elements.json."
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
      "name": "duration",
      "type": [
        "integer",
        "string"
      ],
      "default": 300,
      "description": "Slide duration, in milliseconds."
    },
    {
      "name": "distance",
      "type": [
        "double",
        "integer",
        "string"
      ],
      "default": 0.5,
      "description": "The ratio of sliding distance to area size in direction mode."
    },
    {
      "name": "visibleOnly",
      "type": "boolean",
      "default": true,
      "description": "When true, only visible elements are eligible for single-element lookup in element mode. Set it to false to allow off-screen matches."
    }
  ],
  "constraints": {
    "conditionalRequired": [
      {
        "conditionParam": "mode",
        "conditionValue": "coordinate",
        "requiredParams": [
          "startX",
          "startY",
          "endX",
          "endY"
        ]
      }
    ],
    "conditionalOneOfRequired": [
      {
        "conditionParam": "mode",
        "conditionValue": "element",
        "requiredParams": [
          "element",
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

# android.touch.swipe
