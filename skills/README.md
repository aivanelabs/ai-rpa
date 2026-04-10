# Skills

This directory holds public skills for the `aivanelabs/ai-rpa` GitHub beta.

## Current Skills

- `agent-android/`
  - Public Android phone control REPL skill
  - Uses the installed `agent-android` CLI
  - Focuses on LAN connectivity, launcher app discovery, launch, inspect, and stepwise interaction

## Planned Targets

- Codex
- Claude Code
- OpenClaw

## Scope

These skills are thin wrappers around the AIVane public protocol and Python client.
Keep them aligned with the checked-in protocol, CLI, and docs in this repository.

## How To Use Them Today

- Install the CLI first: `python -m pip install aivane-agent-android`
- Install the skill from GitHub:

```bash
npx skills add aivanelabs/ai-rpa --skill agent-android -a claude-code -a codex -a openclaw -g -y
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


