"""Unit tests for ConversationManager class using TDD principles."""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from agents.conversation_manager import ConversationManager


@pytest.fixture
def conversation_manager():
    """Create a ConversationManager instance for testing."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        return ConversationManager()


class TestParseTravelDetails:
    """Test suite for parse_travel_details - extract only explicitly mentioned fields."""
    
    def test_parse_location_only(self, conversation_manager):
        """Should extract only location when that's all provided."""
        expected_details = {"location": "Paris"}
        conversation_manager.call_openai_api = Mock(return_value=expected_details)
        
        result = conversation_manager.parse_travel_details("Paris")
        
        assert result["location"] == "Paris"
        assert "duration" not in result
        assert "interests" not in result
    
    def test_parse_location_and_duration(self, conversation_manager):
        """Should extract location and duration when both mentioned."""
        expected_details = {"location": "Tokyo", "duration": 5}
        conversation_manager.call_openai_api = Mock(return_value=expected_details)
        
        result = conversation_manager.parse_travel_details("Tokyo for 5 days")
        
        assert result["location"] == "Tokyo"
        assert result["duration"] == 5
        assert "interests" not in result
    
    def test_parse_all_fields_when_provided(self, conversation_manager):
        """Should extract all fields when explicitly mentioned."""
        expected_details = {
            "location": "Barcelona",
            "duration": 4,
            "interests": ["hiking", "food"],
            "budget": "high",
            "travel_type": "couple"
        }
        conversation_manager.call_openai_api = Mock(return_value=expected_details)
        
        result = conversation_manager.parse_travel_details(
            "Barcelona for 4 days, hiking and food, high budget, traveling with partner"
        )
        
        assert result["location"] == "Barcelona"
        assert result["duration"] == 4
        assert "hiking" in result["interests"]
        assert result["budget"] == "high"
        assert result["travel_type"] == "couple"
    
    def test_parse_removes_null_values(self, conversation_manager):
        """Should remove null/None values from response."""
        response_with_nulls = {
            "location": "Rome",
            "duration": None,
            "interests": None,
            "budget": None
        }
        conversation_manager.call_openai_api = Mock(return_value=response_with_nulls)
        
        result = conversation_manager.parse_travel_details("Rome")
        
        assert result["location"] == "Rome"
        assert "duration" not in result
        assert "interests" not in result
        assert "budget" not in result
    
    def test_parse_missing_location_returns_error(self, conversation_manager):
        """Should return error if location is missing."""
        details_without_location = {"duration": 3, "interests": ["museums"]}
        conversation_manager.call_openai_api = Mock(return_value=details_without_location)
        
        result = conversation_manager.parse_travel_details("Just interested in museums")
        
        assert "error" in result
        assert result["error"] == "Location is required"
    
    def test_parse_api_error_handling(self, conversation_manager):
        """Should handle API errors gracefully."""
        error_response = {"error": "API call failed"}
        conversation_manager.call_openai_api = Mock(return_value=error_response)
        
        result = conversation_manager.parse_travel_details("Paris")
        
        assert "error" in result
        assert result["error"] == "Failed to parse travel details"
    
    def test_parse_uses_json_response_format(self, conversation_manager):
        """Should use use_json_response=True for parsing."""
        conversation_manager.call_openai_api = Mock(
            return_value={"location": "Paris"}
        )
        
        conversation_manager.parse_travel_details("Paris")
        
        # Verify call was made with use_json_response=True
        call_kwargs = conversation_manager.call_openai_api.call_args[1]
        assert call_kwargs["use_json_response"] is True
        assert call_kwargs["temperature"] == 0.2


class TestAnalyzeMissingInfo:
    """Test suite for analyze_missing_info - identify missing and provided fields."""
    
    def test_analyze_location_only(self, conversation_manager):
        """Should identify missing fields when only location provided."""
        analysis_response = {
            "provided": ["location"],
            "missing": ["duration", "interests"],
            "unclear": {},
            "confidence": 50
        }
        conversation_manager.call_openai_api = Mock(return_value=analysis_response)
        
        result = conversation_manager.analyze_missing_info("Paris")
        
        assert "location" in result["provided"]
        assert "duration" in result["missing"]
        assert "interests" in result["missing"]
        assert result["confidence"] == 50
    
    def test_analyze_all_provided(self, conversation_manager):
        """Should show high confidence when all info provided."""
        analysis_response = {
            "provided": ["location", "duration", "interests"],
            "missing": [],
            "unclear": {},
            "confidence": 90
        }
        conversation_manager.call_openai_api = Mock(return_value=analysis_response)
        
        result = conversation_manager.analyze_missing_info(
            "Paris 4 days, museums and cafes"
        )
        
        assert result["missing"] == []
        assert result["confidence"] == 90
    
    def test_analyze_includes_defaults_for_missing_keys(self, conversation_manager):
        """Should provide defaults for missing analysis keys."""
        incomplete_response = {"provided": ["location"]}
        conversation_manager.call_openai_api = Mock(return_value=incomplete_response)
        
        result = conversation_manager.analyze_missing_info("Paris")
        
        assert "missing" in result
        assert "unclear" in result
        assert "confidence" in result
    
    def test_analyze_fallback_on_error(self, conversation_manager):
        """Should provide fallback values on error."""
        error_response = {"error": "Analysis failed"}
        conversation_manager.call_openai_api = Mock(return_value=error_response)
        
        result = conversation_manager.analyze_missing_info("Paris")
        
        assert result["provided"] == []
        assert set(result["missing"]) == {"location", "duration", "interests"}
        assert result["confidence"] == 0


class TestShouldContinuePlanning:
    """Test suite for should_continue_planning - validation logic."""
    
    def test_reject_missing_location(self, conversation_manager):
        """Should reject planning without location."""
        parsed = {}
        analysis = {"missing": ["location"]}
        
        should_continue, reason = conversation_manager.should_continue_planning(parsed, analysis)
        
        assert should_continue is False
        assert "where you want to go" in reason
    
    def test_reject_missing_duration(self, conversation_manager):
        """Should reject planning without duration."""
        parsed = {"location": "Paris"}
        analysis = {"missing": ["duration"]}
        
        should_continue, reason = conversation_manager.should_continue_planning(parsed, analysis)
        
        assert should_continue is False
        assert "how long" in reason
    
    def test_reject_missing_interests(self, conversation_manager):
        """Should reject planning without interests."""
        parsed = {"location": "Paris", "duration": 4}
        analysis = {"missing": ["interests"]}
        
        should_continue, reason = conversation_manager.should_continue_planning(parsed, analysis)
        
        assert should_continue is False
        assert "interests" in reason
    
    def test_reject_empty_interests_list(self, conversation_manager):
        """Should reject if interests list is empty."""
        parsed = {"location": "Paris", "duration": 4, "interests": []}
        analysis = {"missing": []}
        
        should_continue, reason = conversation_manager.should_continue_planning(parsed, analysis)
        
        assert should_continue is False
    
    def test_accept_complete_info(self, conversation_manager):
        """Should accept planning with all required fields."""
        parsed = {
            "location": "Paris",
            "duration": 4,
            "interests": ["museums", "cafes"]
        }
        analysis = {"missing": []}
        
        should_continue, reason = conversation_manager.should_continue_planning(parsed, analysis)
        
        assert should_continue is True
        assert reason == ""
    
    def test_accept_with_optional_fields(self, conversation_manager):
        """Should accept even if optional fields (budget, travel_type) are missing."""
        parsed = {
            "location": "Paris",
            "duration": 4,
            "interests": ["museums"]
        }
        analysis = {"missing": ["budget", "travel_type"]}
        
        should_continue, reason = conversation_manager.should_continue_planning(parsed, analysis)
        
        assert should_continue is True


class TestGenerateFollowupQuestion:
    """Test suite for generate_followup_question - conversational prompting."""
    
    def test_generate_question_for_missing_duration(self, conversation_manager):
        """Should ask about duration when missing."""
        parsed = {"location": "Paris"}
        analysis = {"missing": ["duration", "interests"]}
        
        conversation_manager.call_openai_api = Mock(
            return_value={"question": "How long will you be staying?"}
        )
        
        result = conversation_manager.generate_followup_question(parsed, analysis)
        
        assert "How long" in result or "days" in result.lower()
    
    def test_generate_question_for_missing_interests(self, conversation_manager):
        """Should ask about interests when missing."""
        parsed = {"location": "Tokyo", "duration": 5}
        analysis = {"missing": ["interests"]}
        
        conversation_manager.call_openai_api = Mock(
            return_value={"question": "What are your main interests?"}
        )
        
        result = conversation_manager.generate_followup_question(parsed, analysis)
        
        assert "interests" in result.lower() or "like" in result.lower()
    
    def test_generate_question_returns_default_on_error(self, conversation_manager):
        """Should return default question if generation fails."""
        parsed = {"location": "Paris"}
        analysis = {"missing": ["duration"]}
        
        conversation_manager.call_openai_api = Mock(
            return_value={"error": "Failed to generate"}
        )
        
        result = conversation_manager.generate_followup_question(parsed, analysis)
        
        assert result == "Could you tell me more about your trip?"
    
    def test_generate_question_returns_empty_if_no_missing(self, conversation_manager):
        """Should return empty string if no missing fields."""
        parsed = {"location": "Paris", "duration": 4, "interests": ["museums"]}
        analysis = {"missing": []}
        
        result = conversation_manager.generate_followup_question(parsed, analysis)
        
        assert result == ""
    
    def test_generate_question_uses_json_format(self, conversation_manager):
        """Should use JSON response format for question generation."""
        parsed = {"location": "Paris"}
        analysis = {"missing": ["duration"]}
        
        conversation_manager.call_openai_api = Mock(
            return_value={"question": "How long?"}
        )
        
        conversation_manager.generate_followup_question(parsed, analysis)
        
        call_kwargs = conversation_manager.call_openai_api.call_args[1]
        assert call_kwargs["use_json_response"] is True


class TestValidateAndGetFollowup:
    """Test suite for validate_and_get_followup - main orchestration method."""
    
    def test_needs_followup_for_partial_input(self, conversation_manager):
        """Should return needs_more_info=True when input is incomplete."""
        # Mock the internal methods
        conversation_manager.parse_travel_details = Mock(
            return_value={"location": "Paris"}
        )
        conversation_manager.analyze_missing_info = Mock(
            return_value={"provided": ["location"], "missing": ["duration", "interests"], "confidence": 50}
        )
        conversation_manager.should_continue_planning = Mock(return_value=(False, "Need more info"))
        conversation_manager.generate_followup_question = Mock(
            return_value="How many days will you stay?"
        )
        
        result = conversation_manager.validate_and_get_followup("Paris")
        
        assert result["success"] is False
        assert result["needs_more_info"] is True
        assert result["details"]["location"] == "Paris"
        assert result["followup_question"] == "How many days will you stay?"
        assert "duration" in result["missing_fields"]
    
    def test_ready_to_plan_with_complete_input(self, conversation_manager):
        """Should return success=True when all info provided."""
        conversation_manager.parse_travel_details = Mock(
            return_value={"location": "Paris", "duration": 4, "interests": ["museums"]}
        )
        conversation_manager.analyze_missing_info = Mock(
            return_value={"provided": ["location", "duration", "interests"], "missing": [], "confidence": 90}
        )
        conversation_manager.should_continue_planning = Mock(return_value=(True, ""))
        
        result = conversation_manager.validate_and_get_followup(
            "Paris 4 days, museums and cafes"
        )
        
        assert result["success"] is True
        assert result["needs_more_info"] is False
        assert result["details"]["location"] == "Paris"
        assert result["details"]["duration"] == 4
        assert result["confidence"] == 90
    
    def test_stores_parsed_details_on_success(self, conversation_manager):
        """Should store parsed details when validation succeeds."""
        details = {"location": "Tokyo", "duration": 5, "interests": ["temples"]}
        conversation_manager.parse_travel_details = Mock(return_value=details)
        conversation_manager.analyze_missing_info = Mock(
            return_value={"missing": [], "confidence": 100}
        )
        conversation_manager.should_continue_planning = Mock(return_value=(True, ""))
        
        result = conversation_manager.validate_and_get_followup("Tokyo 5 days temples")
        
        assert conversation_manager.parsed_details == details
        assert result["success"] is True
    
    def test_adds_to_history_on_followup(self, conversation_manager):
        """Should add to conversation history when asking follow-up."""
        conversation_manager.parse_travel_details = Mock(
            return_value={"location": "Paris"}
        )
        conversation_manager.analyze_missing_info = Mock(
            return_value={"missing": ["duration"], "confidence": 50}
        )
        conversation_manager.should_continue_planning = Mock(return_value=(False, ""))
        conversation_manager.generate_followup_question = Mock(
            return_value="How many days?"
        )
        
        conversation_manager.validate_and_get_followup("Paris")
        
        assert len(conversation_manager.conversation_history) > 0
    
    def test_error_handling_on_exception(self, conversation_manager):
        """Should return error dict on exception."""
        conversation_manager.parse_travel_details = Mock(
            side_effect=Exception("Test error")
        )
        
        result = conversation_manager.validate_and_get_followup("Paris")
        
        assert result["success"] is False
        assert "error" in result
        assert result["needs_more_info"] is True


class TestConversationHistory:
    """Test suite for add_to_history and conversation tracking."""
    
    def test_add_to_history_tracks_fields(self, conversation_manager):
        """Should track field and value in history."""
        conversation_manager.add_to_history("location", "Paris")
        conversation_manager.add_to_history("duration", 4)
        
        assert len(conversation_manager.conversation_history) == 2
        assert conversation_manager.conversation_history[0]["field"] == "location"
        assert conversation_manager.conversation_history[1]["value"] == 4
    
    def test_history_accumulates(self, conversation_manager):
        """Should accumulate history across multiple calls."""
        conversation_manager.add_to_history("location", "Paris")
        conversation_manager.add_to_history("duration", 4)
        conversation_manager.add_to_history("interests", ["museums"])
        
        assert len(conversation_manager.conversation_history) == 3
    
    def test_reset_clears_history(self, conversation_manager):
        """Should clear history when reset is called."""
        conversation_manager.add_to_history("location", "Paris")
        conversation_manager.add_to_history("duration", 4)
        
        conversation_manager.reset()
        
        assert len(conversation_manager.conversation_history) == 0
        assert conversation_manager.parsed_details == {}
    
    def test_reset_clears_parsed_details(self, conversation_manager):
        """Should clear parsed_details on reset."""
        conversation_manager.parsed_details = {"location": "Paris", "duration": 4}
        
        conversation_manager.reset()
        
        assert conversation_manager.parsed_details == {}


class TestMultiTurnConversation:
    """Integration tests for multi-turn conversation flow."""
    
    def test_full_paris_conversation_flow(self, conversation_manager):
        """Should handle full Paris conversation: ask -> respond -> plan."""
        # Turn 1: User says "Paris"
        conversation_manager.parse_travel_details = Mock(
            return_value={"location": "Paris"}
        )
        conversation_manager.analyze_missing_info = Mock(
            return_value={"provided": ["location"], "missing": ["duration", "interests"], "confidence": 50}
        )
        conversation_manager.should_continue_planning = Mock(return_value=(False, ""))
        conversation_manager.generate_followup_question = Mock(
            return_value="How long will you stay?"
        )
        
        result1 = conversation_manager.validate_and_get_followup("Paris")
        assert result1["needs_more_info"] is True
        assert "How long" in result1["followup_question"]
        
        # Reset mocks for Turn 2
        conversation_manager.conversation_history = []
        conversation_manager.reset()
        
        # Turn 2: User provides "4 days, museums and cafes"
        conversation_manager.parse_travel_details = Mock(
            return_value={"location": "Paris", "duration": 4, "interests": ["museums", "cafes"]}
        )
        conversation_manager.analyze_missing_info = Mock(
            return_value={"provided": ["location", "duration", "interests"], "missing": [], "confidence": 90}
        )
        conversation_manager.should_continue_planning = Mock(return_value=(True, ""))
        
        result2 = conversation_manager.validate_and_get_followup(
            "Paris 4 days, museums and cafes"
        )
        assert result2["success"] is True
        assert result2["needs_more_info"] is False
    
    def test_conversation_with_multiple_followups(self, conversation_manager):
        """Should handle multiple follow-ups before sufficient info."""
        # Turn 1: Location only
        conversation_manager.parse_travel_details = Mock(
            return_value={"location": "Tokyo"}
        )
        conversation_manager.analyze_missing_info = Mock(
            return_value={"missing": ["duration", "interests"], "confidence": 40}
        )
        conversation_manager.should_continue_planning = Mock(return_value=(False, ""))
        conversation_manager.generate_followup_question = Mock(
            return_value="Q1"
        )
        
        r1 = conversation_manager.validate_and_get_followup("Tokyo")
        assert r1["needs_more_info"] is True
        
        conversation_manager.reset()
        
        # Turn 2: Location + duration
        conversation_manager.parse_travel_details = Mock(
            return_value={"location": "Tokyo", "duration": 5}
        )
        conversation_manager.analyze_missing_info = Mock(
            return_value={"missing": ["interests"], "confidence": 70}
        )
        conversation_manager.should_continue_planning = Mock(return_value=(False, ""))
        conversation_manager.generate_followup_question = Mock(
            return_value="Q2"
        )
        
        r2 = conversation_manager.validate_and_get_followup("Tokyo 5 days")
        assert r2["needs_more_info"] is True
        
        conversation_manager.reset()
        
        # Turn 3: All fields
        conversation_manager.parse_travel_details = Mock(
            return_value={"location": "Tokyo", "duration": 5, "interests": ["temples"]}
        )
        conversation_manager.analyze_missing_info = Mock(
            return_value={"missing": [], "confidence": 95}
        )
        conversation_manager.should_continue_planning = Mock(return_value=(True, ""))
        
        r3 = conversation_manager.validate_and_get_followup(
            "Tokyo 5 days temples"
        )
        assert r3["success"] is True
