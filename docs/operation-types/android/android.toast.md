---
{
  "schemaVersion": 1,
  "operationType": "android.toast",
  "executorClass": "aivane.android.executor.ToastExecutor",
  "displayName": "Android Toast",
  "description": "Display Android Toast prompt message.",
  "category": "android_automation",
  "platforms": [
    "android"
  ],
  "parameters": [
    {
      "name": "text",
      "type": "string",
      "required": true,
      "description": "The toast text to display."
    },
    {
      "name": "duration",
      "type": "enum",
      "default": "long",
      "description": "Toast display duration.",
      "enumValues": [
        "short",
        "long"
      ]
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---

# android.toast
