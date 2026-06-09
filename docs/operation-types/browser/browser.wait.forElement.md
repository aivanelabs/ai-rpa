---
{
  "schemaVersion": 1,
  "operationType": "browser.wait.forElement",
  "executorClass": "aivane.browser.executor.BrowserWaitForElementExecutor",
  "displayName": "await element",
  "description": "Wait for the element to reach the specified state (attached, detached, visible, hidden)",
  "category": "browser.wait",
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
      "name": "state",
      "type": "string",
      "default": "visible",
      "enumValues": [
        "attached",
        "detached",
        "visible",
        "hidden"
      ],
      "description": "The state of the element to wait for."
    },
    {
      "name": "timeout",
      "type": [
        "integer",
        "string"
      ],
      "default": 30000,
      "description": "Timeout for waiting for elements, in milliseconds."
    }
  ]
}
---

# browser.wait.forElement
