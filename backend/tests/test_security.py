"""Unit tests for app/security.py: hashing and token format."""
import re

from app.security import hash_password, new_session_token, token_key, verify_password

PASSWORD = "correct-horse-battery"


def test_password_is_never_stored_in_clear():
    stored = hash_password(PASSWORD)

    assert PASSWORD not in stored
    # Argon2id, and the marker is what makes the algorithm identifiable later.
    assert stored.startswith("$argon2id$")


def test_verify_accepts_the_right_password_only():
    stored = hash_password(PASSWORD)

    assert verify_password(PASSWORD, stored) is True
    assert verify_password("wrong-password", stored) is False


def test_same_password_hashes_differently():
    # A unique salt per hash: two admins with the same password must not share a hash.
    assert hash_password(PASSWORD) != hash_password(PASSWORD)


def test_corrupted_hash_fails_closed_instead_of_raising():
    assert verify_password(PASSWORD, "not-a-valid-hash") is False


def test_session_tokens_are_unique_and_url_safe():
    first, second = new_session_token(), new_session_token()

    assert first != second
    assert len(first) >= 43  # 32 random bytes, base64url without padding
    assert re.fullmatch(r"[A-Za-z0-9_-]+", first)


def test_token_key_is_a_digest_not_the_token():
    token = new_session_token()
    key = token_key(token)

    assert key != token
    assert token not in key
    assert re.fullmatch(r"[0-9a-f]{64}", key)  # sha256 hexdigest
    # Deterministic, so the same token always finds the same Redis entry.
    assert token_key(token) == key
    assert token_key(new_session_token()) != key
