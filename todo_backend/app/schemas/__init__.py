"""
Schemas package initializer for the Todo backend.

This module exposes the Todo-related Marshmallow schemas for convenient imports
throughout the application.
"""

from .todo import (
    TodoSchema,
    TodoCreateSchema,
    TodoUpdateSchema,
    PaginationMetaSchema,
)

__all__ = [
    "TodoSchema",
    "TodoCreateSchema",
    "TodoUpdateSchema",
    "PaginationMetaSchema",
]
