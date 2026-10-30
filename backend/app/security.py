"""
Password hashing and opaque session-token helpers.

Nothing outside this module should hash a password or generate a session token,
so hashing parameters and token format can be changed in one place.
"""
import hashlib
import secrets

from pwdlib import PasswordHash

# Argon2id with the library's recommended parameters (OWASP's first choice).
_password_hash = PasswordHash.recommended()


def hash_password(raw_password: str) -> str:
    return _password_hash.hash(raw_password)


def verify_password(raw_password: str, password_hash: str) -> bool:
    try:
        return _password_hash.verify(raw_password, password_hash)
    except Exception:
        # A corrupted hash in the database means "cannot authenticate", not a 500.
        return False


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def token_key(token: str) -> str:
    """Return the Redis key suffix for a session token.

    Only the digest is stored, so a Redis dump or a careless MONITOR does not
    hand out usable sessions. SHA-256 is the right tool here: the token is
    already 256 random bits, this is not password storage.
    """
    return hashlib.sha256(token.encode()).hexdigest()
