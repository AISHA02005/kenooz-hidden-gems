import re
import uuid
from abc import ABC, abstractmethod

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

# Flat, safe image keys only: no slashes, no leading dot, bounded length.
SAFE_KEY_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,254}$")

CONTENT_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
}


class StorageError(Exception):
    """Storage backend failed (disk error, S3 outage, permissions...)."""


class StorageNotFoundError(StorageError):
    """The requested image does not exist."""


def is_safe_image_key(key: str) -> bool:
    return bool(key) and bool(SAFE_KEY_PATTERN.match(key))


def generate_image_key(filename: str | None) -> str:
    """Unique, filesystem/S3-safe key: '<uuid4 hex>.<jpg|jpeg|png>'."""
    safe_name = secure_filename(filename or "")
    ext = safe_name.rsplit(".", 1)[1].lower() if "." in safe_name else "png"
    if ext not in CONTENT_TYPES:
        ext = "png"
    return f"{uuid.uuid4().hex}.{ext}"


def content_type_for(key: str) -> str:
    ext = key.rsplit(".", 1)[1].lower() if "." in key else ""
    return CONTENT_TYPES.get(ext, "application/octet-stream")


class ImageStorage(ABC):
    """Interface implemented by every image storage backend."""

    name: str = "base"

    @abstractmethod
    def save(self, file: FileStorage) -> str:
        """Persist an already-validated upload. Returns the image_key. Raises StorageError."""

    @abstractmethod
    def delete(self, image_key: str) -> bool:
        """Best-effort delete. Never raises. Returns True when the object is gone."""

    @abstractmethod
    def serve(self, image_key: str):
        """Return a Flask response for /uploads/<key>. Raises StorageNotFoundError/StorageError."""

    @abstractmethod
    def url_for(self, image_key: str) -> str:
        """URL placed in the API's image_url field."""

    @abstractmethod
    def check(self) -> None:
        """Readiness probe. Raises StorageError when the backend is unusable."""