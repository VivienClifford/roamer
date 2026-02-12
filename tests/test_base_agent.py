"""Tests for BaseAgent class and methods."""
import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from agents.base_agent import BaseAgent


@pytest.fixture
def agent():
    """Create a BaseAgent instance for testing."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        return BaseAgent(name="TestAgent")


class TestCleanResponse:
    """Test suite for clean_response method."""
    
    def test_plain_json_no_formatting(self, agent):
        """Should handle plain JSON without code blocks."""
        response = '{"key": "value"}'
        assert agent.clean_response(response) == '{"key": "value"}'
    
    def test_plain_json_with_whitespace(self, agent):
        """Should strip leading/trailing whitespace."""
        response = '  {"key": "value"}  '
        assert agent.clean_response(response) == '{"key": "value"}'
    
    def test_json_with_triple_backticks(self, agent):
        """Should remove triple backtick wrappers."""
        response = '```{"key": "value"}```'
        assert agent.clean_response(response) == '{"key": "value"}'
    
    def test_json_with_backticks_and_whitespace(self, agent):
        """Should handle backticks with surrounding whitespace."""
        response = '  ```{"key": "value"}```  '
        assert agent.clean_response(response) == '{"key": "value"}'
    
    def test_json_with_language_identifier(self, agent):
        """Should remove language identifier after backticks."""
        response = '```json\n{"key": "value"}\n```'
        assert agent.clean_response(response) == '{"key": "value"}'
    
    def test_multiline_json(self, agent):
        """Should preserve multiline JSON structure."""
        response = '```json\n{\n  "key": "value"\n}\n```'
        assert agent.clean_response(response) == '{\n  "key": "value"\n}'
    
    def test_empty_string(self, agent):
        """Should handle empty string."""
        assert agent.clean_response("") == ""
    
    def test_only_whitespace(self, agent):
        """Should return empty string for whitespace-only input."""
        assert agent.clean_response("   \n\t  ") == ""


class TestGetApiKey:
    """Test suite for get_api_key method."""
    
    def test_get_api_key_from_environment(self, agent):
        """Should retrieve API key from environment variable."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
            agent2 = BaseAgent(name="TestAgent2")
            assert agent2.get_api_key() == "test-api-key"
    
    def test_get_api_key_missing_raises_error(self):
        """Should raise ValueError when API key is not set."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key must be provided"):
                BaseAgent(name="TestAgent3")
    
    def test_api_key_passed_to_init_is_used(self):
        """Should use API key passed to __init__ instead of environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            agent = BaseAgent(name="TestAgent", api_key="passed-api-key")
            assert agent.client is not None
    
    def test_api_key_from_env_when_not_passed(self):
        """Should use environment variable when API key not passed to __init__."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-api-key"}):
            agent = BaseAgent(name="TestAgent")
            assert agent.client is not None


class TestCallOpenaiApi:
    """Test suite for call_openai_api method."""
    
    def test_successful_api_call(self, agent):
        """Should parse JSON response successfully."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"result": "success"}'
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        agent.client = mock_client
        
        result = agent.call_openai_api(
            system_prompt="test",
            user_prompt="test"
        )
        
        assert result == {"result": "success"}
    
    def test_api_call_with_markdown_response(self, agent):
        """Should handle markdown-wrapped JSON responses."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '```json\n{"result": "success"}\n```'
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        agent.client = mock_client
        
        result = agent.call_openai_api(
            system_prompt="test",
            user_prompt="test"
        )
        
        assert result == {"result": "success"}
    
    def test_api_call_empty_response(self, agent):
        """Should return error dict for empty response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        agent.client = mock_client
        
        result = agent.call_openai_api(
            system_prompt="test",
            user_prompt="test"
        )
        
        assert "error" in result
    
    def test_api_call_invalid_json(self, agent):
        """Should return error dict for invalid JSON."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "not valid json"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        agent.client = mock_client
        
        result = agent.call_openai_api(
            system_prompt="test",
            user_prompt="test"
        )
        
        assert "error" in result
    
    @patch("agents.base_agent.OpenAI")
    def test_api_call_network_error(self, mock_openai_class, agent):
        """Should catch and return network errors."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("Connection failed")
        agent.client = mock_client
        
        result = agent.call_openai_api(
            system_prompt="test",
            user_prompt="test"
        )
        
        assert "error" in result
        assert "Connection failed" in result["error"]
