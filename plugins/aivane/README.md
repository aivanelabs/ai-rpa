# AIVane plugin for Claude Code

Run reusable AIVane browser automations from Claude Code: scrape websites, extract data to CSV, Excel or Google Sheets, fill forms, sign in to portals and download files.

The plugin adds:

- the AIVane cloud MCP server `https://app.aivane.net/mcp` (OAuth sign-in, free AIVane account; run `/mcp`, select `aivane` and authenticate after installing);
- the `aivane` skill, which tells Claude how to list, run, follow and stop automations and how to create new ones.

Install:

```bash
claude plugin marketplace add aivanelabs/ai-rpa
claude plugin install aivane@aivane
```

To build automations locally on Windows with the AIVane desktop app, follow the skill's "Local desktop server" setup; the desktop app gives the connection command under Settings > AI tools (MCP).

`skills/aivane/SKILL.md` in this plugin is a generated copy of the repository's `skills/aivane/SKILL.md`. Edit the source, then run `python scripts/sync_plugin_skills.py`.

Docs: https://aivane.net/docs/ai-tools/ · Privacy: https://aivane.net/privacy/ · Terms: https://aivane.net/terms/ · Support: support@aivane.net

License: MIT
