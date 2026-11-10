import os
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from app.config import config_by_name
from app.extensions import cors, db
from app.routes.health import health_bp
from app.routes.places import places_bp
from app.routes.uploads import uploads_bp


def create_app(config_name: str | None = None) -> Flask:
    """Application factory for Kenooz Flask REST API."""
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    config_class = config_by_name.get(config_name, config_by_name["development"])

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure uploads directory exists
    upload_folder = app.config.get("UPLOAD_FOLDER")
    if upload_folder:
        os.makedirs(upload_folder, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    cors.init_app(
        app,
        resources={
            r"/api/*": {"origins": app.config["CORS_ORIGINS"]},
            r"/uploads/*": {"origins": app.config["CORS_ORIGINS"]},
        },
    )

    # Register blueprints
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(places_bp, url_prefix="/api")
    app.register_blueprint(uploads_bp)

    # Register global JSON error handlers
    register_error_handlers(app)

    # Auto-create tables for local development and testing
    with app.app_context():
        db.create_all()

    return app


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(400)
    def handle_bad_request(err):
        return jsonify({"error": "Bad Request", "message": str(err)}), 400

    @app.errorhandler(404)
    def handle_not_found(err):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(err):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(413)
    def handle_payload_too_large(err):
        return (
            jsonify(
                {
                    "error": "Payload too large",
                    "message": "File exceeds the maximum allowed size of 5 MB.",
                }
            ),
            413,
        )

    @app.errorhandler(500)
    def handle_internal_error(err):
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "message": "An unexpected error occurred.",
                }
            ),
            500,
        )

    @app.errorhandler(HTTPException)
    def handle_generic_http_exception(err):
        return jsonify({"error": err.name, "message": err.description}), err.code
