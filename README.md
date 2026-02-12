# 🌍 Roamer - AI Travel Planning Assistant

Roamer is an intelligent travel planning application that uses a multi-agent AI architecture to create personalized travel itineraries. It combines three specialized AI agents to deliver comprehensive travel plans.

## Features

### 🤖 Multi-Agent Architecture

1. **Attraction Agent** - Recommends attractions and activities based on user interests
2. **Logistic Agent** - Plans daily itineraries and provides transportation suggestions
3. **Coordinator Agent** - Orchestrates all agents to create cohesive travel plans

### ✨ Key Capabilities

- 📍 Intelligent destination analysis
- 🎯 Interest-based attraction recommendations
- 📅 Day-by-day itinerary planning
- 🚗 Local transportation guidance
- 💬 Conversational interface powered by Streamlit
- 🤖 LLM-powered intelligence using OpenAI GPT

## Prerequisites

- Python 3.12 or higher
- OpenAI API key
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd roamer
   ```

2. **Install dependencies with uv**
   ```bash
   uv sync
   ```
   This automatically creates a virtual environment and installs all dependencies.

3. **Install dev dependencies (optional, for testing)**
   ```bash
   uv sync --all-extras
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Start the Streamlit app:

```bash
uv run streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`

### Running Tests

Run the full test suite:
```bash
uv run pytest tests/ -v
```

Run tests with coverage:
```bash
uv run pytest tests/ --cov=agents --cov-report=html
```

Run specific test file:
```bash
uv run pytest tests/test_base_agent.py -v
```

### How to Use

1. **Enter your travel request** in the chat input
2. **Include details** such as:
   - Destination (e.g., "Tokyo")
   - Duration (e.g., "5 days")
   - Interests (e.g., "temples, sushi, technology")
3. **Get your personalized plan** including:
   - Top attractions matching your interests
   - Day-by-day itinerary with timings
   - Transportation recommendations
   - Meal suggestions

### Example Queries

- "I want to visit Paris for 4 days. I love art, museums, and French cuisine."
- "Planning a week in Barcelona. Interested in beaches, architecture, and nightlife."
- "3-day trip to Tokyo. Love hiking, anime, and street food."

## Architecture

The application uses a coordinator pattern where:

1. **User Input** → CoordinatorAgent processes the travel request
2. **Parsing** → Extracts location, duration, interests from user input
3. **Attraction Recommendations** → AttractionAgent finds relevant attractions
4. **Itinerary Planning** → LogisticAgent creates day-by-day plans
5. **Transportation** → LogisticAgent provides transport options
6. **Formatting** → Results are compiled into a readable travel plan

## API Integration

This app uses the OpenAI API with the following models:
- `gpt-3.5-turbo` - For quick, cost-effective processing

### API Calls Made

- `parse_travel_details()` - Extracts travel parameters (~300 tokens)
- `find_attractions()` - Recommends attractions (~500 tokens)
- `create_itinerary()` - Plans daily activities (~1000 tokens)
- `get_transportation_suggestions()` - Transportation info (~300 tokens)

**Estimated cost per request**: ~0.003-0.005 USD (with gpt-3.5-turbo pricing)

## Configuration

You can customize the LLM model by editing the agent files `config.py`

## Error Handling

The app includes error handling for:
- Missing or invalid API keys
- Network connectivity issues
- Invalid JSON responses from LLM
- Missing travel details

Users will receive friendly error messages to help them correct their input.

## Future Enhancements

- [ ] Real-time flight and hotel pricing integration
- [ ] Multi-language support
- [ ] User preference learning and history
- [ ] Integration with booking platforms (Google Flights, Airbnb)
- [ ] Weather forecasting for destinations
- [ ] Budget tracking and recommendations
- [ ] Downloadable trip planner

## Troubleshooting

### "JSON decode error"
The LLM response might not be valid JSON. Try rephrasing your request or check API rate limits.

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review your OpenAI API usage and limits
3. Ensure your travel request includes enough details (location + duration)

---

Happy traveling with Roamer! ✈️🌍
