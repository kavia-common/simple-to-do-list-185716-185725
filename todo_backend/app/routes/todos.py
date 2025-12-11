from flask_smorest import Blueprint
from flask.views import MethodView
from flask import current_app, request, url_for, make_response
from typing import Any, Dict, Optional
from ..schemas import TodoSchema, TodoCreateSchema, TodoUpdateSchema, PaginationMetaSchema

# PUBLIC_INTERFACE
blp = Blueprint(
    "Todos",
    "todos",
    url_prefix="/todos",
    description="CRUD operations for Todo items",
)

def _store():
    """Resolve the TodoStore from app context."""
    store = current_app.extensions.get("todo_store") or current_app.config.get("TODO_STORE")
    if store is None:
        # This should not happen if app/__init__.py is configured properly
        raise RuntimeError("TodoStore is not configured on the Flask application")
    return store


@blp.route("/")
class TodosCollection(MethodView):
    """
    PUBLIC_INTERFACE
    List and create Todo items.

    GET supports filtering, sorting, and pagination via query params.
    POST creates a new Todo.
    """

    @blp.response(
        200,
        description="List todos with pagination and optional filters",
        example={"items": [], "meta": {"page": 1, "per_page": 20, "total": 0, "pages": 1}},
    )
    def get(self):
        """
        Get a paginated list of todos.

        Query parameters:
        - search: string, optional
        - completed: bool, optional (true/false/1/0/yes/no)
        - sort_by: created_at|updated_at|title|priority (default: created_at)
        - sort_dir: asc|desc (default: desc)
        - page: int (default: 1)
        - per_page: int (default: 20)

        Returns JSON object:
        {
          "items": [Todo],
          "meta": PaginationMeta
        }
        """
        args = request.args
        search = args.get("search")
        completed_param = args.get("completed")
        completed: Optional[bool] = None
        if completed_param is not None:
            completed = str(completed_param).lower() in ("1", "true", "yes", "y")

        sort_by = args.get("sort_by", "created_at")
        sort_dir = args.get("sort_dir", "desc")
        # Best-effort conversion with sane defaults
        try:
            page = int(args.get("page", 1))
        except Exception:
            page = 1
        try:
            per_page = int(args.get("per_page", 20))
        except Exception:
            per_page = 20

        items, meta = _store().list(
            search=search,
            completed=completed,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            per_page=per_page,
        )
        # Use explicit schema dumping to ensure OpenAPI compatible shape
        items_data = TodoSchema(many=True).dump(items)
        meta_data = PaginationMetaSchema().dump(meta)
        return {"items": items_data, "meta": meta_data}, 200

    @blp.arguments(TodoCreateSchema, location="json")
    @blp.response(201, schema=TodoSchema, description="Created todo")
    def post(self, payload: Dict[str, Any]):
        """
        Create a new todo.

        Body: TodoCreateSchema
        Returns: the created Todo with 201 Created and Location header pointing to the resource.
        """
        created = _store().create(payload)
        # Set Location header to the new resource URL
        location = url_for("todos.TodoItem", todo_id=created["id"], _external=False)
        resp = make_response(created, 201)
        resp.headers["Location"] = location
        return resp


@blp.route("/<string:todo_id>")
class TodoItem(MethodView):
    """
    PUBLIC_INTERFACE
    Retrieve, update, and delete a single Todo item by id.
    """

    @blp.response(200, schema=TodoSchema, description="Retrieved todo")
    def get(self, todo_id: str):
        """
        Get a todo by id.

        Path params:
        - todo_id: string

        Returns: Todo or 404 if not found
        """
        item = _store().get(todo_id)
        if not item:
            # flask-smorest will keep status and body intact
            return {"message": "Not found"}, 404
        return item, 200

    # Treat PUT as idempotent update; our store.update supports partial fields,
    # which is acceptable for this simple backend.
    @blp.arguments(TodoUpdateSchema, location="json")
    @blp.response(200, schema=TodoSchema, description="Updated todo")
    def put(self, payload: Dict[str, Any], todo_id: str):
        """
        Update a todo (idempotent). Unknown fields are ignored.

        Body: TodoUpdateSchema
        Returns: Updated Todo or 404 if not found
        """
        updated = _store().update(todo_id, payload)
        if not updated:
            return {"message": "Not found"}, 404
        return updated, 200

    @blp.arguments(TodoUpdateSchema, location="json")
    @blp.response(200, schema=TodoSchema, description="Partially updated todo")
    def patch(self, payload: Dict[str, Any], todo_id: str):
        """
        Partially update a todo.

        Path params:
        - todo_id: string

        Body: TodoUpdateSchema
        Returns: Updated Todo or 404 if not found
        """
        updated = _store().update(todo_id, payload)
        if not updated:
            return {"message": "Not found"}, 404
        return updated, 200

    @blp.response(204, description="Todo deleted")
    def delete(self, todo_id: str):
        """
        Delete a todo by id.

        Path params:
        - todo_id: string

        Returns: 204 on success, 404 if not found
        """
        ok = _store().delete(todo_id)
        if not ok:
            return {"message": "Not found"}, 404
        # Return empty body with 204 status
        return "", 204


@blp.route("/<string:todo_id>/toggle")
class TodoToggle(MethodView):
    """
    PUBLIC_INTERFACE
    Toggle completion status for a Todo item.
    """

    @blp.response(200, schema=TodoSchema, description="Toggled todo completion state")
    def patch(self, todo_id: str):
        """
        Toggle the completion status of a todo.

        Path params:
        - todo_id: string

        Returns: Updated Todo or 404 if not found
        """
        updated = _store().toggle(todo_id)
        if not updated:
            return {"message": "Not found"}, 404
        return updated, 200
