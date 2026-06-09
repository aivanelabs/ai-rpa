---
{
  "schemaVersion": 1,
  "operationType": "browser.navigate.back",
  "executorClass": "aivane.browser.executor.BrowserNavigateExecutor",
  "displayName": "Back",
  "description": "Go back to previous page",
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

# browser.navigate.back
