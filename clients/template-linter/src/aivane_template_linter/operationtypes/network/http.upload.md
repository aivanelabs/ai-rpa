---
{
  "schemaVersion": 1,
  "operationType": "http.upload",
  "executorClass": "aivane.network.executor.HttpUploadExecutor",
  "displayName": "File upload",
  "description": "Upload files to the server, supporting local files, Base64 data and URL query parameters.",
  "category": "network",
  "platforms": [
    "network"
  ],
  "parameters": [
    {
      "name": "url",
      "type": "string",
      "required": true,
      "description": "Upload interface URL."
    },
    {
      "name": "filePath",
      "type": "string",
      "description": "Local file path."
    },
    {
      "name": "base64",
      "type": "string",
      "description": "Base64 encoded file content."
    },
    {
      "name": "fileName",
      "type": "string",
      "description": "Upload file name."
    },
    {
      "name": "mimeType",
      "type": "string",
      "description": "MIME type."
    },
    {
      "name": "fieldName",
      "type": "string",
      "default": "file",
      "description": "multipart form field name."
    },
    {
      "name": "formData",
      "type": "object",
      "description": "Additional form fields."
    },
    {
      "name": "headers",
      "type": "object",
      "description": "Request header object."
    },
    {
      "name": "auth",
      "type": "object",
      "description": "Authentication configuration object."
    },
    {
      "name": "queryParams",
      "type": "object",
      "description": "Query parameter object."
    },
    {
      "name": "timeout",
      "type": [
        "integer",
        "string"
      ],
      "default": 30000,
      "description": "Request timeout, in milliseconds."
    },
    {
      "name": "sslVerify",
      "type": "boolean",
      "default": true,
      "description": "Whether to verify the certificate."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "description": "Output variable names."
    },
    {
      "name": "outputKey",
      "type": "enum",
      "default": "body",
      "enumValues": [
        "statusCode",
        "body",
        "headers",
        "contentType",
        "success",
        "full"
      ],
      "description": "Response fields to extract."
    }
  ],
  "constraints": {
    "oneOfRequired": [
      "filePath",
      "base64"
    ]
  }
}
---
# http.upload
