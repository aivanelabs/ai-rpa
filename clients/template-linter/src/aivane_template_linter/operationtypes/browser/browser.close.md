---
{
  "schemaVersion": 1,
  "operationType": "browser.close",
  "executorClass": "aivane.browser.executor.BrowserCloseExecutor",
  "displayName": "Close browser",
  "description": "Close the Playwright browser instance and release resources",
  "category": "browser",
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
      "name": "contextVariable",
      "type": "string",
      "default": "browser",
      "description": "Variable name that saves or reads the browser context."
    }
  ]
}
---

# browser.close
