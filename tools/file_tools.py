"""
File upload/download HTTP endpoints and MCP upload tool for PowerPoint MCP Server.

Registers custom HTTP routes on the FastMCP app (outside MCP protocol):
  POST /upload          – multipart/form-data, field "file", optional field "filename"
  GET  /download/<name> – streams the file back as application/octet-stream
  GET  /files           – lists available PPTX files

Also registers an MCP tool:
  upload_pptx(local_path)  – reads a local file and uploads it to the server

Optional API key protection via environment variable:
  MCP_API_KEY=secret ./start_server.sh

  curl -H "X-API-Key: secret" -F "file=@deck.pptx" http://192.168.55.15:8001/upload
  curl -H "X-API-Key: secret" http://192.168.55.15:8001/download/deck.pptx -o deck.pptx

If MCP_API_KEY is not set, the endpoints are unprotected.
"""
import os
import httpx
from typing import Dict, Optional
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse, Response

PPT_FILES_PATH = "/app/pptx_files"


def _upload_local_file(local_path: str, filename: Optional[str] = None) -> Dict:
    """Copy a local file into PPT_FILES_PATH. Returns same dict as upload_pptx tool."""
    if not os.path.exists(local_path):
        return {"error": f"File not found: {local_path}"}

    upload_filename = filename or os.path.basename(local_path)
    if not str(upload_filename).endswith(".pptx"):
        upload_filename = str(upload_filename) + ".pptx"
    safe_name = os.path.basename(upload_filename)

    os.makedirs(PPT_FILES_PATH, exist_ok=True)
    dest = os.path.join(PPT_FILES_PATH, safe_name)

    try:
        with open(local_path, "rb") as f:
            file_data = f.read()
        with open(dest, "wb") as f:
            f.write(file_data)
        return {
            "file_path": dest,
            "filename": safe_name,
            "size_bytes": len(file_data),
        }
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}


def _check_api_key(request: Request) -> bool:
    """Return True if the request is authorized (or no key is configured)."""
    required = os.environ.get("MCP_API_KEY", "")
    if not required:
        return True
    return request.headers.get("X-API-Key", "") == required


def register_file_routes(app: FastMCP):
    """Register /upload, /download, and /files HTTP routes on the FastMCP app."""

    @app.custom_route("/upload", methods=["POST"])
    async def upload(request: Request) -> Response:
        if not _check_api_key(request):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

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
        if not _check_api_key(request):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

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
        if not _check_api_key(request):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

        os.makedirs(PPT_FILES_PATH, exist_ok=True)
        files = [
            {"filename": f, "size_bytes": os.path.getsize(os.path.join(PPT_FILES_PATH, f))}
            for f in sorted(os.listdir(PPT_FILES_PATH))
            if f.endswith(".pptx")
        ]
        return JSONResponse({"files": files})

    @app.tool()
    def upload_pptx(local_path: str, filename: Optional[str] = None) -> Dict:
        """Upload a local PPTX file to the server so it can be used with open_presentation.

        Use this when the file lives on the local machine (e.g. /Users/…/deck.pptx).
        Returns file_path — the server-side path to pass to open_presentation.
        Note: open_presentation also accepts local paths and uploads automatically.
        """
        return _upload_local_file(local_path, filename)
