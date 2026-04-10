# Quickstart — agent-android

This quickstart introduces the public GitHub beta for AIVane (AI Mobile Automation) under `aivanelabs/ai-rpa`.

## What You Need

- An Android device with the AIVane REPL beta APK installed
- A desktop or laptop on the same LAN
- Python 3.9+
- `curl` or a browser to test `http://<device-ip>:8080/health`

## Why The Phone Hosts The Service

- The beta starts a lightweight HTTP service on the phone itself.
- The desktop talks directly to `http://<device-ip>:8080`, so the full smoke flow runs locally.
- UI reads, taps, inputs, and screenshots are not uploaded to a cloud service as part of this public path.
- The tradeoff is that the first public build is LAN-only. A later optional server-side or relay path is under consideration for scenarios that need control beyond the local network.

## First Run

Before you open the desktop CLI, make sure the phone is actually ready:

1. Open the AIVane app on the phone.
2. Enable the AIVane accessibility service if Android prompts for it.
3. Keep the phone and desktop on the same Wi-Fi network.
4. Find the phone's local IP address on that Wi-Fi network.
5. Check `http://<device-ip>:8080/health`.

If `/health` works but shows `"accessibilityEnabled": false`, stop there and enable the AIVane accessibility service manually in Android Settings before trying `launch`, `list`, `tap`, or `input`.

If `/health` does not respond yet, go to [install-agent-android.md](install-agent-android.md) for the ADB-assisted startup path and troubleshooting steps.

## First 10 Minutes

Use these checkpoints to avoid guessing:

1. `python -m pip install aivane-agent-android`
   Install the CLI with the command that matches your platform:
   - Windows: `py -m pip install --user aivane-agent-android`
   - Linux / macOS: `python3 -m pip install --user aivane-agent-android`
   If Linux / macOS reports `No module named pip`, install `pip` for Python 3 first.
   If the command is not found afterwards:
   - Windows: run `py -m site --user-base` and check the `Scripts` subdirectory
   - Linux / macOS: run `python3 -m site --user-base` and check the user scripts directory, often `~/.local/bin`
2. `curl http://<device-ip>:8080/health`
   Success should be JSON, not a timeout or connection-refused error. The payload should include basic service status and a `permissions` object.
3. `agent-android --health --url http://<device-ip>:8080`
   Success should print formatted JSON from the same `/health` endpoint.
4. `agent-android --repl --url http://<device-ip>:8080`
   Success should open the interactive REPL and print a banner like:

```text
agent-android REPL v5.4  -  Android UI Automation REPL
Server: http://<device-ip>:8080
Type 'h' for help, 'q' to quit.
```

5. Inside the REPL, run `health`, then `apps`.
   If `health` fails here, do not keep guessing at UI commands. Fix connectivity first.

Run the CLI with an explicit URL:

```bash
agent-android --repl --url http://<device-ip>:8080
```

Inside the REPL, save the URL for later:

```text
set url http://<device-ip>:8080
```

## Minimal Smoke Flow

1. Check health:

```bash
curl http://<device-ip>:8080/health
```

2. List launchable apps:

```bash
agent-android --apps --url http://<device-ip>:8080
```

3. Launch an app:

```bash
agent-android --launch <package> --url http://<device-ip>:8080
```

4. Inspect the current screen:

```bash
agent-android --list --url http://<device-ip>:8080
```

5. Interact:

```bash
agent-android --tap <refId> --url http://<device-ip>:8080
agent-android --input <refId> "hello" --url http://<device-ip>:8080
agent-android --back --url http://<device-ip>:8080
```

## Notes

- `/execute` remains available for advanced multi-step templates.
- The public protocol may be narrowed and cleaned up before release.
- Public sample skills are available under [`skills/`](../skills/), and the checked-in `agent-android` skill can be installed directly from GitHub after the CLI is installed.

## Skills Versus CLI

If you are trying the beta for the first time, start with the CLI first:

1. Verify `/health`
2. Run `agent-android --help`
3. Run one smoke flow in the REPL
4. Only then wrap that flow in your own agent skill/prompt

This avoids mixing two separate onboarding problems: device connectivity and agent-specific skill installation.

## Codex Skill Setup Example

If you want to wrap the public CLI in a Codex skill after the smoke flow works, create a local skill/prompt that says:

```text
Use the `agent-android` CLI.

Default loop:
1. Verify `--health --url http://<device-ip>:8080`
2. Use `--apps` if the package is unknown
3. Launch one app
4. Inspect with `--list`
5. Perform one action
6. Inspect again

For Xiaohongshu:
- launch `com.xingin.xhs`
- inspect the current UI
- find the search entry point
- tap it
- input the requested keyword
- inspect the results screen

Do not assume refIds stay stable after navigation. Re-run `--list` after each action.
```

The checked-in [`skills/agent-android/SKILL.md`](../skills/agent-android/SKILL.md) is the fuller reference version of the same idea.

## Task Example: Search Xiaohongshu

After `/health` works, this is a good first exploratory loop:

```text
apps
la com.xingin.xhs
list
find Search
tap <refId>
input <refId> lipstick
list
swipe up
list
```

`refId` values vary by device, language, and app version, so re-run `list` after each action instead of assuming fixed IDs.

## Windows Verification Chain

If you prefer a non-interactive first pass on Windows, run this checkpoint chain:

```powershell
.\examples\start-app-repl.ps1 192.168.3.207 .\aivane.apk
agent-android --health --url http://192.168.3.207:8080
agent-android --launch com.xingin.xhs --url http://192.168.3.207:8080
agent-android --list --url http://192.168.3.207:8080
```

If `/health` includes `permissions.accessibilityEnabled` and it is `false`, stop there and enable the AIVane accessibility service manually in Android Settings before running `--launch` or `--list`.
On non-privileged devices, an ADB `WRITE_SECURE_SETTINGS` denial during helper startup is expected; treat `/health` permissions as the source of truth.

Expected checkpoints:

1. `start-app-repl.ps1` returns `/health` JSON (or at least shows the target URL and no fatal ADB failure).
2. `--health` returns JSON service status.
3. `--launch com.xingin.xhs` reports launch success.
4. `--list` returns a non-empty UI tree.

## Troubleshooting

- If a Python command cannot connect, first check whether the AIVane app or its local API service has exited on the phone.
- Re-open the app or restart the phone-side service, then retry `curl http://<device-ip>:8080/health`.
- Confirm the phone and desktop are still on the same LAN and that `--url` points to the current device IP and port.


