---
{
  "schemaVersion": 1,
  "operationType": "mail.smtp",
  "executorClass": "aivane.network.executor.MailSmtpExecutor",
  "displayName": "SMTP email sending",
  "description": "Send emails via SMTP protocol, supporting SSL/TLS encryption and attachment functions.",
  "category": "network",
  "platforms": [
    "network"
  ],
  "parameters": [
    {
      "name": "smtpHost",
      "type": "string",
      "required": true,
      "description": "SMTP server address."
    },
    {
      "name": "smtpPort",
      "type": [
        "integer",
        "string"
      ],
      "default": 25,
      "description": "SMTP port."
    },
    {
      "name": "username",
      "type": "string",
      "required": true,
      "description": "SMTP username."
    },
    {
      "name": "password",
      "type": "string",
      "required": true,
      "description": "SMTP password."
    },
    {
      "name": "from",
      "type": "string",
      "required": true,
      "description": "Sender address."
    },
    {
      "name": "to",
      "type": "string",
      "required": true,
      "description": "List of recipient addresses."
    },
    {
      "name": "subject",
      "type": "string",
      "required": true,
      "description": "Email subject."
    },
    {
      "name": "content",
      "type": "string",
      "required": true,
      "description": "The body of the email."
    },
    {
      "name": "contentType",
      "type": "string",
      "default": "text/plain",
      "description": "Body content type."
    },
    {
      "name": "charset",
      "type": "string",
      "default": "UTF-8",
      "description": "Text character set."
    },
    {
      "name": "cc",
      "type": "string",
      "description": "CC address list."
    },
    {
      "name": "bcc",
      "type": "string",
      "description": "Bcc address list."
    },
    {
      "name": "useSsl",
      "type": "boolean",
      "default": false,
      "description": "Whether to enable SSL."
    },
    {
      "name": "useTls",
      "type": "boolean",
      "default": false,
      "description": "Whether to enable STARTTLS."
    },
    {
      "name": "timeout",
      "type": [
        "integer",
        "string"
      ],
      "default": 30000,
      "description": "Timeout time in milliseconds."
    },
    {
      "name": "attachments",
      "type": "array",
      "description": "Array of attachment paths."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "description": "The variable name that holds the sent result."
    }
  ]
}
---
# mail.smtp
