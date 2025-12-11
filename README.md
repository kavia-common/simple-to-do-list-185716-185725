# simple-to-do-list-185716-185725

Backend (Flask) exposes:
- Swagger UI: /docs
- Live OpenAPI JSON: /openapi.json
- Export current OpenAPI to file: /docs/export

Verifying OpenAPI and Todos endpoints
1) Visit /openapi.json to see the live spec. Confirm it includes:
   - GET /
   - GET /todos/
   - POST /todos/
   - GET /todos/{todo_id}
   - PUT /todos/{todo_id}
   - PATCH /todos/{todo_id}
   - DELETE /todos/{todo_id}
   - PATCH /todos/{todo_id}/toggle

2) Visit /docs to confirm Swagger UI renders all routes under the Health and Todos tags.

Exporting spec to interfaces/openapi.json
- Call /docs/export. This writes the live spec to todo_backend/interfaces/openapi.json ensuring it is in sync with the app.

Notes
- To change the persistence mode for Todos: set TODO_STORAGE_MODE=memory or file (default). You can also configure TODO_DATA_DIR and TODO_DATA_FILE via environment variables.