"""Gemini Docs MCP Server with Admin Management UI."""

import json
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.datastructures import UploadFile as StarletteUploadFile

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Adjust path for imports when running directly
sys.path.insert(0, str(PROJECT_ROOT))
from src.gemini_docs_mcp.agent import query_docs
from src.gemini_docs_mcp.docs import get_all_docs, get_doc_content, add_doc, delete_doc

# Configuration
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

# Create FastMCP server
transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)
mcp = FastMCP("gemini-docs-mcp", transport_security=transport_security)


@mcp.tool(structured_output=False)
def get_all_resources() -> str:
    """Get a list of all available documents with their id, name, and description."""
    docs = get_all_docs()
    return json.dumps(docs, indent=2)


@mcp.tool(structured_output=False)
async def get_docs_info(doc_id: str, prompt: str) -> str:
    """Get information from a specific document by querying it with a prompt."""
    if not doc_id or not prompt:
        return "Error: doc_id and prompt are required"
    content = get_doc_content(doc_id)
    if content is None:
        return f"Error: Document with id '{doc_id}' not found"
    return await query_docs(content, prompt)


# --- Admin API & UI Implementation using custom_route ---


def verify_admin(request: Request) -> bool:
    """Check if the X-Admin-Password header matches."""
    auth_header = request.headers.get("X-Admin-Password")
    return auth_header == ADMIN_PASSWORD


@mcp.custom_route("/admin", methods=["GET"])
async def admin_page(request: Request) -> Response:
    """Return the admin management page."""
    admin_html_path = Path(__file__).parent / "admin.html"
    if not admin_html_path.exists():
        return HTMLResponse(content="<h1>Admin Page not found</h1>", status_code=404)
    return HTMLResponse(content=admin_html_path.read_text(encoding="utf-8"))


@mcp.custom_route("/api/docs", methods=["GET"])
async def api_get_docs(request: Request) -> Response:
    """List all documents."""
    if not verify_admin(request):
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    return JSONResponse({"docs": get_all_docs()})


@mcp.custom_route("/api/upload", methods=["POST"])
async def api_upload_doc(request: Request) -> Response:
    """Handle document upload from web UI."""
    if not verify_admin(request):
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    try:
        form = await request.form()
        file_field = form.get("file")
        doc_id_field = form.get("doc_id")
        name_field = form.get("name")
        description_field = form.get("description", "")

        if (
            not isinstance(file_field, StarletteUploadFile)
            or not doc_id_field
            or not name_field
        ):
            return JSONResponse(
                {"detail": "Missing required fields or invalid file"}, status_code=400
            )

        doc_id = str(doc_id_field)
        name = str(name_field)
        description = str(description_field)

        content = await file_field.read()
        text_content = content.decode("utf-8")
        doc_entry = add_doc(doc_id, name, text_content, description)
        return JSONResponse({"status": "success", "doc": doc_entry})
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


@mcp.custom_route("/api/docs/{doc_id:path}", methods=["DELETE"])
async def api_delete_doc(request: Request) -> Response:
    """Handle document deletion from web UI."""
    if not verify_admin(request):
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    # Path params are in request.path_params
    doc_id = request.path_params.get("doc_id")
    if not doc_id:
        return JSONResponse({"detail": "Missing doc_id"}, status_code=400)

    success = delete_doc(doc_id)
    if not success:
        return JSONResponse({"detail": "Document not found"}, status_code=404)
    return JSONResponse({"status": "success"})


def main():
    """Main entry point."""
    host = "0.0.0.0"
    port = 8000

    if "--http" in sys.argv or True:
        print(f"Starting Gemini Docs MCP with Admin UI at http://{host}:{port}/admin")
        print(f"MCP endpoint at http://{host}:{port}/mcp")
        # FastMCP.run() handles the lifecycle and initializes the task group
        mcp.settings.host = host
        mcp.settings.port = port
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
