---
{
  "schemaVersion": 1,
  "operationType": "database.execute",
  "executorClass": "aivane.database.executor.DatabaseExecuteExecutor",
  "displayName": "Execute SQL",
  "description": "Execute SQL Server queries or update statements, supporting parameterized queries and result set output.",
  "category": "database",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "sql",
      "type": "string",
      "required": true,
      "description": "The SQL statement to execute."
    },
    {
      "name": "params",
      "type": "object",
      "description": "SQL parameter object; use ${name} form placeholder in SQL."
    },
    {
      "name": "outputVariable",
      "type": "string",
      "description": "Variable name to save query results or update the number of rows."
    },
    {
      "name": "outputKey",
      "type": "string",
      "enumValues": [
        "rows",
        "data",
        "rowCount",
        "firstRow",
        "firstValue"
      ],
      "description": "When setting outputVariable, selects what is written to the variable.",
      "default": "data"
    },
    {
      "name": "connectionName",
      "type": "string",
      "description": "Connection name. If not passed, the default connection will be used."
    }
  ],
  "constraints": {
    "rejectUnknownParams": true
  }
}
---
# database.execute

Execute query or update SQL and optionally write the result into a variable.
