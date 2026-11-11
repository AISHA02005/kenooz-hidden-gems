import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Development server only. In production run: gunicorn run:app
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    # Debug requires BOTH a debug-enabled config (development) and FLASK_DEBUG.
    debug = bool(app.config.get("DEBUG")) and os.environ.get("FLASK_DEBUG", "True").lower() in (
        "true",
        "1",
    )
    app.run(host=host, port=port, debug=debug)