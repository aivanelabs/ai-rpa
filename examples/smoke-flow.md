# Smoke Flow

Use this flow to verify a fresh Android REPL beta installation.

1. Start the app and ensure the service is running.
2. Copy or note the base URL.
3. Run:

```bash
agent-android --apps --url http://<device-ip>:8080
```

4. Launch a known app:

```bash
agent-android --launch <package> --url http://<device-ip>:8080
```

5. List the screen:

```bash
agent-android --list --url http://<device-ip>:8080
```

6. Tap or input.
7. Use back.
8. If needed, stop the current task.

