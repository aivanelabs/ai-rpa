---
{
  "schemaVersion": 1,
  "operationType": "win.device.info",
  "executorClass": "aivane.windows.executor.DeviceInfoExecutor",
  "displayName": "Get Windows device information",
  "description": "Get various information about your Windows computer, including manufacturer, computer name, username, operating system version, architecture, and more.",
  "category": "device_info",
  "platforms": [
    "windows"
  ],
  "parameters": [
    {
      "name": "manufacturer",
      "type": "string",
      "description": "Variable name to hold manufacturer information."
    },
    {
      "name": "model",
      "type": "string",
      "description": "Variable name that holds device model information."
    },
    {
      "name": "platformVersion",
      "type": "string",
      "description": "Variable name that holds platform version information."
    },
    {
      "name": "computerName",
      "type": "string",
      "description": "Variable name to hold the computer name."
    },
    {
      "name": "userName",
      "type": "string",
      "description": "The variable name that holds the current username."
    },
    {
      "name": "osName",
      "type": "string",
      "description": "Variable name holding the name of the operating system."
    },
    {
      "name": "osArch",
      "type": "string",
      "description": "Variable name that holds the operating system architecture."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "description": "The variable name that holds the complete device information object (Map)."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---
# win.device.info

Get Windows device information and write the result into specified variables.
