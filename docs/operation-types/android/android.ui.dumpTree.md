---
{
  "schemaVersion": 1,
  "operationType": "android.ui.dumpTree",
  "executorClass": "aivane.android.executor.AndroidUiDumpTreeExecutor",
  "displayName": "Export UI tree",
  "description": "Export the UI tree obtained by the accessibility service to an XML/JSON file.",
  "category": "android_automation",
  "platforms": [
    "android"
  ],
  "parameters": [
    {
      "name": "filePath",
      "type": "string",
      "required": true,
      "description": "UI tree output file path."
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
      "description": "When true, only keep nodes that are visible on the current screen. Ancestor nodes are preserved when needed to keep the hierarchy connected. Set it to false to include off-screen nodes."
    },
    {
      "name": "variableName",
      "type": "string",
      "default": "uiTree",
      "description": "The name of the variable that holds the text content of the UI tree."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---

# android.ui.dumpTree
