# Python Clients

This folder contains the public Python-side clients for the first agent-android beta.

## Included

- `agent-android.py`
  - Public-facing entrypoint for the Android REPL beta
  - Supports launcher discovery, UI listing, tap, input, swipe, back, home, screenshot, and template execution through `/execute`

## Recommended First Use

Start with:

```bash
python agent-android.py --repl --url http://<device-ip>:8080
```

If the phone enables shared-token protection, you can provide it in any of these ways:

```bash
python agent-android.py --repl --url http://<device-ip>:8080 --token YOUR_TOKEN
```

Set the environment variable `AIVANE_API_TOKEN` when you prefer not to pass the token on every command line.

Inside the REPL you can also persist it locally:

```text
set token YOUR_TOKEN
```

For prepared multi-step flows, use:

```bash
python agent-android.py --template template.json --url http://<device-ip>:8080
```

## Built-in Help

- CLI help: `python agent-android.py --help`
- REPL help: start `--repl`, then type `h`

The REPL is the recommended first path because it keeps the inspect -> act -> inspect loop short and makes connectivity problems easier to diagnose.

## Connectivity Notes

- The phone hosts the beta HTTP service locally and the Python client connects directly to `http://<device-ip>:8080`.
- Commands run locally between the desktop and phone; the public beta path does not require a cloud relay.
- If a Python command cannot connect, first check whether the AIVane app or its local API service has exited on the phone, then retry `/health`.


