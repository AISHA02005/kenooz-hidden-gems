import logging
import os

from flask import Flask, jsonify
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from app.config import ConfigurationError, config_by_name
from app.errors import DB_UNAVAILABLE_MESSAGE, is_db_unavailable
from app.extensions import cors, db, migrate
from app.routes.health import health_bp
from app.routes.places import places_bp
from app.routes.uploads import uploads_bp
from app.storage import init_storage


def create_app(config_name: str | None = None) -> Flask:
    """Application factory for Kenooz Flask REST API."""
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    config_class = config_by_name.get(config_name)
    if config_class is None:
        raise ConfigurationError(
            f"Unknown FLASK_CONFIG '{config_name}'. "
            f"Valid values: {', '.join(sorted(config_by_name))}."
        )
    # Fails fast on unsafe production settings (weak secret, SQLite, missing bucket...)
    config_class.validate()

    app = Flask(__name__)
    app.config.from_object(config_class)
    configure_logging(app)

    # Image storage (local filesystem or Amazon S3)
    init_storage(app)
    if app.config["STORAGE_BACKEND"] == "local":
        upload_folder = app.config.get("UPLOAD_FOLDER")
        if upload_folder:
            os.makedirs(upload_folder, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
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

    # Auto-create tables for local development and testing only.
    # Production schema is managed with Flask-Migrate ("flask db upgrade").
    if app.config.get("AUTO_CREATE_TABLES"):
        with app.app_context():
            db.create_all()

    return app


def configure_logging(app: Flask) -> None:
    level = getattr(logging, str(app.config.get("LOG_LEVEL", "INFO")).upper(), logging.INFO)
    app.logger.setLevel(level)


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

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(err):
        """Database failures never leak internals; connection problems return 503."""
        db.session.rollback()
        app.logger.error("Database error: %s", err, exc_info=err)
        if is_db_unavailable(err):
            return (
                jsonify({"error": DB_UNAVAILABLE_MESSAGE, "message": DB_UNAVAILABLE_MESSAGE}),
                503,
            )
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "message": "An unexpected error occurred.",
                }
            ),
            500,
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