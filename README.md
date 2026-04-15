See the Chinese overview at [README_CN.md](README_CN.md).

# AIVane AI RPA

Control an Android phone from your desktop or AI agent in minutes: inspect UI, tap, type, launch apps, and capture screenshots locally over LAN.

This repository is the public home for `aivanelabs/ai-rpa`. The current public surface is **AIVane Android REPL Beta**: a directly installable `agent-android` CLI plus a GitHub-installable `agent-android` skill for tools such as Codex, Claude Code, and OpenClaw.

## Demo

- Add a calendar event: [demo-calendar.mp4](docs/assets/demo-calendar.mp4)
- Search on Xiaohongshu: [demo-xhs.mp4](docs/assets/demo-xhs.mp4)

## Start Here

- The beta already has a ready-to-install CLI and skill path; use the commands below instead of repo-local script paths.
- Download APK: [GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases)
- Install CLI: `uv tool install aivane-agent-android`
- Install skill: `npx skills add aivanelabs/ai-rpa --skill agent-android`

## 3-Step Quickstart

1. Install the APK on your phone and enable the AIVane accessibility service.
2. Install the CLI:

```bash
uv tool install aivane-agent-android
```

If `agent-android` is not found afterwards, run:

```bash
uv tool update-shell
```

Then reopen the terminal. If you want the current shell to work immediately on Linux, run:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

3. Verify the device is reachable:

```bash
agent-android --health --url http://<device-ip>:8080
```

If that succeeds, start the REPL:

```bash
agent-android --repl --url http://<device-ip>:8080
```

## Choose A Path

### For Humans

Use the CLI directly when you want to manually explore the phone from your desktop:

1. Download the APK from [GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases)
2. Install the CLI with `uv tool install aivane-agent-android`
3. Run `agent-android --repl --url http://<device-ip>:8080`
4. In the REPL, use the short loop: `health` -> `apps` -> `la <package>` -> `list` -> one action -> `list`

### For AI Agents

Use the skill when you want Codex, Claude Code, or another coding agent to drive the phone:

1. Install the CLI with `uv tool install aivane-agent-android`
2. Install the skill:

```bash
npx skills add aivanelabs/ai-rpa --skill agent-android
```

3. Give the agent a concrete task, for example:

```text
Use the installed agent-android skill to:
1. check phone health
2. list launcher apps
3. launch Settings
4. inspect visible UI nodes
5. tap the Wi-Fi entry
```

## First Success Path

This is the shortest practical smoke flow after the phone is reachable:

1. `agent-android --repl --url http://<device-ip>:8080`
2. `set url http://<device-ip>:8080`
3. `health`
4. `apps`
5. `la <package>`
6. `list`
7. `tap <refId>`
8. `list`

If you want the full setup path, see [docs/install-agent-android.md](docs/install-agent-android.md) and [docs/quickstart.md](docs/quickstart.md).

## What This Beta Is

- Local-first Android automation over LAN
- Human-friendly REPL plus agent-friendly skill
- Public CLI command: `agent-android`
- Designed for inspect -> act -> inspect workflows

## What This Beta Is Not

- Not a cloud phone farm
- Not remote control over arbitrary networks by default
- Not iOS support
- Not a visual recorder workflow yet

## Why The Phone Is The Web Server

- The phone runs the lightweight HTTP service locally and the desktop connects directly to `http://<device-ip>:8080`.
- UI inspection, taps, text input, and screenshots stay between the phone and the controlling machine.
- The first smoke flow works without a cloud relay.
- The tradeoff is that this beta is LAN-only.

## Install Sources

- PyPI package: `aivane-agent-android`
- Console command: `agent-android`
- Skill: [`skills/agent-android/`](skills/agent-android/)
- APK builds: [GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases)

## Repo Layout

- `clients/python/`: publishable Python CLI package using a standard `src` layout
- `docs/`: quickstart, install, protocol, permissions, release, and support docs
- `docs/assets/`: README-linked media such as demo videos and screenshots
- `examples/`: smoke-flow examples and launch helpers
- `skills/agent-android/`: installable public skill definition

## Additional Resources

- [docs/quickstart.md](docs/quickstart.md)
- [docs/install-agent-android.md](docs/install-agent-android.md)
- [docs/agent-examples.md](docs/agent-examples.md)
- [docs/release-checklist.md](docs/release-checklist.md)
- [docs/known-limitations.md](docs/known-limitations.md)

## Contact

For questions and light coordination, please email `aivanelabs@gmail.com`.
