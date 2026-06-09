---
{
  "schemaVersion": 1,
  "operationType": "file.append",
  "executorClass": "aivane.file.executor.FileAppendExecutor",
  "displayName": "File Append",
  "description": "Append content to the end of the file.",
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
      "description": "The text content to be appended."
    },
    {
      "name": "encoding",
      "type": "string",
      "default": "UTF-8",
      "description": "File encoding."
    },
    {
      "name": "newLine",
      "type": "boolean",
      "default": true,
      "description": "Whether to wrap lines after appending content."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---
# file.append
