"""
Models package initializer for the Todo backend.

This package currently exposes the TodoStore, which provides a thread-safe
in-memory or file-backed JSON persistence layer for managing Todo items.
"""

from .todo_store import TodoStore

__all__ = ["TodoStore"]
