"""Conversation and application state constants."""

from enum import Enum


class ConversationState(str, Enum):
    """Represents the current state of the travel planning conversation."""
    
    INITIAL = "initial"
    """User just entered input, awaiting validation"""
    
    VALIDATING = "validating"
    """Currently validating user input with ConversationManager"""
    
    NEEDS_MORE_INFO = "needs_more_info"
    """Validation complete - more information needed, follow-up question shown"""
    
    PLANNING = "planning"
    """All info gathered, generating travel plan with CoordinatorAgent"""
    
    PLAN_READY = "plan_ready"
    """Travel plan successfully generated and displayed"""
    
    ERROR = "error"
    """Error occurred during validation or planning"""


def get_state_description(state: str) -> str:
    """Return human-readable description of current state for debugging."""
    descriptions = {
        ConversationState.INITIAL: "Starting new input",
        ConversationState.VALIDATING: "Analyzing travel request...",
        ConversationState.NEEDS_MORE_INFO: "Awaiting additional user information",
        ConversationState.PLANNING: "Generating personalized itinerary...",
        ConversationState.PLAN_READY: "Plan generated successfully",
        ConversationState.ERROR: "Error occurred",
    }
    return descriptions.get(state, "Unknown state")
