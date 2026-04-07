"""Pytest configuration and fixtures for FastAPI tests with dependency injection."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.app import app


@pytest.fixture
def mock_activities():
    """
    Fixture providing a fresh in-memory database of test activities.
    Each test gets a clean copy with predictable test data.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["alice@example.com"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["bob@example.com"]
        },
        "Soccer Team": {
            "description": "Train for matches and build teamwork on the field",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 18,
            "participants": []
        },
    }


@pytest.fixture
def client(mock_activities):
    """
    Fixture providing a FastAPI TestClient with dependency injection.
    Uses unittest.mock.patch to inject fresh mock_activities for each test.
    This ensures app.py remains unchanged while enabling test isolation.
    """
    with patch("src.app.activities", mock_activities):
        yield TestClient(app)
