---
{
  "schemaVersion": 1,
  "operationType": "file.exists",
  "executorClass": "aivane.file.executor.FileExistsExecutor",
  "displayName": "File Exists",
  "description": "Checks if the file exists and writes the result to a variable. On Android 10+, public shared media paths are checked through MediaStore when the Android host bridge is registered.",
  "category": "file",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "filePath",
      "type": "string",
      "required": true,
      "description": "The file path to check. Android public media paths can be resolved through the host MediaStore bridge."
    },
    {
      "name": "variableName",
      "type": "string",
      "default": "__file_exists__",
      "description": "The variable name to save the inspection results."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---
# file.exists
