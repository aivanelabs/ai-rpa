---
{
  "schemaVersion": 1,
  "operationType": "http.download",
  "executorClass": "aivane.network.executor.HttpDownloadExecutor",
  "displayName": "HTTP File Download",
  "description": "Download an HTTP response directly to a local file path. On Android 10+, public shared media paths such as /storage/emulated/0/DCIM/... are written through MediaStore when the Android host bridge is registered.",
  "category": "network",
  "platforms": [
    "network"
  ],
  "parameters": [
    {
      "name": "url",
      "type": "string",
      "required": true,
      "description": "Download URL."
    },
    {
      "name": "filePath",
      "type": "string",
      "required": true,
      "description": "Target local file path. Parent directories are created automatically for normal file paths. Android public media paths are created through MediaStore."
    },
    {
      "name": "params",
      "type": "object",
      "description": "Query parameter object."
    },
    {
      "name": "headers",
      "type": "object",
      "description": "Request header object."
    },
    {
      "name": "timeout",
      "type": [
        "integer",
        "string"
      ],
      "default": 30000,
      "description": "Request timeout in milliseconds."
    },
    {
      "name": "sslVerify",
      "type": "boolean",
      "default": true,
      "description": "Whether to verify SSL certificates."
    },
    {
      "name": "overwrite",
      "type": "boolean",
      "default": true,
      "description": "Whether to replace the target file if it already exists."
    },
    {
      "name": "outputVariables",
      "type": "object",
      "description": "Output mapping for multiple download result fields."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "description": "Variable name used for single-field output."
    },
    {
      "name": "outputKey",
      "type": "enum",
      "default": "filePath",
      "enumValues": [
        "statusCode",
        "filePath",
        "bytesWritten",
        "contentType",
        "contentLength",
        "elapsedTime",
        "success",
        "url",
        "headers",
        "full"
      ],
      "description": "Download result field to extract when outputVariable is used."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---
# http.download
