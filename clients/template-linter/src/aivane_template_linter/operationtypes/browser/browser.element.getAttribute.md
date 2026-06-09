---
{
  "schemaVersion": 1,
  "operationType": "browser.element.getAttribute",
  "executorClass": "aivane.browser.executor.BrowserElementGetAttributeExecutor",
  "displayName": "Get properties",
  "description": "Get the specified attribute value of the element",
  "category": "browser.element",
  "platforms": [
    "browser"
  ],
  "parameters": [
    {
      "name": "sessionId",
      "type": "string",
      "description": "Browser session ID; when empty, the current context session is used."
    },
    {
      "name": "selector",
      "type": "string",
      "required": true,
      "description": "Selectors supported by CSS or Playwright."
    },
    {
      "name": "attribute",
      "type": "string",
      "required": true,
      "description": "The name of the property to read."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "required": true,
      "description": "The name of the variable that holds the attribute value."
    },
    {
      "name": "timeout",
      "type": [
        "integer",
        "string"
      ],
      "default": 30000,
      "description": "Timeout for obtaining attributes, in milliseconds."
    }
  ]
}
---

# browser.element.getAttribute
