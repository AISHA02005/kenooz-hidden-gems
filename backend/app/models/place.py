import uuid
from datetime import datetime, timezone

from flask import current_app

from app.constants import PLACE_STATUS_PENDING
from app.extensions import db


def _resolve_image_url(image_key: str) -> str:
    """Absolute URLs pass through; otherwise ask the active storage backend."""
    if image_key.startswith("http://") or image_key.startswith("https://"):
        return image_key
    try:
        storage = current_app.extensions.get("image_storage")
    except RuntimeError:  # no application context
        storage = None
    if storage is None:
        return f"/uploads/{image_key}"
    return storage.url_for(image_key)


class Place(db.Model):
    __tablename__ = "places"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    governorate = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    image_key = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=PLACE_STATUS_PENDING)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        """Serialize place to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "governorate": self.governorate,
            "description": self.description or "",
            "image_key": self.image_key,
            "image_url": _resolve_image_url(self.image_key),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Place {self.name} ({self.status})>"