import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
backend_dir = os.path.abspath(os.path.join(basedir, ".."))

# Load environment variables from backend/.env if present
load_dotenv(os.path.join(backend_dir, ".env"))


def normalize_database_url(url: str | None) -> str:
    """Normalize database URL for SQLAlchemy compatibility."""
    if not url:
        # Default local SQLite database file inside backend/
        db_path = os.path.join(backend_dir, "kenooz.db")
        return f"sqlite:///{db_path}"

    # Handle Heroku/RDS style mysql:// -> mysql+pymysql://
    if url.startswith("mysql://"):
        return url.replace("mysql://", "mysql+pymysql://", 1)

    # Handle postgres:// legacy prefixes if needed
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)

    return url


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = normalize_database_url(os.environ.get("DATABASE_URL"))

    _upload_env = os.environ.get("UPLOAD_FOLDER", "uploads")
    UPLOAD_FOLDER = (
        _upload_env
        if os.path.isabs(_upload_env)
        else os.path.abspath(os.path.join(backend_dir, _upload_env))
    )
    MAX_CONTENT_LENGTH = int(
        os.environ.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024)
    )  # 5 MB

    # CORS configuration - default to local Next.js frontend
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Testing upload folder will be overridden with temp directory in pytest fixtures


class ProductionConfig(BaseConfig):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
