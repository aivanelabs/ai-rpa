---
{
  "schemaVersion": 1,
  "operationType": "file.read",
  "executorClass": "aivane.file.executor.FileReadExecutor",
  "displayName": "File Read",
  "description": "Read file content and store it in a variable.",
  "category": "file",
  "platforms": ["core"],
  "parameters": [
    {
      "name": "filePath",
      "type": "string",
      "required": true,
      "description": "File path to read."
    },
    {
      "name": "variableName",
      "type": "string",
      "default": "__file_content__",
      "description": "Variable name used to store file content."
    },
    {
      "name": "encoding",
      "type": "string",
      "default": "UTF-8",
      "description": "File encoding."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---

# file.read
