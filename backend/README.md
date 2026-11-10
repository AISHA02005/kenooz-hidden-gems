# Kenooz Backend API (Phase 1)

Clean, modular, and maintainable Python Flask REST API for **Kenooz – Hidden Gems of Egypt**.

---

## 1. Overview & Architecture

This backend serves as the core data and API layer for Kenooz. It runs independently of the Next.js frontend and provides endpoints for health monitoring, retrieving published hidden gems, and accepting community place submissions for moderation.

### Technology Stack
* **Framework:** Python Flask 3.1+
* **ORM:** Flask-SQLAlchemy / SQLAlchemy 2.0+
* **Database:** SQLite (default for local development) with zero-code switch to **AWS RDS MySQL** via PyMySQL.
* **CORS:** Flask-CORS (restricted to Next.js frontend at `http://localhost:3000` by default).
* **Validation & Storage:** Pillow for authentic image verification, Werkzeug for secure uploads up to 5 MB.
* **Testing:** Pytest with in-memory database and mock upload isolation.

---

## 2. Directory Structure

```text
backend/
├── app/
│   ├── __init__.py           # Flask application factory (create_app)
│   ├── config.py             # Environment configurations (SQLite & MySQL normalization)
│   ├── constants.py          # Categories, 27 governorates, statuses, allowed mime types
│   ├── extensions.py         # SQLAlchemy and CORS instances
│   ├── models/
│   │   ├── __init__.py
│   │   └── place.py          # Place database model (UUID pk, status, timestamps)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py         # GET /api/health
│   │   ├── places.py         # GET /api/places, GET /api/places/<id>, POST /api/places
│   │   └── uploads.py        # GET /uploads/<filename> (local image server)
│   └── services/
│       ├── __init__.py
│       └── place_service.py  # Validation, secure file storage, and DB queries
├── uploads/                  # Local storage for uploaded place images
│   └── .gitkeep
├── tests/                    # Automated pytest suite
│   ├── __init__.py
│   ├── conftest.py           # In-memory test app, fixtures, and mock images
│   ├── test_health.py        # Health endpoint tests
│   └── test_places.py        # Querying, pending isolation, and validation tests
├── .env.example              # Configuration template
├── .env                      # Local environment variables
├── requirements.txt          # Python dependencies
├── run.py                    # Server startup script
├── seed.py                   # Initial database seeder (6 Egypt gems)
└── README.md                 # Documentation
```

---

## 3. Data Model (`Place`)

| Field | Type | Description |
|---|---|---|
| `id` | `VARCHAR(36)` | UUID primary key (auto-generated) |
| `name` | `VARCHAR(100)` | Place name (required, 3-100 characters) |
| `category` | `VARCHAR(50)` | Required category (`Historical Places`, `Beaches & Nature`, `Cafés & Restaurants`, `Photography Spots`, `Other`) |
| `governorate` | `VARCHAR(50)` | Required Egyptian governorate (from official 27 governorates) |
| `description` | `VARCHAR(500)` | Optional description (up to 500 characters) |
| `image_key` | `VARCHAR(255)` | Storage identifier/path (e.g. `siwa-shali.png` or S3 object key) |
| `status` | `VARCHAR(20)` | Moderation status: `pending` (default) or `published` |
| `created_at` | `DATETIME` | UTC timestamp of submission |

> **Privacy & Moderation Rule:** Places with `status='pending'` are **never** exposed on public endpoints (`GET /api/places` and `GET /api/places/<id>`).

---

## 4. Quickstart: Running Locally

### Step 1: Create and activate virtual environment

**Windows (PowerShell):**
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default settings point to local SQLite (`kenooz.db`) and allow CORS from `http://localhost:3000`.

### Step 4: Seed Initial Data (Optional but Recommended)
Populates the local database with the 6 curated Egypt places matching the frontend:
```bash
python seed.py
```

### Step 5: Start the API Server
```bash
python run.py
```
The server will start on **`http://127.0.0.1:5000`**.

---

## 5. API Endpoints

### 1. Health Check
* **`GET /api/health`**
* **Response (200 OK):**
  ```json
  {
    "status": "healthy",
    "service": "kenooz-api",
    "version": "1.0.0"
  }
  ```

---

### 2. List Published Places
* **`GET /api/places`**
* **Query Parameters (optional):**
  * `category`: Filter by category (e.g., `?category=Historical Places`)
  * `governorate`: Filter by governorate (e.g., `?governorate=South Sinai`)
  * `search`: Substring search in name (e.g., `?search=desert`)
* **Response (200 OK):**
  ```json
  {
    "places": [
      {
        "id": "shali-fortress",
        "name": "Shali Fortress",
        "category": "Historical Places",
        "governorate": "Matrouh",
        "description": "A 13th-century mudbrick citadel rising above the palm groves of Siwa Oasis...",
        "image_key": "siwa-shali.png",
        "image_url": "/uploads/siwa-shali.png",
        "status": "published",
        "created_at": "2026-11-09T22:30:00Z"
      }
    ],
    "count": 1
  }
  ```

---

### 3. Get Single Place Details
* **`GET /api/places/<id>`**
* **Response (200 OK):**
  ```json
  {
    "place": {
      "id": "shali-fortress",
      "name": "Shali Fortress",
      "category": "Historical Places",
      "governorate": "Matrouh",
      "description": "A 13th-century mudbrick citadel rising above the palm groves of Siwa Oasis...",
      "image_key": "siwa-shali.png",
      "image_url": "/uploads/siwa-shali.png",
      "status": "published",
      "created_at": "2026-11-09T22:30:00Z"
    }
  }
  ```
* **Response (404 Not Found):** Returned if the place does not exist or has `status='pending'`.

---

### 4. Submit a Place (Community Submission)
* **`POST /api/places`**
* **Content-Type:** `multipart/form-data`
* **Form Fields:**
  * `name` (string, required): Place name (3-100 characters).
  * `category` (string, required): Valid category name.
  * `governorate` (string, required): Valid Egyptian governorate.
  * `description` (string, optional): Notes / visitor tips (max 500 characters).
  * `image` (file, required): JPG or PNG image file up to 5 MB.
* **Response (201 Created):**
  ```json
  {
    "message": "Place submitted for review",
    "place": {
      "id": "c1f7b09e-7bdc-4d7a-b5e1-8761a29b3ce5",
      "name": "Wadi El Hitan",
      "category": "Historical Places",
      "governorate": "Faiyum",
      "description": "Valley of the Whales with prehistoric fossil remains.",
      "image_key": "4e18b0fae7df4807b5a19cb2b19213bc.png",
      "image_url": "/uploads/4e18b0fae7df4807b5a19cb2b19213bc.png",
      "status": "pending",
      "created_at": "2026-11-10T00:15:30Z"
    }
  }
  ```
* **Validation Error (400 Bad Request):**
  ```json
  {
    "error": "Validation failed",
    "details": {
      "name": "Place name must be at least 3 characters.",
      "image": "Invalid image file type. Only JPG and PNG files are allowed."
    }
  }
  ```

---

### 5. Static Upload Media Server (Local Dev)
* **`GET /uploads/<filename>`**
* Serves images saved in the local `backend/uploads/` directory during local development. In production with AWS, this will point directly to S3 / CloudFront URLs.

---

## 6. Database Configuration (SQLite vs Amazon RDS MySQL)

The backend dynamically detects the database driver from `DATABASE_URL`:

* **Local SQLite (Default):**
  ```env
  DATABASE_URL=sqlite:///kenooz.db
  ```
* **Amazon RDS MySQL (Production):**
  ```env
  DATABASE_URL=mysql+pymysql://<user>:<password>@<rds-host>:3306/<database>
  ```
  *(PyMySQL and cryptography are pre-installed in `requirements.txt` to support MySQL 8+ authentication without extra setup).*

---

## 7. Running the Automated Tests

Run the complete test suite:
```bash
pytest
```
To run with verbose output:
```bash
pytest -v
```

All 19 automated tests run against an isolated in-memory SQLite database and temporary upload folders, testing:
1. Health check availability.
2. Published places listing and filtering (category, governorate, name).
3. Public isolation of pending places (never returned via GET).
4. Successful PNG and JPEG multipart uploads and image saving.
5. All validation rules (missing fields, field length limits, invalid categories/governorates, corrupted images, and 5 MB size limit).
