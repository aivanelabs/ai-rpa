---
{
  "schemaVersion": 1,
  "operationType": "http.post",
  "executorClass": "aivane.network.executor.HttpPostExecutor",
  "displayName": "POST request",
  "description": "Send HTTP POST request to submit data, supporting multiple content types such as JSON and forms.",
  "category": "network",
  "platforms": [
    "network"
  ],
  "parameters": [
    {
      "name": "url",
      "type": "string",
      "required": true,
      "description": "Request URL."
    },
    {
      "name": "body",
      "type": "any",
      "required": true,
      "description": "Request body."
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
      "description": "Request timeout, in milliseconds."
    },
    {
      "name": "followRedirects",
      "type": "boolean",
      "default": true,
      "description": "Whether to follow redirects."
    },
    {
      "name": "sslVerify",
      "type": "boolean",
      "default": true,
      "description": "Whether to verify the certificate."
    },
    {
      "name": "auth",
      "type": "object",
      "description": "Authentication configuration object."
    },
    {
      "name": "outputVariables",
      "type": "object",
      "description": "Multifield output mapping."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "description": "Single field output variable name."
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
      "description": "The response fields to extract when outputting a single field."
    }
  ]
}
---
# http.post
