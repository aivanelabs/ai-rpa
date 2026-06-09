---
{
  "schemaVersion": 1,
  "operationType": "file.write",
  "executorClass": "aivane.file.executor.FileWriteExecutor",
  "displayName": "File Write",
  "description": "Write contents to file (overwrite mode).",
  "category": "file",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "filePath",
      "type": "string",
      "required": true,
      "description": "Target file path."
    },
    {
      "name": "content",
      "type": "string",
      "required": true,
      "description": "The text content to be written."
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
# file.write
