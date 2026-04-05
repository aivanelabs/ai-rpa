# Public Protocol v1

This document outlines the public-facing protocol surface for the first AIVane Android REPL beta.

## Core Endpoints

- `GET /health`
  - Basic service diagnostics and permission readiness (`permissions.accessibilityEnabled`, `permissions.overlayPermissionGranted`, `permissions.screenshotPermissionGranted`)
- `GET /apps`
  - List launchable apps
- `POST /stop`
  - Request stop for the current task
- `GET /screenshot`
  - Capture a screenshot
- `GET /download`
  - Download a generated file

## Advanced / Compatibility Endpoint

- `POST /execute`
  - Compatibility and advanced path
  - Allows multi-step template execution
  - Kept for powerful workflows, but not the main public story

## Product Story

Public story:

- REPL for AI agents
- Phone control over LAN
- Observe -> decide -> act -> observe again

Compatibility story:

- Advanced users can still execute prepared multi-step templates

## Security

- LAN usage only
- Optional shared token
- Client transport can send the token through the `x-api-token` header
- Visible service state and stop controls

This protocol will continue to be refined as the public beta evolves.
