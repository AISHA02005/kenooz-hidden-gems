import os

from dotenv import load_dotenv

from app.constants import MAX_IMAGE_SIZE_BYTES

basedir = os.path.abspath(os.path.dirname(__file__))
backend_dir = os.path.abspath(os.path.join(basedir, ".."))

# Load environment variables from backend/.env if present
load_dotenv(os.path.join(backend_dir, ".env"))

DEV_SECRET_KEY = "dev-secret-key-change-in-production"
MIN_SECRET_KEY_LENGTH = 32
# Whole-request limit = max image + room for multipart boundaries/form fields.
MULTIPART_OVERHEAD_BYTES = 1024 * 1024


class ConfigurationError(ValueError):
    """Raised when the application configuration is invalid or unsafe."""


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer.") from exc


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


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


def build_engine_options(database_uri: str) -> dict:
    """
    SQLAlchemy engine options.
    SQLite (local/tests) needs none. MySQL/RDS gets pooling, health checks,
    connection recycling (RDS/NAT drop idle connections), timeouts and utf8mb4.
    """
    if database_uri.startswith("sqlite"):
        return {}

    connect_args: dict = {
        "charset": "utf8mb4",
        "connect_timeout": _env_int("DB_CONNECT_TIMEOUT", 10),
    }
    ssl_ca = (os.environ.get("DB_SSL_CA") or "").strip()
    if ssl_ca:
        connect_args["ssl"] = {"ca": ssl_ca}

    return {
        "pool_pre_ping": True,
        "pool_recycle": _env_int("DB_POOL_RECYCLE", 1800),
        "pool_size": _env_int("DB_POOL_SIZE", 5),
        "max_overflow": _env_int("DB_MAX_OVERFLOW", 10),
        "pool_timeout": _env_int("DB_POOL_TIMEOUT", 30),
        "connect_args": connect_args,
    }


def collect_production_problems(
    *,
    secret_key: str | None,
    database_uri: str | None,
    storage_backend: str | None,
    s3_bucket: str | None,
    aws_region: str | None,
) -> list[str]:
    """Return a list of human-readable problems with production settings."""
    problems: list[str] = []

    key = secret_key or ""
    if (
        not key
        or key == DEV_SECRET_KEY
        or key.startswith("replace-with")
        or len(key) < MIN_SECRET_KEY_LENGTH
    ):
        problems.append(
            f"SECRET_KEY must be set to a real random value of at least "
            f"{MIN_SECRET_KEY_LENGTH} characters (not the development default)."
        )

    if not database_uri or database_uri.startswith("sqlite"):
        problems.append(
            "DATABASE_URL must point to Amazon RDS MySQL "
            "(mysql+pymysql://user:password@host:3306/dbname); SQLite is not allowed in production."
        )

    backend = (storage_backend or "").lower()
    if backend not in ("local", "s3"):
        problems.append("STORAGE_BACKEND must be 'local' or 's3'.")
    if backend == "s3":
        if not s3_bucket:
            problems.append("S3_BUCKET_NAME is required when STORAGE_BACKEND=s3.")
        if not aws_region:
            problems.append("AWS_REGION is required when STORAGE_BACKEND=s3.")

    return problems


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", DEV_SECRET_KEY)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = normalize_database_url(os.environ.get("DATABASE_URL"))
    SQLALCHEMY_ENGINE_OPTIONS = build_engine_options(SQLALCHEMY_DATABASE_URI)

    # Create tables at startup (dev/test only). Production uses Flask-Migrate.
    AUTO_CREATE_TABLES = _env_bool("AUTO_CREATE_TABLES", True)
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

    # ---- Local uploads ----
    _upload_env = os.environ.get("UPLOAD_FOLDER", "uploads")
    UPLOAD_FOLDER = (
        _upload_env
        if os.path.isabs(_upload_env)
        else os.path.abspath(os.path.join(backend_dir, _upload_env))
    )
    # Request-size cap: 5 MB image + multipart overhead. The exact 5 MB image
    # limit is enforced by service-layer validation.
    MAX_CONTENT_LENGTH = _env_int(
        "MAX_CONTENT_LENGTH", MAX_IMAGE_SIZE_BYTES + MULTIPART_OVERHEAD_BYTES
    )

    # ---- Image storage ----
    STORAGE_BACKEND = os.environ.get("STORAGE_BACKEND", "local").strip().lower() or "local"
    AWS_REGION = (
        os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "eu-north-1"
    )
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME") or "kenooz11-gems-2026"
    S3_KEY_PREFIX = os.environ.get("S3_KEY_PREFIX", "places/")
    IMAGE_DELIVERY = os.environ.get("IMAGE_DELIVERY", "proxy").strip().lower() or "proxy"
    S3_PRESIGNED_EXPIRY = _env_int("S3_PRESIGNED_EXPIRY", 900)
    S3_SERVER_SIDE_ENCRYPTION = (os.environ.get("S3_SERVER_SIDE_ENCRYPTION") or "").strip() or None

    # CORS configuration - default to local Next.js frontend
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]

    @classmethod
    def validate(cls) -> None:
        """Hook for config-specific validation. Raises ConfigurationError."""
        return None


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS: dict = {}
    AUTO_CREATE_TABLES = True
    # Tests must never touch AWS, whatever the environment says.
    STORAGE_BACKEND = "local"
    IMAGE_DELIVERY = "proxy"
    # Testing upload folder will be overridden with temp directory in pytest fixtures


class ProductionConfig(BaseConfig):
    DEBUG = False
    # No development fallback: must come from the environment.
    SECRET_KEY = os.environ.get("SECRET_KEY")
    AUTO_CREATE_TABLES = _env_bool("AUTO_CREATE_TABLES", False)

    @classmethod
    def validate(cls) -> None:
        problems = collect_production_problems(
            secret_key=cls.SECRET_KEY,
            database_uri=cls.SQLALCHEMY_DATABASE_URI,
            storage_backend=cls.STORAGE_BACKEND,
            s3_bucket=cls.S3_BUCKET_NAME,
            aws_region=cls.AWS_REGION,
        )
        if problems:
            raise ConfigurationError(
                "Invalid production configuration:\n- " + "\n- ".join(problems)
            )


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}