from flask import Flask
from flask_cors import CORS
from flask_smorest import Api
import os

# Import blueprints
from .routes.health import blp as health_blp
# Note: todos blueprint module must exist; importing here for registration.
# If not yet implemented, create app/routes/todos.py with a flask_smorest Blueprint named 'blp'.
from .routes import todos  # noqa: F401  # ensure module is importable
from .routes.todos import blp as todos_blp

# Import TodoStore
from .models import TodoStore


# Initialize Flask app
app = Flask(__name__)
app.url_map.strict_slashes = False

# Enable CORS for all routes (broad for simplicity; tighten for production)
CORS(app, resources={r"/*": {"origins": "*"}})

# OpenAPI / Swagger configuration
app.config["API_TITLE"] = "My Flask API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Instantiate TodoStore based on environment variables
# TODO_STORAGE_MODE: "file" (default) or "memory"
# TODO_DATA_FILE: file name for JSON when using file persistence (default "todos.json")
_storage_mode = os.getenv("TODO_STORAGE_MODE", "file").strip().lower()
_data_file = os.getenv("TODO_DATA_FILE", "todos.json").strip() or "todos.json"
_data_dir = os.getenv("TODO_DATA_DIR", "./data").strip() or "./data"

todo_store = TodoStore(
    persistence=_storage_mode,
    data_dir=_data_dir,
    file_name=_data_file,
)

# Attach to app for access across blueprints
# Expose under both extensions and config for flexibility
app.extensions = getattr(app, "extensions", {})
app.extensions["todo_store"] = todo_store
app.config["TODO_STORE"] = todo_store

# Initialize API and register blueprints
api = Api(app)
api.register_blueprint(health_blp)
api.register_blueprint(todos_blp)
