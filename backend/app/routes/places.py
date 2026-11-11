from flask import Blueprint, current_app, jsonify, request

from app.errors import (
    DB_UNAVAILABLE_MESSAGE,
    SUBMISSION_FAILED_MESSAGE,
    is_db_unavailable,
)
from app.extensions import db
from app.services.place_service import (
    create_place,
    get_published_place_by_id,
    get_published_places,
    validate_place_submission,
)
from app.storage import StorageError, get_storage

places_bp = Blueprint("places", __name__)


@places_bp.route("/places", methods=["GET"])
def list_places():
    """
    List published places only.
    Optional query params:
      - category: filter by category
      - governorate: filter by governorate
      - search: filter by place name substring
    """
    category = request.args.get("category")
    governorate = request.args.get("governorate")
    search = request.args.get("search")

    places = get_published_places(
        category=category,
        governorate=governorate,
        search=search,
    )
    return (
        jsonify(
            {
                "places": [place.to_dict() for place in places],
                "count": len(places),
            }
        ),
        200,
    )


@places_bp.route("/places/<place_id>", methods=["GET"])
def get_place(place_id: str):
    """
    Get a single published place by ID.
    Pending places return 404 to ensure they are never exposed publicly.
    """
    place = get_published_place_by_id(place_id)
    if not place:
        return jsonify({"error": "Place not found"}), 404

    return jsonify({"place": place.to_dict()}), 200


@places_bp.route("/places", methods=["POST"])
def submit_place():
    """
    Submit a new place for community review.
    Accepts multipart/form-data:
      - name: required string (3-100 chars)
      - category: required string (one of valid categories)
      - governorate: required string (one of 27 governorates)
      - description: optional string (max 500 chars)
      - image: required image file (JPG, PNG up to 5 MB)

    Returns 201 Created with pending place record.

    Consistency: the image is stored first; if the database write then fails,
    the stored image is deleted so no orphaned object/file remains. If the
    image cannot be stored, no database row is created.
    """
    is_valid, sanitized_data, errors = validate_place_submission(
        request.form, request.files
    )

    if not is_valid:
        return (
            jsonify(
                {
                    "error": "Validation failed",
                    "details": errors,
                }
            ),
            400,
        )

    storage = get_storage()

    # 1) Store the image
    try:
        image_key = storage.save(request.files["image"])
    except StorageError:
        current_app.logger.exception("Image storage failed during place submission")
        return jsonify({"error": SUBMISSION_FAILED_MESSAGE}), 500

    # 2) Save the database record; undo the image if this fails
    try:
        place = create_place(sanitized_data, image_key)
    except Exception as exc:
        db.session.rollback()
        if not storage.delete(image_key):
            current_app.logger.error(
                "Orphaned image left in %s storage after failed DB write: %s",
                storage.name,
                image_key,
            )
        current_app.logger.exception("Failed to save place submission: %s", exc)
        if is_db_unavailable(exc):
            return (
                jsonify({"error": DB_UNAVAILABLE_MESSAGE, "message": DB_UNAVAILABLE_MESSAGE}),
                503,
            )
        return jsonify({"error": SUBMISSION_FAILED_MESSAGE}), 500

    # The place is committed; never delete its image after this point.
    return (
        jsonify(
            {
                "message": "Place submitted for review",
                "place": place.to_dict(),
            }
        ),
        201,
    )