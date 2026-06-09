---
{
  "schemaVersion": 1,
  "operationType": "browser.element.get",
  "executorClass": "aivane.browser.executor.BrowserElementGetExecutor",
  "displayName": "Get element",
  "description": "Get a single element via CSS selector",
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
      "name": "outputVariable",
      "type": "string",
      "required": true,
      "description": "The variable name that holds the element object."
    },
    {
      "name": "timeout",
      "type": [
        "integer",
        "string"
      ],
      "default": 30000,
      "description": "Timeout for finding elements, in milliseconds."
    }
  ]
}
---

# browser.element.get
