---
{
  "schemaVersion": 1,
  "operationType": "android.device.info",
  "executorClass": "aivane.android.executor.DeviceInfoExecutor",
  "displayName": "Get device information",
  "description": "Get various information about Android devices, including manufacturer, model, system version, API level, device name, ANDROID_ID, etc.",
  "category": "device_info",
  "platforms": [
    "android"
  ],
  "parameters": [
    {
      "name": "manufacturer",
      "type": "string",
      "description": "Save the device manufacturer's variable name."
    },
    {
      "name": "model",
      "type": "string",
      "description": "Variable name that holds the device model."
    },
    {
      "name": "platformVersion",
      "type": "string",
      "description": "The variable name that holds the Android system version number."
    },
    {
      "name": "apiLevel",
      "type": "string",
      "description": "Saves Android API level variable names."
    },
    {
      "name": "deviceName",
      "type": "string",
      "description": "Variable name that holds the device name, read from persist.sys.device_name first and then Settings.Global.DEVICE_NAME when the system property is empty."
    },
    {
      "name": "androidId",
      "type": "string",
      "description": "Variable name holding ANDROID_ID."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "description": "Variable name that holds the complete device information object."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---

# android.device.info
