import json
from pathlib import Path

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Load .env from project root
load_dotenv(Path(__file__).parent.parent.parent / ".env")

from .agent import query_docs
from .docs import get_all_docs, get_doc_content

server = Server("gemini-docs-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_all_resources",
            description="Get a list of all available documents with their id, name, and description",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_docs_info",
            description="Get information from a specific document by querying it with a prompt",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "The ID of the document to query",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "The prompt/question to ask about the document",
                    },
                },
                "required": ["doc_id", "prompt"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "get_all_resources":
        docs = get_all_docs()
        result = json.dumps(docs, indent=2)
        return [TextContent(type="text", text=result)]

    elif name == "get_docs_info":
        doc_id = arguments.get("doc_id")
        prompt = arguments.get("prompt")

        if not doc_id or not prompt:
            return [
                TextContent(type="text", text="Error: doc_id and prompt are required")
            ]

        content = get_doc_content(doc_id)
        if content is None:
            return [
                TextContent(
                    type="text", text=f"Error: Document with id '{doc_id}' not found"
                )
            ]

        answer = query_docs(content, prompt)
        return [TextContent(type="text", text=answer)]

    else:
        return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]


async def run_server():
    """Run the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main():
    """Main entry point."""
    import asyncio

    asyncio.run(run_server())


if __name__ == "__main__":
    main()
