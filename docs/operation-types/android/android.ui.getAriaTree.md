---
{
  "operationType": "android.ui.getAriaTree",
  "executorClass": "aivane.android.executor.AndroidUiGetAriaTreeExecutor",
  "displayName": "Get ARIA tree",
  "description": "Generate a simplified version of the UI tree, containing only actionable elements (clickable/focusable/editable), each with a refId and XPath.",
  "category": "android_automation",
  "platforms": [
    "android"
  ],
  "parameters": [
    {
      "name": "visibleOnly",
      "type": "boolean",
      "default": true,
      "description": "When true, only include elements that are visible on the current screen. Set it to false to include off-screen elements as well."
    },
    {
      "name": "variableName",
      "type": "string",
      "default": "ariaTree",
      "description": "Variable name to hold ARIA tree results."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---

# android.ui.getAriaTree

Generate a simplified ARIA tree that contains actionable elements and their XPath locators.

## Return Format

```json
{
  "elements": [
    {
      "refId": 1,
      "className": "android.widget.TextView",
      "simpleClassName": "TextView",
      "text": "Home",
      "resourceId": "com.xingin.xhs:id/tab_title",
      "bounds": "[0,2080][216,2204]",
      "x": 108,
      "y": 2142,
      "clickable": true,
      "enabled": true,
      "visible": true,
      "xpath": "/WindowRoot/.../TextView[1][@refId=1]",
      "selector": "id=com.xingin.xhs:id/tab_title"
    }
  ]
}
```

## How To Use refId

When executing templates via HTTP API, you can use refId to locate elements quickly:

```json
{
  "operationType": "android.element.get",
  "parameters": {
    "id": "com.xingin.xhs:id/tab_title"
  }
}
```
