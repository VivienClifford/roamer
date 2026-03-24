"""Tests for AttractionAgent class."""
import pytest
import os
from unittest.mock import Mock, patch
from agents.attraction_agent import AttractionAgent


@pytest.fixture
def attraction_agent():
    """Create an AttractionAgent instance for testing."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        return AttractionAgent(name="TestAttractionAgent")


class TestFindAttractions:
    """Test suite for find_attractions method."""
    
    def test_find_attractions_success(self, attraction_agent):
        """Should return attractions when API response is valid."""
        expected_response = {
            "attractions": [
                {
                    "name": "Eiffel Tower",
                    "description": "Iconic iron tower",
                    "hours_needed": "2-3 hours",
                    "category": "landmark"
                }
            ]
        }
        
        attraction_agent.call_openai_api = Mock(return_value=expected_response)
        
        result = attraction_agent.find_attractions("Paris", ["landmarks"], 3)
        
        assert "attractions" in result
        assert len(result["attractions"]) == 1
        assert result["attractions"][0]["name"] == "Eiffel Tower"
    
    def test_find_attractions_with_multiple_interests(self, attraction_agent):
        """Should format multiple interests correctly."""
        expected_response = {"attractions": []}
        attraction_agent.call_openai_api = Mock(return_value=expected_response)
        
        result = attraction_agent.find_attractions("Tokyo", ["temples", "food", "museums"], 5)
        
        # Verify the prompt was built correctly
        call_args = attraction_agent.call_openai_api.call_args
        assert "temples, food, museums" in call_args[1]["user_prompt"]
    
    def test_find_attractions_with_empty_interests(self, attraction_agent):
        """Should handle empty interests list."""
        expected_response = {"attractions": []}
        attraction_agent.call_openai_api = Mock(return_value=expected_response)
        
        result = attraction_agent.find_attractions("Rome", [], 3)
        
        call_args = attraction_agent.call_openai_api.call_args
        assert "general tourism" in call_args[1]["user_prompt"]
    
    def test_find_attractions_invalid_response(self, attraction_agent):
        """Should handle invalid response gracefully."""
        invalid_response = {"error": "API failed"}
        attraction_agent.call_openai_api = Mock(return_value=invalid_response)
        
        result = attraction_agent.find_attractions("London", ["museums"], 3)
        
        assert "attractions" in result
        assert result["attractions"] == []
    
    def test_find_attractions_uses_correct_config(self, attraction_agent):
        """Should use correct config values for API call."""
        attraction_agent.call_openai_api = Mock(return_value={"attractions": []})
        
        attraction_agent.find_attractions("Berlin", ["history"], 2)
        
        call_args = attraction_agent.call_openai_api.call_args
        assert call_args[1]["max_tokens"] > 0  # Should use TOKENS_ATTRACTION
