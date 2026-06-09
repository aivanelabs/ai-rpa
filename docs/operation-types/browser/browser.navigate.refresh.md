---
{
  "schemaVersion": 1,
  "operationType": "browser.navigate.refresh",
  "executorClass": "aivane.browser.executor.BrowserNavigateExecutor",
  "displayName": "refresh page",
  "description": "Refresh current page",
  "category": "browser",
  "platforms": [
    "browser"
  ],
  "parameters": [
    {
      "name": "sessionId",
      "type": "string",
      "description": "Browser session ID; when empty, the current context session is used."
    }
  ]
}
---

# browser.navigate.refresh
