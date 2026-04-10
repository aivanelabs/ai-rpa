See the Chinese overview at [README_CN.md](README_CN.md).

# AIVane AI RPA

This repository is the public home for `aivanelabs/ai-rpa`.

The current public surface is **AIVane Android REPL Beta**: a local-first Android automation CLI, public docs, examples, and an installable `agent-android` skill for agent tools such as Codex, Claude Code, and OpenClaw.

## Why The Phone Is The Web Server

- The phone runs the lightweight HTTP service locally and the desktop connects directly to `http://<device-ip>:8080`.
- UI inspection, taps, text input, and screenshots stay between the phone and the controlling machine.
- The first smoke flow works without a cloud relay.
- The tradeoff is that this beta is LAN-only.

## Install The CLI From PyPI

First install `uv` from the official guide:

- https://docs.astral.sh/uv/getting-started/installation/

Then install the CLI:

```bash
uv tool install aivane-agent-android
```

Upgrade it with:

```bash
uv tool install --upgrade aivane-agent-android
```

If `agent-android` is not found after install, run:

```bash
uv tool update-shell
```

Then reopen the terminal and retry the command.

After install, the command is:

```bash
agent-android --help
agent-android --repl --url http://<device-ip>:8080
```

## Install The Skill From GitHub

Use the checked-in skill directly from this repository:

```bash
npx skills add aivanelabs/ai-rpa --skill agent-android
```

The skill assumes the `agent-android` CLI is already installed and available on `PATH`.

## Quick Start

1. Install the AIVane Android REPL beta APK on your phone.
2. Enable the AIVane accessibility service on the phone.
3. Keep the phone and computer on the same Wi-Fi network.
4. Confirm the phone-side service is reachable:
   - run `curl http://<device-ip>:8080/health`
   - expect JSON instead of a connection error
5. Start the REPL:

```bash
agent-android --repl --url http://<device-ip>:8080
```

6. Inside the REPL, save the URL and run the first smoke flow:
   - `set url http://<device-ip>:8080`
   - `health`
   - `apps`
   - `la <package>`
   - `list`
   - `tap <refId>`
   - `input <refId> "hello"`
   - `back`
   - `press home`
   - `screenshot`

If you want an ADB-assisted setup path, see [docs/install-agent-android.md](docs/install-agent-android.md).

## Install Sources

- PyPI package: `aivane-agent-android`
- Console command: `agent-android`
- Skill: [`skills/agent-android/`](skills/agent-android/)
- APK builds: [GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases)

## Repo Layout

- `clients/python/`: publishable Python CLI package using a standard `src` layout
- `docs/`: quickstart, install, protocol, permissions, release, and support docs
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
