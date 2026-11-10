from flask import Blueprint, jsonify

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
