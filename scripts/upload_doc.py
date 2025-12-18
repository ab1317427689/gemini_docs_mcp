#!/usr/bin/env python3
"""CLI script for manually uploading documents to the docs store.

Usage:
    uv run python scripts/upload_doc.py --id "langchain/llms.txt" --name "LangChain LLMs" --file ./langchain_llms.txt
"""

import argparse
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gemini_docs_mcp.docs import add_doc


def main() -> int:
    """Parse arguments and upload document."""
    parser = argparse.ArgumentParser(
        description="Upload a document to the docs store.",
        epilog='Example: uv run python scripts/upload_doc.py --id "langchain/llms.txt" --name "LangChain LLMs" --file ./langchain_llms.txt',
    )
    parser.add_argument(
        "--id",
        required=True,
        help='Document ID (e.g., "langchain/llms.txt")',
    )
    parser.add_argument(
        "--name",
        required=True,
        help='Display name (e.g., "LangChain LLMs")',
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to the local file to upload",
    )
    parser.add_argument(
        "--description",
        default="",
        help="Optional description for the document",
    )

    args = parser.parse_args()

    # Read the file content
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1

    try:
        content = file_path.read_text(encoding="utf-8")
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    # Upload the document
    doc_entry = add_doc(
        doc_id=args.id,
        name=args.name,
        content=content,
        description=args.description,
    )

    print("Document uploaded successfully!")
    print(f"  ID: {doc_entry['id']}")
    print(f"  Name: {doc_entry['name']}")
    print(f"  Path: {doc_entry['path']}")
    if doc_entry.get("description"):
        print(f"  Description: {doc_entry['description']}")
    print(f"  Updated: {doc_entry['updated_at']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
