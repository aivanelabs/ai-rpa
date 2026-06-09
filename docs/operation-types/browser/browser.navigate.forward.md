---
{
  "schemaVersion": 1,
  "operationType": "browser.navigate.forward",
  "executorClass": "aivane.browser.executor.BrowserNavigateExecutor",
  "displayName": "go ahead",
  "description": "Go to next page",
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

# browser.navigate.forward
