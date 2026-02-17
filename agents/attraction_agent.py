from agents.base_agent import BaseAgent
from config.config import DEFAULT_TEMPERATURE, TOKENS_ATTRACTION, SYSTEM_TRAVEL_GUIDE
from agents.validation import ResponseValidator
import logging

logger = logging.getLogger(__name__)


class AttractionAgent(BaseAgent):
    """Agent responsible for finding and recommending attractions."""
    
    FIND_ATTRACTIONS_PROMPT = """As a travel expert, recommend top attractions and activities in {location} for a {duration}-day trip. 
Focus on these interests: {interests}. 
Provide 3-5 recommendations with brief descriptions and estimated time needed for each.

JSON structure: {{"attractions": [{{ "name": "string", "description": "string", "hours_needed": "string like 2-3 hours", "category": "string" }}]}}"""

    def find_attractions(self, location: str, interests: list[str], duration: int) -> dict:
        """
        Find attractions based on location, interests, and duration.
        
        Args:
            location: The travel destination
            interests: List of user interests (e.g., ['hiking', 'museums', 'food'])
            duration: Number of days for the trip
        
        Returns:
            Dictionary with attraction recommendations
        """
        interests_str = ", ".join(interests) if interests else "general tourism"
        prompt = self.FIND_ATTRACTIONS_PROMPT.format(
            location=location,
            interests=interests_str,
            duration=duration
        )
        
        result = self.call_openai_api(
            system_prompt=SYSTEM_TRAVEL_GUIDE,
            user_prompt=prompt,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=TOKENS_ATTRACTION,
            use_json_response=True,
        )
        
        # Validate response structure
        is_valid, error_msg = ResponseValidator.validate_attractions(result)
        if not is_valid:
            logger.warning(f"Attractions validation failed: {error_msg}")
            result.setdefault("attractions", [])
        
        return result