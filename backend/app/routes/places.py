from flask import Blueprint, current_app, jsonify, request

from app.services.place_service import (
    create_place,
    get_published_place_by_id,
    get_published_places,
    save_image_file,
    validate_place_submission,
)

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

    image_file = request.files["image"]
    upload_folder = current_app.config["UPLOAD_FOLDER"]

    try:
        image_key = save_image_file(image_file, upload_folder)
        place = create_place(sanitized_data, image_key)

        return (
            jsonify(
                {
                    "message": "Place submitted for review",
                    "place": place.to_dict(),
                }
            ),
            201,
        )
    except Exception as exc:
        current_app.logger.exception("Failed to save place submission: %s", exc)
        return (
            jsonify(
                {
                    "error": "Failed to save place submission. Please try again.",
                }
            ),
            500,
        )
