"""Tests for display utilities."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from agents.display import display_travel_plan, TravelPlanDisplay


class TestDisplayTravelPlan:
    """Test suite for display_travel_plan function."""
    
    @patch("agents.display.st")
    def test_display_with_complete_data(self, mock_st):
        """Should display plan with all sections."""
        # Mock st.columns to return proper mock objects that support context managers
        mock_col = MagicMock()
        # Handle multiple calls to st.columns with different numbers
        def mock_columns(n):
            return [mock_col] * n
        mock_st.columns.side_effect = mock_columns
        mock_st.expander.return_value = MagicMock()
        mock_st.warning.return_value = MagicMock()
        
        plan_data = {
            "details": {
                "location": "Paris",
                "duration": 3,
                "travel_type": "couple",
                "interests": ["art", "food"]
            },
            "attractions": {
                "attractions": [
                    {
                        "name": "Louvre",
                        "category": "museum",
                        "hours_needed": "3 hours",
                        "description": "Art museum"
                    }
                ]
            },
            "itinerary": {
                "days": [
                    {
                        "day_number": "1",
                        "title": "Arrival",
                        "activities": [
                            {
                                "time": "09:00",
                                "activity": "Check-in",
                                "duration": "1 hour"
                            }
                        ],
                        "meals": {
                            "breakfast": "Hotel",
                            "lunch": "Café",
                            "dinner": "Restaurant"
                        },
                        "notes": "Rest and explore"
                    }
                ]
            },
            "transport": {
                "transportation": [
                    {
                        "method": "Metro",
                        "description": "Fast transport",
                        "cost_estimate": "$5/day",
                        "recommended_for": "Daily travel"
                    }
                ]
            },
            "errors": []
        }
        
        # Should not raise any exceptions
        display_travel_plan(plan_data)
        
        # Verify key display methods were called
        assert mock_st.metric.called
        assert mock_st.subheader.called
    
    @patch("agents.display.st")
    def test_display_with_errors(self, mock_st):
        """Should display error messages."""
        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col, mock_col, mock_col]
        mock_st.warning.return_value = MagicMock()
        
        plan_data = {
            "details": {"location": "Unknown"},
            "attractions": {},
            "itinerary": {},
            "transport": {},
            "errors": ["Could not fetch attractions", "Could not fetch transportation"]
        }
        
        display_travel_plan(plan_data)
        
        # Should display warnings for errors
        assert mock_st.warning.called or mock_st.info.called
    
    @patch("agents.display.st")
    def test_display_with_missing_attractions(self, mock_st):
        """Should handle missing attractions gracefully."""
        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col, mock_col, mock_col]
        
        plan_data = {
            "details": {"location": "Rome"},
            "attractions": {},
            "itinerary": {},
            "transport": {},
            "errors": []
        }
        
        display_travel_plan(plan_data)
        
        # Should call info() for missing data
        assert mock_st.info.called
    
    @patch("agents.display.st")
    def test_display_with_missing_itinerary(self, mock_st):
        """Should handle missing itinerary gracefully."""
        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col, mock_col, mock_col]
        mock_st.expander.return_value = MagicMock()
        
        plan_data = {
            "details": {"location": "Rome"},
            "attractions": {"attractions": []},
            "itinerary": {},
            "transport": {},
            "errors": []
        }
        
        display_travel_plan(plan_data)
        
        assert mock_st.info.called
    
    @patch("agents.display.st")
    def test_display_with_missing_transportation(self, mock_st):
        """Should handle missing transportation gracefully."""
        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col, mock_col, mock_col]
        mock_st.expander.return_value = MagicMock()
        
        plan_data = {
            "details": {"location": "Rome"},
            "attractions": {"attractions": []},
            "itinerary": {"days": []},
            "transport": {},
            "errors": []
        }
        
        display_travel_plan(plan_data)
        
        assert mock_st.info.called
    
    @patch("agents.display.st")
    def test_display_with_default_values(self, mock_st):
        """Should use defaults when data is missing."""
        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col, mock_col, mock_col]
        
        plan_data = {}
        
        display_travel_plan(plan_data)
        
        # Should still display without crashing
        assert mock_st.metric.called or mock_st.subheader.called

    @patch("agents.display.st")
    def test_display_day_plan_no_duplicate_day_prefix(self, mock_st):
        """Should not display duplicate 'Day' when title already includes day info."""
        mock_col = MagicMock()
        mock_st.columns.side_effect = lambda n: [mock_col] * n
        mock_st.expander.return_value = MagicMock()
        
        plan_data = {
            "details": {"location": "Test"},
            "attractions": {"attractions": []},
            "itinerary": {
                "days": [
                    {
                        "day_number": "1",
                        "title": "Day 1: Arrival in Queenstown",
                        "activities": [],
                        "meals": {},
                        "notes": ""
                    }
                ]
            },
            "transport": {"transportation": []},
            "errors": []
        }
        
        display_travel_plan(plan_data)
        
        # Verify expander was called without duplicate "Day"
        # Should be "Day 1: Arrival in Queenstown" not "Day Day 1: Arrival in Queenstown"
        mock_st.expander.assert_called_with("Day 1: Arrival in Queenstown")

    @patch("agents.display.st")
    def test_display_day_plan_with_simple_title(self, mock_st):
        """Should add 'Day X:' prefix when title is simple description."""
        mock_col = MagicMock()
        mock_st.columns.side_effect = lambda n: [mock_col] * n
        mock_st.expander.return_value = MagicMock()
        
        plan_data = {
            "details": {"location": "Test"},
            "attractions": {"attractions": []},
            "itinerary": {
                "days": [
                    {
                        "day_number": "1",
                        "title": "Arrival",
                        "activities": [],
                        "meals": {},
                        "notes": ""
                    }
                ]
            },
            "transport": {"transportation": []},
            "errors": []
        }
        
        display_travel_plan(plan_data)
        
        # Verify expander was called with proper format
        # Should be "Day 1: Arrival"
        mock_st.expander.assert_called_with("Day 1: Arrival")
