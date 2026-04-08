# Skills

This directory holds public skills for the `aivanelabs/ai-rpa` GitHub beta.

## Current Skills

- `agent-android/`
  - Public Android phone control REPL skill
  - Uses the public Python CLI
  - Focuses on LAN connectivity, launcher app discovery, launch, inspect, and stepwise interaction

## Planned Targets

- Codex
- Claude Code
- OpenClaw

## Scope

These skills are thin wrappers around the AIVane public protocol and Python client.
Keep them aligned with the checked-in protocol, CLI, and docs in this repository.

## How To Use Them Today

- Treat these skills as public reference prompts and workflow guides.
- This repo does not yet ship a one-click installer for Codex, Claude Code, or OpenClaw.
- Start by validating the phone connection with the Python CLI.
- After the CLI smoke flow works, copy or adapt the relevant skill text into your own agent environment.

### Codex Example

For Codex, the simplest starting point is to copy the core loop from `agent-android/SKILL.md` into your local skill or system prompt:

```text
Use the AIVane Android public client at `clients/python/agent-android.py`.
Verify /health first, then inspect -> act -> inspect.
Prefer `apps`, `launch`, `list`, `tap`, `input`, `swipe`, `back`, and `screenshot`.
Re-run `list` after every UI action because refIds may change.
```


