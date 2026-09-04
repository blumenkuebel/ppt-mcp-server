"""
File upload/download tools for PowerPoint MCP Server.
Allows transferring PPTX files via base64-encoded content.
"""
from typing import Dict, Optional
import os
import base64
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

PPT_FILES_PATH = "/app/pptx_files"


def register_file_tools(app: FastMCP):
    """Register file upload/download tools with the FastMCP app."""

    @app.tool(
        annotations=ToolAnnotations(title="Upload PPTX File"),
    )
    def upload_pptx(filename: str, content_base64: str) -> Dict:
        """Upload a PPTX file to the server by providing its base64-encoded content.

        Use this to transfer a file from the client to the server before opening it.
        The file is saved under the server's files directory and can then be opened
        with open_presentation using the returned file_path.
        """
        if not filename.endswith(".pptx"):
            filename += ".pptx"

        # Prevent directory traversal
        safe_name = os.path.basename(filename)
        dest = os.path.join(PPT_FILES_PATH, safe_name)
        os.makedirs(PPT_FILES_PATH, exist_ok=True)

        try:
            data = base64.b64decode(content_base64)
        except Exception as e:
            return {"error": f"Invalid base64 content: {e}"}

        with open(dest, "wb") as f:
            f.write(data)

        return {
            "message": f"File uploaded successfully.",
            "file_path": dest,
            "size_bytes": len(data),
        }

    @app.tool(
        annotations=ToolAnnotations(title="Download PPTX File", readOnlyHint=True),
    )
    def download_pptx(file_path: str) -> Dict:
        """Download a PPTX file from the server as base64-encoded content.

        Use this to retrieve a file after creating or modifying a presentation,
        so the client can save it locally.
        """
        if not os.path.isabs(file_path):
            file_path = os.path.join(PPT_FILES_PATH, file_path)

        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        with open(file_path, "rb") as f:
            data = f.read()

        return {
            "filename": os.path.basename(file_path),
            "content_base64": base64.b64encode(data).decode("utf-8"),
            "size_bytes": len(data),
        }
