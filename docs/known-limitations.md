# Known Limitations — v0.1.0 Beta

This Beta milestone exposes a hands-on Android REPL. The following constraints are expected when you first try it.

1. **Screenshot requires first-run authorization.** MediaProjection still needs an explicit on-device approval flow before screenshots work reliably.
2. **LAN only.** The desktop agent must be on the same Wi-Fi as the phone; there is no cloud relay or NAT traversal build yet.
3. **REPL-first product surface.** The public story is stepwise control and smoke flows; advanced multi-step template execution remains available through `/api/execute`, but there is not yet a polished public template UI.
4. **Beta permissions are still hands-on.** Accessibility and screenshot capabilities may still require manual confirmation on the phone.
5. **Beta APK distribution is GitHub-first.** The official beta download path is the GitHub Releases page for this repository.
