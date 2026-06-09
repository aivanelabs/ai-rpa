---
{
  "schemaVersion": 1,
  "operationType": "browser.tab.open",
  "executorClass": "aivane.browser.executor.BrowserTabOpenExecutor",
  "displayName": "Open tab",
  "description": "Open a new browser tab",
  "category": "browser.tab",
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
      "name": "url",
      "type": "string",
      "default": "about:blank",
      "description": "The target URL after a new tab is opened."
    }
  ]
}
---

# browser.tab.open
