---
{
  "schemaVersion": 1,
  "operationType": "android.element.getAttribute",
  "executorClass": "aivane.android.executor.AndroidElementGetAttributeExecutor",
  "displayName": "Element attribute reading",
  "description": "Read the text, contentDesc, bounds and other attributes of Android UI elements.",
  "category": "android_automation",
  "platforms": [
    "android"
  ],
  "parameters": [
    {
      "name": "attribute",
      "type": "enum",
      "required": true,
      "description": "The name of the element attribute to be read.",
      "enumValues": [
        "text",
        "content-desc",
        "contentDesc",
        "content-description",
        "contentDescription",
        "bounds",
        "classname",
        "className",
        "class",
        "package",
        "packageName",
        "clickable",
        "checkable",
        "checked",
        "enabled",
        "focusable",
        "focused",
        "scrollable",
        "long-clickable",
        "longclickable",
        "selected"
      ]
    },
    {
      "name": "targetVariable",
      "type": "string",
      "required": true,
      "description": "The name of the variable that holds the attribute value."
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
      "name": "optional",
      "type": [
        "boolean",
        "string"
      ],
      "default": false,
      "description": "Whether to return null instead of reporting an error when the element is not found."
    },
    {
      "name": "visibleOnly",
      "type": "boolean",
      "default": true,
      "description": "When true, only visible elements are eligible for single-element lookup. Set it to false to allow reading attributes from off-screen matches."
    }
  ],
  "constraints": {
    "oneOfRequired": [
      "element",
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

# android.element.getAttribute
