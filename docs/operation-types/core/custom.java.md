---
{
  "schemaVersion": 1,
  "operationType": "custom.java",
  "executorClass": "aivane.core.executor.CustomJavaExecutor",
  "displayName": "Custom Java code",
  "description": "Execute user-defined Java static methods. Supports parameter passing and return values. Users can create Java files in the application's custom directory and write static methods containing Map<String, Object> parameters.",
  "category": "customize",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "className",
      "type": "string",
      "required": true,
      "description": "The name of the Java class to load."
    },
    {
      "name": "methodName",
      "type": "string",
      "required": true,
      "description": "The name of the static method to be called."
    },
    {
      "name": "sourceFile",
      "type": "string",
      "required": true,
      "description": "Java source file path."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "required": false,
      "description": "The variable name to save the execution results."
    },
    {
      "name": "outputKey",
      "type": "string",
      "required": false,
      "description": "Extract only returns the value of the specified key in the Map."
    }
  ],
  "constraints": {
    "rejectUnknownParams": false
  }
}
---

# custom.java
