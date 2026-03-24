"""Reusable Streamlit UI components."""

import streamlit as st
import os
from app.ui.messages import UIMessages


def render_header() -> None:
    """Render page header and title."""
    st.markdown(UIMessages.HEADER_TITLE)
    st.markdown(UIMessages.HEADER_SUBTITLE)


def render_sidebar_config() -> str | None:
    """
    Render sidebar configuration section with API key input.
    
    Returns:
        API key from input or environment, or None if not available.
    """
    with st.sidebar:
        st.markdown(UIMessages.SIDEBAR_CONFIG_TITLE)
        
        # API Key input
        api_key = st.text_input(
            UIMessages.API_KEY_LABEL,
            value=st.session_state.get("api_key", ""),
            type="password",
            help=UIMessages.API_KEY_HELP
        )
        
        if api_key:
            st.session_state.api_key = api_key
            return api_key
        elif not st.session_state.get("api_key"):
            # Try to get from environment variable
            env_api_key = os.getenv("OPENAI_API_KEY")
            if env_api_key:
                st.session_state.api_key = env_api_key
                st.success(UIMessages.API_KEY_SUCCESS)
                return env_api_key
            else:
                st.warning(UIMessages.API_KEY_WARNING)
                return None
        else:
            return st.session_state.get("api_key")


def render_sidebar_about() -> None:
    """Render sidebar about section."""
    with st.sidebar:
        st.markdown("---")
        st.markdown(UIMessages.SIDEBAR_ABOUT_TITLE)
        st.markdown(UIMessages.SIDEBAR_ABOUT_TEXT)
        
        st.markdown("---")
        st.markdown(UIMessages.SIDEBAR_HOW_TO_USE_TITLE)
        st.markdown(UIMessages.SIDEBAR_HOW_TO_USE_TEXT)


def render_sidebar_clear_button() -> bool:
    """
    Render clear chat history button in sidebar.
    
    Returns:
        True if button was clicked, False otherwise.
    """
    with st.sidebar:
        return st.button(UIMessages.CLEAR_HISTORY_BUTTON)


def render_chat_history(messages: list) -> None:
    """
    Display all messages from chat history.
    
    Args:
        messages: List of message dicts with "role" and "content" keys.
    """
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def render_user_message(content: str) -> None:
    """
    Display a user message in the chat.
    
    Args:
        content: The user's message text.
    """
    with st.chat_message("user"):
        st.markdown(content)


def render_assistant_message(content: str) -> None:
    """
    Display an assistant message in the chat.
    
    Args:
        content: The assistant's message text.
    """
    with st.chat_message("assistant"):
        st.markdown(content)


def get_chat_input() -> str | None:
    """
    Get user input from chat input widget.
    
    Returns:
        User's input text, or None if no input.
    """
    return st.chat_input(UIMessages.CHAT_INPUT_PLACEHOLDER)
