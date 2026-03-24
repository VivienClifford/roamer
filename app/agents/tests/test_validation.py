"""Tests for ResponseValidator class."""
import pytest
from agents.validation import ResponseValidator


class TestValidateAttractions:
    """Test suite for validate_attractions method."""
    
    def test_valid_attractions_response(self):
        """Should validate correct attractions structure."""
        valid_data = {
            "attractions": [
                {
                    "name": "Louvre",
                    "description": "Art museum",
                    "hours_needed": "3-4 hours",
                    "category": "museum"
                }
            ]
        }
        
        is_valid, error = ResponseValidator.validate_attractions(valid_data)
        
        assert is_valid is True
        assert error is None
    
    def test_attractions_with_error_key(self):
        """Should reject response with error key."""
        invalid_data = {"error": "API failed"}
        
        is_valid, error = ResponseValidator.validate_attractions(invalid_data)
        
        assert is_valid is False
        assert "API failed" in error
    
    def test_attractions_missing_key(self):
        """Should reject missing attractions key."""
        invalid_data = {"results": []}
        
        is_valid, error = ResponseValidator.validate_attractions(invalid_data)
        
        assert is_valid is False
        assert "Missing 'attractions' key" in error
    
    def test_attractions_not_list(self):
        """Should reject if attractions is not a list."""
        invalid_data = {"attractions": {"name": "Museum"}}
        
        is_valid, error = ResponseValidator.validate_attractions(invalid_data)
        
        assert is_valid is False
        assert "must be a list" in error
    
    def test_attraction_missing_required_fields(self):
        """Should reject attraction missing required fields."""
        invalid_data = {
            "attractions": [
                {
                    "name": "Museum",
                    "description": "Art"
                    # Missing hours_needed and category
                }
            ]
        }
        
        is_valid, error = ResponseValidator.validate_attractions(invalid_data)
        
        assert is_valid is False
        assert "missing fields" in error


class TestValidateItinerary:
    """Test suite for validate_itinerary method."""
    
    def test_valid_itinerary_response(self):
        """Should validate correct itinerary structure."""
        valid_data = {
            "days": [
                {
                    "day_number": "1",
                    "title": "Day 1",
                    "activities": [
                        {"time": "09:00", "activity": "Breakfast", "duration": "1 hour"}
                    ]
                }
            ]
        }
        
        is_valid, error = ResponseValidator.validate_itinerary(valid_data)
        
        assert is_valid is True
        assert error is None
    
    def test_itinerary_with_error_key(self):
        """Should reject response with error key."""
        invalid_data = {"error": "Failed"}
        
        is_valid, error = ResponseValidator.validate_itinerary(invalid_data)
        
        assert is_valid is False
    
    def test_itinerary_missing_days_key(self):
        """Should reject missing days key."""
        invalid_data = {"schedule": []}
        
        is_valid, error = ResponseValidator.validate_itinerary(invalid_data)
        
        assert is_valid is False
        assert "Missing 'days' key" in error
    
    def test_itinerary_days_not_list(self):
        """Should reject if days is not a list."""
        invalid_data = {"days": {"day": 1}}
        
        is_valid, error = ResponseValidator.validate_itinerary(invalid_data)
        
        assert is_valid is False
    
    def test_itinerary_activities_not_list(self):
        """Should reject if activities is not a list."""
        invalid_data = {
            "days": [
                {
                    "day_number": "1",
                    "activities": "breakfast"
                }
            ]
        }
        
        is_valid, error = ResponseValidator.validate_itinerary(invalid_data)
        
        assert is_valid is False


class TestValidateTransportation:
    """Test suite for validate_transportation method."""
    
    def test_valid_transportation_response(self):
        """Should validate correct transportation structure."""
        valid_data = {
            "transportation": [
                {
                    "method": "Metro",
                    "description": "Fast",
                    "cost_estimate": "$5/day",
                    "recommended_for": "Daily travel"
                }
            ]
        }
        
        is_valid, error = ResponseValidator.validate_transportation(valid_data)
        
        assert is_valid is True
        assert error is None
    
    def test_transportation_with_error_key(self):
        """Should reject response with error key."""
        invalid_data = {"error": "API failed"}
        
        is_valid, error = ResponseValidator.validate_transportation(invalid_data)
        
        assert is_valid is False
    
    def test_transportation_empty_response(self):
        """Should reject empty response."""
        invalid_data = {}
        
        is_valid, error = ResponseValidator.validate_transportation(invalid_data)
        
        assert is_valid is False
    
    def test_transportation_missing_key(self):
        """Should reject missing transportation key."""
        invalid_data = {"methods": []}
        
        is_valid, error = ResponseValidator.validate_transportation(invalid_data)
        
        assert is_valid is False
        assert "Missing 'transportation' key" in error
    
    def test_transportation_not_list(self):
        """Should reject if transportation is not a list."""
        invalid_data = {"transportation": {"method": "Metro"}}
        
        is_valid, error = ResponseValidator.validate_transportation(invalid_data)
        
        assert is_valid is False


class TestValidateTravelDetails:
    """Test suite for validate_travel_details method."""
    
    def test_valid_travel_details(self):
        """Should validate correct travel details structure."""
        valid_data = {
            "location": "Paris",
            "duration": 5,
            "interests": ["art", "food"],
            "budget": "medium",
            "travel_type": "couple"
        }
        
        is_valid, error = ResponseValidator.validate_travel_details(valid_data)
        
        assert is_valid is True
        assert error is None
    
    def test_travel_details_with_error_key(self):
        """Should reject response with error key."""
        invalid_data = {"error": "Parse failed"}
        
        is_valid, error = ResponseValidator.validate_travel_details(invalid_data)
        
        assert is_valid is False
    
    def test_travel_details_missing_location(self):
        """Should reject missing location field."""
        invalid_data = {"duration": 5}
        
        is_valid, error = ResponseValidator.validate_travel_details(invalid_data)
        
        assert is_valid is False
        assert "Missing required 'location' field" in error
    
    def test_travel_details_invalid_duration_type(self):
        """Should reject non-integer duration."""
        invalid_data = {
            "location": "Paris",
            "duration": "5 days"
        }
        
        is_valid, error = ResponseValidator.validate_travel_details(invalid_data)
        
        assert is_valid is False
        assert "'duration' must be an integer" in error
