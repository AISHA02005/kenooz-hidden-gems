# Valid categories aligned with frontend lib/places.ts
VALID_CATEGORIES = [
    "Historical Places",
    "Beaches & Nature",
    "Cafés & Restaurants",
    "Photography Spots",
    "Other",
]

# 27 Egyptian governorates aligned with frontend lib/places.ts
VALID_GOVERNORATES = [
    "Alexandria",
    "Aswan",
    "Asyut",
    "Beheira",
    "Beni Suef",
    "Cairo",
    "Dakahlia",
    "Damietta",
    "Faiyum",
    "Gharbia",
    "Giza",
    "Ismailia",
    "Kafr El Sheikh",
    "Luxor",
    "Matrouh",
    "Minya",
    "Monufia",
    "New Valley",
    "North Sinai",
    "Port Said",
    "Qalyubia",
    "Qena",
    "Red Sea",
    "Sharqia",
    "Sohag",
    "South Sinai",
    "Suez",
]

PLACE_STATUS_PENDING = "pending"
PLACE_STATUS_PUBLISHED = "published"
VALID_STATUSES = (PLACE_STATUS_PENDING, PLACE_STATUS_PUBLISHED)

# Supported image upload extensions (JPG and PNG only)
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

# Max upload size: 5 MB in bytes
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
