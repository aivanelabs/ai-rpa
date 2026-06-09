---
{
  "schemaVersion": 1,
  "operationType": "http.get",
  "executorClass": "aivane.network.executor.HttpGetExecutor",
  "displayName": "HTTP GET Request",
  "description": "Send an HTTP GET request and optionally include query parameters.",
  "category": "network",
  "platforms": ["network"],
  "parameters": [
    {
      "name": "url",
      "type": "string",
      "required": true,
      "description": "Request URL."
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
      "type": ["integer", "string"],
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
      "name": "outputVariables",
      "type": "object",
      "description": "Output mapping for multiple response fields."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "description": "Variable name used for single-field output."
    },
    {
      "name": "outputKey",
      "type": "enum",
      "default": "body",
      "enumValues": ["statusCode", "body", "headers", "contentType", "contentLength", "elapsedTime", "success", "full"],
      "description": "Response field to extract when outputVariable is used."
    }
  ]
}
---

# http.get
