# Installing the Android REPL Beta

This guide covers the public prerequisites for running the agent-android beta (AI Mobile Automation).

## 1. Install the APK

1. Download the APK from the [GitHub Releases](https://github.com/aivanelabs/ai-rpa/releases) page for `aivanelabs/ai-rpa`.
2. Enable `Install unknown apps` for your browser or file manager.
3. Install the APK on your Android device; it will appear as **AIVane** in the launcher.

## 2. Connect to the same LAN

- Make sure the desktop/laptop and phone are on the same Wi-Fi network (no VPN/proxy).
- Note the phone’s local IP (e.g., `192.168.3.207`), and keep the REPL port as `8080`.
- Confirm connectivity with `adb connect <ip>:5555` (optional) and `curl http://<ip>:8080/health`.

## 3. Start the REPL service

Optionally use `examples/start-app-repl.sh` to launch the service via ADB:

```bash
./examples/start-app-repl.sh 192.168.3.207
```

If you already have an APK file locally, you can pass it as the second argument:

```bash
./examples/start-app-repl.sh 192.168.3.207 ./aivane.apk
```

The helper enables accessibility, starts the app, and tries to bring up the API service before checking `/health`.

## 4. Run the first smoke

1. Open the REPL client:  
   `python clients/python/agent-android.py --repl --url http://<device-ip>:8080`
2. Inside the REPL save the URL (`set url ...`) and run: `health`, `apps`, `la <package>`, `list`, `tap <refId>`, `input <refId>`, `back`, `press home`.
3. If you granted screenshot permission, run `screenshot` to confirm capture.

This smoke ensures the base APIs and CLI actions function before automating larger flows.


