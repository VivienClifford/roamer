"""Configuration settings for travel planning agents."""

# OpenAI API Configuration
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_TEMPERATURE = 0.7

# Token limits for different operations
TOKENS_ATTRACTION = 1000
TOKENS_ITINERARY = 2000
TOKENS_TRANSPORT = 1000
TOKENS_PARSING = 500

# System prompts
SYSTEM_TRAVEL_GUIDE = "You are a knowledgeable travel guide. Respond with valid JSON only."
SYSTEM_TRAVEL_PLANNER = "You are an expert travel planner. Respond with valid JSON only."
SYSTEM_TRAVEL_DETAILS = "Extract travel details. Respond with valid JSON only."
SYSTEM_LOGISTIC_EXPERT = "You are a travel logistics expert. Respond with valid JSON only."
