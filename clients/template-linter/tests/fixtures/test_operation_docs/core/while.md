---
{
  "operationType": "while",
  "displayName": "While loop",
  "category": "FLOW_CONTROL",
  "platforms": ["core"],
  "parameters": [
    {
      "name": "condition",
      "type": "string",
      "required": true,
      "description": "Loop condition"
    },
    {
      "name": "operations",
      "type": "array",
      "required": true,
      "description": "Loop body"
    }
  ],
  "constraints": {
    "nestedOperations": ["operations"],
    "requiresLoopContext": false
  }
}
---
