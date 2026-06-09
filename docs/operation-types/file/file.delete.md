---
{
  "schemaVersion": 1,
  "operationType": "file.delete",
  "executorClass": "aivane.file.executor.FileDeleteExecutor",
  "displayName": "File Delete",
  "description": "Delete the specified file.",
  "category": "file",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "filePath",
      "type": "string",
      "required": true,
      "description": "The path of the file to be deleted."
    },
    {
      "name": "ignoreIfNotExists",
      "type": "boolean",
      "default": false,
      "description": "Whether to ignore errors when the file does not exist."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---
# file.delete
