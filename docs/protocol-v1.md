# Public Protocol v1

This document outlines the public-facing protocol surface for the first AIVane Android REPL beta.

## Core Endpoints

- `GET /health`
  - Basic service diagnostics, REPL app version (`version`), configured address/port, and permission readiness (`permissions.accessibilityEnabled`, `permissions.overlayPermissionGranted`, `permissions.screenshotPermissionGranted`)
- `GET /apps`
  - List launchable apps
- `POST /stop`
  - Request stop for the current task
- `GET /screenshot`
  - Capture a screenshot
- `GET /download`
  - Download a generated file
- `POST /upload`
  - Upload a file from the controlling computer to a phone-local path
  - Supports raw `application/octet-stream` uploads and multipart form uploads
  - `path` may be absolute or relative to the app external files directory
  - `overwrite` defaults to `true`; set `overwrite=false` to reject existing targets
  - Uses the same shared-token check as the protected REPL endpoints
- `POST /executeApplication`
  - Upload and execute a zipped application template bundle
  - Use this for local workflows that have one main template plus child templates
  - Child template resolution is scoped to the uploaded bundle to avoid phone-local name collisions
  - Optional query/form parameters include `mainTemplateFile`, `applicationId`, and `variables`
  - Uses the same shared-token check as the protected REPL endpoints

## Advanced / Compatibility Endpoint

- `POST /execute`
  - Compatibility and advanced path
  - Allows multi-step template execution
  - Kept for powerful workflows, but not the main public story

## Template Operation Notes

- `http.download`
  - Download a URL response as bytes and save it to `filePath`
  - Use this for images, JSON template files, zip archives, text files, and other binary content
  - Creates the parent directory for `filePath`
  - `overwrite` defaults to `true`
- `http.get`
  - Keep using this for text or JSON HTTP responses that should be read into variables
- `file.read`, `file.write`, `file.append`, `file.delete`, `file.exists`
  - Available in the app REPL
  - `file.write` and `file.append` create parent directories automatically

## Product Story

Public story:

- REPL for AI agents
- Phone control over LAN
- Observe -> decide -> act -> observe again

Compatibility story:

- Advanced users can still execute prepared multi-step templates
- Template bundles can be executed directly with `/executeApplication`
- Standalone files can be synced with `/upload`, then consumed by templates through file operations

## Security

- LAN usage only
- Optional shared token
- Client transport can send the token through the `x-api-token` header
- `/upload` and `/executeApplication` are not public unauthenticated file drops; protect them with the same token configuration used for the rest of the REPL service
- Visible service state and stop controls

This protocol will continue to be refined as the public beta evolves.
