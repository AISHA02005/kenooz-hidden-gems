from flask import Blueprint, current_app, jsonify
from sqlalchemy import text

from app.extensions import db
from app.storage import get_storage

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify backend service status."""
    return (
        jsonify(
            {
                "status": "healthy",
                "service": "kenooz-api",
                "version": "1.0.0",
            }
        ),
        200,
    )


@health_bp.route("/health/ready", methods=["GET"])
def readiness_check():
    """Readiness probe: can the API reach its database and image storage?"""
    checks: dict[str, str] = {}

    try:
        db.session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Readiness check: database unavailable")
        checks["database"] = "unavailable"

    try:
        get_storage().check()
        checks["storage"] = "ok"
    except Exception:
        current_app.logger.exception("Readiness check: storage unavailable")
        checks["storage"] = "unavailable"

    ready = all(value == "ok" for value in checks.values())
    return (
        jsonify({"status": "ready" if ready else "degraded", "checks": checks}),
        200 if ready else 503,
    )