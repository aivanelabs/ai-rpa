# Quickstart — agent-android

This quickstart introduces the public GitHub beta for AIVane (AI Mobile Automation) under `aivanelabs/ai-rpa`.

## What You Need

- An Android device with the AIVane REPL beta APK installed
- A desktop or laptop on the same LAN
- Python 3.7+

## Why The Phone Hosts The Service

- The beta starts a lightweight HTTP service on the phone itself.
- The desktop talks directly to `http://<device-ip>:8080`, so the full smoke flow runs locally.
- UI reads, taps, inputs, and screenshots are not uploaded to a cloud service as part of this public path.
- The tradeoff is that the first public build is LAN-only. A later optional server-side or relay path is under consideration for scenarios that need control beyond the local network.

## First Run

Run the CLI with an explicit URL:

```bash
python clients/python/agent-android.py --repl --url http://<device-ip>:8080
```

Inside the REPL, save the URL for later:

```text
set url http://<device-ip>:8080
```

## Minimal Smoke Flow

1. Check health:

```bash
curl http://<device-ip>:8080/health
```

2. List launchable apps:

```bash
python clients/python/agent-android.py --apps --url http://<device-ip>:8080
```

3. Launch an app:

```bash
python clients/python/agent-android.py --launch <package> --url http://<device-ip>:8080
```

4. Inspect the current screen:

```bash
python clients/python/agent-android.py --list --url http://<device-ip>:8080
```

5. Interact:

```bash
python clients/python/agent-android.py --tap <refId> --url http://<device-ip>:8080
python clients/python/agent-android.py --input <refId> "hello" --url http://<device-ip>:8080
python clients/python/agent-android.py --back --url http://<device-ip>:8080
```

## Notes

- `/execute` remains available for advanced multi-step templates.
- The public protocol may be narrowed and cleaned up before release.
- Public sample skills are not staged yet.

## Troubleshooting

- If a Python command cannot connect, first check whether the AIVane app or its local API service has exited on the phone.
- Re-open the app or restart the phone-side service, then retry `curl http://<device-ip>:8080/health`.
- Confirm the phone and desktop are still on the same LAN and that `--url` points to the current device IP and port.


