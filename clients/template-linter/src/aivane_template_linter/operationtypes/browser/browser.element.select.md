---
{
  "schemaVersion": 1,
  "operationType": "browser.element.select",
  "executorClass": "aivane.browser.executor.BrowserElementSelectExecutor",
  "displayName": "Select options",
  "description": "Select an option from the drop-down list",
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
      "name": "value",
      "type": "string",
      "required": true,
      "description": "The option value to select."
    },
    {
      "name": "timeout",
      "type": [
        "integer",
        "string"
      ],
      "default": 30000,
      "description": "Select the timeout period for the operation, in milliseconds."
    }
  ]
}
---

# browser.element.select
