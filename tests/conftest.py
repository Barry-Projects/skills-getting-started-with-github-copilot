"""
Test configuration and fixtures for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """Sample activities data for testing."""
    return {
        "Test Activity": {
            "description": "A test activity for unit testing",
            "schedule": "Test schedule",
            "max_participants": 5,
            "participants": ["test1@example.com", "test2@example.com"]
        },
        "Empty Activity": {
            "description": "An activity with no participants",
            "schedule": "Test schedule",
            "max_participants": 10,
            "participants": []
        }
    }


@pytest.fixture
def reset_activities():
    """Reset activities to original state after each test."""
    # Store original activities
    original_activities = activities.copy()
    
    yield
    
    # Restore original activities
    activities.clear()
    activities.update(original_activities)