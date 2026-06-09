---
{
  "schemaVersion": 1,
  "operationType": "browser.tab.switch",
  "executorClass": "aivane.browser.executor.BrowserTabSwitchExecutor",
  "displayName": "Switch tabs",
  "description": "Switch to the tab page of the specified index",
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
      "default": 0,
      "description": "The index of the tab to switch to."
    }
  ]
}
---

# browser.tab.switch
