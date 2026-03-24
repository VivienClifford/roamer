"""UI builders that compose Streamlit components into cohesive sections."""

import streamlit as st
from app.ui import components
from app.ui.messages import UIMessages


class HeaderBuilder:
    """Builds the header and sidebar sections of the application."""
    
    def build(self) -> str | None:
        """
        Build and render the header and sidebar UI.
        
        Returns:
            API key from configuration, or None if not available.
        """
        # Render main header
        components.render_header()
        
        # Render sidebar config and get API key
        api_key = components.render_sidebar_config()
        
        # Render sidebar about and instructions
        components.render_sidebar_about()
        
        # Check for clear button
        if components.render_sidebar_clear_button():
            st.session_state.messages = [
                {"role": "assistant", "content": UIMessages.INITIAL_GREETING}
            ]
            st.rerun()
        
        return api_key


class ChatUIBuilder:
    """Builds the main chat interaction UI."""
    
    def render_history(self, messages: list) -> None:
        """
        Render all messages in chat history.
        
        Args:
            messages: List of message dicts with "role" and "content" keys.
        """
        components.render_chat_history(messages)
    
    def get_user_input(self) -> str | None:
        """
        Get user input from chat input widget.
        
        Returns:
            User's input text, or None if no input.
        """
        return components.get_chat_input()
    
    def add_user_message_to_history(self, content: str) -> None:
        """
        Add user message to session state history and display it.
        
        Args:
            content: The user's message text.
        """
        st.session_state.messages.append({"role": "user", "content": content})
        components.render_user_message(content)
    
    def add_assistant_message_to_history(self, content: str) -> None:
        """
        Add assistant message to session state history and display it.
        
        Args:
            content: The assistant's message text.
        """
        st.session_state.messages.append({"role": "assistant", "content": content})
        components.render_assistant_message(content)
