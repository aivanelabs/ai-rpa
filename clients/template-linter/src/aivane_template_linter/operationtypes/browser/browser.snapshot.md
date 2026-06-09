---
{
  "schemaVersion": 1,
  "operationType": "browser.snapshot",
  "executorClass": "aivane.browser.executor.BrowserSnapshotExecutor",
  "displayName": "Browser snapshot",
  "description": "Get the ARIA tree of the current page and generate element reference mapping",
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
      "name": "outputVariable",
      "type": "string",
      "default": "snapshot",
      "description": "The variable name that holds the PageSnapshot object."
    },
    {
      "name": "saveTree",
      "type": [
        "boolean",
        "string"
      ],
      "default": true,
      "description": "Whether to save the enhanced ARIA tree separately."
    },
    {
      "name": "saveRefs",
      "type": [
        "boolean",
        "string"
      ],
      "default": true,
      "description": "Whether to save ref mappings separately."
    },
    {
      "name": "selector",
      "type": "string",
      "description": "Selectors supported by CSS or Playwright."
    },
    {
      "name": "treeVariable",
      "type": "string",
      "default": "ariaTree",
      "description": "Variable name that holds the augmented ARIA tree."
    },
    {
      "name": "refsVariable",
      "type": "string",
      "default": "refs",
      "description": "Save the variable name mapped by ref."
    }
  ]
}
---

# browser.snapshot
