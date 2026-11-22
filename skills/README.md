# Skills

Installable agent skills from `aivanelabs/ai-rpa`. Each skill lives in its own directory with a `SKILL.md`.

| Skill | Who it is for | What it needs |
| --- | --- | --- |
| [`computer-automation/`](computer-automation/SKILL.md) | Anyone who wants an AI agent (Claude, ChatGPT, Codex, Cursor, Hermes, OpenClaw and other MCP clients) to run, follow and create AIVane browser and desktop automations: scraping and data extraction to CSV, Excel or Google Sheets, form filling, portal sign-in and downloads | The AIVane MCP server: cloud `https://app.aivane.net/mcp` (OAuth, free account) or the local server of the AIVane desktop app for Windows |
| [`agent-android/`](agent-android/SKILL.md) | Developers who want an agent or a terminal to control an Android phone over LAN (beta): launcher app discovery, launch, inspect, and stepwise interaction | The installed `agent-android` CLI and the AIVane Android REPL APK on a phone in the same network ([guide](../docs/android/README.md)) |

`computer-automation` is also published as a Claude Code plugin (`plugins/aivane/`, marketplace `.claude-plugin/marketplace.json`) that bundles the skill and the cloud MCP server.

## Install the `computer-automation` skill

skills.sh CLI (Codex, Claude Code, Cursor and other agents):

```bash
npx skills add aivanelabs/ai-rpa --skill computer-automation
```

Hermes Agent:

```bash
hermes skills install aivanelabs/ai-rpa/skills/computer-automation
```

Claude Code plugin (skill plus the cloud MCP server):

```bash
claude plugin marketplace add aivanelabs/ai-rpa
claude plugin install aivane@aivane
```

Then run `/mcp` in Claude Code, select `aivane` and authenticate.

OpenClaw: `openclaw skills install computer-automation` (published on ClawHub).

The skill only explains how to use AIVane; the agent still needs the AIVane MCP server connected. Setup for each client is in [`computer-automation/references/setup.md`](computer-automation/references/setup.md) and at https://aivane.net/docs/ai-tools/.

`plugins/aivane/skills/computer-automation/` is a generated copy (plugins cannot reference files outside their directory). Edit `skills/computer-automation/` and run `python scripts/sync_plugin_skills.py`; CI runs it with `--check`.

## Scope

`agent-android` is a thin wrapper around the AIVane public protocol and the installed `agent-android` CLI. `computer-automation` is a thin guide to the AIVane MCP tools.
Keep them aligned with the checked-in protocol, CLI, and docs in this repository and with https://aivane.net/docs/ai-tools/.

## How To Use `agent-android` Today

- Install the CLI first: `uv tool install aivane-agent-android`
- If the command is not found afterwards, run: `uv tool update-shell`
- Install the skill from GitHub:

```bash
npx skills add aivanelabs/ai-rpa --skill agent-android
```

- Start by validating the phone connection with the CLI.
- After the smoke flow works, use the checked-in skill as-is or adapt it for your environment.

### Codex Example

For Codex, the simplest starting point is to use the installed skill or copy the core loop from `agent-android/SKILL.md`:

```text
Use the `agent-android` CLI.
Verify /health first, then inspect -> act -> inspect.
Prefer `apps`, `launch`, `list`, `tap`, `input`, `swipe`, `back`, and `screenshot`.
Re-run `list` after every UI action because refIds may change.
```


