"""
Routes package exposing available blueprints.

This module ensures the health and todos blueprints are importable via:
    from app.routes.health import blp as health_blp
    from app.routes.todos import blp as todos_blp
"""
# PUBLIC_INTERFACE
# Re-export modules for convenience
from . import health  # noqa: F401
from . import todos  # noqa: F401

__all__ = ["health", "todos"]
