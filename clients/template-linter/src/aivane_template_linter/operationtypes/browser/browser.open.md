---
{
  "schemaVersion": 1,
  "operationType": "browser.open",
  "executorClass": "aivane.browser.executor.BrowserOpenExecutor",
  "displayName": "Open browser",
  "description": "Launch a Playwright browser instance, supporting headless mode and custom viewports",
  "category": "browser",
  "platforms": [
    "browser"
  ],
  "parameters": [
    {
      "name": "url",
      "type": "string",
      "default": "about:blank",
      "description": "The URL to navigate to immediately after opening."
    },
    {
      "name": "headless",
      "type": [
        "boolean",
        "string"
      ],
      "default": true,
      "description": "Whether to launch the browser in headless mode."
    },
    {
      "name": "timeout",
      "type": [
        "integer",
        "string"
      ],
      "default": 30000,
      "description": "Browser default timeout, in milliseconds."
    },
    {
      "name": "contextVariable",
      "type": "string",
      "default": "browser",
      "description": "Variable name that saves or reads the browser context."
    },
    {
      "name": "sessionId",
      "type": "string",
      "default": "default",
      "description": "Browser session ID; when empty, the current context session is used."
    },
    {
      "name": "keepAlive",
      "type": [
        "boolean",
        "string"
      ],
      "default": true,
      "description": "Whether to keep the browser session alive after closing the template."
    },
    {
      "name": "viewportWidth",
      "type": [
        "integer",
        "string"
      ],
      "default": 1280,
      "description": "Browser viewport width."
    },
    {
      "name": "viewportHeight",
      "type": [
        "integer",
        "string"
      ],
      "default": 720,
      "description": "Browser viewport height."
    }
  ]
}
---

# browser.open
