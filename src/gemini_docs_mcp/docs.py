"""Document storage and retrieval module."""

import json
from datetime import datetime, timezone
from pathlib import Path


def _get_project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent.parent


DOCS_DIR = _get_project_root() / "docs"
INDEX_FILE = DOCS_DIR / "index.json"


def get_docs_dir() -> Path:
    """Return the docs directory path."""
    return DOCS_DIR


def get_index_path() -> Path:
    """Return the index.json path."""
    return INDEX_FILE


def load_index() -> dict:
    """Load and return index.json content, create empty structure if not exists."""
    if not INDEX_FILE.exists():
        return {"docs": []}

    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"docs": []}


def save_index(data: dict) -> None:
    """Save index data to index.json."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_all_docs() -> list[dict]:
    """Return list of all docs from index."""
    index = load_index()
    return index.get("docs", [])


def get_doc_content(doc_id: str) -> str | None:
    """Read and return full content of a doc file by its id (which is also the path)."""
    doc_path = DOCS_DIR / doc_id

    if not doc_path.exists():
        return None

    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            return f.read()
    except IOError:
        return None


def add_doc(doc_id: str, name: str, content: str, description: str = "") -> dict:
    """Add a new doc - save content to file, update index, return the doc entry."""
    doc_path = DOCS_DIR / doc_id

    # Ensure parent directories exist
    doc_path.parent.mkdir(parents=True, exist_ok=True)

    # Write content to file
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Create doc entry
    doc_entry = {
        "id": doc_id,
        "name": name,
        "description": description,
        "path": doc_id,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # Update index
    index = load_index()

    # Check if doc already exists and update it, otherwise append
    existing_index = next(
        (i for i, doc in enumerate(index["docs"]) if doc["id"] == doc_id), None
    )

    if existing_index is not None:
        index["docs"][existing_index] = doc_entry
    else:
        index["docs"].append(doc_entry)

    save_index(index)

    return doc_entry


def delete_doc(doc_id: str) -> bool:
    """Delete a doc - remove file and update index."""
    index = load_index()

    # Check if doc exists in index
    docs = index.get("docs", [])
    doc_to_delete = next((doc for doc in docs if doc["id"] == doc_id), None)

    if not doc_to_delete:
        return False

    # Remove from index
    index["docs"] = [doc for doc in docs if doc["id"] != doc_id]
    save_index(index)

    # Delete the physical file
    doc_path = DOCS_DIR / doc_id
    if doc_path.exists():
        try:
            doc_path.unlink()

            # Clean up empty parent directories up to DOCS_DIR
            parent = doc_path.parent
            while parent != DOCS_DIR and parent.is_dir() and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent
        except OSError:
            pass

    return True
