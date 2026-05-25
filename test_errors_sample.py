"""
Unit tests for error handling and validation.

Run with: pytest tests/test_errors.py -v
"""

import pytest
from src.errors import (
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    validate_username,
    validate_password,
    validate_name,
    validate_subject_code,
    validate_email,
    Result,
)


class TestValidation:
    """Test input validation functions."""

    def test_validate_username_valid(self):
        """Valid username should pass."""
        result = validate_username("john.doe-123")
        assert result == "john.doe-123"

    def test_validate_username_too_short(self):
        """Username less than 3 chars should fail."""
        with pytest.raises(ValidationError, match="at least 3 characters"):
            validate_username("jo")

    def test_validate_username_too_long(self):
        """Username longer than 50 chars should fail."""
        with pytest.raises(ValidationError, match="not exceed 50"):
            validate_username("a" * 51)

    def test_validate_username_invalid_chars(self):
        """Username with invalid chars should fail."""
        with pytest.raises(ValidationError, match="can only contain"):
            validate_username("john@domain")

    def test_validate_username_empty(self):
        """Empty username should fail."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_username("")

    def test_validate_password_valid(self):
        """Valid password should pass."""
        result = validate_password("SecurePass1")
        assert result == "SecurePass1"

    def test_validate_password_too_short(self):
        """Password less than 8 chars should fail."""
        with pytest.raises(ValidationError, match="at least 8 characters"):
            validate_password("Pass1")

    def test_validate_password_no_uppercase(self):
        """Password without uppercase should fail."""
        with pytest.raises(ValidationError, match="uppercase"):
            validate_password("securepass1")

    def test_validate_password_no_lowercase(self):
        """Password without lowercase should fail."""
        with pytest.raises(ValidationError, match="lowercase"):
            validate_password("SECUREPASS1")

    def test_validate_password_no_digit(self):
        """Password without digit should fail."""
        with pytest.raises(ValidationError, match="at least one digit"):
            validate_password("SecurePass")

    def test_validate_name_valid(self):
        """Valid name should pass."""
        result = validate_name("John O'Brien-Smith")
        assert result == "John O'Brien-Smith"

    def test_validate_name_too_long(self):
        """Name longer than max should fail."""
        with pytest.raises(ValidationError):
            validate_name("A" * 101)

    def test_validate_name_invalid_chars(self):
        """Name with invalid chars should fail."""
        with pytest.raises(ValidationError):
            validate_name("John123")

    def test_validate_subject_code_valid(self):
        """Valid subject code should pass."""
        result = validate_subject_code("CS101")
        assert result == "CS101"  # Uppercase normalized

    def test_validate_subject_code_too_short(self):
        """Subject code less than 3 chars should fail."""
        with pytest.raises(ValidationError):
            validate_subject_code("CS")

    def test_validate_subject_code_too_long(self):
        """Subject code longer than 10 chars should fail."""
        with pytest.raises(ValidationError):
            validate_subject_code("VERYLONGCODE123")

    def test_validate_subject_code_invalid_chars(self):
        """Subject code with invalid chars should fail."""
        with pytest.raises(ValidationError):
            validate_subject_code("CS-101")

    def test_validate_email_valid(self):
        """Valid email should pass."""
        result = validate_email("user@example.com")
        assert result == "user@example.com"

    def test_validate_email_invalid(self):
        """Invalid email should fail."""
        with pytest.raises(ValidationError):
            validate_email("not-an-email")


class TestResult:
    """Test Result wrapper class."""

    def test_result_ok(self):
        """Result.ok() should create successful result."""
        result = Result.ok(data={"id": 1})
        assert result.success is True
        assert result.data == {"id": 1}
        assert result.error is None

    def test_result_err(self):
        """Result.err() should create error result."""
        result = Result.err("Something went wrong")
        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.data is None

    def test_result_bool(self):
        """Result should be truthy/falsy based on success."""
        ok_result = Result.ok()
        err_result = Result.err("error")
        
        assert bool(ok_result) is True
        assert bool(err_result) is False

    def test_result_repr(self):
        """Result repr should show status."""
        ok = Result.ok(data=42)
        err = Result.err("fail")
        
        assert "Result.ok" in repr(ok)
        assert "Result.err" in repr(err)


class TestExceptions:
    """Test custom exception hierarchy."""

    def test_validation_error_hierarchy(self):
        """ValidationError should inherit from AttendanceAppError."""
        from src.errors import AttendanceAppError
        
        err = ValidationError("test")
        assert isinstance(err, AttendanceAppError)
        assert isinstance(err, Exception)

    def test_authorization_error_hierarchy(self):
        """AuthorizationError should inherit from AttendanceAppError."""
        from src.errors import AttendanceAppError
        
        err = AuthorizationError("test")
        assert isinstance(err, AttendanceAppError)
