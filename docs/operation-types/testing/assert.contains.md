---
{
  "schemaVersion": 1,
  "operationType": "assert.contains",
  "executorClass": "aivane.testing.executor.AssertContainsExecutor",
  "displayName": "Contains assertions",
  "description": "Asserts that the string contains the specified substring, otherwise execution fails.",
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
      "description": "The substring or value to include."
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
# assert.contains
