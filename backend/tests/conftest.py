import io
import os
import shutil
import sys
import tempfile
import pytest
from PIL import Image

# Ensure backend root is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app
from app.constants import PLACE_STATUS_PENDING, PLACE_STATUS_PUBLISHED
from app.extensions import db
from app.models.place import Place


@pytest.fixture
def app():
    """Create and configure a clean Flask test application."""
    test_upload_dir = tempfile.mkdtemp()

    app = create_app("testing")
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "UPLOAD_FOLDER": test_upload_dir,
            "MAX_CONTENT_LENGTH": 5 * 1024 * 1024,
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    shutil.rmtree(test_upload_dir, ignore_errors=True)


@pytest.fixture
def client(app):
    """Test client for issuing requests."""
    return app.test_client()


@pytest.fixture
def sample_image_bytes():
    """Generate a real 100x100 PNG image in-memory."""
    buf = io.BytesIO()
    img = Image.new("RGB", (100, 100), color=(201, 87, 61))
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


@pytest.fixture
def sample_jpeg_bytes():
    """Generate a real 100x100 JPEG image in-memory."""
    buf = io.BytesIO()
    img = Image.new("RGB", (100, 100), color=(239, 137, 80))
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.getvalue()


@pytest.fixture
def seeded_places(app):
    """Seed test database with published and pending places."""
    with app.app_context():
        p1 = Place(
            id="shali-fortress",
            name="Shali Fortress",
            category="Historical Places",
            governorate="Matrouh",
            description="13th-century mudbrick citadel rising above Siwa Oasis.",
            image_key="siwa-shali.png",
            status=PLACE_STATUS_PUBLISHED,
        )
        p2 = Place(
            id="blue-hole",
            name="Blue Hole Coast",
            category="Beaches & Nature",
            governorate="South Sinai",
            description="Red mountains meet crystal reef waters north of Dahab.",
            image_key="blue-hole-dahab.png",
            status=PLACE_STATUS_PUBLISHED,
        )
        p3 = Place(
            id="secret-oasis",
            name="Secret Desert Spring",
            category="Beaches & Nature",
            governorate="New Valley",
            description="A secluded thermal spring awaiting moderator review.",
            image_key="pending-spring.png",
            status=PLACE_STATUS_PENDING,
        )
        db.session.add_all([p1, p2, p3])
        db.session.commit()

        return {
            "published": [p1, p2],
            "pending": [p3],
        }
