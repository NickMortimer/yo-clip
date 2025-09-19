"""Tests for utility functions."""

from yoclip.utils import validate_input, format_output


def test_validate_email_valid():
    """Test email validation with valid email."""
    assert validate_input("test@example.com", "email") is True


def test_validate_email_invalid():
    """Test email validation with invalid email."""
    assert validate_input("invalid-email", "email") is False


def test_validate_email_empty():
    """Test email validation with empty string."""
    assert validate_input("", "email") is False


def test_validate_input_default():
    """Test validation with default type."""
    assert validate_input("any string") is True
