See the Chinese overview at [README_CN.md](README_CN.md).

# AIVane AI RPA

This repository is the public-facing launch repo for `aivanelabs/ai-rpa` on GitHub.

The first public surface is **AIVane Android REPL Beta**: a lightweight Python CLI, public docs, examples, and sample skills that let AI agents inspect Android UI state and control a phone step by step over LAN.

## Why The Phone Is The Web Server

- In this beta, the phone runs the lightweight HTTP service locally and the desktop connects straight to `http://<device-ip>:8080`.
- All operations stay local: UI inspection, taps, text input, and screenshots are executed without uploading user data.
- You can complete the first smoke flow without any cloud dependency, which keeps early evaluation simple on a trusted LAN.
- This local-first design also explains the current LAN-only limitation. An optional server-side or relay path is being considered for a later step so control is not limited to the local network, while the direct local path remains available.

## Current Status

- The repo structure and public CLI are ready for evaluation.
- GitHub is the only official entry point for the beta.
- APK builds are distributed through [GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases).

## Get the Beta

- [Download APK (v0.1.0-beta.1)](https://github.com/aivanelabs/ai-rpa/releases/download/v0.1.0-beta.1/aivane.apk)
- [View all releases](https://github.com/aivanelabs/ai-rpa/releases)

## Who This Is For

- AI agent users working with Codex, Claude Code, OpenClaw, or similar tools
- Automation users who want stepwise Android control: inspect, tap, input, swipe, back, home, screenshot
- Early evaluators who are comfortable running a Python CLI and testing on a trusted LAN

## What Is Open In This Repo

- `clients/python/agent-android.py`
- Public protocol and user-facing docs
- Smoke examples and launch helpers
- Sample agent skills under `skills/`

## Security Note

- Use the beta only on a trusted LAN.
- Do not expose the device port to the public internet.
- The public beta path does not require a cloud relay; device traffic stays between the controller and the phone.
- Accessibility and screenshot capabilities require explicit user approval on the phone.

## Quick Start

1. Install the AIVane Android REPL beta APK on your phone.
2. Enable the required on-device permissions:
   - turn on the AIVane accessibility service
   - accept the screenshot permission prompt the first time you use `screenshot`
3. Make sure the phone and computer are on the same Wi-Fi network.
4. Confirm the phone-side service is reachable:
   - find the phone's local IP address on the same Wi-Fi network
   - run `curl http://<device-ip>:8080/health`
   - expect a JSON response instead of a connection error
   - some builds return only basic service status here, while others also include a `permissions` object
   - if your `/health` response includes `permissions.accessibilityEnabled` and it is `false`, open Android Settings and enable the AIVane accessibility service manually before expecting `launch`, `list`, `tap`, or `input` to work
5. Run the CLI:
   ```bash
   python clients/python/agent-android.py --repl --url http://<device-ip>:8080
   ```
6. Inside the REPL, save the URL (`set url http://<device-ip>:8080`) and run the first smoke path:
   - `health`
   - `apps`
   - `la <package>`
   - `list`
   - `tap <refId>`
   - `input <refId> "hello"`
   - `back`
   - `press home`
   - `screenshot`

If you want an ADB-assisted setup path, see [docs/install-agent-android.md](docs/install-agent-android.md). That guide includes both shell and Windows PowerShell examples.

## You Are Ready If

Your first-run setup is in good shape if you can do all of the following:

1. `curl http://<device-ip>:8080/health` returns JSON instead of a connection error
2. `python clients/python/agent-android.py --repl --url http://<device-ip>:8080` opens the REPL banner
3. `apps` lists launcher apps, or you can launch a known package directly if your build does not expose `/apps`
4. `la <package>` opens a target app
5. `list` shows the current UI tree
6. one inspect -> act -> inspect loop works, such as `list` -> `tap` -> `list`

## Skills

This beta is currently CLI-first.

- The `skills/` directory contains public reference prompts and workflow guidance.
- There is not yet a one-click public installer for Codex, Claude Code, or OpenClaw skills in this repo.
- If you use an agent platform with local skill files, copy the relevant text from `skills/agent-android/SKILL.md` into your own skill or prompt setup.
- If you only want to verify the product quickly, start with the Python CLI first and add a skill wrapper later.

Minimal Codex starter:

```text
Use the AIVane Android public client at `clients/python/agent-android.py`.
Verify `--health` first.
Then follow inspect -> act -> inspect:
- `--apps` if the package is unknown
- `--launch <package>`
- `--list`
- one action such as `--tap`, `--input`, `--swipe`, `--back`, or `--screenshot`
- `--list` again

Do not assume refIds remain stable after navigation.
```

## First Task Example: Xiaohongshu Search

Once `/health` works, a typical Xiaohongshu exploration loop looks like this:

1. `apps`
2. `la com.xingin.xhs`
3. `list`
4. `find Search`
5. `tap <refId>` for the search field or search entry point
6. `input <refId> "<keyword>"`
7. `list`
8. `swipe up` to inspect more results if needed

Notes:

- If `apps` returns `404 Not Found` on your build, skip it and launch `com.xingin.xhs` directly.
- `refId` values change across devices and screens, so re-run `list` after each action.
- If a tap or input fails after navigation, run `snapshot` or `list` again before retrying.
- For more detail, see [docs/agent-examples.md](docs/agent-examples.md).

## Public Assets

- `clients/python/agent-android.py`: public-facing REPL entrypoint for Android device control.
- `docs/`: quickstart, protocol, permissions, known limitations, feedback, release notes, and repo scope.
- `examples/`: smoke flows and minimal usage examples.
- `skills/agent-android/`: sample skill definition with prompts and agent metadata.
- [GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases): the only official place to download beta APK builds.

## Installation & Launch

- `docs/install-agent-android.md`: how to install the APK, confirm LAN connectivity, and run the first smoke.
- `examples/start-app-repl.sh`: a public-friendly starter script to connect to a device, optionally install the APK, and launch the Android REPL service.

## Additional Resources

- `docs/agent-examples.md`: starter prompts and usage snippets for Codex / Claude Code / OpenClaw.
- `.github/ISSUE_TEMPLATE/`: bug and feature report templates to capture actionable information from early users.

## Known Limitations

See `docs/known-limitations.md` for the current Beta boundaries (permission prompts, LAN-only use, and other beta limits). These limitations reflect the state of the remote Android runtime and the permissions it can request today.

## Contact

For questions and light coordination, please email `aivanelabs@gmail.com`.


