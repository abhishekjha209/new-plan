"""
Day 8: Real password authentication. Day 10: the two-token model.

This module owns two security boundaries:
  1. Password storage  -> bcrypt (slow + salted, defeats offline brute force)
  2. Session identity  -> JWT (signed, stateless, self-expiring access tokens)

Day 10 update - the token split:
  - Access tokens stay stateless but are now SHORT-lived (15 min default). The theft
    window shrinks to minutes, so we no longer need to revoke them.
  - Refresh tokens are the opposite: long-lived, OPAQUE (random strings, no claims),
    and STATEFUL - each is a row in Postgres, stored SHA-256-hashed. That state is
    what makes logout/revocation possible: revoke the row and the renewal chain dies.
  - Rotation: every /auth/refresh mints a new refresh token and revokes the old one.

Key properties to remember:
  - bcrypt's slowness IS the defense. Do not "optimize" it away.
  - A JWT is SIGNED, not ENCRYPTED. Anyone can read its payload.
    Never put secrets, PII, or anything sensitive in the claims.
  - Access tokens cannot be revoked - that is fine now, because they die in minutes.
    What CAN be revoked is the refresh token: that is what "logout" means.
"""
import os
import secrets
import hashlib
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
# Day 10: access tokens shrink from 60 min to 15 min. Short access + long refresh
# is the whole point of the two-token model.
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "15"))

# --- Refresh token configuration (Day 10) ---
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


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
    PyJWT converts the datetimes to timestamps and enforces 'exp' on decode.
    Deliberately NO role claim (Day 9): the DB is the authority on permissions."""
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


# --- Refresh tokens (Day 10) ---

def hash_refresh_token(raw: str) -> str:
    """SHA-256 of the opaque token. Fast hash is safe here: the token is
    high-entropy random (secrets.token_urlsafe(48) ~ 384 bits), so there is
    no brute-force surface to stretch. bcrypt is for human passwords."""
    return hashlib.sha256(raw.encode()).hexdigest()


def generate_refresh_token() -> tuple[str, str]:
    """Mint an opaque refresh token. Returns (raw_token, sha256_hex).
    The raw value goes to the client exactly once; only the hash is persisted,
    so a DB leak does not leak usable refresh tokens."""
    raw = secrets.token_urlsafe(48)
    return raw, hash_refresh_token(raw)


def refresh_expiry() -> datetime:
    """Naive UTC timestamp, matching the naive DateTime columns func.now() populates."""
    return datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
