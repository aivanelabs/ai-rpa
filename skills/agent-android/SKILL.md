---
name: agent-android
description: Connect to AIVane (AI Mobile Automation) over LAN, inspect launcher apps and UI state, and control the phone step by step through the public REPL/CLI path. Use this when Codex needs Android phone control for AI-agent tasks such as checking device connectivity, listing launchable apps, launching an app, inspecting the current UI tree, tapping, inputting text, swiping, navigating back/home, taking screenshots, or running a small end-to-end smoke flow with the public CLI.
---

# Android REPL

Use this skill to drive an Android device through the public `agent-android` beta surface published in the `aivanelabs/ai-rpa` repo.

Prerequisites:

- install `uv` first:
  - https://docs.astral.sh/uv/getting-started/installation/
- install the CLI:
  - `uv tool install aivane-agent-android`
- if `agent-android` is not found afterwards:
  - `uv tool update-shell`
- make sure `agent-android` is available on `PATH`
- install the skill from GitHub with:
  `npx skills add aivanelabs/ai-rpa --skill agent-android`

The public path is local-first:

- the phone hosts the lightweight HTTP service locally
- the desktop connects directly to `http://<device-ip>:8080`
- UI reads, taps, inputs, and screenshots stay on the phone and controlling machine
- the current tradeoff is LAN-only control; an optional server-side or relay path may arrive later

If a Python command suddenly stops working, first check whether the AIVane app or its local API service has exited on the phone.

## Core Workflow

Every Android control task should follow the same short loop:

1. Confirm connectivity with `/health`
2. Discover the target app with `apps` if needed
3. Launch one app
4. Inspect the current UI tree
5. Perform one action
6. Inspect again

Keep the loop short. Prefer inspect -> act -> inspect over long speculative command chains.

## Quick Start

Start the REPL:

```bash
agent-android --repl --url http://<device-ip>:8080
```

Save the current device URL inside the REPL:

```text
set url http://<device-ip>:8080
```

Built-in help:

```bash
agent-android --help
```

```text
h
```

## Essential CLI Commands

Use the one-off CLI when you already know the exact action you want.

```bash
# Connectivity
agent-android --health --url http://<device-ip>:8080

# Discovery
agent-android --apps --url http://<device-ip>:8080
agent-android --list --url http://<device-ip>:8080
agent-android --id com.example:id/search --url http://<device-ip>:8080
agent-android --text Search --url http://<device-ip>:8080
agent-android --inputs --url http://<device-ip>:8080
agent-android --refId 7 --url http://<device-ip>:8080
agent-android --xpath 7 --url http://<device-ip>:8080
agent-android --get-attr 7 text --url http://<device-ip>:8080

# Actions
agent-android --launch com.xingin.xhs --url http://<device-ip>:8080
agent-android --tap 7 --url http://<device-ip>:8080
agent-android --input 7 "hello world" --url http://<device-ip>:8080
agent-android --swipe up --url http://<device-ip>:8080
agent-android --back --url http://<device-ip>:8080
agent-android --press home --url http://<device-ip>:8080
agent-android --screenshot --url http://<device-ip>:8080

# Waiting and output
agent-android --wait-for Search --timeout 30 --url http://<device-ip>:8080
agent-android --list --raw --output tree.json --url http://<device-ip>:8080
```

## REPL Command Reference

Use the REPL for exploratory tasks and smoke runs. Short aliases and long names both work.

### Browse

- `health` or `hl`
  Check `/health`.
- `l [n]` or `list [n]`
  List the first `n` elements, or all cached elements when `n` is omitted.
- `ss` or `snapshot`
  Force-refresh the UI tree and print it again.
- `f <text>` or `find <text>`
  Filter by text or content description.
- `id <resourceId>`
  Filter by Android resource ID.
- `ref <refId>`
  Show the full element detail for one refId.
- `x <refId>` or `xpath <refId>`
  Generate XPath candidates and validate their runtime match counts.
- `xx <refId>`
  Tap by the best unique generated XPath candidate. Refuses ambiguous matches.
- `vx <xpath> [idx]` or `validatex <xpath> [idx]`
  Validate one XPath against the runtime. Optionally inspect one match by zero-based index.

### Interact

- `t <refId>` or `tap <refId>`
  Tap the element center point from the current tree.
- `tx <xpath>` or `tapx <xpath>`
  Tap one runtime-resolved XPath target.
- `i <refId> <text>` or `input <refId> <text>`
  Input text into a refId target.
  Use `--clear` or `""` to clear instead of typing.
- `ix <xpath> <text>` or `inputx <xpath> <text>`
  Input text into one XPath target.
  Use `ix <xpath> --` or `--clear` to clear the field.
- `sw <d|u|l|r> [--dur N] [--dist N]` or `swipe ...`
  Swipe down/up/left/right with optional duration and distance.
- `p <back|home|recents>` or `press ...`
  Press a system key.
- `b` or `back`
  Press Back.
- `la <package>` or `launch <package>`
  Launch an app by package name.
- `s [path]` or `screenshot [path]`
  Capture a screenshot to an auto-generated or explicit path.

### Wait And Inspect

- `wf <text> [--t N]` or `waitfor ...`
  Wait for an element to appear.
- `g <refId> <attr>` or `get <refId> <attr>`
  Read an attribute such as `text`, `class`, `bounds`, `x`, `y`, or `xpath`.
- `apps`
  List launcher apps from `/apps`.

### Session

- `raw`
  Toggle raw JSON mode.
- `vars`
  Show current URL, timeout, raw mode, and tree cache state.
- `set url http://<device-ip>:8080`
  Switch the server URL and persist it to local config.
- `set timeout 30`
  Set the default wait timeout in seconds.
- `h` or `help`
  Show the built-in help text.
- `q` or `quit`
  Exit the REPL.

## Common Patterns

### First smoke flow

1. `set url http://<device-ip>:8080`
2. `health`
3. `apps`
4. `la <package>`
5. `l`
6. `t <refId>`
7. `i <refId> hello`
8. `b`
9. `s`

### Find the right package before launch

```text
apps
la com.example.app
l
```

### Inspect an element before using XPath

```text
l
ref 12
x 12
vx //EditText[@text='Search']
```

### Clear and refill an input

```text
i 7 --clear
i 7 hello world
```

```text
ix //EditText[@text='Search'] --
ix //EditText[@text='Search'] -- hello world
```

## Troubleshooting

- If a Python call fails, first check whether the AIVane app or phone-side API service has exited.
- If `agent-android` is not found, run `uv tool update-shell`, reopen the terminal, and retry.
- Re-open the app or restart the phone-side service, then retry `curl http://<device-ip>:8080/health`.
- If `health` works but UI commands fail, run `ss` to force-refresh the tree before tapping or inputting.
- If `tx` or `ix` fails, run `vx <xpath>` and make sure the XPath resolves to exactly one runtime match.
- If screenshots fail the first time, confirm the on-device MediaProjection permission prompt was accepted.
- If everything suddenly stops responding, confirm the phone IP did not change and that the desktop is still on the same LAN.

## When To Stop

Stop and ask for user help when:

- the device is unreachable on LAN
- the app is not running and cannot be restarted from the current path
- required Android permissions are missing
- launcher discovery returns nothing useful
- the runtime UI no longer matches the expected screen after repeated refreshes

## References

- Smoke checklist: [GitHub](https://github.com/aivanelabs/ai-rpa/blob/main/skills/agent-android/references/smoke-flow.md)
- Quickstart: [GitHub](https://github.com/aivanelabs/ai-rpa/blob/main/docs/quickstart.md)
- Install guide: [GitHub](https://github.com/aivanelabs/ai-rpa/blob/main/docs/install-agent-android.md)
- Public protocol: [GitHub](https://github.com/aivanelabs/ai-rpa/blob/main/docs/protocol-v1.md)
- Known beta limits: [GitHub](https://github.com/aivanelabs/ai-rpa/blob/main/docs/known-limitations.md)
