# Skills

This directory holds public skills for the `aivanelabs/ai-rpa` GitHub beta.

## Current Skills

- `aivane/`
  - Run, follow and create AIVane browser and desktop automations from an AI agent
  - Uses the AIVane MCP server: cloud `https://app.aivane.net/mcp` (OAuth, free account) or the local server of the AIVane desktop app for Windows
  - Also published as a Claude Code plugin (`plugins/aivane/`, marketplace `.claude-plugin/marketplace.json`) that bundles the skill and the cloud MCP server
- `agent-android/`
  - Public Android phone control REPL skill
  - Uses the installed `agent-android` CLI
  - Focuses on LAN connectivity, launcher app discovery, launch, inspect, and stepwise interaction

## Install the `aivane` skill

skills.sh CLI (Codex, Claude Code, Cursor and other agents):

```bash
npx skills add aivanelabs/ai-rpa --skill aivane
```

Hermes Agent:

```bash
hermes skills install aivanelabs/ai-rpa/skills/aivane
```

Claude Code plugin (skill plus the cloud MCP server):

```bash
claude plugin marketplace add aivanelabs/ai-rpa
claude plugin install aivane@aivane
```

Then run `/mcp` in Claude Code, select `aivane` and authenticate.

OpenClaw: install from ClawHub once the skill is published there (`openclaw skills install` with the published name).

The skill only explains how to use AIVane; the agent still needs the AIVane MCP server connected. Setup for each client is in [`aivane/SKILL.md`](aivane/SKILL.md) and at https://aivane.net/docs/ai-tools/.

`plugins/aivane/skills/aivane/` is a generated copy (plugins cannot reference files outside their directory). Edit `skills/aivane/` and run `python scripts/sync_plugin_skills.py`; CI runs it with `--check`.

## Scope

`agent-android` is a thin wrapper around the AIVane public protocol and the installed `agent-android` CLI. `aivane` is a thin guide to the AIVane MCP tools.
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


