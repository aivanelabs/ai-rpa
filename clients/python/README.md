# Python Client

This directory contains the publishable Python CLI package for the AIVane Android REPL beta.

## Install

Run these commands from `clients/python/`:

```bash
python -m pip install .
```

For editable development:

```bash
python -m pip install -e .
```

To build distributions locally:

```bash
python -m pip install --upgrade build
python -m build
```

## Run

After installation, use the console script:

```bash
agent-android --help
agent-android --repl --url http://<device-ip>:8080
agent-android --health --url http://<device-ip>:8080
```

If the phone requires a shared token:

```bash
agent-android --repl --url http://<device-ip>:8080 --token YOUR_TOKEN
```

Set the environment variable `AIVANE_API_TOKEN` when you prefer not to pass the token on every command line.

Inside the REPL you can also persist it locally:

```text
set token YOUR_TOKEN
```

For prepared multi-step flows:

```bash
agent-android --template template.json --url http://<device-ip>:8080
```

## Package Layout

- `pyproject.toml`: setuptools package metadata and console-script registration
- `src/agent_android/`: installable package source
- `tests/`: unit and device smoke tests

## Notes

- The package uses a standard `src` layout under `src/agent_android`.
- The phone hosts the beta HTTP service locally and the client connects directly to `http://<device-ip>:8080`.
- If a command cannot connect, first check whether the AIVane app or its local API service has exited on the phone, then retry `/health`.


