# AIVane for AI agents

See the Chinese overview at [README_CN.md](README_CN.md). **Official website:** [aivane.net](https://aivane.net/)

Skills, plugins and example automations that let AI agents use [AIVane](https://aivane.net/). AIVane turns web tasks into reusable, no-code automations: build one once (describe the task or record it once in the AIVane desktop app), then run it again with new inputs in AIVane's cloud browser or on your own computer.

## Choose your path

| I want to... | Use | Details |
| --- | --- | --- |
| **① Run and create browser/desktop automations** from Claude, ChatGPT, Codex, Cursor, Hermes or OpenClaw | [`skills/aivane`](skills/aivane/SKILL.md) + the AIVane MCP server `https://app.aivane.net/mcp` | [Browser and desktop automations](#browser-and-desktop-automations) |
| **② Control an Android phone over LAN** (beta) | [`skills/agent-android`](skills/agent-android/SKILL.md) + the `agent-android` CLI | [Android phone control over LAN](#android-phone-control-over-lan-beta) |

## Browser and desktop automations

Typical tasks: scraping websites and extracting data to CSV, Excel or Google Sheets, filling forms, signing in to portals and downloading reports or invoices, repeated price and stock checks. Through the AIVane MCP server an agent lists your automations, runs them with new inputs, follows each run and reads back outputs, saved files and a screenshot. It can also start creating a new automation.

Connect an MCP server:

- **Cloud server** (any OS): `https://app.aivane.net/mcp` (Streamable HTTP, OAuth sign-in, free AIVane account).
- **Local desktop server** (Windows): install AIVane from [aivane.net/download](https://aivane.net/download), then copy the connection setup from Settings > AI tools (MCP).

Add the skill, which tells the agent how to use the AIVane MCP tools:

```bash
# skills.sh CLI (Codex, Claude Code, Cursor and other agents)
npx skills add aivanelabs/ai-rpa --skill aivane

# Claude Code plugin (skill plus the cloud MCP server); then run /mcp, select aivane and authenticate
claude plugin marketplace add aivanelabs/ai-rpa
claude plugin install aivane@aivane

# Hermes Agent
hermes skills install aivanelabs/ai-rpa/skills/aivane
```

Claude (claude.ai, Claude Desktop), ChatGPT and VS Code connect from their own connector or MCP settings with the same address. Setup for each client: [aivane.net/docs/ai-tools](https://aivane.net/docs/ai-tools/) and [`skills/aivane/SKILL.md`](skills/aivane/SKILL.md). More install options: [skills/README.md](skills/README.md).

## Android phone control over LAN (beta)

**AIVane Android REPL Beta** controls an Android phone from your desktop or AI agent: inspect UI, tap, type, launch apps, and capture screenshots locally over LAN.

First install the APK from [GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases) on the phone and enable the AIVane accessibility service. Then:

```bash
uv tool install aivane-agent-android
npx skills add aivanelabs/ai-rpa --skill agent-android
agent-android --health --url http://<device-ip>:8080
```

Full guide with demos, quickstart, REPL commands, template upload and validation: [docs/android/README.md](docs/android/README.md).

## Repository layout

| Path | Contents |
| --- | --- |
| [`skills/`](skills/README.md) | Installable agent skills: `aivane/` (browser and desktop automations via MCP) and `agent-android/` (Android LAN beta) |
| [`plugins/`](plugins/aivane/README.md) | Claude Code plugins; `plugins/aivane/` bundles the `aivane` skill and the cloud MCP server. The marketplace is [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) |
| [`examples/`](examples/README.md) | Example AIVane automations (Applications), plus the Android smoke flow and ADB launch helpers |
| `clients/` | Publishable Python packages: [`clients/python/`](clients/python/README.md) (`aivane-agent-android`, command `agent-android`) and [`clients/template-linter/`](clients/template-linter/README.md) (`aivane-template-linter`, command `aivane-template-lint`) |
| `docs/` | [`docs/android/`](docs/android/README.md) Android beta guide (it links the quickstart, install, protocol, permissions and release docs in `docs/`); [`docs/templates/`](docs/templates/README.md) template authoring and linting; [`docs/operation-types/`](docs/operation-types/README.md) OperationType reference; `docs/assets/` media |
| `scripts/` | Repository tooling, for example `sync_plugin_skills.py`, which copies `skills/aivane/` into the plugin |
| `aivane.apk` | Android REPL beta APK build (releases are on [GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases)) |

## Contributing, security, license

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [LICENSE](LICENSE) (MIT)
- Support: `support@aivane.net` · Privacy: [aivane.net/privacy](https://aivane.net/privacy/) · Terms: [aivane.net/terms](https://aivane.net/terms/)
