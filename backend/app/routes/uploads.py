from flask import Blueprint, current_app, jsonify

from app.storage import StorageError, StorageNotFoundError, get_storage

uploads_bp = Blueprint("uploads", __name__)


@uploads_bp.route("/uploads/<path:filename>", methods=["GET"])
def serve_upload(filename: str):
    """
    Serve a place image by key.
    - local backend: file from the uploads folder (local development)
    - s3 backend: object read from the PRIVATE bucket (or a redirect to a
      presigned URL when IMAGE_DELIVERY=presigned)
    """
    try:
        return get_storage().serve(filename)
    except StorageNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except StorageError:
        current_app.logger.exception("Image storage error while serving %s", filename)
        return jsonify({"error": "Image storage is temporarily unavailable"}), 502