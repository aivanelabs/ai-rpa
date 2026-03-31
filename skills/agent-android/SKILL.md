---
name: agent-android
description: Connect to AIVane (AI Mobile Automation) over LAN, inspect launcher apps and UI state, and control the phone step by step through the public REPL/CLI path. Use this when Codex needs Android phone control for AI-agent tasks such as checking device connectivity, listing launchable apps, launching an app, inspecting the current UI tree, tapping, inputting text, swiping, navigating back/home, taking screenshots, or running a small end-to-end smoke flow with the public Python client.
---

# Android REPL

## Overview

Use this skill to drive an Android device through the public agent-android beta surface published in the `aivanelabs/ai-rpa` GitHub repo.

This skill assumes:

- the phone and the controlling machine are on the same LAN
- the Android REPL app is installed and its local API service is running
- the public Python client at `../../clients/python/agent-android.py` is available

## Quick Start

Use the public client directly:

```bash
python ../../clients/python/agent-android.py --repl --url http://<device-ip>:8080
```

If the user already saved the device URL before, the client can be used without `--url`.

To persist the current device address inside the REPL:

```text
set url http://<device-ip>:8080
```

## Core Workflow

### 1. Confirm connectivity

Check that the Android REPL service is alive:

```bash
curl http://<device-ip>:8080/health
```

If health fails, stop and fix connectivity before trying UI actions.

### 2. Discover launchable apps

List launcher apps:

```bash
python ../../clients/python/agent-android.py --apps --url http://<device-ip>:8080
```

Inside the REPL, use:

```text
apps
```

Use launcher discovery when the user does not know the package name.

### 3. Launch and inspect

Launch an app:

```bash
python ../../clients/python/agent-android.py --launch <package> --url http://<device-ip>:8080
```

Then inspect the current UI:

```bash
python ../../clients/python/agent-android.py --list --url http://<device-ip>:8080
```

### 4. Interact step by step

Use the smallest possible action loop:

1. list current elements
2. choose one action
3. perform one action
4. inspect again

Typical actions:

- tap
- input
- swipe
- back
- press home
- screenshot

Prefer short feedback loops over long speculative chains.

### 5. Use templates only when needed

The public story is REPL-first. Keep advanced multi-step template execution as a compatibility path for stronger workflows, not the default first choice.

Use advanced flows only when:

- the user already has a prepared template
- the task is clearly repetitive
- a deterministic multi-step path is more valuable than stepwise exploration

## Smoke Flow

For a minimal end-to-end verification, follow this path:

1. `set url http://<device-ip>:8080`
2. health check
3. `apps`
4. `la <package>`
5. `list`
6. `tap <refId>`
7. `input <refId> <text>`
8. `back`

See [references/smoke-flow.md](references/smoke-flow.md) for a concise checklist.

## When To Stop

Stop and ask for user help when:

- the device is unreachable on LAN
- the Android REPL app is not running
- required Android permissions are missing
- launcher discovery returns nothing useful
- UI state no longer matches the expected screen after repeated retries

## References

- For the smoke checklist: [references/smoke-flow.md](references/smoke-flow.md)
- For public protocol expectations: [../../docs/protocol-v1.md](../../docs/protocol-v1.md)
- For first-run instructions: [../../docs/quickstart.md](../../docs/quickstart.md)


