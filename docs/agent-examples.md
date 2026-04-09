# Agent Examples — Android REPL Beta

These prompt snippets show how Codex, Claude Code, or OpenClaw can call the agent-android via the public `agent-android.py` entrypoint.

## Codex (plain CLI)

```
Use the agent-android client at `clients/python/agent-android.py`.
1. Run `python agent-android.py --repl --url http://<device-ip>:8080`.
2. Save the URL (`set url http://<device-ip>:8080`).
3. Use `apps`, `la com.xingin.xhs`, `list`, `tap 127`, `input 3 "hello"`, `back`, `press home`.
4. Request `screenshot` if MediaProjection permission is granted.
```

## Codex Task Example: Xiaohongshu Search

```
Goal: Open Xiaohongshu, search for a keyword, and inspect the first screen of results.

Use the public client at `clients/python/agent-android.py`.
1. Verify connectivity with `python clients/python/agent-android.py --health --url http://<device-ip>:8080`.
2. List apps with `--apps` and launch Xiaohongshu with `--launch com.xingin.xhs`.
3. Inspect the current UI with `--list`.
4. Find the search entry point with `--text Search`, `--inputs`, or another fresh `--list`.
5. Tap the relevant `refId`, then input the keyword.
6. Run `--list` again to inspect visible results.
7. Repeat inspect -> act -> inspect instead of assuming the same `refId` still exists after navigation.
```

## Claude Code (structured guidance)

```
Goal: Open the Xiaomi Weather app, find a weather detail card, tap it, then return home.
Steps:
- `set url` (if needed)
- `health`
- `apps` -> confirm com.xiaomi.weather2
- `la com.xiaomi.weather2`
- `list` -> take note of a refId for a weather detail card
- `tap <refId>`
- `back`
- `press home`
```

## OpenClaw (tool-invocation)

```
Tool: agent-android
Inputs:
  - command: ["--launch", "com.xingin.xhs"]
  - command: ["--list"]
  - command: ["--tap", "127"]
  - command: ["--input", "3", "hello"]
```

Each agent can expand on these snippets with more specific selectors, loops, or input strings once a stable ARIA tree snapshot is available.


