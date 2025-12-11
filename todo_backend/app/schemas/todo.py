"""
Todo Marshmallow schemas compatible with flask-smorest.

These schemas define the structure for:
- Full Todo representation (TodoSchema)
- Create payload (TodoCreateSchema)
- Update payload (TodoUpdateSchema)
- Optional pagination metadata (PaginationMetaSchema)

Notes:
- Fields id, created_at, updated_at are dump_only since they are server-managed.
- Validate priority range when present (1..5).
- Use ISO8601 string for date-time fields for OpenAPI compatibility.
"""

from marshmallow import Schema, fields, validate, EXCLUDE


class PaginationMetaSchema(Schema):
    """Pagination metadata for list responses."""
    # PUBLIC_INTERFACE
    page = fields.Integer(required=True, metadata={"description": "Current page number", "example": 1})
    # PUBLIC_INTERFACE
    per_page = fields.Integer(required=True, metadata={"description": "Items per page", "example": 20})
    # PUBLIC_INTERFACE
    total = fields.Integer(required=True, metadata={"description": "Total number of items", "example": 125})
    # PUBLIC_INTERFACE
    pages = fields.Integer(required=True, metadata={"description": "Total number of pages", "example": 7})


class TodoSchema(Schema):
    """Full Todo representation for responses and serialization."""
    # PUBLIC_INTERFACE
    id = fields.String(dump_only=True, metadata={"description": "Todo unique identifier"})
    # PUBLIC_INTERFACE
    title = fields.String(required=True, metadata={"description": "Short title of the todo", "example": "Buy groceries"})
    # PUBLIC_INTERFACE
    description = fields.String(allow_none=True, load_default=None, metadata={"description": "Detailed description", "example": "Milk, eggs, bread"})
    # PUBLIC_INTERFACE
    completed = fields.Boolean(load_default=False, metadata={"description": "Completion status", "example": False})
    # PUBLIC_INTERFACE
    created_at = fields.String(dump_only=True, metadata={"description": "Creation timestamp in ISO8601", "example": "2024-01-01T10:00:00Z"})
    # PUBLIC_INTERFACE
    updated_at = fields.String(dump_only=True, metadata={"description": "Last update timestamp in ISO8601", "example": "2024-01-01T11:00:00Z"})
    # PUBLIC_INTERFACE
    due_date = fields.String(allow_none=True, load_default=None, metadata={"description": "Due date in ISO8601", "example": "2024-01-15T23:59:59Z"})
    # PUBLIC_INTERFACE
    priority = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=1, max=5),
        load_default=None,
        metadata={"description": "Priority (1=lowest .. 5=highest)", "example": 3},
    )


class TodoCreateSchema(Schema):
    """Schema for Todo creation payloads."""
    # PUBLIC_INTERFACE
    title = fields.String(required=True, metadata={"description": "Short title of the todo"})
    # PUBLIC_INTERFACE
    description = fields.String(required=False, allow_none=True, load_default=None, metadata={"description": "Detailed description"})
    # PUBLIC_INTERFACE
    due_date = fields.String(required=False, allow_none=True, load_default=None, metadata={"description": "Due date in ISO8601"})
    # PUBLIC_INTERFACE
    priority = fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.Range(min=1, max=5),
        load_default=None,
        metadata={"description": "Priority (1..5)"},
    )
    # completed should not be provided by client; if sent, it will be ignored by view if not bound.
    # Do not include completed here so @blp.arguments enforces schema.


class TodoUpdateSchema(Schema):
    """Schema for partial updates to a Todo.

    All fields are optional to support PATCH-like updates. Unknown fields are ignored.
    """
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields gracefully

    # PUBLIC_INTERFACE
    title = fields.String(required=False, metadata={"description": "New title"})
    # PUBLIC_INTERFACE
    description = fields.String(required=False, allow_none=True, metadata={"description": "New description"})
    # PUBLIC_INTERFACE
    completed = fields.Boolean(required=False, metadata={"description": "Toggle completion status"})
    # PUBLIC_INTERFACE
    due_date = fields.String(required=False, allow_none=True, metadata={"description": "New due date ISO8601"})
    # PUBLIC_INTERFACE
    priority = fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.Range(min=1, max=5),
        metadata={"description": "New priority (1..5)"},
    )
