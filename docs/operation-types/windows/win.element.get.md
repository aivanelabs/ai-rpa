---
{
  "schemaVersion": 1,
  "operationType": "win.element.get",
  "executorClass": "aivane.windows.executor.WinElementGetExecutor",
  "displayName": "Get Windows elements",
  "description": "Find Windows UI elements based on elements.json or XPath and save them as variables.",
  "category": "windows_automation",
  "platforms": [
    "windows"
  ],
  "parameters": [
    {
      "name": "xpath",
      "type": "string",
      "description": "XPath used directly to find elements."
    },
    {
      "name": "elementName",
      "type": "string",
      "description": "The element name defined in elements.json."
    },
    {
      "name": "variableName",
      "type": "string",
      "description": "Variable name that holds the found element; default fallback to elementName or element."
    },
    {
      "name": "applicationDir",
      "type": "string",
      "description": "The application directory where elements.json is located."
    }
  ],
  "constraints": {
    "oneOfRequired": [
      "xpath",
      "elementName"
    ],
    "rejectUnknownParams": true
  }
}
---
# win.element.get

Find Windows UI elements by XPath or by element name from elements.json, and save the element object into a variable.
