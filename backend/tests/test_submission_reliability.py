import io
import os

import pytest
from PIL import Image
from sqlalchemy.exc import OperationalError

from app.constants import PLACE_STATUS_PENDING
from app.extensions import db
from app.models.place import Place
from app.storage.s3 import S3Storage
from tests.fakes import FakeS3Client

BUCKET = "kenooz11-gems-2026"
MB = 1024 * 1024


def form(image_bytes: bytes, filename: str = "photo.png", mimetype: str = "image/png"):
    return {
        "name": "Wadi El Hitan",
        "category": "Historical Places",
        "governorate": "Faiyum",
        "description": "Valley of the Whales.",
        "image": (io.BytesIO(image_bytes), filename, mimetype),
    }


def post(client, data):
    return client.post("/api/places", data=data, content_type="multipart/form-data")


def db_down(*args, **kwargs):
    raise OperationalError("INSERT", {}, Exception("connection refused"))


@pytest.fixture
def fake_s3(app):
    fake = FakeS3Client()
    app.extensions["image_storage"] = S3Storage(
        bucket=BUCKET, region="eu-north-1", client=fake
    )
    return fake


def place_count() -> int:
    return db.session.query(Place).count()


# ------------------------------------------------------------ S3 submissions
def test_submission_with_s3_stores_private_object_and_pending(
    client, fake_s3, sample_image_bytes
):
    response = post(client, form(sample_image_bytes))
    assert response.status_code == 201

    place = response.get_json()["place"]
    key = place["image_key"]
    assert place["status"] == PLACE_STATUS_PENDING
    assert place["image_url"] == f"/uploads/{key}"
    assert (BUCKET, f"places/{key}") in fake_s3.objects

    # Pending place is never public
    assert client.get("/api/places").get_json()["count"] == 0
    assert client.get(f"/api/places/{place['id']}").status_code == 404

    # Frontend-compatible image URL works through the backend
    image = client.get(place["image_url"])
    assert image.status_code == 200
    assert image.data == sample_image_bytes
    assert image.mimetype == "image/png"


def test_published_s3_place_has_working_image_url(client, app, fake_s3, sample_image_bytes):
    key = "seed-example.png"
    fake_s3.objects[(BUCKET, f"places/{key}")] = {
        "Body": sample_image_bytes,
        "ContentType": "image/png",
    }
    db.session.add(
        Place(
            id="p1",
            name="Seed Place",
            category="Other",
            governorate="Cairo",
            description="",
            image_key=key,
            status="published",
        )
    )
    db.session.commit()

    data = client.get("/api/places").get_json()
    assert data["count"] == 1
    assert data["places"][0]["image_url"] == f"/uploads/{key}"
    assert client.get(data["places"][0]["image_url"]).status_code == 200


def test_s3_upload_failure_returns_500_without_db_record(client, fake_s3, sample_image_bytes):
    fake_s3.fail_put = True
    response = post(client, form(sample_image_bytes))
    assert response.status_code == 500
    assert response.get_json()["error"] == "Failed to save place submission. Please try again."
    assert place_count() == 0
    assert fake_s3.objects == {}


def test_db_failure_after_s3_upload_removes_object(
    client, fake_s3, sample_image_bytes, monkeypatch
):
    monkeypatch.setattr("app.routes.places.create_place", db_down)
    response = post(client, form(sample_image_bytes))
    assert response.status_code == 503
    assert "temporarily unavailable" in response.get_json()["error"]
    assert fake_s3.objects == {}  # no orphaned object


def test_db_failure_with_local_storage_removes_file(
    client, app, sample_image_bytes, monkeypatch
):
    monkeypatch.setattr("app.routes.places.create_place", db_down)
    response = post(client, form(sample_image_bytes))
    assert response.status_code == 503
    assert os.listdir(app.config["UPLOAD_FOLDER"]) == []


def test_unexpected_error_returns_500_and_cleans_up(
    client, fake_s3, sample_image_bytes, monkeypatch
):
    def boom(*args, **kwargs):
        raise RuntimeError("unexpected")

    monkeypatch.setattr("app.routes.places.create_place", boom)
    response = post(client, form(sample_image_bytes))
    assert response.status_code == 500
    assert response.get_json()["error"] == "Failed to save place submission. Please try again."
    assert fake_s3.objects == {}


def test_cleanup_failure_does_not_mask_original_error(
    client, fake_s3, sample_image_bytes, monkeypatch
):
    fake_s3.fail_delete = True
    monkeypatch.setattr("app.routes.places.create_place", db_down)
    response = post(client, form(sample_image_bytes))
    assert response.status_code == 503


# ----------------------------------------------------------- read-side errors
def test_list_places_returns_503_when_database_unavailable(client, monkeypatch):
    monkeypatch.setattr("app.routes.places.get_published_places", db_down)
    response = client.get("/api/places")
    assert response.status_code == 503
    assert "error" in response.get_json()


def test_missing_image_returns_404(client):
    response = client.get("/uploads/missing.png")
    assert response.status_code == 404
    assert response.get_json()["error"] == "File not found"


def test_upload_route_rejects_unsafe_paths(client):
    assert client.get("/uploads/sub/dir.png").status_code == 404


def test_s3_missing_object_returns_404(client, fake_s3):
    assert client.get("/uploads/not-there.png").status_code == 404


def test_s3_read_failure_returns_502(client, fake_s3):
    fake_s3.fail_get = True
    response = client.get("/uploads/anything.png")
    assert response.status_code == 502
    assert "error" in response.get_json()


# ------------------------------------------------------------ size limit rules
def test_image_just_under_limit_accepted_despite_multipart_overhead(client, app):
    app.config["MAX_CONTENT_LENGTH"] = 6 * MB  # new default: 5 MB + 1 MB overhead
    img = Image.frombytes("RGB", (1280, 1280), os.urandom(1280 * 1280 * 3))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    data = buf.getvalue()
    assert len(data) < 5 * MB, "test image must be under the 5 MB limit"

    response = post(client, form(data))
    assert response.status_code == 201


def test_image_over_5mb_rejected_by_validation(client, app):
    app.config["MAX_CONTENT_LENGTH"] = 6 * MB
    response = post(client, form(b"0" * (5 * MB + 1)))
    assert response.status_code == 400
    assert "5 MB" in response.get_json()["details"]["image"]