---
{
  "schemaVersion": 1,
  "operationType": "android.navigate.backUntil",
  "executorClass": "aivane.android.executor.AndroidNavigateBackUntilExecutor",
  "displayName": "Return until condition is hit",
  "description": "Keep executing the back key in Android until the targeting condition is hit or the maximum number of backs is reached.",
  "category": "android_automation",
  "platforms": [
    "android"
  ],
  "parameters": [
    {
      "name": "xpath",
      "type": "string",
      "description": "Use XPath to locate hit criteria."
    },
    {
      "name": "id",
      "type": "string",
      "description": "Target hits using resource IDs."
    },
    {
      "name": "text",
      "type": "string",
      "description": "Target hit criteria using text content."
    },
    {
      "name": "className",
      "type": "string",
      "description": "Use class names to locate hit criteria."
    },
    {
      "name": "contentDescription",
      "type": "string",
      "description": "Use contentDescription to target hit criteria."
    },
    {
      "name": "elementName",
      "type": "string",
      "description": "Element name read from elements.json."
    },
    {
      "name": "maxBacks",
      "type": [
        "integer",
        "string"
      ],
      "defaultValue": 10,
      "description": "Maximum number of returns."
    },
    {
      "name": "settleMs",
      "type": [
        "integer",
        "string"
      ],
      "defaultValue": 500,
      "description": "The waiting time after each return, in milliseconds."
    },
    {
      "name": "minCount",
      "type": [
        "integer",
        "string"
      ],
      "defaultValue": 1,
      "description": "Minimum number of matches required for a hit to succeed."
    },
    {
      "name": "launchPackageName",
      "type": "string",
      "description": "Optional: Start the specified application before execution."
    },
    {
      "name": "withinPackageName",
      "type": "string",
      "description": "Optional: Only continue to return if the current foreground package name still has this value."
    },
    {
      "name": "matchedCountVariable",
      "type": "string",
      "description": "Optional: Save the variable name of the last matched number."
    },
    {
      "name": "backCountVariable",
      "type": "string",
      "description": "Optional: Save the variable name of the number of times the return has been executed."
    },
    {
      "name": "waitFor",
      "type": [
        "integer",
        "string"
      ],
      "defaultValue": 0,
      "description": "The maximum length of time to wait for an element to appear during each round of checking conditions, in milliseconds."
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

# android.navigate.backUntil
