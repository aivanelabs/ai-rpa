---
{
  "operationType": "assert.equals",
  "displayName": "Equality assertion",
  "category": "TESTING",
  "platforms": ["core"],
  "parameters": [
    {
      "name": "expected",
      "type": "any",
      "required": true,
      "description": "Expected value"
    },
    {
      "name": "actual",
      "type": "any",
      "required": true,
      "description": "Actual value"
    },
    {
      "name": "message",
      "type": "string",
      "description": "Assertion failure message"
    }
  ],
  "constraints": {
    "requiresLoopContext": false
  }
}
---
