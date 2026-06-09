---
{
  "schemaVersion": 1,
  "operationType": "browser.navigate.to",
  "executorClass": "aivane.browser.executor.BrowserNavigateExecutor",
  "displayName": "Navigate to URL",
  "description": "Navigate to the specified URL",
  "category": "browser",
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
      "required": true,
      "description": "The target URL to navigate to."
    },
    {
      "name": "waitUntil",
      "type": "string",
      "default": "load",
      "enumValues": [
        "load",
        "domcontentloaded",
        "networkidle",
        "commit"
      ],
      "description": "Navigation completion judgment conditions."
    }
  ]
}
---

# browser.navigate.to
