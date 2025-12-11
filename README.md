# simple-to-do-list-185716-185725

## Overview
This repository contains a Flask-based to-do backend that provides CRUD operations for to-do items, live OpenAPI documentation, and a simple runtime configuration for persistence. The service starts on port 3001 by default and serves Swagger UI at /docs with the live OpenAPI spec at /openapi.json.

## Running the backend
- Local run:
  - Python: set up a virtual environment, install dependencies from todo_backend/requirements.txt, and run:
    ```bash
    cd simple-to-do-list-185716-185725/todo_backend
    python run.py
    ```
  - The API will be available at http://localhost:3001

- Documentation:
  - Swagger UI: http://localhost:3001/docs
  - Live OpenAPI JSON: http://localhost:3001/openapi.json

## Base URL and routes
The app exposes a health check at / and all to-do routes under /todos. If your client expects a prefix like /api, mount or proxy the app accordingly (for example, proxy /api to the Flask root). The examples below use the root paths as implemented in code.

Available endpoints:
- Health
  - GET /
- Todos
  - GET /todos/
  - POST /todos/
  - GET /todos/{todo_id}
  - PUT /todos/{todo_id}
  - PATCH /todos/{todo_id}
  - DELETE /todos/{todo_id}
  - PATCH /todos/{todo_id}/toggle

## Example usage with curl (CRUD)
Below are example curl requests using the default base URL of http://localhost:3001.

- Create a todo
  ```bash
  curl -i -X POST http://localhost:3001/todos/ \
    -H "Content-Type: application/json" \
    -d '{
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "priority": 3
    }'
  ```
  Notes: On success returns 201 Created with the created JSON object and a Location header pointing to /todos/{id}.

- List todos (with optional filters and pagination)
  ```bash
  # Basic list
  curl -s http://localhost:3001/todos/

  # Filter completed=true and search by title/description
  curl -s "http://localhost:3001/todos/?completed=true&search=groceries"

  # Sort, paginate
  curl -s "http://localhost:3001/todos/?sort_by=updated_at&sort_dir=asc&page=1&per_page=10"
  ```

- Get a todo by id
  ```bash
  curl -s http://localhost:3001/todos/REPLACE_WITH_TODO_ID
  ```

- Update a todo (PUT, idempotent; partial fields accepted)
  ```bash
  curl -i -X PUT http://localhost:3001/todos/REPLACE_WITH_TODO_ID \
    -H "Content-Type: application/json" \
    -d '{
      "title": "Buy groceries and fruits",
      "completed": true
    }'
  ```

- Partially update a todo (PATCH)
  ```bash
  curl -i -X PATCH http://localhost:3001/todos/REPLACE_WITH_TODO_ID \
    -H "Content-Type: application/json" \
    -d '{
      "priority": 5
    }'
  ```

- Toggle completion
  ```bash
  curl -s -X PATCH http://localhost:3001/todos/REPLACE_WITH_TODO_ID/toggle
  ```

- Delete a todo
  ```bash
  curl -i -X DELETE http://localhost:3001/todos/REPLACE_WITH_TODO_ID
  ```

## Swagger UI and OpenAPI
- Swagger UI is served at /docs and renders all routes under Health and Todos.
- The live OpenAPI spec is served at /openapi.json and reflects current code and schemas.

To verify the docs:
1) Visit /openapi.json and confirm it includes:
   - GET /
   - GET /todos/
   - POST /todos/
   - GET /todos/{todo_id}
   - PUT /todos/{todo_id}
   - PATCH /todos/{todo_id}
   - DELETE /todos/{todo_id}
   - PATCH /todos/{todo_id}/toggle

2) Visit /docs to confirm Swagger UI renders all routes under the Health and Todos tags.

## Syncing the OpenAPI file
The running app can export the live schema to the repository for consumption by tooling:
- Call /docs/export. This writes the live spec to todo_backend/interfaces/openapi.json ensuring it is in sync with the app.

## Environment configuration
The backend supports simple runtime configuration via environment variables:

- TODO_STORAGE_MODE
  - Accepted values: file | memory
  - Default: file
  - Behavior: 
    - file persists todos to a JSON file on disk.
    - memory keeps data in memory only, which resets on restart.

- TODO_DATA_FILE
  - Accepted values: any filename
  - Default: todos.json
  - Behavior: only used when TODO_STORAGE_MODE=file to set the persistence filename.

- TODO_DATA_DIR
  - Accepted values: any directory path
  - Default: ./data
  - Behavior: only used when TODO_STORAGE_MODE=file to select the directory to store the JSON file.

Example:
```bash
export TODO_STORAGE_MODE=file
export TODO_DATA_DIR=./data
export TODO_DATA_FILE=todos.json
python simple-to-do-list-185716-185725/todo_backend/run.py
```

## Repository layout
- todo_backend/app/__init__.py: Flask app factory and API/Swagger configuration; provides /openapi.json and /docs/export.
- todo_backend/app/routes/*.py: Blueprints for Health and Todos routes.
- todo_backend/app/models/todo_store.py: Thread-safe store with file or memory persistence.
- todo_backend/app/schemas/*.py: Marshmallow schemas used by flask-smorest to produce OpenAPI.
- todo_backend/interfaces/openapi.json: Exported OpenAPI file synced by calling /docs/export.
- todo_backend/run.py: Entrypoint to run the Flask app.

## Notes
- If you plan to mount this behind a reverse proxy with a path prefix like /api, ensure your proxy maps /api to the Flask root. In that setup, the endpoints would appear under /api/todos and docs at /api/docs with the spec at /api/openapi.json.