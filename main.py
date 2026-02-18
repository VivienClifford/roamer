import streamlit as st
import os
import logging
from dotenv import load_dotenv
from agents.coordinator_agent import CoordinatorAgent
from agents.conversation_manager import ConversationManager
from agents.display import display_travel_plan

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    # Set page title and layout
    st.set_page_config(
        page_title="Roamer Travel Planner", 
        page_icon=":earth_americas:", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.markdown("# ✈️ Roamer Travel Planner")
    st.markdown("Your AI-powered travel planning assistant powered by advanced language models.")
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "🔑 OpenAI API Key",
            value=st.session_state.get("api_key", ""),
            type="password",
            help="Enter your OpenAI API key. Get one at https://platform.openai.com/api-keys"
        )
        
        if api_key:
            st.session_state.api_key = api_key
        elif not st.session_state.get("api_key"):
            # Try to get from environment variable
            env_api_key = os.getenv("OPENAI_API_KEY")
            if env_api_key:
                st.session_state.api_key = env_api_key
                st.success("✓ Using API key from environment")
            else:
                st.warning("⚠️ Please enter your OpenAI API key to continue")
        
        st.markdown("---")
        st.markdown("## About Roamer")
        st.markdown("""
        Roamer uses AI agents to create personalized travel itineraries:
        
        - 🏛️ **Attraction Agent**: Recommends attractions based on your interests
        - 🗺️ **Logistic Agent**: Plans daily itineraries and transportation
        - 🤝 **Coordinator Agent**: Orchestrates all agents to create your perfect trip
        """)
        
        st.markdown("---")
        st.markdown("### How to use:")
        st.markdown("""
        1. Tell us where you want to go
        2. Mention how long you'll be staying
        3. Share your interests and preferences
        4. Let our AI agents plan your trip!
        
        Example: "I want to visit Tokyo for 5 days. I love sushi, temples, and technology."
        """)
        
        if st.button("🔄 Clear Chat History"):
            st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]
            st.rerun()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! 👋 I'm Roamer, your AI travel planner. Tell me where you'd like to go, how long you'll stay, and what interests you. I'll create a personalized itinerary for you!"}]
    
    # Initialize conversation and coordinator agents once per session
    if "conversation_manager" not in st.session_state:
        api_key = st.session_state.get("api_key")
        if not api_key:
            st.error("❌ Please enter your OpenAI API key in the sidebar to use Roamer")
            st.stop()
        st.session_state.conversation_manager = ConversationManager(api_key=api_key)
        st.session_state.coordinator = CoordinatorAgent("Travel Coordinator", api_key=api_key)
    
    # Track conversation context for gathering information
    if "conversation_context" not in st.session_state:
        st.session_state.conversation_context = []
    
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Accept user input
    if prompt := st.chat_input("Tell me about your dream trip..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display the user message immediately in the chat
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add to conversation context for cumulative analysis
        st.session_state.conversation_context.append(prompt)
        combined_input = " ".join(st.session_state.conversation_context)
        
        # Generate response using conversation manager first
        with st.chat_message("assistant"):
            with st.spinner("🤔 Processing..."):
                validation_result = st.session_state.conversation_manager.validate_and_get_followup(combined_input)
            
            if validation_result.get("needs_more_info"):
                # We need more information - show follow-up question
                followup = validation_result.get("followup_question", "Could you provide more details?")
                st.write(f"💭 {followup}")
                st.session_state.messages.append({"role": "assistant", "content": followup})
            
            elif validation_result.get("success"):
                # We have enough information - generate the trip plan
                st.session_state.conversation_context = []  # Reset for next trip planning
                
                with st.spinner("✈️ Generating your personalized itinerary..."):
                    plan_data = st.session_state.coordinator.plan_trip(combined_input)
                
                # Display the plan
                if plan_data.get("success"):
                    display_travel_plan(plan_data)
                    st.session_state.messages.append({"role": "assistant", "content": "✅ Trip plan generated successfully!"})
                else:
                    error_msg = plan_data.get("error", "Could not generate plan")
                    st.error(f"❌ {error_msg}")
                    st.session_state.messages.append({"role": "assistant", "content": f"❌ Error: {error_msg}"})
            
            else:
                # Error occurred
                error_msg = validation_result.get("error", "An error occurred")
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": f"❌ {error_msg}"})


if __name__ == "__main__":
    main()
