from agents.base_agent import BaseAgent
from config.config import DEFAULT_TEMPERATURE, TOKENS_ITINERARY, TOKENS_TRANSPORT, SYSTEM_TRAVEL_PLANNER, SYSTEM_LOGISTIC_EXPERT
from agents.validation import ResponseValidator
import json
import logging

logger = logging.getLogger(__name__)


class LogisticAgent(BaseAgent):
    """Agent responsible for creating itineraries and transportation suggestions."""
    
    CREATE_ITINERARY_PROMPT = """Create a detailed {duration}-day itinerary for {location} using these attractions:
{attractions_str}

Plan considering: travel time, opening hours, meals, rest times, and activity levels.

IMPORTANT: For each day's "title" field, provide ONLY the main activity or theme (e.g., "Arrival", "Museum Day", "Beach Exploration") WITHOUT any day number prefix. The display layer will automatically format it as "Day N: Title".

JSON structure: {{"days": [{{"day_number": "string", "title": "string", "activities": [{{"time": "HH:MM", "activity": "string", "duration": "string"}}], "meals": {{"breakfast": "string", "lunch": "string", "dinner": "string"}}, "notes": "string"}}]}}"""

    TRANSPORTATION_PROMPT = """Provide practical transportation tips for visiting {location}. Include best ways to get around, costs, apps, and safety tips.

JSON structure: {{"transportation": [{{"method": "string", "description": "string", "cost_estimate": "string like $10-20/day", "recommended_for": "string"}}]}}"""

    def create_itinerary(self, location: str, duration: int, attractions: dict) -> dict:
        """
        Create a detailed daily itinerary based on attractions.
        
        Args:
            location: The travel destination
            duration: Number of days for the trip
            attractions: Dictionary of attractions from AttractionAgent
        
        Returns:
            Dictionary with day-by-day itinerary
        """
        attractions_str = json.dumps(attractions, indent=2)
        prompt = self.CREATE_ITINERARY_PROMPT.format(
            duration=duration,
            location=location,
            attractions_str=attractions_str
        )
        
        result = self.call_openai_api(
            system_prompt=SYSTEM_TRAVEL_PLANNER,
            user_prompt=prompt,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=TOKENS_ITINERARY,
        )
        
        # Validate response structure
        is_valid, error_msg = ResponseValidator.validate_itinerary(result)
        if not is_valid:
            logger.warning(f"Itinerary validation failed: {error_msg}")
            result.setdefault("days", [])
        
        return result

    def get_transportation_suggestions(self, location: str) -> dict:
        """
        Get local transportation suggestions for the destination.
        
        Args:
            location: The travel destination
        
        Returns:
            Dictionary with transportation recommendations
        """
        prompt = self.TRANSPORTATION_PROMPT.format(location=location)
        
        result = self.call_openai_api(
            system_prompt=SYSTEM_LOGISTIC_EXPERT,
            user_prompt=prompt,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=TOKENS_TRANSPORT,
        )
        
        # Validate response structure
        is_valid, error_msg = ResponseValidator.validate_transportation(result)
        if not is_valid:
            logger.warning(f"Transportation validation failed: {error_msg}")
            result.setdefault("transportation", [])
        
        return result