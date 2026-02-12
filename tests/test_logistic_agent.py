"""Tests for LogisticAgent class."""
import pytest
import os
import json
from unittest.mock import Mock, patch
from agents.logistic_agent import LogisticAgent


@pytest.fixture
def logistic_agent():
    """Create a LogisticAgent instance for testing."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        return LogisticAgent(name="TestLogistic")


class TestCreateItinerary:
    """Test suite for create_itinerary method."""
    
    def test_create_itinerary_success(self, logistic_agent):
        """Should create valid itinerary from attractions."""
        attractions = {
            "attractions": [
                {"name": "Museum", "hours_needed": "2 hours"}
            ]
        }
        expected_itinerary = {
            "days": [
                {
                    "day_number": "1",
                    "title": "Exploration",
                    "activities": [
                        {"time": "09:00", "activity": "Visit Museum", "duration": "2 hours"}
                    ],
                    "meals": {"breakfast": "Hotel", "lunch": "Café", "dinner": "Restaurant"},
                    "notes": "Rest in afternoon"
                }
            ]
        }
        
        logistic_agent.call_openai_api = Mock(return_value=expected_itinerary)
        
        result = logistic_agent.create_itinerary("Paris", 3, attractions)
        
        assert "days" in result
        assert len(result["days"]) > 0
    
    def test_create_itinerary_with_multiple_days(self, logistic_agent):
        """Should handle multi-day itineraries."""
        attractions = {"attractions": [{"name": "Site1"}, {"name": "Site2"}]}
        expected = {"days": [{"day_number": f"{i}"} for i in range(1, 4)]}
        
        logistic_agent.call_openai_api = Mock(return_value=expected)
        
        result = logistic_agent.create_itinerary("London", 3, attractions)
        
        assert len(result["days"]) == 3
    
    def test_create_itinerary_serializes_attractions(self, logistic_agent):
        """Should serialize attractions dict to JSON string."""
        attractions = {"attractions": [{"name": "Tower"}]}
        logistic_agent.call_openai_api = Mock(return_value={"days": []})
        
        logistic_agent.create_itinerary("London", 1, attractions)
        
        call_args = logistic_agent.call_openai_api.call_args
        prompt = call_args[1]["user_prompt"]
        assert '"name": "Tower"' in prompt
    
    def test_create_itinerary_invalid_response(self, logistic_agent):
        """Should handle invalid itinerary response."""
        attractions = {"attractions": []}
        invalid_response = {"error": "API error"}
        
        logistic_agent.call_openai_api = Mock(return_value=invalid_response)
        
        result = logistic_agent.create_itinerary("Rome", 3, attractions)
        
        assert result["days"] == []


class TestGetTransportationSuggestions:
    """Test suite for get_transportation_suggestions method."""
    
    def test_get_transportation_success(self, logistic_agent):
        """Should return transportation suggestions."""
        expected = {
            "transportation": [
                {
                    "method": "Metro",
                    "description": "Fast and cheap",
                    "cost_estimate": "$5/day",
                    "recommended_for": "Getting around"
                }
            ]
        }
        
        logistic_agent.call_openai_api = Mock(return_value=expected)
        
        result = logistic_agent.get_transportation_suggestions("Tokyo")
        
        assert "transportation" in result
        assert result["transportation"][0]["method"] == "Metro"
    
    def test_get_transportation_multiple_methods(self, logistic_agent):
        """Should return multiple transportation options."""
        expected = {
            "transportation": [
                {"method": "Metro", "description": "Fast", "cost_estimate": "$5/day", "recommended_for": "Daily"},
                {"method": "Taxi", "description": "Convenient", "cost_estimate": "$20/day", "recommended_for": "Night"},
                {"method": "Bike", "description": "Eco-friendly", "cost_estimate": "$2/day", "recommended_for": "Sightseeing"}
            ]
        }
        
        logistic_agent.call_openai_api = Mock(return_value=expected)
        
        result = logistic_agent.get_transportation_suggestions("Amsterdam")
        
        assert len(result["transportation"]) == 3
    
    def test_get_transportation_invalid_response(self, logistic_agent):
        """Should handle invalid response gracefully."""
        invalid_response = {"error": "API error"}
        
        logistic_agent.call_openai_api = Mock(return_value=invalid_response)
        
        result = logistic_agent.get_transportation_suggestions("Berlin")
        
        assert result["transportation"] == []
    
    def test_get_transportation_uses_correct_config(self, logistic_agent):
        """Should use correct configuration values."""
        logistic_agent.call_openai_api = Mock(return_value={"transportation": []})
        
        logistic_agent.get_transportation_suggestions("Rome")
        
        call_args = logistic_agent.call_openai_api.call_args
        assert call_args[1]["max_tokens"] > 0
