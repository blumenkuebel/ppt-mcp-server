"""
File upload/download HTTP endpoints for PowerPoint MCP Server.

Registers custom HTTP routes on the FastMCP app (outside MCP protocol):
  POST /upload          – multipart/form-data, field "file", optional field "filename"
  GET  /download/<name> – streams the file back as application/octet-stream
  GET  /files           – lists available PPTX files

Optional API key protection via environment variable:
  MCP_API_KEY=secret ./start_server.sh

  curl -H "X-API-Key: secret" -F "file=@deck.pptx" http://<server-host>:8001/upload
  curl -H "X-API-Key: secret" http://<server-host>:8001/download/deck.pptx -o deck.pptx

If MCP_API_KEY is not set, the endpoints are unprotected.
"""
import os
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse, Response

PPT_FILES_PATH = "/app/pptx_files"


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

    @app.custom_route("/files/{filename}", methods=["DELETE"])
    async def delete_file(request: Request) -> Response:
        if not _check_api_key(request):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

        safe_name = os.path.basename(request.path_params["filename"])
        file_path = os.path.join(PPT_FILES_PATH, safe_name)

        if not os.path.exists(file_path):
            return JSONResponse({"error": f"File not found: {safe_name}"}, status_code=404)

        os.remove(file_path)
        return JSONResponse({"message": f"Deleted {safe_name}"})

    @app.custom_route("/files", methods=["DELETE"])
    async def delete_all_files(request: Request) -> Response:
        if not _check_api_key(request):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

        os.makedirs(PPT_FILES_PATH, exist_ok=True)
        deleted = []
        for f in os.listdir(PPT_FILES_PATH):
            if f.endswith(".pptx"):
                os.remove(os.path.join(PPT_FILES_PATH, f))
                deleted.append(f)
        return JSONResponse({"message": f"Deleted {len(deleted)} file(s)", "deleted": deleted})
