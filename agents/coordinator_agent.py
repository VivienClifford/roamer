import logging
from typing import Optional
from agents.base_agent import BaseAgent
from agents.attraction_agent import AttractionAgent
from agents.logistic_agent import LogisticAgent
from config.config import TOKENS_PARSING, SYSTEM_TRAVEL_DETAILS

logger = logging.getLogger(__name__)


class CoordinatorAgent(BaseAgent):
    """Agent that orchestrates all other agents to plan a complete trip."""
    
    PARSE_TRAVEL_DETAILS_PROMPT = """Extract travel planning details from: '{user_input}'

Identify: location (required), duration (days, default 3), interests (list), budget (low/medium/high), travel_type (solo/couple/family/group)

Example: {{"location": "Tokyo", "duration": 5, "interests": ["temples", "sushi"], "budget": "medium", "travel_type": "solo"}}"""
    
    def __init__(self, name: str, api_key: Optional[str] = None):
        super().__init__(name, api_key)
        self.attraction_agent = AttractionAgent("Attraction Agent", api_key=api_key)
        self.logistic_agent = LogisticAgent("Logistic Agent", api_key=api_key)
        self.travel_context = {}

    def parse_travel_details(self, user_input: str) -> dict:
        """
        Extract travel details from user input using LLM.
        
        Args:
            user_input: User's travel request
        
        Returns:
            Dictionary with extracted location, duration, and interests
        """
        prompt = self.PARSE_TRAVEL_DETAILS_PROMPT.format(user_input=user_input)
        
        details = self.call_openai_api(
            system_prompt=SYSTEM_TRAVEL_DETAILS,
            user_prompt=prompt,
            temperature=0.5,
            max_tokens=TOKENS_PARSING,
        )
        
        # Add default error response if needed
        if "error" in details or "location" not in details:
            if "error" not in details:
                details["error"] = "Failed to extract location from request"
            details.setdefault("location", "Unknown")
            details.setdefault("duration", 3)
            details.setdefault("interests", [])
        
        logger.debug(f"Parsed travel details: {details}")
        return details

    def plan_trip(self, user_input: str) -> dict:
        """
        Orchestrate the trip planning by coordinating all agents.
        
        Args:
            user_input: User's travel request
        
        Returns:
            A dictionary with structured travel plan data
        """
        try:
            # Step 1: Parse user input
            travel_details = self.parse_travel_details(user_input)
            
            if "error" in travel_details:
                return {
                    "success": False,
                    "error": "I had trouble understanding your request. Could you please provide: location, duration, and interests?"
                }
            
            location = travel_details.get("location", "Unknown")
            duration = travel_details.get("duration", 3)
            interests = travel_details.get("interests", [])
            
            self.travel_context = travel_details
            
            # Step 2: Get attractions from AttractionAgent
            attractions_response = self.attraction_agent.find_attractions(location, interests, duration)
            
            # Step 3: Create itinerary with LogisticAgent
            itinerary_response = self.logistic_agent.create_itinerary(location, duration, attractions_response)
            
            # Step 4: Get transportation suggestions
            transport_response = self.logistic_agent.get_transportation_suggestions(location)
            
            # Collect any errors
            errors = []
            if "error" in attractions_response:
                errors.append(f"Could not fetch attractions: {attractions_response['error']}")
            if "error" in itinerary_response:
                errors.append(f"Could not create itinerary: {itinerary_response['error']}")
            if "error" in transport_response:
                errors.append(f"Could not fetch transportation: {transport_response['error']}")
            
            # Return structured data
            return {
                "success": True,
                "details": travel_details,
                "attractions": attractions_response,
                "itinerary": itinerary_response,
                "transport": transport_response,
                "errors": errors
            }
        except Exception as e:
            logger.error(f"Trip planning failed: {str(e)}")
            return {
                "success": False,
                "error": f"An error occurred while planning your trip: {str(e)}"
            }

    def fetch_travel_details(self, user_input: str) -> dict:
        """
        Main method called from main.py to generate travel plan.
        Returns structured data for rendering.
        """
        return self.plan_trip(user_input)