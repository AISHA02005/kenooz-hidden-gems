from app.extensions import db
from app.storage.s3 import S3Storage
from tests.fakes import FakeS3Client


def test_readiness_ok_locally(client):
    response = client.get("/api/health/ready")
    assert response.status_code == 200
    assert response.get_json()["checks"] == {"database": "ok", "storage": "ok"}


def test_readiness_reports_storage_failure(client, app):
    fake = FakeS3Client()
    fake.fail_head = True
    app.extensions["image_storage"] = S3Storage(
        bucket="kenooz11-gems-2026", region="eu-north-1", client=fake
    )
    response = client.get("/api/health/ready")
    assert response.status_code == 503
    checks = response.get_json()["checks"]
    assert checks["storage"] == "unavailable"
    assert checks["database"] == "ok"


def test_readiness_reports_database_failure(client, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("db down")

    monkeypatch.setattr(db.session, "execute", boom)
    response = client.get("/api/health/ready")
    assert response.status_code == 503
    assert response.get_json()["checks"]["database"] == "unavailable"