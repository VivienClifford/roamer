# 🌍 Roamer - AI Travel Planning Assistant

Roamer is an intelligent travel planning application that uses a multi-agent AI architecture to create personalized travel itineraries. It combines three specialized AI agents to deliver comprehensive travel plans.

## Features

### 🤖 Multi-Agent Architecture

1. **Conversation Manager** - Gathers and validates travel information, asks clarifying follow-up questions
2. **Attraction Agent** - Recommends attractions and activities based on user interests
3. **Logistic Agent** - Plans daily itineraries and provides transportation suggestions
4. **Coordinator Agent** - Orchestrates planning agents to create cohesive travel plans

### ✨ Key Capabilities

- � **Interactive prompting** - Asks follow-up questions if information is incomplete
- 📍 **Intelligent destination analysis** - Parses travel requests and validates required fields
- 🎯 **Interest-based recommendations** - Suggests attractions matching your interests
- 📅 **Day-by-day planning** - Creates detailed itineraries with timings
- 🚗 **Transportation guidance** - Provides local transport options
- 🎨 **Conversational Streamlit UI** - Natural chat-based interaction
- 🤖 **LLM-powered** - Uses OpenAI GPT for intelligent analysis

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

### What Information Roamer Needs

For a personalized itinerary, Roamer requires:
- **Destination** (required) - Where do you want to go?
- **Duration** (required) - How many days will you stay?
- **Interests** (required) - What activities interest you?
- **Budget** (optional) - low, medium, or high
- **Travel type** (optional) - solo, couple, family, or group

### Example Conversations

**Example 1 - Minimal to Complete**
```
You: Paris
Roamer: How long will you stay?
You: 4 days, museums and cafes
Roamer: ✨ Generates 4-day Parisian itinerary
```

**Example 2 - Complete Request**
```
You: I want to visit Tokyo for 5 days. I love temples, sushi, and technology.
Roamer: ✨ Generates personalized 5-day Tokyo itinerary
```

**Example 3 - Multi-turn with Multiple Follow-ups**
```
You: Barcelona
Roamer: How many days will you be there?
You: A week
Roamer: What are your main interests?
You: Beaches, architecture, and nightlife
Roamer: ✨ Generates comprehensive 7-day Barcelona plan
```

## Architecture

Roamer uses a multi-stage processing pipeline:

1. **Conversation Manager** → Validates user input and gathers missing information
   - Parses travel details (location, duration, interests, etc.)
   - Analyzes what information is provided vs. missing
   - Generates contextual follow-up questions if needed
   - Validates complete information before proceeding

2. **Coordinator Agent** → Orchestrates planning once all info is complete
   - Requests attraction recommendations from AttractionAgent
   - Creates itinerary with LogisticAgent
   - Gathers transportation suggestions
   - Compiles results into structured travel plan

3. **Supporting Agents**
   - **AttractionAgent** → Finds attractions matching user interests
   - **LogisticAgent** → Creates day-by-day itineraries and transport options

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
