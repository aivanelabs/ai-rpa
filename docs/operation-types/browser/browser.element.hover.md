---
{
  "schemaVersion": 1,
  "operationType": "browser.element.hover",
  "executorClass": "aivane.browser.executor.BrowserElementHoverExecutor",
  "displayName": "hover element",
  "description": "Hover the mouse over the specified element",
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
      "name": "timeout",
      "type": [
        "integer",
        "string"
      ],
      "default": 30000,
      "description": "The timeout for the hover operation, in milliseconds."
    }
  ]
}
---

# browser.element.hover
