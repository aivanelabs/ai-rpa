---
{
  "schemaVersion": 1,
  "operationType": "browser.script.execute",
  "executorClass": "aivane.browser.executor.BrowserScriptExecuteExecutor",
  "displayName": "Execute script",
  "description": "Execute JavaScript code in the page",
  "category": "browser.script",
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
      "name": "script",
      "type": "string",
      "required": true,
      "description": "JavaScript code to be executed in the context of the page."
    }
  ]
}
---

# browser.script.execute
