import logging
import os

from flask import current_app, send_from_directory
from werkzeug.datastructures import FileStorage

from app.storage.base import (
    ImageStorage,
    StorageError,
    StorageNotFoundError,
    generate_image_key,
    is_safe_image_key,
)

logger = logging.getLogger(__name__)


class LocalStorage(ImageStorage):
    """Stores images on the local filesystem (local development and tests)."""

    name = "local"

    def __init__(self, folder: str | None = None):
        # When None, the folder is read from app config at call time.
        self._folder = folder

    @property
    def folder(self) -> str:
        return self._folder or current_app.config["UPLOAD_FOLDER"]

    def save(self, file: FileStorage) -> str:
        key = generate_image_key(file.filename)
        path = os.path.join(self.folder, key)
        try:
            os.makedirs(self.folder, exist_ok=True)
            file.save(path)
        except OSError as exc:
            try:
                os.remove(path)  # remove a partially written file
            except OSError:
                pass
            raise StorageError("Failed to write image to local storage.") from exc
        return key

    def delete(self, image_key: str) -> bool:
        if not is_safe_image_key(image_key):
            return False
        try:
            os.remove(os.path.join(self.folder, image_key))
            return True
        except FileNotFoundError:
            return True
        except OSError:
            logger.warning("Could not delete local image %s", image_key, exc_info=True)
            return False

    def serve(self, image_key: str):
        if not is_safe_image_key(image_key) or not os.path.isfile(
            os.path.join(self.folder, image_key)
        ):
            raise StorageNotFoundError(image_key)
        return send_from_directory(self.folder, image_key)

    def url_for(self, image_key: str) -> str:
        return f"/uploads/{image_key}"

    def check(self) -> None:
        try:
            os.makedirs(self.folder, exist_ok=True)
        except OSError as exc:
            raise StorageError("Upload folder is not available.") from exc
        if not os.access(self.folder, os.W_OK):
            raise StorageError("Upload folder is not writable.")