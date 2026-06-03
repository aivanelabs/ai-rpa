# Release Notes - v0.1.3

## Summary

This release makes template and asset iteration much faster. You can now push files from your computer to the phone-side REPL storage with `/upload`, use the Python CLI or REPL to upload templates and images without writing `curl`, and let phone-side templates download binary files with `http.download`.

## Install And Download

- Python CLI: `uv tool install aivane-agent-android` or `uv tool upgrade aivane-agent-android`
- Android APK asset: download `aivane.apk` from the GitHub Release assets
- Device endpoint: keep using `http://<device-ip>:8080` on a trusted LAN

## Upload Files To The Phone

Use `/upload` when the file already exists on your computer and you want to push it directly to a phone-local path that the REPL can read.

CLI:

```bash
agent-android --upload foo.json --remote-path Templates/foo.json --url http://<device-ip>:8080
agent-android --upload image.png --remote-path Images/image.png --url http://<device-ip>:8080
```

REPL:

```text
up foo.json Templates/foo.json
up image.png Images/image.png
```

Uploads overwrite by default. Add `--no-overwrite` when you want the command to fail instead of replacing an existing file:

```bash
agent-android --upload foo.json --remote-path Templates/foo.json --no-overwrite --url http://<device-ip>:8080
```

Raw HTTP is still available for scripts:

```bash
curl -X POST "http://PHONE_IP:8080/upload?path=Templates/foo.json&overwrite=true" \
  -H "X-Api-Token: TOKEN" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@foo.json"
```

`/upload` uses the existing shared-token check. Do not expose the phone-side service as an unauthenticated public file upload endpoint.

## Recommended Sub-Template Workflow

When you edit sub-templates on your computer, upload the updated file first:

```bash
agent-android --upload child.json --remote-path Templates/child.json --url http://<device-ip>:8080
agent-android --template main.json --url http://<device-ip>:8080
```

After the upload, `template.execute` inside the main template can resolve the updated sub-template from the phone-side `TemplateRepository`.

## Download Files From Templates

Use `http.download` inside a template when the phone should fetch a file from a URL and save it locally. It streams bytes to disk, so it is the right operation for images, JSON template files, zip archives, text files, and other binary content.

```json
{
  "operationType": "http.download",
  "parameters": {
    "url": "http://192.168.1.10:8000/templates/foo.json",
    "filePath": "${externalStorage}/Templates/foo.json",
    "overwrite": true
  }
}
```

Use `http.get` when you want a text or JSON HTTP response stored in variables. Use `http.download` when you want an actual file saved on the phone.

## Phone-Side File Operations

The app REPL now includes the `file` module:

- `file.read`
- `file.write`
- `file.append`
- `file.delete`
- `file.exists`

`file.write` and `file.append` create parent directories automatically, which makes it easier for templates to maintain local config, logs, downloaded assets, or generated sub-templates.

## Full Changelog

https://github.com/aivanelabs/ai-rpa/compare/v0.1.2...v0.1.3
