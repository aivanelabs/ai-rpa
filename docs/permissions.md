# Permissions Overview

This document summarizes the permissions the Android REPL beta requests and why they matter for the first public release.

## Accessibility

- The app exposes an accessibility service so it can read the current UI tree (`android.ui.getAriaTree`) and produce refIds/xpaths. The service should be enabled once per device and can be disabled later; no other OS permissions are required for this surface.

## Screenshot / MediaProjection

- Capturing screenshots uses Android’s `MediaProjection` API. Users must grant screenshot permission after running `agent-android --screenshot` once. The CLI falls back to template-based captures when the permission is absent. The permission prompt is shown by the system (not the app), and users can revoke it later.

## Local Network / Token

- The desktop agent communicates with the device over LAN (`http://<device-ip>:8080`). The health endpoint (`/health`) reports basic service status plus a `permissions` object for accessibility, overlay, and screenshot readiness. There is no transport encryption in this beta, so keep the device on a trusted network segment.
- The service runs on the phone itself for this public beta. The local-first path avoids uploading UI data or screenshots to a cloud relay during normal use.
- Because the public path is direct device-to-desktop communication, current control is limited to the same LAN. A later optional server-side path may expand that boundary.
- If you enable a shared token on the phone, the Python client can send it via `--token YOUR_TOKEN`, the `AIVANE_API_TOKEN` environment variable, or `set token YOUR_TOKEN` inside the REPL.

## Security Notes

- Only expose `/execute`, `/health`, `/screenshot`, `/apps`, `/stop`, `/download`, and the documented launcher endpoints. Do not forward requests beyond the documented surface. You can disable the REPL by stopping the phone-side service or killing the app.


