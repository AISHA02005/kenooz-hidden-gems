import uuid
from datetime import datetime, timezone
from app.extensions import db
from app.constants import PLACE_STATUS_PENDING


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
            "image_url": (
                self.image_key
                if self.image_key.startswith("http://")
                or self.image_key.startswith("https://")
                else f"/uploads/{self.image_key}"
            ),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Place {self.name} ({self.status})>"
