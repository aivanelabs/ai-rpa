---
{
  "schemaVersion": 1,
  "operationType": "browser.ref.resolve",
  "executorClass": "aivane.browser.executor.BrowserRefResolveExecutor",
  "displayName": "Parse Ref",
  "description": "Convert ref references to precise CSS selectors for obtaining specific positioning information of elements",
  "category": "browser.analysis",
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
      "name": "ref",
      "type": "string",
      "required": true,
      "description": "The element ref to parse."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "default": "selector",
      "description": "Save the variable name of the parsed exact selector."
    }
  ]
}
---

# browser.ref.resolve
