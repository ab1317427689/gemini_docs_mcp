"""Gemini Docs MCP Server using FastMCP."""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import TextContent

# Load .env from project root
load_dotenv(Path(__file__).parent.parent.parent / ".env")

from .agent import query_docs
from .docs import get_all_docs, get_doc_content

# Disable DNS rebinding protection for remote access
transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)

# Create FastMCP server
mcp = FastMCP("gemini-docs-mcp", transport_security=transport_security)


@mcp.tool()
def get_all_resources() -> list[TextContent]:
    """Get a list of all available documents with their id, name, and description."""
    docs = get_all_docs()
    return [TextContent(type="text", text=json.dumps(docs, indent=2))]


@mcp.tool()
def get_docs_info(doc_id: str, prompt: str) -> list[TextContent]:
    """Get information from a specific document by querying it with a prompt.

    Args:
        doc_id: The ID of the document to query
        prompt: The prompt/question to ask about the document
    """
    if not doc_id or not prompt:
        return [TextContent(type="text", text="Error: doc_id and prompt are required")]

    content = get_doc_content(doc_id)
    if content is None:
        return [
            TextContent(
                type="text", text=f"Error: Document with id '{doc_id}' not found"
            )
        ]

    return [TextContent(type="text", text=query_docs(content, prompt))]


def main():
    """Main entry point."""
    # Check for --http flag
    if "--http" in sys.argv:
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = 8000
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
