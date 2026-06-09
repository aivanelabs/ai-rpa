---
{
  "schemaVersion": 1,
  "operationType": "browser.screenshot.capture",
  "executorClass": "aivane.browser.executor.BrowserScreenshotCaptureExecutor",
  "displayName": "Page screenshot",
  "description": "Take a screenshot of the current page",
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
      "name": "path",
      "type": "string",
      "description": "Screenshot output file path; if empty, it will not be saved to disk."
    },
    {
      "name": "fullPage",
      "type": [
        "boolean",
        "string"
      ],
      "default": false,
      "description": "Whether to capture the entire page instead of the current viewport."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "description": "Variable name to save screenshot Base64 string."
    }
  ]
}
---

# browser.screenshot.capture
