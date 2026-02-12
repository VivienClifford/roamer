"""Tests for CoordinatorAgent class."""
import pytest
import os
from unittest.mock import Mock, patch
from agents.coordinator_agent import CoordinatorAgent


@pytest.fixture
def coordinator_agent():
    """Create a CoordinatorAgent instance for testing."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        return CoordinatorAgent(name="TestCoordinator")


class TestParseTravelDetails:
    """Test suite for parse_travel_details method."""
    
    def test_parse_valid_travel_details(self, coordinator_agent):
        """Should extract travel details from user input."""
        expected_details = {
            "location": "Tokyo",
            "duration": 5,
            "interests": ["temples", "food"],
            "budget": "medium",
            "travel_type": "solo"
        }
        
        coordinator_agent.call_openai_api = Mock(return_value=expected_details)
        
        result = coordinator_agent.parse_travel_details("I want to go to Tokyo for 5 days")
        
        assert result["location"] == "Tokyo"
        assert result["duration"] == 5
        assert "temples" in result["interests"]
    
    def test_parse_travel_details_missing_location(self, coordinator_agent):
        """Should handle missing location field."""
        invalid_response = {"duration": 3}
        coordinator_agent.call_openai_api = Mock(return_value=invalid_response)
        
        result = coordinator_agent.parse_travel_details("Help me plan")
        
        assert result["location"] == "Unknown"
        assert "error" in result
    
    def test_parse_travel_details_with_error(self, coordinator_agent):
        """Should handle API errors gracefully."""
        error_response = {"error": "Failed to parse"}
        coordinator_agent.call_openai_api = Mock(return_value=error_response)
        
        result = coordinator_agent.parse_travel_details("invalid input")
        
        assert "error" in result
        assert result["location"] == "Unknown"
        assert result["duration"] == 3
    
    def test_parse_sets_default_values(self, coordinator_agent):
        """Should set default values for missing fields when location is present."""
        partial_response = {"location": "Paris", "duration": 3, "interests": []}
        coordinator_agent.call_openai_api = Mock(return_value=partial_response)
        
        result = coordinator_agent.parse_travel_details("Paris trip")
        
        assert result["location"] == "Paris"
        assert result["duration"] == 3
        assert result["interests"] == []


class TestPlanTrip:
    """Test suite for plan_trip method."""
    
    def test_plan_trip_success(self, coordinator_agent):
        """Should orchestrate all agents successfully."""
        coordinator_agent.parse_travel_details = Mock(return_value={
            "location": "Paris",
            "duration": 3,
            "interests": ["art"],
            "budget": "medium",
            "travel_type": "couple"
        })
        coordinator_agent.attraction_agent.find_attractions = Mock(return_value={
            "attractions": [{"name": "Louvre"}]
        })
        coordinator_agent.logistic_agent.create_itinerary = Mock(return_value={
            "days": [{"day_number": "1"}]
        })
        coordinator_agent.logistic_agent.get_transportation_suggestions = Mock(return_value={
            "transportation": [{"method": "metro"}]
        })
        
        result = coordinator_agent.plan_trip("Paris 3 days")
        
        assert result["success"] is True
        assert result["details"]["location"] == "Paris"
        assert "attractions" in result
        assert "itinerary" in result
    
    def test_plan_trip_parse_error(self, coordinator_agent):
        """Should return error when parsing fails."""
        coordinator_agent.parse_travel_details = Mock(return_value={
            "error": "Could not parse"
        })
        
        result = coordinator_agent.plan_trip("invalid")
        
        assert result["success"] is False
        assert "error" in result
    
    def test_plan_trip_handles_agent_errors(self, coordinator_agent):
        """Should collect errors from all agents."""
        coordinator_agent.parse_travel_details = Mock(return_value={
            "location": "Rome",
            "duration": 3,
            "interests": []
        })
        coordinator_agent.attraction_agent.find_attractions = Mock(return_value={
            "error": "Attractions API failed"
        })
        coordinator_agent.logistic_agent.create_itinerary = Mock(return_value={
            "error": "Itinerary API failed"
        })
        coordinator_agent.logistic_agent.get_transportation_suggestions = Mock(return_value={
            "transportation": []
        })
        
        result = coordinator_agent.plan_trip("Rome")
        
        assert result["success"] is True
        assert len(result["errors"]) >= 2
    
    def test_fetch_travel_details_delegates_to_plan_trip(self, coordinator_agent):
        """Should return structured data for main.py."""
        coordinator_agent.plan_trip = Mock(return_value={"success": True})
        
        result = coordinator_agent.fetch_travel_details("Trip request")
        
        coordinator_agent.plan_trip.assert_called_once()
        assert result["success"] is True
