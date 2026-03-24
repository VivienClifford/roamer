"""UI state manager for handling display transitions."""

import streamlit as st
from app.ui.builders import ChatUIBuilder
from app.ui.messages import UIMessages
from app.agents.display import TravelPlanDisplay


class UIManager:
    """Manages display state transitions and message rendering."""
    
    def __init__(self):
        """Initialize the UI manager with a chat builder."""
        self.chat_builder = ChatUIBuilder()
    
    def show_validating_state(self) -> None:
        """Display validating spinner while processing."""
        with st.chat_message("assistant"):
            with st.spinner(UIMessages.VALIDATING_SPINNER):
                # Spinner persists until parent function completes
                pass
    
    def show_followup_question(self, question: str) -> None:
        """
        Display a follow-up question and add it to chat history.
        
        Args:
            question: The follow-up question text.
        """
        followup_text = f"💭 {question}"
        
        with st.chat_message("assistant"):
            st.write(followup_text)
        
        self.chat_builder.add_assistant_message_to_history(followup_text)
    
    def show_planning_in_progress(self) -> None:
        """Display planning spinner while generating itinerary."""
        with st.chat_message("assistant"):
            with st.spinner(UIMessages.PLANNING_SPINNER):
                # Spinner persists until parent function completes
                pass
    
    def show_travel_plan(self, plan_data: dict) -> None:
        """
        Display the generated travel plan and add success message to history.
        
        Args:
            plan_data: Dictionary with travel plan details from CoordinatorAgent.
        """
        with st.chat_message("assistant"):
            # Use existing TravelPlanDisplay to render the plan
            display = TravelPlanDisplay(plan_data)
            display.render()
        
        # Add success message to history
        self.chat_builder.add_assistant_message_to_history(
            UIMessages.SUCCESS_PLAN_GENERATED
        )
    
    def show_error(self, error_msg: str) -> None:
        """
        Display an error message and add it to chat history.
        
        Args:
            error_msg: The error message text.
        """
        formatted_error = UIMessages.ERROR_GENERIC.format(error=error_msg)
        
        with st.chat_message("assistant"):
            st.error(formatted_error)
        
        self.chat_builder.add_assistant_message_to_history(formatted_error)
    
    def show_no_api_key_error(self) -> None:
        """Display error when API key is missing and stop execution."""
        st.error(UIMessages.ERROR_NO_API_KEY)
        st.stop()
