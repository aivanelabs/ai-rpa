---
{
  "schemaVersion": 1,
  "operationType": "container",
  "executorClass": "aivane.core.executor.ContainerExecutor",
  "displayName": "container executor",
  "description": "A container that performs multiple operations sequentially",
  "category": "process_control",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "operations",
      "type": "array",
      "required": true,
      "description": "An array of operations to be performed in sequence."
    }
  ],
  "constraints": {
    "nestedOperations": [
      "operations"
    ]
  }
}
---

# container
