# Changelog

All notable changes to this project will be documented here.

## [Unreleased] – Local Fork

### Based on
Original project by **GongRzhe** –
[github.com/GongRzhe/Office-PowerPoint-MCP-Server](https://github.com/GongRzhe/Office-PowerPoint-MCP-Server).
All credit for the core implementation goes to the original author.

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
