---
{
  "schemaVersion": 1,
  "operationType": "android.touch.tap",
  "displayName": "Android Tap",
  "description": "Execute an Android tap gesture.",
  "category": "Android automation",
  "platforms": ["android"],
  "parameters": [
    {
      "name": "mode",
      "type": "string",
      "required": true,
      "enumValues": ["coordinate", "element", "locator"]
    },
    {
      "name": "x",
      "type": ["integer", "string"]
    },
    {
      "name": "y",
      "type": ["integer", "string"]
    },
    {
      "name": "element",
      "type": "any"
    },
    {
      "name": "xpath",
      "type": "string"
    },
    {
      "name": "id",
      "type": "string"
    },
    {
      "name": "text",
      "type": "string"
    },
    {
      "name": "contentDescription",
      "type": "string"
    },
    {
      "name": "className",
      "type": "string"
    },
    {
      "name": "elementName",
      "type": "string"
    }
  ],
  "constraints": {
    "conditionalRequired": [
      {
        "conditionParam": "mode",
        "conditionValue": "coordinate",
        "requiredParams": ["x", "y"]
      },
      {
        "conditionParam": "mode",
        "conditionValue": "element",
        "requiredParams": ["element"]
      }
    ],
    "conditionalOneOfRequired": [
      {
        "conditionParam": "mode",
        "conditionValue": "locator",
        "requiredParams": ["xpath", "id", "text", "contentDescription", "className", "elementName"]
      }
    ],
    "rejectUnknownParams": true
  }
}
---

# android.touch.tap
