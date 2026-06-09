---
{
  "schemaVersion": 1,
  "operationType": "browser.screenshot.element",
  "executorClass": "aivane.browser.executor.BrowserScreenshotElementExecutor",
  "displayName": "Element screenshot",
  "description": "Take a screenshot of the specified element",
  "category": "browser.screenshot",
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
      "name": "selector",
      "type": "string",
      "required": true,
      "description": "Selectors supported by CSS or Playwright."
    },
    {
      "name": "path",
      "type": "string",
      "description": "Element screenshot output file path; will not be saved when empty."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "description": "Variable name to save screenshot Base64 string."
    }
  ]
}
---

# browser.screenshot.element
