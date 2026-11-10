import os
from flask import Blueprint, current_app, jsonify, send_from_directory

uploads_bp = Blueprint("uploads", __name__)


@uploads_bp.route("/uploads/<path:filename>", methods=["GET"])
def serve_upload(filename: str):
    """
    Serve uploaded static media files during local development.
    In production with AWS, images will be served directly from S3/CloudFront.
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(upload_folder, filename)
