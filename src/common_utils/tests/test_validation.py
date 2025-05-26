"""
Tests for validation utilities.
"""

import pytest
from ..validation import (
    ValidationError,
    Validator,
    validate_email,
    validate_username,
    validate_password
)

def test_validation_error():
    """Test ValidationError class."""
    error = ValidationError("email", "Invalid email format")
    assert error.field == "email"
    assert error.message == "Invalid email format"

def test_validator():
    """Test Validator class."""
    validator = Validator()
    
    # Test adding error
    validator.add_error("username", "Too short")
    assert validator.has_errors()
    assert validator.get_errors() == {"username": "Too short"}
    
    # Test min length validation
    validator = Validator()
    validator.validate_min_length("username", "a", 3)
    assert validator.has_errors()
    
    # Test max length validation
    validator = Validator()
    validator.validate_max_length("email", "test@example.com", 10)
    assert validator.has_errors()
    
    # Test length range validation
    validator = Validator()
    validator.validate_length_range("password", "123", 4, 8)
    assert validator.has_errors()
    
    # Test number range validation
    validator = Validator()
    validator.validate_number_range("age", "25", 18, 100)
    assert not validator.has_errors()
    
    validator = Validator()
    validator.validate_number_range("age", "15", 18, 100)
    assert validator.has_errors()

def test_validate_email():
    """Test email validation."""
    assert validate_email("test@example.com")
    assert validate_email("user.name@domain.co.uk")
    assert not validate_email("invalid-email")
    assert not validate_email("test@")
    assert not validate_email("@example.com")

def test_validate_username():
    """Test username validation."""
    assert validate_username("user123")
    assert validate_username("user-name")
    assert validate_username("user_name")
    assert not validate_username("a")  # Too short
    assert not validate_username("invalid@username")  # Invalid chars
    assert not validate_username("a" * 17)  # Too long

def test_validate_password():
    """Test password validation."""
    assert validate_password("Password123")
    assert validate_password("12345678a")
    assert not validate_password("short")  # Too short
    assert not validate_password("password")  # No numbers
    assert not validate_password("12345678")  # No letters 