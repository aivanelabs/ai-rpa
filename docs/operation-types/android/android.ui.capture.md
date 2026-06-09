---
{
  "schemaVersion": 1,
  "operationType": "android.ui.capture",
  "executorClass": "aivane.android.executor.AndroidUiCaptureExecutor",
  "displayName": "Capture UI state",
  "description": "Capture the UI tree and screenshot simultaneously to ensure an exact match.",
  "category": "android_automation",
  "platforms": [
    "android"
  ],
  "parameters": [
    {
      "name": "uiTreePath",
      "type": "string",
      "required": true,
      "description": "UI tree output file path when synchronously capturing."
    },
    {
      "name": "screenshotPath",
      "type": "string",
      "required": true,
      "description": "Screenshot output file path during synchronous capture."
    },
    {
      "name": "format",
      "type": "enum",
      "default": "xml",
      "description": "UI tree output format.",
      "enumValues": [
        "xml",
        "json"
      ]
    },
    {
      "name": "visibleOnly",
      "type": "boolean",
      "default": true,
      "description": "When true, only keep nodes that are visible on the current screen. Set it to false to include off-screen nodes."
    },
    {
      "name": "variableName",
      "type": "string",
      "default": "capture",
      "description": "The variable name that holds the capture result object."
    },
    {
      "name": "screenshotFormat",
      "type": "enum",
      "default": "png",
      "description": "Screenshot output format.",
      "enumValues": [
        "png",
        "jpeg",
        "jpg"
      ]
    },
    {
      "name": "screenshotQuality",
      "type": [
        "integer",
        "string"
      ],
      "default": 90,
      "description": "JPEG screenshot quality, range 1-100."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---

# android.ui.capture
