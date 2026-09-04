# PowerPoint MCP Server

Based on [Office-PowerPoint-MCP-Server](https://github.com/GongRzhe/Office-PowerPoint-MCP-Server) by **GongRzhe** – all credit for the core implementation goes to the original author.

## Setup

```bash
./start_server.sh
```

The script creates a `.venv`, installs dependencies from `requirements.txt`, and starts the server on port **8001**.

## MCP Registration

```bash
# Docker / remote
claude mcp add --scope user --transport http ppt http://192.168.55.15:8001/mcp

# Local
claude mcp add --scope user --transport http ppt http://127.0.0.1:8001/mcp
```

## File Transfer

The server runs in Docker and **cannot access local file paths** (e.g. `/Users/…`). PPTX files must be uploaded via HTTP before they can be opened with MCP tools.

Files are stored in `/app/pptx_files` inside the container (mapped to `/mnt/dockershare/powerpoint`).

```bash
# Upload (required before open_presentation)
curl -s -H "X-API-Key: $KEY" -F "file=@deck.pptx" http://192.168.55.15:8001/upload
# → returns JSON with "file_path": "/app/pptx_files/deck.pptx"

# Download
curl -H "X-API-Key: $KEY" http://192.168.55.15:8001/download/deck.pptx -o deck.pptx

# List files
curl -H "X-API-Key: $KEY" http://192.168.55.15:8001/files
```

### Workflow for agents

1. Upload the local file via `curl -s -F "file=@/path/to/file.pptx" http://<server-host>:8001/upload`
2. Use the returned `file_path` with `open_presentation(file_path="/app/pptx_files/file.pptx")`

## API Key

Set `MCP_API_KEY` in the container environment to require `X-API-Key` on all `/upload`, `/download`, and `/files` requests. If unset, endpoints are unprotected.

See `docker-compose.yml` for the placeholder and `CHANGELOG.md` for security notes.

## License

MIT
