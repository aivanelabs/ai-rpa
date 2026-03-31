See the Chinese overview at [README_CN.md](README_CN.md).

# AIVane AI RPA

This repository is the public-facing launch repo for `aivanelabs/ai-rpa` on GitHub.

The first public surface is **AIVane Android REPL Beta**: a lightweight Python CLI, public docs, examples, and sample skills that let AI agents inspect Android UI state and control a phone step by step over LAN.

## Current Status

- The repo structure and public CLI are ready for evaluation.
- GitHub is the only official entry point for the beta.
- APK builds are distributed through GitHub pre-releases.

## Who This Is For

- AI agent users working with Codex, Claude Code, OpenClaw, or similar tools
- Automation users who want stepwise Android control: inspect, tap, input, swipe, back, home, screenshot
- Early evaluators who are comfortable running a Python CLI and testing on a trusted LAN

## What Is Open In This Repo

- `clients/python/agent-android.py`
- Public protocol and user-facing docs
- Smoke examples and launch helpers
- Sample agent skills under `skills/`

## What Is Not Open In This Repo

- Core Java workflow engine internals
- Android runtime internals beyond the public surface
- Internal deployment and release infrastructure
- Private update channels, credentials, and commercial packaging

## Security Note

- Use the beta only on a trusted LAN.
- Do not expose the device port to the public internet.
- Accessibility and screenshot capabilities require explicit user approval on the phone.

## Quick Start

1. Install the AIVane Android REPL beta APK on your phone.
2. Make sure the phone and computer are on the same Wi-Fi network.
3. Run the CLI:
   ```bash
   python clients/python/agent-android.py --repl --url http://<device-ip>:8080
   ```
4. Inside the REPL, save the URL (`set url http://<device-ip>:8080`) and run the first smoke path:
   - `health`
   - `apps`
   - `la <package>`
   - `list`
   - `tap <refId>`
   - `input <refId> "hello"`
   - `back`
   - `press home`
   - `screenshot`

## Public Assets

- `clients/python/agent-android.py`: public-facing REPL entrypoint for Android device control.
- `docs/`: quickstart, protocol, permissions, known limitations, feedback, release notes, and repo scope.
- `examples/`: smoke flows and minimal usage examples.
- `skills/agent-android/`: sample skill definition with prompts and agent metadata.
- GitHub Releases: the only official place to download beta APK builds.

## Installation & Launch

- `docs/install-agent-android.md`: how to install the APK, confirm LAN connectivity, and run the first smoke.
- `examples/start-app-repl.sh`: a public-friendly starter script to connect to a device, optionally install the APK, and launch the Android REPL service.

## Additional Resources

- `docs/agent-examples.md`: starter prompts and usage snippets for Codex / Claude Code / OpenClaw.
- `.github/ISSUE_TEMPLATE/`: bug and feature report templates to capture actionable information from early users.

## Known Limitations

See `docs/known-limitations.md` for the current Beta boundaries (permission prompts, LAN-only use, and other beta limits). These limitations reflect the state of the remote Android runtime and the permissions it can request today.

## Contact

For questions and light coordination, please email `aivanelabs@gmail.com`.


