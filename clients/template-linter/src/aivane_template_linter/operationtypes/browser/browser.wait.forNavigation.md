---
{
  "schemaVersion": 1,
  "operationType": "browser.wait.forNavigation",
  "executorClass": "aivane.browser.executor.BrowserWaitForNavigationExecutor",
  "displayName": "Waiting for navigation",
  "description": "Wait for page navigation to complete",
  "category": "browser.wait",
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
      "name": "urlPattern",
      "type": "string",
      "description": "The URL matching pattern parameter is reserved and is not used by the current implementation to filter navigation."
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
    },
    {
      "name": "timeout",
      "type": [
        "integer",
        "string"
      ],
      "default": 30000,
      "description": "Timeout for waiting for navigation, in milliseconds."
    }
  ]
}
---

# browser.wait.forNavigation
