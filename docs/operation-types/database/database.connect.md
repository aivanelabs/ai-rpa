---
{
  "schemaVersion": 1,
  "operationType": "database.connect",
  "executorClass": "aivane.database.executor.DatabaseConnectExecutor",
  "displayName": "Database connection",
  "description": "Create a SQL Server database connection, supporting connection string or parameter configuration.",
  "category": "database",
  "platforms": [
    "core"
  ],
  "parameters": [
    {
      "name": "connectionString",
      "type": "string",
      "description": "Full database connection string (host/port/databaseName/username/password will be ignored if provided)."
    },
    {
      "name": "host",
      "type": "string",
      "description": "Database host address."
    },
    {
      "name": "port",
      "type": [
        "integer",
        "string"
      ],
      "description": "Database port, default 1433."
    },
    {
      "name": "databaseName",
      "type": "string",
      "description": "Database name."
    },
    {
      "name": "username",
      "type": "string",
      "description": "Database username."
    },
    {
      "name": "password",
      "type": "string",
      "description": "Database password."
    },
    {
      "name": "connectionName",
      "type": "string",
      "description": "Connection name. If not passed, the default connection will be used."
    },
    {
      "name": "maxPoolSize",
      "type": [
        "integer",
        "string"
      ],
      "description": "The maximum number of connections in the connection pool, default 10."
    },
    {
      "name": "minPoolSize",
      "type": [
        "integer",
        "string"
      ],
      "description": "The minimum number of connections in the connection pool, default 2."
    },
    {
      "name": "connectTimeout",
      "type": [
        "integer",
        "string"
      ],
      "description": "Connection timeout (seconds), default 15."
    },
    {
      "name": "connectionLifetime",
      "type": [
        "integer",
        "string"
      ],
      "description": "Maximum connection lifetime (seconds), default 0 (no limit)."
    },
    {
      "name": "encrypt",
      "type": "boolean",
      "description": "Whether to enable encrypted connections, default false."
    },
    {
      "name": "trustServerCertificate",
      "type": "boolean",
      "description": "Whether to trust the server certificate, default true."
    }
  ],
  "constraints": {
    "oneOfRequired": [
      "connectionString",
      "host"
    ],
    "rejectUnknownParams": true
  }
}
---
# database.connect

Establish a database connection and register it in the connection manager for reuse by `database.execute` and related operations.
