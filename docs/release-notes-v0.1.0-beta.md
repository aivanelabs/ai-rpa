# Release Notes — v0.1.0 Beta

## Download

- APK asset: `aivane.apk`
- Download from the `Assets` section on this GitHub pre-release page.

## Highlights

- Exposed the Python REPL client as the installable `agent-android` CLI that talks to `/execute`, `/health`, `/screenshot`, `/apps`, `/stop`, and `/download`.
- Added launcher-app discovery, tap/input/swipe/back/home/stop operations, and a small smoke flow documentation.
- Published the public permission notes, known limitations, and release checklist for `aivanelabs/ai-rpa`.

## Behavior Notes

- `agent-android --apps` lists all launcher-ready packages returned by `/apps`.
- `--screenshot` uses Android’s MediaProjection flow and succeeds after first-run permission is granted.
- `/stop` is available as a remote stop signal for the current task.

## Next Steps

- Improve public template examples for advanced `/execute` flows.
- Improve screenshot retry experience when permission is denied.
- Keep iterating on the GitHub pre-release notes, install guide, and examples as beta feedback arrives.


