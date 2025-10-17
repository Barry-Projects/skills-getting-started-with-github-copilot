"""
Tests for the FastAPI application endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestApp:
    """Test class for FastAPI application."""
    
    def setup_method(self):
        """Setup method to reset activities before each test."""
        # Store original activities
        self.original_activities = activities.copy()
        
    def teardown_method(self):
        """Teardown method to restore activities after each test."""
        # Restore original activities
        activities.clear()
        activities.update(self.original_activities)
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI application."""
        return TestClient(app)
    
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"
    
    def test_get_activities(self, client):
        """Test getting all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that we get a dictionary of activities
        assert isinstance(data, dict)
        
        # Check that each activity has required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity."""
        # Get an existing activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        activity_name = list(activities_data.keys())[0]
        
        # Test signup
        response = client.post(
            f"/activities/{activity_name}/signup?email=newuser@test.com"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newuser@test.com" in data["message"]
        assert activity_name in data["message"]
        
        # Verify user was added to the activity
        updated_activities = client.get("/activities").json()
        assert "newuser@test.com" in updated_activities[activity_name]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for a non-existent activity."""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@test.com"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_user(self, client):
        """Test that duplicate signup is prevented."""
        # Get an existing activity with participants
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        # Find an activity with existing participants
        activity_name = None
        existing_email = None
        for name, data in activities_data.items():
            if data["participants"]:
                activity_name = name
                existing_email = data["participants"][0]
                break
        
        if activity_name and existing_email:
            response = client.post(
                f"/activities/{activity_name}/signup?email={existing_email}"
            )
            assert response.status_code == 400
            data = response.json()
            assert data["detail"] == "Student already signed up for this activity"
    
    def test_unregister_from_activity_success(self, client):
        """Test successful unregistration from an activity."""
        # First, sign up a user
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        activity_name = list(activities_data.keys())[0]
        
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email=testunregister@test.com"
        )
        assert signup_response.status_code == 200
        
        # Now unregister the user
        response = client.delete(
            f"/activities/{activity_name}/unregister?email=testunregister@test.com"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "testunregister@test.com" in data["message"]
        assert activity_name in data["message"]
        
        # Verify user was removed from the activity
        updated_activities = client.get("/activities").json()
        assert "testunregister@test.com" not in updated_activities[activity_name]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistration from a non-existent activity."""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=test@test.com"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_nonexistent_user(self, client):
        """Test unregistration of a user not signed up for the activity."""
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        activity_name = list(activities_data.keys())[0]
        
        response = client.delete(
            f"/activities/{activity_name}/unregister?email=nonexistent@test.com"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student not signed up for this activity"
    
    def test_activities_data_integrity(self, client):
        """Test that activities maintain data integrity."""
        # Get initial activities
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        
        # Test signup and unregister cycle
        activity_name = list(initial_data.keys())[0]
        test_email = "integrity@test.com"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        assert signup_response.status_code == 200
        
        # Check that participant count increased
        after_signup = client.get("/activities").json()
        initial_count = len(initial_data[activity_name]["participants"])
        after_signup_count = len(after_signup[activity_name]["participants"])
        assert after_signup_count == initial_count + 1
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={test_email}"
        )
        assert unregister_response.status_code == 200
        
        # Check that we're back to original state
        final_response = client.get("/activities")
        final_data = final_response.json()
        final_count = len(final_data[activity_name]["participants"])
        assert final_count == initial_count
        assert test_email not in final_data[activity_name]["participants"]
    
    def test_email_validation(self, client):
        """Test that emails are properly handled in URLs."""
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        activity_name = list(activities_data.keys())[0]
        
        # Test email with special characters (URL encoding)
        import urllib.parse
        special_email = "test+user@example.com"
        encoded_email = urllib.parse.quote(special_email)
        response = client.post(
            f"/activities/{activity_name}/signup?email={encoded_email}"
        )
        assert response.status_code == 200
        
        # Verify the email was properly stored
        updated_activities = client.get("/activities").json()
        assert special_email in updated_activities[activity_name]["participants"]