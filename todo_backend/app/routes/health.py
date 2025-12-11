from flask_smorest import Blueprint
from flask.views import MethodView

# Use a consistent tag/name to appear cleanly in OpenAPI
blp = Blueprint("Health", "health", url_prefix="/", description="Health check route")


@blp.route("/")
class HealthCheck(MethodView):
    """Simple health check endpoint."""
    def get(self):
        """Return a basic health status."""
        return {"message": "Healthy"}
