import os
import uuid
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from PIL import Image as PILImage

from app.constants import (
    ALLOWED_EXTENSIONS,
    MAX_IMAGE_SIZE_BYTES,
    PLACE_STATUS_PENDING,
    PLACE_STATUS_PUBLISHED,
    VALID_CATEGORIES,
    VALID_GOVERNORATES,
)
from app.extensions import db
from app.models.place import Place


def is_allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def validate_place_submission(
    form_data: dict, files: dict
) -> tuple[bool, dict, dict]:
    """
    Validate place submission input.
    Returns: (is_valid, sanitized_data, errors_dict)
    """
    errors: dict[str, str] = {}
    sanitized: dict[str, str] = {}

    # Validate Name
    raw_name = form_data.get("name", "")
    name = raw_name.strip() if isinstance(raw_name, str) else ""
    if not name:
        errors["name"] = "Place name is required."
    elif len(name) < 3:
        errors["name"] = "Place name must be at least 3 characters."
    elif len(name) > 100:
        errors["name"] = "Place name must not exceed 100 characters."
    else:
        sanitized["name"] = name

    # Validate Category
    category = form_data.get("category", "")
    if isinstance(category, str):
        category = category.strip()
    if not category:
        errors["category"] = "Category is required."
    elif category not in VALID_CATEGORIES:
        errors["category"] = f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}."
    else:
        sanitized["category"] = category

    # Validate Governorate
    governorate = form_data.get("governorate", "")
    if isinstance(governorate, str):
        governorate = governorate.strip()
    if not governorate:
        errors["governorate"] = "Governorate is required."
    elif governorate not in VALID_GOVERNORATES:
        errors["governorate"] = f"Invalid Egyptian governorate. Must be one of the 27 official governorates."
    else:
        sanitized["governorate"] = governorate

    # Validate Description (optional)
    raw_desc = form_data.get("description", "")
    description = raw_desc.strip() if isinstance(raw_desc, str) else ""
    if len(description) > 500:
        errors["description"] = "Description must not exceed 500 characters."
    else:
        sanitized["description"] = description

    # Validate Image File
    image_file = files.get("image")
    if not image_file or not isinstance(image_file, FileStorage) or not image_file.filename:
        errors["image"] = "An image file is required."
    else:
        filename = secure_filename(image_file.filename)
        if not filename or not is_allowed_file(filename):
            errors["image"] = "Invalid image file type. Only JPG and PNG files are allowed."
        else:
            # Check file size (seek to end, check position, seek back to 0)
            image_file.seek(0, os.SEEK_END)
            size = image_file.tell()
            image_file.seek(0)

            if size == 0:
                errors["image"] = "The uploaded image file is empty."
            elif size > MAX_IMAGE_SIZE_BYTES:
                errors["image"] = "Image file size exceeds the 5 MB limit."
            else:
                # Verify file is an authentic, readable image using Pillow
                try:
                    with PILImage.open(image_file.stream) as img:
                        img.verify()
                    # Reset stream position after verify
                    image_file.stream.seek(0)
                except Exception:
                    errors["image"] = "The file uploaded is corrupted or not a valid image."

    return (len(errors) == 0, sanitized, errors)


def save_image_file(file: FileStorage, upload_folder: str) -> str:
    """Save the uploaded file with a unique secure filename and return image_key."""
    os.makedirs(upload_folder, exist_ok=True)
    original_filename = secure_filename(file.filename or "image.png")
    ext = original_filename.rsplit(".", 1)[1].lower() if "." in original_filename else "png"
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    destination_path = os.path.join(upload_folder, unique_filename)
    file.save(destination_path)
    return unique_filename


def create_place(data: dict, image_key: str) -> Place:
    """Create a new place record with pending status."""
    place = Place(
        name=data["name"],
        category=data["category"],
        governorate=data["governorate"],
        description=data.get("description", ""),
        image_key=image_key,
        status=PLACE_STATUS_PENDING,
    )
    db.session.add(place)
    db.session.commit()
    return place


def get_published_places(
    category: str | None = None,
    governorate: str | None = None,
    search: str | None = None,
) -> list[Place]:
    """Retrieve published places only, with optional filters."""
    query = Place.query.filter_by(status=PLACE_STATUS_PUBLISHED)

    if category and category.lower() != "all":
        query = query.filter_by(category=category)

    if governorate and governorate.lower() != "all":
        query = query.filter_by(governorate=governorate)

    if search:
        search_term = f"%{search.strip().lower()}%"
        query = query.filter(db.func.lower(Place.name).like(search_term))

    return query.order_by(Place.created_at.desc()).all()


def get_published_place_by_id(place_id: str) -> Place | None:
    """
    Retrieve a single place by ID only if published.
    Pending places are explicitly filtered out.
    """
    return Place.query.filter_by(
        id=place_id, status=PLACE_STATUS_PUBLISHED
    ).first()
