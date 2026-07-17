"""
Community Builders Network - Sierra Leone
Configuration file.

All settings can be overridden with environment variables so the
same file works locally and in production. In production, set at
least DB_PASSWORD, ADMIN_PASSWORD and SESSION_SECRET via your
process manager / hosting environment.
"""

import os

# ---------- Server ----------
HOST = os.environ.get("CBN_HOST", "0.0.0.0")
PORT = int(os.environ.get("CBN_PORT", "8000"))

# Where the static HTML/CSS/JS files live (repo root by default)
STATIC_ROOT = os.environ.get(
    "CBN_STATIC_ROOT",
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

# ---------- Database (MySQL) ----------
DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "127.0.0.1"),
    "port":     int(os.environ.get("DB_PORT", "3306")),
    "user":     os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "cbn_sierra_leone"),
    "charset":  "utf8mb4",
    "autocommit": True,
    "connection_timeout": 10,
}

# ---------- Admin bootstrap ----------
# Auto-created on first server start if the admin_users table is empty.
BOOTSTRAP_ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
BOOTSTRAP_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# ---------- Session ----------
SESSION_LIFETIME_HOURS = int(os.environ.get("SESSION_HOURS", "12"))

# ---------- Misc ----------
DEBUG = os.environ.get("CBN_DEBUG", "0") == "1"
