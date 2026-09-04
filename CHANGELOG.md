# Changelog

All notable changes to this project will be documented here.

## [Unreleased] – Local Fork

### Based on
Original project by **GongRzhe** –
[github.com/GongRzhe/Office-PowerPoint-MCP-Server](https://github.com/GongRzhe/Office-PowerPoint-MCP-Server).
All credit for the core implementation goes to the original author.

---

> ⚠️ **SECURITY WARNING – Single-user deployment only**
>
> This fork is designed and tested for **a single trusted user** on a private network.
> The following issues must be resolved before exposing this server to multiple users
> or any public/semi-public network:
>
> - **No user isolation**: all users share the same file directory (`/app/pptx_files`).
>   Any user can read, overwrite, or delete any other user's files.
> - **Single shared API key**: `MCP_API_KEY` is one secret for all callers — there is
>   no per-user authentication or authorisation.
> - **No rate limiting or quotas**: a single client can exhaust disk space or CPU.
> - **DNS rebinding protection disabled**: `enable_dns_rebinding_protection=False` was
>   set to allow access via Docker/network IP. Re-enable it (and use a reverse proxy
>   with a proper hostname + TLS) for any multi-user or internet-facing scenario.
>
> **TODO before multi-user use:**
> - [ ] Per-user subdirectories (e.g. `/app/pptx_files/<user-id>/`)
> - [ ] Per-user tokens (OAuth2/JWT via `app.settings.auth`)
> - [ ] Re-enable DNS rebinding protection and add TLS termination (nginx/Caddy)
> - [ ] Add rate limiting and disk quota per user

---

### Added

#### HTTP transport: DNS rebinding protection disabled (`ppt_mcp_server.py`)
The MCP SDK's `TransportSecuritySettings` now has DNS rebinding protection enabled
by default, which rejected connections from non-localhost Host headers (HTTP 421).
Added `transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)`
so the server can be reached via its Docker/network IP address.

#### File upload/download HTTP endpoints (`tools/file_tools.py`)
Three custom HTTP routes for transferring PPTX files without shared filesystem access:

- **`POST /upload`** – multipart/form-data upload (`curl -F "file=@deck.pptx" http://host:8001/upload`)
- **`GET  /download/<filename>`** – streams the file back as octet-stream
- **`GET  /files`** – lists all available PPTX files on the server

The returned `file_path` from `/upload` can be passed directly to `open_presentation`.

#### Optional API key protection (`MCP_API_KEY`)
Set `MCP_API_KEY` environment variable to require an `X-API-Key` header on all
`/upload`, `/download`, and `/files` requests. If unset, endpoints are unprotected.
