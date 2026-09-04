"""
File upload/download HTTP endpoints for PowerPoint MCP Server.

Registers two custom HTTP routes on the FastMCP app (outside MCP protocol):
  POST /upload          – multipart/form-data, field "file", optional field "filename"
  GET  /download/<name> – streams the file back as application/octet-stream

Usage from Claude (via Bash/curl):
  # Upload
  curl -F "file=@/path/to/deck.pptx" http://192.168.55.15:8001/upload

  # Download
  curl http://192.168.55.15:8001/download/deck.pptx -o deck.pptx
"""
import os
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse, Response

PPT_FILES_PATH = "/app/pptx_files"


def register_file_routes(app: FastMCP):
    """Register /upload and /download HTTP routes on the FastMCP app."""

    @app.custom_route("/upload", methods=["POST"])
    async def upload(request: Request) -> Response:
        form = await request.form()
        file = form.get("file")
        if file is None:
            return JSONResponse({"error": "Missing 'file' field"}, status_code=400)

        filename = form.get("filename") or file.filename or "upload.pptx"
        if not str(filename).endswith(".pptx"):
            filename = str(filename) + ".pptx"
        safe_name = os.path.basename(filename)

        os.makedirs(PPT_FILES_PATH, exist_ok=True)
        dest = os.path.join(PPT_FILES_PATH, safe_name)

        data = await file.read()
        with open(dest, "wb") as f:
            f.write(data)

        return JSONResponse({
            "message": "File uploaded successfully.",
            "file_path": dest,
            "filename": safe_name,
            "size_bytes": len(data),
        })

    @app.custom_route("/download/{filename}", methods=["GET"])
    async def download(request: Request) -> Response:
        filename = request.path_params["filename"]
        safe_name = os.path.basename(filename)
        file_path = os.path.join(PPT_FILES_PATH, safe_name)

        if not os.path.exists(file_path):
            return JSONResponse({"error": f"File not found: {safe_name}"}, status_code=404)

        return FileResponse(
            file_path,
            media_type="application/octet-stream",
            filename=safe_name,
        )

    @app.custom_route("/files", methods=["GET"])
    async def list_files(request: Request) -> Response:
        os.makedirs(PPT_FILES_PATH, exist_ok=True)
        files = [
            {"filename": f, "size_bytes": os.path.getsize(os.path.join(PPT_FILES_PATH, f))}
            for f in sorted(os.listdir(PPT_FILES_PATH))
            if f.endswith(".pptx")
        ]
        return JSONResponse({"files": files})
