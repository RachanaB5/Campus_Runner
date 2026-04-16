"""WSGI entrypoint for Render and Gunicorn.

This keeps ``gunicorn app:app`` working from the repository root while the
actual Flask application continues to live in ``backend/app.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path


backend_dir = Path(__file__).resolve().parent / "backend"
backend_path = str(backend_dir)

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from backend.app import app  # noqa: E402
