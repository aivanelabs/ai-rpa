---
{
  "schemaVersion": 1,
  "operationType": "browser.element.getText",
  "executorClass": "aivane.browser.executor.BrowserElementGetTextExecutor",
  "displayName": "Get text",
  "description": "Get the text content of an element",
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
      "description": "The variable name that holds the text content."
    },
    {
      "name": "timeout",
      "type": [
        "integer",
        "string"
      ],
      "default": 30000,
      "description": "Timeout for getting text, in milliseconds."
    }
  ]
}
---

# browser.element.getText
