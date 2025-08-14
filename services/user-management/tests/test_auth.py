"""
Test per auth module
"""

import pytest

from auth import (
    create_access_token,
    hash_password,
    is_email_valid,
    validate_password_strength,
    verify_password,
    verify_token,
)


class TestPasswordSecurity:
    """Test per password security functions."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password(self):
        """Test password verification."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    def test_validate_password_strength(self):
        """Test password strength validation."""
        # Strong password
        result = validate_password_strength("StrongPassword123!")
        assert result["is_valid"] is True
        assert result["score"] >= 4

        # Weak password
        result = validate_password_strength("weak")
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0


class TestJWTTokens:
    """Test per JWT token management."""

    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "user123", "role": "user"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        with pytest.raises(Exception):  # Should raise HTTPException
            verify_token("invalid_token")


class TestUtilities:
    """Test per utility functions."""

    def test_is_email_valid(self):
        """Test email validation."""
        assert is_email_valid("test@example.com") is True
        assert is_email_valid("user.name+tag@domain.co.uk") is True
        assert is_email_valid("invalid-email") is False
        assert is_email_valid("@domain.com") is False
        assert is_email_valid("test@") is False
