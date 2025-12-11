"""
Thread-safe Todo store with optional file-backed JSON persistence.

This module defines the TodoStore which provides CRUD operations, list with
filtering, sorting, and pagination for todo items. The store can operate in:
- file-backed mode (default): persists todos to ./data/todos.json (relative to container root)
- in-memory mode: does not persist; useful for testing

Persistence format: a JSON object with `todos` as a list of items.

Each todo item fields:
- id: string (uuid4)
- title: string
- description: string | None
- completed: bool
- created_at: ISO8601 UTC string
- updated_at: ISO8601 UTC string
- due_date: ISO8601 UTC string | None
- priority: int 1..5 | None
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4
from datetime import datetime, timezone


def _utc_now_iso() -> str:
    """Return current UTC time as ISO8601 string with 'Z' suffix."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_lower(s: Optional[str]) -> str:
    return (s or "").lower()


class TodoStore:
    # PUBLIC_INTERFACE
    def __init__(self, persistence: str = "file", data_dir: Optional[str] = None, file_name: str = "todos.json"):
        """Initialize the TodoStore.

        PUBLIC_INTERFACE
        :param persistence: "file" for file-backed JSON persistence (default), "memory" for in-memory only.
        :param data_dir: Base directory for data when using file persistence. Defaults to "./data".
        :param file_name: File name for persistence when using file persistence. Defaults to "todos.json".
        """
        self._lock = Lock()
        self._persistence = persistence.lower().strip()
        self._todos: List[Dict[str, Any]] = []

        # Setup file path if using file persistence
        if self._persistence == "file":
            base_dir = data_dir or "./data"
            self._data_dir = Path(base_dir)
            self._data_dir.mkdir(parents=True, exist_ok=True)
            self._file_path = self._data_dir / file_name
            self._load_from_disk()
        elif self._persistence == "memory":
            self._data_dir = None
            self._file_path = None
        else:
            raise ValueError("Unsupported persistence mode. Use 'file' or 'memory'.")

    def _load_from_disk(self) -> None:
        """Load todos from disk if present."""
        with self._lock:
            if self._file_path and self._file_path.exists():
                try:
                    raw = self._file_path.read_text(encoding="utf-8")
                    data = json.loads(raw or "{}")
                    self._todos = list(data.get("todos", []))
                except Exception:
                    # If file is corrupt, fallback to empty list but do not crash the app.
                    self._todos = []
            else:
                self._todos = []
                # Ensure file exists with empty structure
                self._persist_locked()

    def _persist_locked(self) -> None:
        """Persist current todos to disk. Must be called with lock held."""
        if self._persistence != "file" or not self._file_path:
            return
        payload = {"todos": self._todos}
        tmp_path = str(self._file_path) + ".tmp"
        # Write atomically
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self._file_path)

    # PUBLIC_INTERFACE
    def list(
        self,
        search: Optional[str] = None,
        completed: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """List todos with optional filtering, sorting and pagination.

        PUBLIC_INTERFACE
        :param search: Case-insensitive substring to match against title or description.
        :param completed: If set, filter by completion status.
        :param sort_by: One of 'created_at', 'updated_at', 'title', 'priority'.
        :param sort_dir: 'asc' or 'desc'.
        :param page: Page number starting at 1.
        :param per_page: Number of items per page.
        :return: (items, meta) where meta = {page, per_page, total, pages}
        """
        with self._lock:
            items = list(self._todos)

        # Filtering
        if search:
            q = _safe_lower(search)
            items = [
                t
                for t in items
                if q in _safe_lower(t.get("title")) or q in _safe_lower(t.get("description"))
            ]
        if completed is not None:
            items = [t for t in items if bool(t.get("completed", False)) == completed]

        # Sorting
        allowed_sort = {"created_at", "updated_at", "title", "priority"}
        if sort_by not in allowed_sort:
            sort_by = "created_at"
        reverse = (sort_dir or "desc").lower() == "desc"

        def sort_key(todo: Dict[str, Any]):
            val = todo.get(sort_by)
            # Normalize missing values for consistent sorting
            if sort_by in {"created_at", "updated_at"}:
                return val or ""
            if sort_by == "title":
                return (val or "").lower()
            if sort_by == "priority":
                # None priorities should sort last in ascending order
                return (val if val is not None else float("inf"))
            return val

        items.sort(key=sort_key, reverse=reverse)

        # Pagination
        page = max(1, int(page or 1))
        per_page = max(1, int(per_page or 20))
        total = len(items)
        pages = (total + per_page - 1) // per_page if total > 0 else 1
        start = (page - 1) * per_page
        end = start + per_page
        page_items = items[start:end]

        meta = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
        }
        return page_items, meta

    # PUBLIC_INTERFACE
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new todo item.

        PUBLIC_INTERFACE
        :param data: Dict with keys title, description?, due_date?, priority?
        :return: The created todo object.
        """
        now = _utc_now_iso()
        todo: Dict[str, Any] = {
            "id": str(uuid4()),
            "title": (data.get("title") or "").strip(),
            "description": data.get("description"),
            "completed": bool(data.get("completed", False)),
            "created_at": now,
            "updated_at": now,
            "due_date": data.get("due_date"),
            "priority": data.get("priority"),
        }

        with self._lock:
            self._todos.append(todo)
            self._persist_locked()
            # return a copy to prevent external mutation
            return dict(todo)

    # PUBLIC_INTERFACE
    def get(self, todo_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a todo by id.

        PUBLIC_INTERFACE
        :param todo_id: The id of the todo.
        :return: The todo dict or None if not found.
        """
        with self._lock:
            for t in self._todos:
                if t.get("id") == todo_id:
                    return dict(t)
        return None

    # PUBLIC_INTERFACE
    def update(self, todo_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update fields of a todo.

        PUBLIC_INTERFACE
        :param todo_id: The id of the todo.
        :param data: Fields to update (title, description, completed, due_date, priority).
        :return: Updated todo or None if not found.
        """
        with self._lock:
            for idx, t in enumerate(self._todos):
                if t.get("id") == todo_id:
                    updated = dict(t)  # work on a copy
                    # Only update provided fields
                    if "title" in data and data["title"] is not None:
                        updated["title"] = str(data["title"]).strip()
                    if "description" in data:
                        updated["description"] = data["description"]
                    if "completed" in data and data["completed"] is not None:
                        updated["completed"] = bool(data["completed"])
                    if "due_date" in data:
                        updated["due_date"] = data["due_date"]
                    if "priority" in data:
                        updated["priority"] = data["priority"]
                    updated["updated_at"] = _utc_now_iso()

                    self._todos[idx] = updated
                    self._persist_locked()
                    return dict(updated)
        return None

    # PUBLIC_INTERFACE
    def toggle(self, todo_id: str) -> Optional[Dict[str, Any]]:
        """Toggle the completion status of a todo.

        PUBLIC_INTERFACE
        :param todo_id: The id of the todo.
        :return: Updated todo or None if not found.
        """
        with self._lock:
            for idx, t in enumerate(self._todos):
                if t.get("id") == todo_id:
                    updated = dict(t)
                    updated["completed"] = not bool(updated.get("completed", False))
                    updated["updated_at"] = _utc_now_iso()
                    self._todos[idx] = updated
                    self._persist_locked()
                    return dict(updated)
        return None

    # PUBLIC_INTERFACE
    def delete(self, todo_id: str) -> bool:
        """Delete a todo by id.

        PUBLIC_INTERFACE
        :param todo_id: The id of the todo.
        :return: True if deleted, False otherwise.
        """
        with self._lock:
            for idx, t in enumerate(self._todos):
                if t.get("id") == todo_id:
                    del self._todos[idx]
                    self._persist_locked()
                    return True
        return False
