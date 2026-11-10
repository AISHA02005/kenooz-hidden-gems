import io
from app.constants import PLACE_STATUS_PENDING, PLACE_STATUS_PUBLISHED
from app.models.place import Place


def test_list_places_returns_published_only(client, seeded_places):
    """GET /api/places returns published places and never pending places."""
    response = client.get("/api/places")
    assert response.status_code == 200

    data = response.get_json()
    assert "places" in data
    assert "count" in data
    assert data["count"] == 2

    place_ids = [p["id"] for p in data["places"]]
    assert "shali-fortress" in place_ids
    assert "blue-hole" in place_ids
    assert "secret-oasis" not in place_ids

    # Verify all returned places have status published
    for p in data["places"]:
        assert p["status"] == PLACE_STATUS_PUBLISHED


def test_list_places_filtering_by_category(client, seeded_places):
    """GET /api/places?category=Historical+Places filters correctly."""
    response = client.get("/api/places?category=Historical Places")
    assert response.status_code == 200

    data = response.get_json()
    assert data["count"] == 1
    assert data["places"][0]["id"] == "shali-fortress"


def test_list_places_filtering_by_governorate(client, seeded_places):
    """GET /api/places?governorate=South+Sinai filters correctly."""
    response = client.get("/api/places?governorate=South Sinai")
    assert response.status_code == 200

    data = response.get_json()
    assert data["count"] == 1
    assert data["places"][0]["id"] == "blue-hole"


def test_list_places_filtering_by_search(client, seeded_places):
    """GET /api/places?search=shali performs case-insensitive name search."""
    response = client.get("/api/places?search=shali")
    assert response.status_code == 200

    data = response.get_json()
    assert data["count"] == 1
    assert data["places"][0]["name"] == "Shali Fortress"


def test_get_single_published_place(client, seeded_places):
    """GET /api/places/<id> returns the published place details."""
    response = client.get("/api/places/shali-fortress")
    assert response.status_code == 200

    data = response.get_json()
    assert "place" in data
    place = data["place"]
    assert place["id"] == "shali-fortress"
    assert place["name"] == "Shali Fortress"
    assert place["category"] == "Historical Places"
    assert place["governorate"] == "Matrouh"
    assert place["status"] == PLACE_STATUS_PUBLISHED
    assert place["image_key"] == "siwa-shali.png"
    assert place["image_url"] == "/uploads/siwa-shali.png"


def test_get_pending_place_returns_404(client, seeded_places):
    """GET /api/places/<pending_id> returns 404 to never expose pending places."""
    response = client.get("/api/places/secret-oasis")
    assert response.status_code == 404

    data = response.get_json()
    assert "error" in data


def test_get_nonexistent_place_returns_404(client):
    """GET /api/places/<nonexistent_id> returns 404."""
    response = client.get("/api/places/does-not-exist")
    assert response.status_code == 404


def test_submit_place_success_png(client, sample_image_bytes):
    """POST /api/places creates a pending place with valid PNG image."""
    form_data = {
        "name": "Wadi El Hitan",
        "category": "Historical Places",
        "governorate": "Faiyum",
        "description": "Valley of the Whales with prehistoric fossil remains.",
        "image": (io.BytesIO(sample_image_bytes), "wadi-hitan.png", "image/png"),
    }

    response = client.post(
        "/api/places",
        data=form_data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 201

    data = response.get_json()
    assert data["message"] == "Place submitted for review"
    assert "place" in data

    place = data["place"]
    assert place["name"] == "Wadi El Hitan"
    assert place["category"] == "Historical Places"
    assert place["governorate"] == "Faiyum"
    assert place["description"] == "Valley of the Whales with prehistoric fossil remains."
    assert place["status"] == PLACE_STATUS_PENDING
    assert place["image_key"].endswith(".png")
    assert place["image_url"].startswith("/uploads/")

    # Verify place cannot be accessed via public GET
    public_list = client.get("/api/places").get_json()
    assert not any(p["name"] == "Wadi El Hitan" for p in public_list["places"])

    public_single = client.get(f"/api/places/{place['id']}")
    assert public_single.status_code == 404

    # Verify the uploaded image can be served
    img_response = client.get(place["image_url"])
    assert img_response.status_code == 200
    assert img_response.data == sample_image_bytes


def test_submit_place_success_jpeg(client, sample_jpeg_bytes):
    """POST /api/places creates a pending place with valid JPEG image."""
    form_data = {
        "name": "Ras Mohamed",
        "category": "Beaches & Nature",
        "governorate": "South Sinai",
        "description": "Marine national park with reefs and mangroves.",
        "image": (io.BytesIO(sample_jpeg_bytes), "ras-mohamed.jpg", "image/jpeg"),
    }

    response = client.post(
        "/api/places",
        data=form_data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 201

    data = response.get_json()
    place = data["place"]
    assert place["name"] == "Ras Mohamed"
    assert place["status"] == PLACE_STATUS_PENDING
    assert place["image_key"].endswith(".jpg")


def test_submit_place_validation_missing_name(client, sample_image_bytes):
    """POST /api/places rejects submission without name."""
    form_data = {
        "category": "Historical Places",
        "governorate": "Cairo",
        "image": (io.BytesIO(sample_image_bytes), "test.png", "image/png"),
    }

    response = client.post("/api/places", data=form_data, content_type="multipart/form-data")
    assert response.status_code == 400
    details = response.get_json()["details"]
    assert "name" in details


def test_submit_place_validation_name_too_long(client, sample_image_bytes):
    """POST /api/places rejects name exceeding 100 characters."""
    form_data = {
        "name": "A" * 101,
        "category": "Historical Places",
        "governorate": "Cairo",
        "image": (io.BytesIO(sample_image_bytes), "test.png", "image/png"),
    }

    response = client.post("/api/places", data=form_data, content_type="multipart/form-data")
    assert response.status_code == 400
    details = response.get_json()["details"]
    assert "name" in details


def test_submit_place_validation_invalid_category(client, sample_image_bytes):
    """POST /api/places rejects invalid category."""
    form_data = {
        "name": "Test Spot",
        "category": "Unknown Invalid Category",
        "governorate": "Cairo",
        "image": (io.BytesIO(sample_image_bytes), "test.png", "image/png"),
    }

    response = client.post("/api/places", data=form_data, content_type="multipart/form-data")
    assert response.status_code == 400
    details = response.get_json()["details"]
    assert "category" in details


def test_submit_place_validation_invalid_governorate(client, sample_image_bytes):
    """POST /api/places rejects invalid governorate."""
    form_data = {
        "name": "Test Spot",
        "category": "Historical Places",
        "governorate": "NonExistentGovernorate",
        "image": (io.BytesIO(sample_image_bytes), "test.png", "image/png"),
    }

    response = client.post("/api/places", data=form_data, content_type="multipart/form-data")
    assert response.status_code == 400
    details = response.get_json()["details"]
    assert "governorate" in details


def test_submit_place_validation_description_too_long(client, sample_image_bytes):
    """POST /api/places rejects description exceeding 500 characters."""
    form_data = {
        "name": "Valid Name",
        "category": "Historical Places",
        "governorate": "Cairo",
        "description": "x" * 501,
        "image": (io.BytesIO(sample_image_bytes), "test.png", "image/png"),
    }

    response = client.post("/api/places", data=form_data, content_type="multipart/form-data")
    assert response.status_code == 400
    details = response.get_json()["details"]
    assert "description" in details


def test_submit_place_validation_missing_image(client):
    """POST /api/places rejects submission without image file."""
    form_data = {
        "name": "No Image Place",
        "category": "Historical Places",
        "governorate": "Cairo",
    }

    response = client.post("/api/places", data=form_data, content_type="multipart/form-data")
    assert response.status_code == 400
    details = response.get_json()["details"]
    assert "image" in details


def test_submit_place_validation_disallowed_file_extension(client):
    """POST /api/places rejects disallowed file extensions (.txt, .pdf, .exe)."""
    form_data = {
        "name": "Bad File Extension",
        "category": "Historical Places",
        "governorate": "Cairo",
        "image": (io.BytesIO(b"dummy payload"), "exploit.exe", "application/octet-stream"),
    }

    response = client.post("/api/places", data=form_data, content_type="multipart/form-data")
    assert response.status_code == 400
    details = response.get_json()["details"]
    assert "image" in details


def test_submit_place_validation_corrupted_image(client):
    """POST /api/places rejects fake/corrupted images disguised as .png."""
    fake_png_bytes = b"This is just plain text content renamed to .png"
    form_data = {
        "name": "Corrupted Image Spot",
        "category": "Historical Places",
        "governorate": "Cairo",
        "image": (io.BytesIO(fake_png_bytes), "fake.png", "image/png"),
    }

    response = client.post("/api/places", data=form_data, content_type="multipart/form-data")
    assert response.status_code == 400
    details = response.get_json()["details"]
    assert "image" in details


def test_submit_place_validation_oversized_file(client):
    """POST /api/places rejects files larger than 5 MB."""
    oversized_bytes = b"0" * (5 * 1024 * 1024 + 1024)  # 5 MB + 1 KB
    form_data = {
        "name": "Huge File Place",
        "category": "Historical Places",
        "governorate": "Cairo",
        "image": (io.BytesIO(oversized_bytes), "large.png", "image/png"),
    }

    response = client.post("/api/places", data=form_data, content_type="multipart/form-data")
    # Will be caught either by Flask MAX_CONTENT_LENGTH (413) or service validation (400)
    assert response.status_code in (400, 413)


def test_submit_place_validation_webp_rejected(client):
    """POST /api/places rejects WebP files (only JPG and PNG allowed)."""
    form_data = {
        "name": "WebP Place",
        "category": "Historical Places",
        "governorate": "Cairo",
        "image": (io.BytesIO(b"RIFF....WEBP"), "photo.webp", "image/webp"),
    }

    response = client.post("/api/places", data=form_data, content_type="multipart/form-data")
    assert response.status_code == 400
    details = response.get_json()["details"]
    assert "image" in details
    assert "Only JPG and PNG files are allowed" in details["image"]

