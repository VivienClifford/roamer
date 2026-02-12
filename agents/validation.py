"""Utilities for validating API responses against expected schemas."""

import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


class ResponseValidator:
    """Validates API responses match expected structures."""
    
    @staticmethod
    def validate_attractions(data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate attractions response structure.
        
        Args:
            data: Response data to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if "error" in data:
            return False, data["error"]
        
        if "attractions" not in data:
            return False, "Missing 'attractions' key in response"
        
        if not isinstance(data["attractions"], list):
            return False, "'attractions' must be a list"
        
        required_fields = {"name", "description", "hours_needed", "category"}
        for i, attraction in enumerate(data["attractions"]):
            if not isinstance(attraction, dict):
                return False, f"Attraction {i} is not a dictionary"
            missing = required_fields - set(attraction.keys())
            if missing:
                return False, f"Attraction {i} missing fields: {missing}"
        
        return True, None
    
    @staticmethod
    def validate_itinerary(data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate itinerary response structure.
        
        Args:
            data: Response data to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if "error" in data:
            return False, data["error"]
        
        if "days" not in data:
            return False, "Missing 'days' key in response"
        
        if not isinstance(data["days"], list):
            return False, "'days' must be a list"
        
        for i, day in enumerate(data["days"]):
            if not isinstance(day, dict):
                return False, f"Day {i} is not a dictionary"
            if "activities" in day and not isinstance(day["activities"], list):
                return False, f"Day {i} activities must be a list"
        
        return True, None
    
    @staticmethod
    def validate_transportation(data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate transportation response structure.
        
        Args:
            data: Response data to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if "error" in data:
            return False, data["error"]
        
        if not data:
            return False, "Empty response from API"
        
        if "transportation" not in data:
            return False, f"Missing 'transportation' key in response. Keys present: {list(data.keys())}"
        
        if not isinstance(data["transportation"], list):
            return False, f"'transportation' must be a list, got {type(data['transportation'])}"
        
        return True, None
    
    @staticmethod
    def validate_travel_details(data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate travel details response structure.
        
        Args:
            data: Response data to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if "error" in data:
            return False, data["error"]
        
        if "location" not in data:
            return False, "Missing required 'location' field"
        
        if "duration" in data and not isinstance(data["duration"], int):
            return False, "'duration' must be an integer"
        
        return True, None
