"""
Community Builders Network - Sierra Leone
Small utility helpers (password hashing, validation, tokens).
"""

import hashlib
import hmac
import os
import re
import secrets

# ------------------------------------------------------------------
# Password hashing (PBKDF2-SHA256, from stdlib — no framework)
# ------------------------------------------------------------------
_ITERATIONS = 120_000
_ALGO = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return f"{_ALGO}${_ITERATIONS}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iters, salt_hex, hash_hex = stored.split("$")
        if algo != _ALGO:
            return False
        dk = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iters)
        )
        return hmac.compare_digest(dk.hex(), hash_hex)
    except (ValueError, AttributeError):
        return False


def new_session_token() -> str:
    return secrets.token_hex(32)


# ------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_email(value: str) -> bool:
    return bool(value) and bool(EMAIL_RE.match(value.strip()))


def clean(value, max_len: int = 500) -> str:
    """Trim + length-limit + basic sanitising of any user text field."""
    if value is None:
        return ""
    s = str(value).strip()
    return s[:max_len]


def require(data: dict, fields: list):
    """Return a list of missing/empty field names."""
    missing = []
    for f in fields:
        if not clean(data.get(f)):
            missing.append(f)
    return missing
