"""
Database seed script for Kenooz backend.
Populates the local database with initial published hidden gems
aligned with frontend lib/places.ts.
"""

import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app
from app.constants import PLACE_STATUS_PUBLISHED
from app.extensions import db
from app.models.place import Place

INITIAL_PLACES = [
    {
        "id": "shali-fortress",
        "name": "Shali Fortress",
        "category": "Historical Places",
        "governorate": "Matrouh",
        "description": "A 13th-century mudbrick citadel rising above the palm groves of Siwa Oasis, best visited at sunset.",
        "image_key": "siwa-shali.png",
        "status": PLACE_STATUS_PUBLISHED,
    },
    {
        "id": "blue-hole",
        "name": "Blue Hole Coast",
        "category": "Beaches & Nature",
        "governorate": "South Sinai",
        "description": "Red mountains meet crystal reef waters north of Dahab, a calm spot for snorkeling away from the crowds.",
        "image_key": "blue-hole-dahab.png",
        "status": PLACE_STATUS_PUBLISHED,
    },
    {
        "id": "el-fishawy",
        "name": "El Fishawy Café",
        "category": "Cafés & Restaurants",
        "governorate": "Cairo",
        "description": "A centuries-old café tucked inside Khan el-Khalili, known for its mirrors, lanterns, and mint tea.",
        "image_key": "el-fishawy.png",
        "status": PLACE_STATUS_PUBLISHED,
    },
    {
        "id": "white-desert",
        "name": "White Desert",
        "category": "Photography Spots",
        "governorate": "New Valley",
        "description": "Wind-carved chalk formations near Farafra that glow orange at dusk and silver under the stars.",
        "image_key": "white-desert.png",
        "status": PLACE_STATUS_PUBLISHED,
    },
    {
        "id": "tuna-el-gebel",
        "name": "Tuna el-Gebel",
        "category": "Historical Places",
        "governorate": "Minya",
        "description": "An ancient necropolis with the beautifully carved tomb of Petosiris, blending Egyptian and Greek art.",
        "image_key": "tuna-el-gebel.png",
        "status": PLACE_STATUS_PUBLISHED,
    },
    {
        "id": "gharb-soheil",
        "name": "Gharb Soheil Village",
        "category": "Other",
        "governorate": "Aswan",
        "description": "A colorful Nubian village on the Nile's west bank with painted homes, local crafts, and warm hospitality.",
        "image_key": "gharb-soheil.png",
        "status": PLACE_STATUS_PUBLISHED,
    },
]


def seed_database():
    app = create_app()
    with app.app_context():
        count = Place.query.count()
        if count > 0:
            print(f"Database already has {count} places. Skipping seed.")
            return

        for p_data in INITIAL_PLACES:
            place = Place(
                id=p_data["id"],
                name=p_data["name"],
                category=p_data["category"],
                governorate=p_data["governorate"],
                description=p_data["description"],
                image_key=p_data["image_key"],
                status=p_data["status"],
            )
            db.session.add(place)

        db.session.commit()
        print(f"Successfully seeded {len(INITIAL_PLACES)} published places into the database.")


if __name__ == "__main__":
    seed_database()
