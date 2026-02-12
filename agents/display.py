"""Display utilities for rendering travel plans in Streamlit."""

import streamlit as st
from dataclasses import dataclass
from typing import Optional


# UI Configuration Constants - easy to customize
@dataclass
class UIConfig:
    """Centralized UI labels and emojis."""
    DESTINATION_EMOJI = "📍"
    DURATION_EMOJI = "📅"
    TRAVEL_TYPE_EMOJI = "👥"
    INTERESTS_EMOJI = "🎯"
    ATTRACTIONS_EMOJI = "🏛️"
    ITINERARY_EMOJI = "📋"
    TRANSPORT_EMOJI = "🚗"
    BREAKFAST_EMOJI = "🌅"
    LUNCH_EMOJI = "🌤️"
    DINNER_EMOJI = "🌙"
    WARNING_EMOJI = "⚠️"
    SUCCESS_EMOJI = "✨"


class TravelPlanDisplay:
    """Manages the display of travel plan data using Streamlit components."""
    
    def __init__(self, plan_data: dict, config: Optional[UIConfig] = None):
        """
        Initialize the display handler.
        
        Args:
            plan_data: Dictionary with keys: details, attractions, itinerary, transport, errors
            config: Optional UI configuration for customizing labels and emojis
        """
        self.plan_data = plan_data
        self.config = config or UIConfig()
    
    def render(self) -> None:
        """Render the complete travel plan display."""
        self._display_errors()
        self._display_trip_summary()
        self._display_attractions()
        self._display_itinerary()
        self._display_transportation()
        self._display_closing()
    
    def _display_errors(self) -> None:
        """Display any errors that occurred during plan generation."""
        error_messages = self.plan_data.get("errors", [])
        if error_messages:
            with st.warning(f"{self.config.WARNING_EMOJI} Some information could not be fetched:"):
                for error in error_messages:
                    st.write(f"  • {error}")
    
    def _display_trip_summary(self) -> None:
        """Display high-level trip details in a metrics row."""
        details = self.plan_data.get("details", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            location = details.get("location", "Unknown")
            st.metric(f"{self.config.DESTINATION_EMOJI} Destination", location)
        
        with col2:
            duration = details.get("duration", 3)
            st.metric(f"{self.config.DURATION_EMOJI} Duration", f"{duration} days")
        
        with col3:
            travel_type = details.get("travel_type", "Not specified")
            st.metric(f"{self.config.TRAVEL_TYPE_EMOJI} Travel Type", travel_type)
        
        with col4:
            interests = self._format_interests(details.get("interests", []))
            st.subheader(f"{self.config.INTERESTS_EMOJI} Interests")
            st.write(interests)
    
    def _display_attractions(self) -> None:
        """Display the list of top attractions."""
        st.subheader(f"{self.config.ATTRACTIONS_EMOJI} Top Attractions")
        
        attractions = self.plan_data.get("attractions", {})
        attractions_list = attractions.get("attractions", [])
        
        if not attractions_list:
            st.info("No attractions fetched")
            return
        
        attractions_data = [
            {
                "Attraction": attraction.get("name", "N/A"),
                "Category": attraction.get("category", "N/A"),
                "Duration": attraction.get("hours_needed", "N/A"),
                "Description": attraction.get("description", "N/A")
            }
            for attraction in attractions_list
        ]
        st.dataframe(attractions_data, width='stretch', hide_index=True)
    
    def _display_itinerary(self) -> None:
        """Display the day-by-day itinerary."""
        st.subheader(f"{self.config.ITINERARY_EMOJI} Day-by-Day Itinerary")
        
        itinerary = self.plan_data.get("itinerary", {})
        days = itinerary.get("days", [])
        
        if not days:
            st.info("No itinerary created")
            return
        
        for day_plan in days:
            self._display_day_plan(day_plan)
    
    def _display_day_plan(self, day_plan: dict) -> None:
        """Display a single day's plan in an expander."""
        day_number = day_plan.get("day_number", "?")
        day_title = day_plan.get("title", "Day")
        
        expander_label = self._format_day_label(day_number, day_title)
        
        with st.expander(expander_label):
            self._display_day_activities(day_plan)
            self._display_day_meals(day_plan)
            self._display_day_notes(day_plan)
    
    @staticmethod
    def _format_day_label(day_number: str, day_title: str) -> str:
        """
        Format the day label for display, preventing duplicate "Day" prefix.
        
        Args:
            day_number: The day number (e.g., "1", "2")
            day_title: The day title or description
        
        Returns:
            Formatted label (e.g., "Day 1: Arrival" or "Day 1: Arrival in Queenstown")
        """
        # Prevent duplicate "Day" prefix if title already contains day information
        if day_title.strip().startswith(f"Day {day_number}"):
            # Title already includes day info (e.g., "Day 1: Arrival"), use as-is
            return day_title
        else:
            # Title is just a description, prepend day info (e.g., "Arrival" -> "Day 1: Arrival")
            return f"Day {day_number}: {day_title}"
    
    def _display_day_activities(self, day_plan: dict) -> None:
        """Display activities for a day."""
        activities = day_plan.get("activities", [])
        
        if not activities:
            return
        
        st.write("**Activities:**")
        activities_data = [
            {
                "Time": activity.get("time", "N/A"),
                "Activity": activity.get("activity", "N/A"),
                "Duration": activity.get("duration", "N/A")
            }
            for activity in activities
        ]
        st.dataframe(activities_data, width='stretch', hide_index=True)
    
    def _display_day_meals(self, day_plan: dict) -> None:
        """Display meal recommendations for a day."""
        meals = day_plan.get("meals", {})
        
        if not isinstance(meals, dict) or not meals:
            return
        
        st.write("**Meals:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            breakfast = meals.get("breakfast", "TBD")
            st.write(f"{self.config.BREAKFAST_EMOJI} Breakfast: {breakfast}")
        
        with col2:
            lunch = meals.get("lunch", "TBD")
            st.write(f"{self.config.LUNCH_EMOJI} Lunch: {lunch}")
        
        with col3:
            dinner = meals.get("dinner", "TBD")
            st.write(f"{self.config.DINNER_EMOJI} Dinner: {dinner}")
    
    def _display_day_notes(self, day_plan: dict) -> None:
        """Display notes for a day."""
        notes = day_plan.get("notes")
        if notes:
            st.write(f"**Notes:** {notes}")
    
    def _display_transportation(self) -> None:
        """Display transportation options."""
        st.subheader(f"{self.config.TRANSPORT_EMOJI} Transportation Options")
        
        transport = self.plan_data.get("transport", {})
        transportation_list = transport.get("transportation", [])
        
        if not transportation_list:
            st.info("No transportation options fetched")
            return
        
        trans_data = [
            {
                "Method": method.get("method", "N/A"),
                "Description": method.get("description", "N/A"),
                "Cost": method.get("cost_estimate", "N/A"),
                "Recommended For": method.get("recommended_for", "N/A")
            }
            for method in transportation_list
        ]
        st.dataframe(trans_data, width='stretch', hide_index=True)
    
    def _display_closing(self) -> None:
        """Display closing message."""
        st.success(f"{self.config.SUCCESS_EMOJI} Have a great trip!")
    
    @staticmethod
    def _format_interests(interests: list) -> str:
        """Format interests list as a comma-separated string."""
        if not interests:
            return "Not specified"
        return ", ".join(interests)


# Backward compatibility function
def display_travel_plan(plan_data: dict) -> None:
    """
    Display a structured travel plan using Streamlit components.
    
    Args:
        plan_data: Dictionary with keys: details, attractions, itinerary, transport, errors
    """
    display = TravelPlanDisplay(plan_data)
    display.render()