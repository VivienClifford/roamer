import streamlit as st
import logging
from dotenv import load_dotenv
from app.agents.coordinator_agent import CoordinatorAgent
from app.agents.conversation_manager import ConversationManager
from app.ui.builders import HeaderBuilder, ChatUIBuilder
from app.ui.manager import UIManager
from app.ui.messages import UIMessages

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)


def setup_page_config() -> None:
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Roamer Travel Planner",
        page_icon=":earth_americas:",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def initialize_session_state() -> None:
    """Initialize all session state variables."""
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": UIMessages.INITIAL_GREETING}
        ]
    
    # Initialize agents (once per session)
    if "conversation_manager" not in st.session_state:
        api_key = st.session_state.get("api_key")
        if not api_key:
            return
        st.session_state.conversation_manager = ConversationManager(api_key=api_key)
        st.session_state.coordinator = CoordinatorAgent("Travel Coordinator", api_key=api_key)
    
    # Track conversation context for cumulative analysis
    if "conversation_context" not in st.session_state:
        st.session_state.conversation_context = []


def get_or_validate_api_key() -> str | None:
    """
    Get API key from sidebar config or stop if unavailable.
    
    Returns:
        API key string, or None if validation fails and stops execution.
    """
    header_builder = HeaderBuilder()
    api_key = header_builder.build()
    
    if not api_key:
        ui_manager = UIManager()
        ui_manager.show_no_api_key_error()
    
    return api_key


def handle_user_input(chat_builder: ChatUIBuilder, ui_manager: UIManager) -> None:
    """
    Handle incoming user message through validation and planning.
    
    Args:
        chat_builder: UI builder for chat interactions.
        ui_manager: Manager for display state transitions.
    """
    if prompt := chat_builder.get_user_input():
        # Add user message to history and display
        chat_builder.add_user_message_to_history(prompt)
        
        # Add to conversation context
        st.session_state.conversation_context.append(prompt)
        combined_input = " ".join(st.session_state.conversation_context)
        
        # Step 1: Validate and get follow-up if needed
        ui_manager.show_validating_state()
        validation_result = st.session_state.conversation_manager.validate_and_get_followup(
            combined_input
        )
        
        if validation_result.get("needs_more_info"):
            # Need more information - show follow-up question
            followup = validation_result.get("followup_question", "Could you provide more details?")
            ui_manager.show_followup_question(followup)
        
        elif validation_result.get("success"):
            # Have all info - generate travel plan
            st.session_state.conversation_context = []  # Reset for next trip
            
            ui_manager.show_planning_in_progress()
            plan_data = st.session_state.coordinator.plan_trip(combined_input)
            
            # Display the plan
            if plan_data.get("success"):
                ui_manager.show_travel_plan(plan_data)
            else:
                error_msg = plan_data.get("error", UIMessages.ERROR_PLAN_GENERATION)
                ui_manager.show_error(error_msg)
        
        else:
            # Validation error occurred
            error_msg = validation_result.get("error", "An error occurred")
            ui_manager.show_error(error_msg)


def main():
    """Main application entry point."""
    setup_page_config()
    
    # Build header and get API key
    api_key = get_or_validate_api_key()
    if not api_key:
        return
    
    # Initialize session state
    initialize_session_state()
    
    # Build chat UI
    chat_builder = ChatUIBuilder()
    ui_manager = UIManager()
    
    # Display chat history
    chat_builder.render_history(st.session_state.messages)
    
    # Handle user input
    handle_user_input(chat_builder, ui_manager)


if __name__ == "__main__":
    main()
