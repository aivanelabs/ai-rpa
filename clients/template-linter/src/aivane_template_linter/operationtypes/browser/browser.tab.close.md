---
{
  "schemaVersion": 1,
  "operationType": "browser.tab.close",
  "executorClass": "aivane.browser.executor.BrowserTabCloseExecutor",
  "displayName": "Close tab",
  "description": "Close the tab of the specified index (if not specified, close the current tab)",
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
      "name": "index",
      "type": [
        "integer",
        "string"
      ],
      "description": "The index of the tab to close; closes the current page if empty."
    }
  ]
}
---

# browser.tab.close
