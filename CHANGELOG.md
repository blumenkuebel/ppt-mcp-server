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

#### File upload/download tools (`tools/file_tools.py`)
Two new MCP tools to transfer PPTX files between client and server without requiring
shared filesystem access:

- **`upload_pptx(filename, content_base64)`** – saves a base64-encoded PPTX file to
  `/app/pptx_files/` on the server; returns the `file_path` to use with `open_presentation`.
- **`download_pptx(file_path)`** – reads a PPTX file from the server and returns it
  as a base64-encoded string so the client can save it locally.

This mirrors the deployment topology: the server runs in Docker with
`/mnt/dockershare/powerpoint` mounted at `/app/pptx_files`, and the client (Claude)
has no direct access to that path.
