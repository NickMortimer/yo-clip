"""Test configuration and fixtures."""

import pytest
from typer.testing import CliRunner
from yoclip.main import app


@pytest.fixture
def runner():
    """CLI test runner fixture."""
    return CliRunner()


@pytest.fixture
def sample_data():
    """Sample data for testing."""
    return {
        "name": "test_user",
        "email": "test@example.com",
        "count": 3
    }
