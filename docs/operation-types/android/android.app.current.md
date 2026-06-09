---
{
  "schemaVersion": 1,
  "operationType": "android.app.current",
  "executorClass": "aivane.android.executor.AppCurrentExecutor",
  "displayName": "Get Current Android App",
  "description": "Get the package name of the current foreground Android app.",
  "category": "android_automation",
  "platforms": ["android"],
  "parameters": [
    {
      "name": "packageName",
      "type": "string",
      "default": "currentPackage",
      "description": "Variable name used to store the current foreground app package name."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---

# android.app.current
