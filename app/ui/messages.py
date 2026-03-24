"""Centralized UI message templates."""


class UIMessages:
    """Centralized store of all UI markdown strings."""
    
    # Header
    HEADER_TITLE = "# ✈️ Roamer Travel Planner"
    HEADER_SUBTITLE = "Your AI-powered travel planning assistant powered by advanced language models."
    
    # Initial greeting
    INITIAL_GREETING = (
        "Hello! 👋 I'm Roamer, your AI travel planner. "
        "Tell me where you'd like to go, how long you'll stay, and what interests you. "
        "I'll create a personalized itinerary for you!"
    )
    
    # Sidebar
    SIDEBAR_CONFIG_TITLE = "## ⚙️ Configuration"
    SIDEBAR_ABOUT_TITLE = "## About Roamer"
    SIDEBAR_ABOUT_TEXT = """Roamer uses AI agents to create personalized travel itineraries:

- 🏛️ **Attraction Agent**: Recommends attractions based on your interests
- 🗺️ **Logistic Agent**: Plans daily itineraries and transportation
- 🤝 **Coordinator Agent**: Orchestrates all agents to create your perfect trip"""
    
    SIDEBAR_HOW_TO_USE_TITLE = "### How to use:"
    SIDEBAR_HOW_TO_USE_TEXT = """1. Tell us where you want to go
2. Mention how long you'll be staying
3. Share your interests and preferences
4. Let our AI agents plan your trip!

Example: "I want to visit Tokyo for 5 days. I love sushi, temples, and technology.\""""
    
    API_KEY_LABEL = "🔑 OpenAI API Key"
    API_KEY_HELP = (
        "Enter your OpenAI API key. Get one at https://platform.openai.com/api-keys"
    )
    API_KEY_SUCCESS = "✓ Using API key from environment"
    API_KEY_WARNING = "⚠️ Please enter your OpenAI API key to continue"
    
    # Chat
    CHAT_INPUT_PLACEHOLDER = "Tell me about your dream trip..."
    
    # Processing states
    VALIDATING_SPINNER = "🤔 Processing..."
    PLANNING_SPINNER = "✈️ Generating your personalized itinerary..."
    
    # Error messages
    ERROR_NO_API_KEY = "❌ Please enter your OpenAI API key in the sidebar to use Roamer"
    ERROR_GENERIC = "❌ {error}"
    ERROR_PLAN_GENERATION = "❌ Could not generate plan"
    
    # Success messages
    SUCCESS_PLAN_GENERATED = "✅ Trip plan generated successfully!"
    
    # Clear history
    CLEAR_HISTORY_BUTTON = "🔄 Clear Chat History"
