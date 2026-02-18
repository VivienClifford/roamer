"""Conversation manager for gathering travel information from users."""

import logging
from typing import Optional, List, Dict, Tuple
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ConversationManager(BaseAgent):
    """Manages multi-turn conversation to gather complete travel information."""
    
    ANALYZE_MISSING_PROMPT = """Analyze this travel request and identify what information is clearly provided vs what's missing or unclear:

Request: '{user_input}'

Respond with JSON containing:
- provided: list of fields that are clearly mentioned (e.g., ["location", "duration"])
- missing: list of fields that are not mentioned (e.g., ["interests", "budget"])
- unclear: dict of fields with conflicting or ambiguous information (e.g., {{"interests": "mentioned but vague"}})
- confidence: overall confidence score 0-100 that we understand the full request

Example: {{"provided": ["location", "interests"], "missing": ["duration"], "unclear": {{}}, "confidence": 75}}"""
    
    GENERATE_FOLLOWUP_PROMPT = """Generate a friendly, concise follow-up question to gather missing travel information.

What we know: {known}
What's missing: {missing}
What we've already asked about: {already_asked}

Generate ONE natural follow-up question (max 2 sentences) to gather the most important missing information.
Ask about the most critical missing field first (priority: duration > interests > budget > travel_type).
Make it conversational, not robotic.

Example responses:
"How many days are you planning to spend there?"
"What kind of activities interest you most? (e.g., culture, food, adventure, relaxation)"
"Are you traveling solo, with a partner, or with family?"

Question:"""
    
    PARSE_TRAVEL_DETAILS_PROMPT = """EXTRACT ONLY explicitly mentioned information. DO NOT infer or guess.

User input: '{user_input}'

Return JSON with ONLY the fields explicitly mentioned:
- location: string or null
- duration: number (days) or null  
- interests: list of strings or null
- budget: string or null
- travel_type: string or null

RULES:
1. If a field is NOT explicitly mentioned, set it to null
2. Do NOT provide default values
3. Do NOT guess or infer missing information
4. Only extract exact information that appears in the input

Examples:
Input: "Paris"
{{location: "Paris", duration: null, interests: null, budget: null, travel_type: null}}

Input: "Tokyo for 5 days"
{{location: "Tokyo", duration: 5, interests: null, budget: null, travel_type: null}}

Input: "Barcelona, 3 days, love hiking"
{{location: "Barcelona", duration: 3, interests: ["hiking"], budget: null, travel_type: null}}"""
    
    def __init__(self, name: str = "Conversation Manager", api_key: Optional[str] = None):
        super().__init__(name, api_key)
        self.conversation_history: List[Dict] = []
        self.parsed_details = {}
    
    def parse_travel_details(self, user_input: str) -> dict:
        """
        Extract travel details from user input using LLM.
        Only extracts explicitly mentioned information - no defaults or inference.
        
        Args:
            user_input: User's travel request
        
        Returns:
            Dictionary with extracted location, duration, and interests (null for missing fields)
        """
        from config.config import TOKENS_PARSING, SYSTEM_TRAVEL_DETAILS
        
        prompt = self.PARSE_TRAVEL_DETAILS_PROMPT.format(user_input=user_input)
        
        details = self.call_openai_api(
            system_prompt="You are a data extractor. Return ONLY valid JSON. Never infer or provide defaults.",
            user_prompt=prompt,
            temperature=0.2,
            max_tokens=TOKENS_PARSING,
            use_json_response=True,
        )
        
        # Check for critical errors
        if "error" in details:
            logger.warning(f"Parse error: {details.get('error')}")
            return {"error": "Failed to parse travel details"}
        
        # Remove null values, keep only explicitly mentioned fields
        cleaned_details = {k: v for k, v in details.items() if v is not None}
        
        # Require location to be present
        if "location" not in cleaned_details or not cleaned_details.get("location"):
            return {"error": "Location is required"}
        
        logger.debug(f"Parsed travel details: {cleaned_details}")
        return cleaned_details
    
    def analyze_missing_info(self, user_input: str) -> dict:
        """
        Analyze what information is provided vs missing in the user request.
        
        Args:
            user_input: User's travel request
        
        Returns:
            Dict with provided, missing, unclear fields and confidence score
        """
        prompt = self.ANALYZE_MISSING_PROMPT.format(user_input=user_input)
        
        analysis = self.call_openai_api(
            system_prompt="You are a travel information analyst. Respond only with valid JSON.",
            user_prompt=prompt,
            temperature=0.3,
            max_tokens=300,
            use_json_response=True,
        )
        
        # Set defaults if analysis failed
        if "error" in analysis:
            logger.warning(f"Analysis failed, using basic fallback: {analysis.get('error')}")
            analysis = {
                "provided": [],
                "missing": ["location", "duration", "interests"],
                "unclear": {},
                "confidence": 0
            }
        
        # Ensure all keys exist
        analysis.setdefault("provided", [])
        analysis.setdefault("missing", [])
        analysis.setdefault("unclear", {})
        analysis.setdefault("confidence", 0)
        
        logger.debug(f"Info analysis: {analysis}")
        return analysis
    
    def generate_followup_question(self, parsed_details: dict, analysis: dict) -> str:
        """
        Generate a follow-up question for missing information.
        
        Args:
            parsed_details: Already parsed travel details
            analysis: Missing info analysis  
        
        Returns:
            A follow-up question string
        """
        provided_fields = {k: v for k, v in parsed_details.items() if v and k != "error"}
        missing_fields = analysis.get("missing", [])
        
        if not missing_fields:
            return ""
        
        already_asked = [item.get("field") for item in self.conversation_history if item.get("field")]
        
        prompt = self.GENERATE_FOLLOWUP_PROMPT.format(
            known=str(provided_fields),
            missing=", ".join(missing_fields),
            already_asked=", ".join(already_asked) if already_asked else "nothing yet"
        )
        
        response = self.call_openai_api(
            system_prompt="You are a friendly travel assistant. Respond with JSON: {\"question\": \"your question here\"}",
            user_prompt=prompt,
            temperature=0.7,
            max_tokens=100,
            use_json_response=True,
        )
        
        # Extract question from JSON response
        if "error" in response:
            logger.warning(f"Failed to generate followup question: {response.get('error')}")
            return "Could you tell me more about your trip?"
        
        question = response.get("question", "").strip()
        
        if not question:
            logger.warning("Generated empty followup question")
            return "Could you tell me more about your trip?"
        
        logger.debug(f"Generated follow-up question: {question}")
        return question
    
    def should_continue_planning(self, parsed_details: dict, analysis: dict) -> Tuple[bool, str]:
        """
        Determine if we have enough information to proceed with planning.
        Requires: location + duration + at least one interest
        
        Args:
            parsed_details: Parsed travel details
            analysis: Missing info analysis
        
        Returns:
            Tuple of (should_continue: bool, reason: str)
        """
        # Must have location
        if not parsed_details.get("location"):
            return False, "We need to know where you want to go."
        
        # Must have duration (in days)
        if not parsed_details.get("duration"):
            return False, "We need to know how long you'll be staying."
        
        # Should have at least one interest for personalization
        interests = parsed_details.get("interests", [])
        if not interests or (isinstance(interests, list) and len(interests) == 0):
            return False, "We need to know what interests you to personalize your trip."
        
        return True, ""
    
    def add_to_history(self, field: str, value: any) -> None:
        """Track what we've asked about in the conversation."""
        self.conversation_history.append({"field": field, "value": value})
    
    def validate_and_get_followup(self, user_input: str) -> dict:
        """
        Validate user input and determine if we need more information.
        
        Args:
            user_input: User's message
        
        Returns:
            Dict with:
            - success: bool, whether we have enough info to plan
            - details: parsed travel details
            - needs_more_info: bool, whether we need follow-up
            - followup_question: str, the question to ask (if needs_more_info is True)
            - missing_fields: list, fields that are missing
            - confidence: int, confidence score
        """
        try:
            # Step 1: Parse the input
            details = self.parse_travel_details(user_input)
            
            # Step 2: Analyze what's missing
            analysis = self.analyze_missing_info(user_input)
            
            # Step 3: Check if we should continue
            should_continue, reason = self.should_continue_planning(details, analysis)
            
            if not should_continue:
                # Generate a follow-up question
                followup = self.generate_followup_question(details, analysis)
                self.add_to_history("question", followup)
                
                return {
                    "success": False,
                    "needs_more_info": True,
                    "details": details,
                    "followup_question": followup or "Could you provide more details about your trip?",
                    "missing_fields": analysis.get("missing", []),
                    "confidence": analysis.get("confidence", 0)
                }
            
            # Store the context for later
            self.parsed_details = details
            
            # We have enough info to proceed with planning
            return {
                "success": True,
                "needs_more_info": False,
                "details": details,
                "confidence": analysis.get("confidence", 100)
            }
        
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Error validating your request: {str(e)}",
                "needs_more_info": True
            }
    
    def reset(self) -> None:
        """Reset conversation state for a new trip planning session."""
        self.conversation_history = []
        self.parsed_details = {}
