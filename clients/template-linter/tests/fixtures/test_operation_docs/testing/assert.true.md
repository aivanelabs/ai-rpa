---
{
  "operationType": "assert.true",
  "displayName": "True assertion",
  "category": "TESTING",
  "platforms": ["core"],
  "parameters": [
    {
      "name": "condition",
      "type": "string",
      "required": true,
      "description": "Assertion expression; must use ${...} syntax"
    },
    {
      "name": "message",
      "type": "string",
      "description": "Message printed when the assertion fails"
    }
  ],
  "constraints": {
    "requiresLoopContext": false
  }
}
---
