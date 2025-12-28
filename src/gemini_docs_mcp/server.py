"""Gemini Docs MCP Server with Admin Management UI."""

import json
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Header, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
import uvicorn

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
def get_docs_info(doc_id: str, prompt: str) -> str:
    """Get information from a specific document by querying it with a prompt."""
    if not doc_id or not prompt:
        return "Error: doc_id and prompt are required"
    content = get_doc_content(doc_id)
    if content is None:
        return f"Error: Document with id '{doc_id}' not found"
    return query_docs(content, prompt)


# --- Admin API & UI Implementation ---
app = FastAPI(title="Gemini Docs MCP Admin")

# Integrate MCP routes into our main FastAPI app
mcp_app = mcp.streamable_http_app()
app.router.routes.extend(mcp_app.routes)


async def verify_admin(x_admin_password: Optional[str] = Header(None)):
    """Simple password verification dependency."""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    """Return the admin management page."""
    admin_html_path = Path(__file__).parent / "admin.html"
    if not admin_html_path.exists():
        return HTMLResponse(content="<h1>Admin Page not found</h1>", status_code=404)
    return admin_html_path.read_text(encoding="utf-8")


@app.get("/api/docs")
async def api_get_docs(_: bool = Depends(verify_admin)):
    """List all documents."""
    return {"docs": get_all_docs()}


@app.post("/api/upload")
async def api_upload_doc(
    file: UploadFile = File(...),
    doc_id: str = Form(...),
    name: str = Form(...),
    description: str = Form(""),
    _: bool = Depends(verify_admin),
):
    """Handle document upload from web UI."""
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        doc_entry = add_doc(doc_id, name, text_content, description)
        return {"status": "success", "doc": doc_entry}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/docs/{doc_id:path}")
async def api_delete_doc(doc_id: str, _: bool = Depends(verify_admin)):
    """Handle document deletion from web UI."""
    success = delete_doc(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success"}


def main():
    """Main entry point."""
    host = "0.0.0.0"
    port = 8000

    if "--http" in sys.argv:
        print(f"Starting Gemini Docs MCP with Admin UI at http://{host}:{port}/admin")
        print(f"MCP endpoint at http://{host}:{port}/mcp")
        uvicorn.run(app, host=host, port=port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
