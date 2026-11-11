from flask import Flask, current_app

from app.storage.base import (
    ImageStorage,
    StorageError,
    StorageNotFoundError,
)
from app.storage.local import LocalStorage

__all__ = [
    "ImageStorage",
    "StorageError",
    "StorageNotFoundError",
    "LocalStorage",
    "init_storage",
    "get_storage",
]


def init_storage(app: Flask) -> ImageStorage:
    """Select the storage backend from STORAGE_BACKEND and attach it to the app."""
    backend = str(app.config.get("STORAGE_BACKEND") or "local").lower()

    if backend == "local":
        storage: ImageStorage = LocalStorage()
    elif backend == "s3":
        # Imported lazily so local development never needs AWS configuration.
        from app.storage.s3 import S3Storage

        storage = S3Storage(
            bucket=app.config.get("S3_BUCKET_NAME"),
            region=app.config.get("AWS_REGION"),
            prefix=app.config.get("S3_KEY_PREFIX", "places/"),
            delivery=app.config.get("IMAGE_DELIVERY", "proxy"),
            presigned_expiry=app.config.get("S3_PRESIGNED_EXPIRY", 900),
            server_side_encryption=app.config.get("S3_SERVER_SIDE_ENCRYPTION"),
        )
    else:
        raise ValueError(f"Unsupported STORAGE_BACKEND '{backend}'. Use 'local' or 's3'.")

    app.extensions["image_storage"] = storage
    app.logger.info("Image storage backend: %s", storage.name)
    return storage


def get_storage() -> ImageStorage:
    return current_app.extensions["image_storage"]