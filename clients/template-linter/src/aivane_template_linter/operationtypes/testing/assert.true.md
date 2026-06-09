---
{
  "schemaVersion": 1,
  "operationType": "assert.true",
  "executorClass": "aivane.testing.executor.AssertTrueExecutor",
  "displayName": "Assertion that the condition is true",
  "description": "Assert conditional expressions to be true, supporting complex logical expressions and variable substitution.",
  "category": "testing_assertion",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "condition",
      "type": "string",
      "required": true,
      "description": "An assertion expression of the form ${...} must be used."
    },
    {
      "name": "message",
      "type": "string",
      "description": "The message returned when an assertion fails."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---
# assert.true
