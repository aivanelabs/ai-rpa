---
{
  "operationType": "ifelse",
  "displayName": "Conditional branch",
  "category": "FLOW_CONTROL",
  "platforms": ["core"],
  "parameters": [
    {
      "name": "condition",
      "type": "string",
      "required": true,
      "description": "Condition expression"
    },
    {
      "name": "ifBranch",
      "type": ["object", "array"],
      "description": "Single operation or operation array to run when the condition is true"
    },
    {
      "name": "elseBranch",
      "type": ["object", "array"],
      "description": "Single operation or operation array to run when the condition is false"
    }
  ],
  "constraints": {
    "nestedOperations": ["ifBranch", "elseBranch"],
    "requiresLoopContext": false
  }
}
---
