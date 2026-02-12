import streamlit as st
import os
import logging
from agents.coordinator_agent import CoordinatorAgent
from agents.display import display_travel_plan

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
    
    # Initialize coordinator agent once per session
    if "coordinator" not in st.session_state:
        api_key = st.session_state.get("api_key")
        if not api_key:
            st.error("❌ Please enter your OpenAI API key in the sidebar to use Roamer")
            st.stop()
        st.session_state.coordinator = CoordinatorAgent("Travel Coordinator", api_key=api_key)
    
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
        
        # Generate response using coordinator agent
        with st.chat_message("assistant"):
            with st.spinner("🤔 Planning your trip..."):
                plan_data = st.session_state.coordinator.fetch_travel_details(prompt)
            
            # Display the plan
            if plan_data.get("success"):
                display_travel_plan(plan_data)
            else:
                st.error(plan_data.get("error", "An error occurred"))
        
        # Store the plan in chat history (as a serializable format)
        st.session_state.messages.append({"role": "assistant", "content": f"Trip plan: {plan_data}"})


if __name__ == "__main__":
    main()
