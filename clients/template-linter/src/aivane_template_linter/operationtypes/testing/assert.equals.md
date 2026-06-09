---
{
  "schemaVersion": 1,
  "operationType": "assert.equals",
  "executorClass": "aivane.testing.executor.AssertEqualsExecutor",
  "displayName": "equality assertion",
  "description": "Asserts that two values ​​are equal and fails if they are not equal.",
  "category": "testing_assertion",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "actual",
      "type": "any",
      "required": true,
      "description": "actual value."
    },
    {
      "name": "expected",
      "type": "any",
      "required": true,
      "description": "Expected value."
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
# assert.equals
