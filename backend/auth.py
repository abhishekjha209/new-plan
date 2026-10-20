"""
Day 8: Real password authentication.

This module owns two security boundaries:
  1. Password storage  -> bcrypt (slow + salted, defeats offline brute force)
  2. Session identity  -> JWT (signed, stateless, self-expiring access tokens)

Key properties to remember:
  - bcrypt's slowness IS the defense. Do not "optimize" it away.
  - A JWT is SIGNED, not ENCRYPTED. Anyone can read its payload.
    Never put secrets, PII, or anything sensitive in the claims.
  - The server stores no session state. That means a token cannot be
    revoked before it expires (refresh tokens / logout come on Day 10).
"""
import os
import secrets
import logging
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

logger = logging.getLogger(__name__)

# --- JWT configuration (environment-driven, per Master Brief) ---
# If JWT_SECRET is missing we generate a random one so local dev still works.
# Consequence: every server restart invalidates all tokens, which is exactly
# what would happen in production if you rotated the secret.
_jwt_secret_env = os.getenv("JWT_SECRET")
if not _jwt_secret_env:
    _jwt_secret_env = secrets.token_hex(32)
    logger.warning(
        "JWT_SECRET is not set! Generated an ephemeral secret for this process. "
        "All tokens will be invalidated on restart. Set JWT_SECRET in your .env file."
    )

JWT_SECRET: str = _jwt_secret_env
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


def hash_password(plain_password: str) -> str:
    """One-way transform. The plaintext password is never stored anywhere."""
    password_bytes = plain_password.encode("utf-8")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Constant-time comparison. Returns False on malformed hashes (e.g. legacy
    plaintext rows still sitting in the database) instead of raising."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            stored_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def create_access_token(user_id: int) -> str:
    """Mint a signed JWT. Claims: 'sub' (user id), 'iat' (issued at), 'exp' (expiry).
    PyJWT converts the datetimes to timestamps and enforces 'exp' on decode."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),  # subject: who this token identifies
        "iat": now,           # issued at
        "exp": now + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Verify signature + expiry and return the claims payload.
    Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError on failure -
    the caller (get_current_user) translates those into HTTP 401s."""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
