---
{
  "schemaVersion": 1,
  "operationType": "win.element.click",
  "executorClass": "aivane.windows.executor.WinElementClickExecutor",
  "displayName": "Windows element click",
  "description": "Click on a Windows UI element (via XPath or elements.json).",
  "category": "windows_automation",
  "platforms": [
    "windows"
  ],
  "parameters": [
    {
      "name": "xpath",
      "type": "string",
      "description": "Direct XPath for clicks."
    },
    {
      "name": "elementName",
      "type": "string",
      "description": "The element name defined in elements.json."
    },
    {
      "name": "waitFor",
      "type": [
        "integer",
        "string"
      ],
      "default": 0,
      "description": "Number of milliseconds to wait before clicking."
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
# win.element.click

Locate and click Windows UI elements by XPath or by element name defined in elements.json.
