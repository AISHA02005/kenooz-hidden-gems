import pytest

from app import create_app
from app.config import (
    DEV_SECRET_KEY,
    ConfigurationError,
    ProductionConfig,
    TestingConfig,
    build_engine_options,
    collect_production_problems,
    normalize_database_url,
)

GOOD = dict(
    secret_key="x" * 40,
    database_uri="mysql+pymysql://user:pw@host:3306/db",
    storage_backend="s3",
    s3_bucket="my-bucket",
    aws_region="eu-north-1",
)


def test_valid_production_settings_have_no_problems():
    assert collect_production_problems(**GOOD) == []


@pytest.mark.parametrize(
    "secret", [None, "", DEV_SECRET_KEY, "short", "replace-with-" + "x" * 40]
)
def test_weak_production_secret_rejected(secret):
    problems = collect_production_problems(**{**GOOD, "secret_key": secret})
    assert any("SECRET_KEY" in p for p in problems)


def test_sqlite_rejected_in_production():
    problems = collect_production_problems(**{**GOOD, "database_uri": "sqlite:///x.db"})
    assert any("DATABASE_URL" in p for p in problems)


def test_s3_backend_requires_bucket_and_region():
    problems = collect_production_problems(**{**GOOD, "s3_bucket": "", "aws_region": ""})
    assert any("S3_BUCKET_NAME" in p for p in problems)
    assert any("AWS_REGION" in p for p in problems)


def test_unknown_storage_backend_rejected():
    problems = collect_production_problems(**{**GOOD, "storage_backend": "ftp"})
    assert any("STORAGE_BACKEND" in p for p in problems)


def test_create_app_production_fails_fast_on_unsafe_settings(monkeypatch):
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", None)
    with pytest.raises(ConfigurationError):
        create_app("production")


def test_unknown_config_name_is_rejected_not_silently_development():
    with pytest.raises(ConfigurationError):
        create_app("prodution")


def test_sqlite_has_no_pool_options():
    assert build_engine_options("sqlite:///x.db") == {}


def test_mysql_engine_options_enable_health_checks_and_utf8mb4():
    opts = build_engine_options("mysql+pymysql://u:p@h:3306/db")
    assert opts["pool_pre_ping"] is True
    assert opts["pool_recycle"] > 0
    assert opts["connect_args"]["charset"] == "utf8mb4"
    assert opts["connect_args"]["connect_timeout"] > 0


def test_mysql_url_is_normalized_to_pymysql():
    assert normalize_database_url("mysql://u:p@h/db") == "mysql+pymysql://u:p@h/db"


def test_testing_config_always_uses_local_storage_and_memory_db():
    assert TestingConfig.STORAGE_BACKEND == "local"
    assert TestingConfig.SQLALCHEMY_DATABASE_URI == "sqlite:///:memory:"