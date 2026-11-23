---
{
  "schemaVersion": 1,
  "operationType": "android.press.enter",
  "executorClass": "aivane.android.executor.AndroidPressEnterExecutor",
  "displayName": "Press Enter",
  "description": "Presses the keyboard's action key (Enter, Search, Send or Go) on the focused input field. Unlike the back, home and recents keys it acts on the focused field, so tap or fill the field first. Requires Android 11 (API 30) or later.",
  "category": "android_automation",
  "platforms": [
    "android"
  ],
  "parameters": [],
  "constraints": {
    "rejectUnknownParams": true
  },
  "display": {
    "summary": {
      "template": "Press Enter on the focused Android input",
      "tokens": {}
    }
  }
}
---

# android.press.enter

Runtime schema source of truth for the Android IME action key.
