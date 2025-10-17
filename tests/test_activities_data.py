"""
Tests for the activities data structure and validation.
"""

import pytest
from src.app import activities


class TestActivitiesData:
    """Test class for activities data structure."""
    
    def test_activities_structure(self):
        """Test that all activities have the required structure."""
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            # Check that activity name is a string
            assert isinstance(activity_name, str)
            assert len(activity_name) > 0
            
            # Check that activity data is a dictionary
            assert isinstance(activity_data, dict)
            
            # Check that all required fields are present
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in activity '{activity_name}'"
            
            # Check field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Check that max_participants is positive
            assert activity_data["max_participants"] > 0
            
            # Check that participants list contains valid emails (basic check)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant
                assert len(participant) > 0
    
    def test_activities_capacity(self):
        """Test that no activity exceeds its maximum capacity."""
        for activity_name, activity_data in activities.items():
            participants_count = len(activity_data["participants"])
            max_participants = activity_data["max_participants"]
            
            assert participants_count <= max_participants, \
                f"Activity '{activity_name}' has {participants_count} participants " \
                f"but max is {max_participants}"
    
    def test_no_duplicate_participants(self):
        """Test that there are no duplicate participants in any activity."""
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            unique_participants = set(participants)
            
            assert len(participants) == len(unique_participants), \
                f"Activity '{activity_name}' has duplicate participants: {participants}"
    
    def test_email_format_basic(self):
        """Test basic email format validation for existing participants."""
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                # Basic email validation
                assert "@" in participant
                assert "." in participant.split("@")[1]  # Domain should have a dot
                assert len(participant.split("@")) == 2  # Should have exactly one @
                assert not participant.startswith("@")
                assert not participant.endswith("@")
    
    def test_activities_have_content(self):
        """Test that activities have meaningful content."""
        for activity_name, activity_data in activities.items():
            # Description should not be empty
            assert len(activity_data["description"].strip()) > 0
            
            # Schedule should not be empty
            assert len(activity_data["schedule"].strip()) > 0
            
            # Activity name should not be empty
            assert len(activity_name.strip()) > 0