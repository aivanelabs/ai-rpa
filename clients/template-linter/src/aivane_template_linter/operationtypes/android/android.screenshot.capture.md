---
{
  "schemaVersion": 1,
  "operationType": "android.screenshot.capture",
  "executorClass": "aivane.android.executor.ScreenshotCaptureExecutor",
  "displayName": "screenshot",
  "description": "Capture screenshot and save to file.",
  "category": "android_automation",
  "platforms": [
    "android"
  ],
  "parameters": [
    {
      "name": "savePath",
      "type": "string",
      "required": true,
      "description": "Screenshot output file path."
    },
    {
      "name": "format",
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
      "name": "quality",
      "type": [
        "integer",
        "string"
      ],
      "default": 90,
      "description": "JPEG screenshot quality, range 1-100."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "description": "The variable name to save the screenshot result object."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---

# android.screenshot.capture
