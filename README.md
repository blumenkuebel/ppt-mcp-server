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

PPTX files live in `/app/pptx_files` inside the container (mapped to `/mnt/dockershare/powerpoint`).

```bash
# Upload
curl -H "X-API-Key: $KEY" -F "file=@deck.pptx" http://192.168.55.15:8001/upload

# Download
curl -H "X-API-Key: $KEY" http://192.168.55.15:8001/download/deck.pptx -o deck.pptx

# List files
curl -H "X-API-Key: $KEY" http://192.168.55.15:8001/files
```

## API Key

Set `MCP_API_KEY` in the container environment to require `X-API-Key` on all `/upload`, `/download`, and `/files` requests. If unset, endpoints are unprotected.

See `docker-compose.yml` for the placeholder and `CHANGELOG.md` for security notes.

## License

MIT
