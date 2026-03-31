# Release Notes — v0.1.0 Beta

## Highlights

- Exposed the Python REPL client (`clients/python/agent-android.py`) that talks to `/api/execute`, `/health`, `/screenshot`, `/api/apps`, and `/api/stop`.
- Added launcher-app discovery, tap/input/swipe/back/home/stop operations, and a small smoke flow documentation.
- Published the public permission notes, known limitations, and release checklist for `aivanelabs/ai-rpa`.

## Behavior Notes

- `agent-android.py --apps` lists all launcher-ready packages returned by `/api/apps`.
- `--screenshot` uses Android’s MediaProjection flow and succeeds after first-run permission is granted.
- `/api/stop` is available as a remote stop signal for the current task.

## Next Steps

- Improve public template examples for advanced `/api/execute` flows.
- Improve screenshot retry experience when permission is denied.
- Publish beta APK builds through GitHub pre-releases and iterate on the release notes as testing continues.


