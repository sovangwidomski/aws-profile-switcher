"""
Test suite for AWS Profile Switcher

This package contains all tests for the aws-profile-switcher project.

Test Structure:
- test_cli.py: Tests for CLI functions and interactive mode
- (Add more test modules here as the project grows)

Running Tests:
    pytest                    # Run all tests
    pytest tests/             # Run tests from this directory
    pytest tests/test_cli.py  # Run specific test file
    pytest -v                 # Verbose output
    pytest --cov=awsprofile   # Run with coverage

Requirements for Testing:
    pip install pytest pytest-cov

Note: Tests use mocking to avoid requiring actual AWS credentials or AWS CLI calls.
"""

# Version info for test compatibility
__version__ = "1.5.1"

# Test configuration constants
TEST_TIMEOUT = 10  # seconds for subprocess timeouts in tests
MOCK_PROFILES = {
    'default': {'account': '123456789012', 'user': 'arn:aws:iam::123456789012:user/testuser'},
    'work': {'account': '987654321098', 'user': 'arn:aws:iam::987654321098:user/workuser'},
    'personal': {'account': '555666777888', 'user': 'arn:aws:iam::555666777888:user/personaluser'}
}

# Import pytest fixtures that might be used across multiple test modules
# (Currently none, but this is where you'd put shared fixtures)

# Ensure the awsprofile module can be imported for testing
try:
    import awsprofile
except ImportError as e:
    raise ImportError(
        f"Cannot import awsprofile module: {e}\n"
        "Make sure you've installed the package in development mode:\n"
        "pip install -e ."
    ) from e