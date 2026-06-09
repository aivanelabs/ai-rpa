---
{
  "schemaVersion": 1,
  "operationType": "android.app.launch",
  "executorClass": "aivane.android.executor.AppLaunchExecutor",
  "displayName": "Launch Android App",
  "description": "Launch a specified Android app by package name.",
  "category": "app_operations",
  "platforms": ["android"],
  "parameters": [
    {
      "name": "packageName",
      "type": "string",
      "required": true,
      "description": "Package name of the Android app to launch."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "description": "Variable name used to store the launch result object or field."
    },
    {
      "name": "outputKey",
      "type": "string",
      "description": "When outputVariable is set, store only this field from the result object."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---

# android.app.launch
