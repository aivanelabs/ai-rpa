---
{
  "schemaVersion": 1,
  "operationType": "browser.script.evaluate",
  "executorClass": "aivane.browser.executor.BrowserScriptEvaluateExecutor",
  "displayName": "script evaluation",
  "description": "Execute a JavaScript expression and save the result to a variable",
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
      "description": "JavaScript code to execute and return results."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "required": true,
      "description": "The name of the variable that holds the script's return value."
    }
  ]
}
---

# browser.script.evaluate
