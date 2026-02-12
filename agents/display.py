"""Display utilities for rendering travel plans in Streamlit."""

import streamlit as st
from typing import Optional


def display_travel_plan(plan_data: dict) -> None:
    """
    Display a structured travel plan using Streamlit components.
    
    Args:
        plan_data: Dictionary with keys: details, attractions, itinerary, transport
    """
    details = plan_data.get("details", {})
    attractions = plan_data.get("attractions", {})
    itinerary = plan_data.get("itinerary", {})
    transport = plan_data.get("transport", {})
    
    # Display errors if any
    error_messages = plan_data.get("errors", [])
    if error_messages:
        with st.warning("⚠️ Some information could not be fetched:"):
            for error in error_messages:
                st.write(f"  • {error}")
    
    # Header with trip details
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📍 Destination", details.get("location", "Unknown"))
    with col2:
        st.metric("📅 Duration", f"{details.get('duration', 3)} days")
    with col3:
        st.metric("👥 Travel Type", details.get("travel_type", "Not specified"))
    with col4:
        interests_text = ", ".join(details.get("interests", [])) if details.get("interests") else "Not specified"
        st.subheader("🎯 Interests")
        st.write(interests_text)
    
    # Attractions section
    st.subheader("🏛️ Top Attractions")
    if "attractions" in attractions and attractions["attractions"]:
        attractions_data = []
        for attraction in attractions["attractions"]:
            attractions_data.append({
                "Attraction": attraction.get("name", "N/A"),
                "Category": attraction.get("category", "N/A"),
                "Duration": attraction.get("hours_needed", "N/A"),
                "Description": attraction.get("description", "N/A")
            })
        st.dataframe(attractions_data, width='stretch', hide_index=True)
    else:
        st.info("No attractions fetched")
    
    # Itinerary section
    st.subheader("📋 Day-by-Day Itinerary")
    if "days" in itinerary and itinerary["days"]:
        for day_plan in itinerary["days"]:
            with st.expander(f"Day {day_plan.get('day_number', '?')}: {day_plan.get('title', 'Day')}"):
                # Activities table
                if "activities" in day_plan and day_plan["activities"]:
                    st.write("**Activities:**")
                    activities_data = []
                    for activity in day_plan["activities"]:
                        activities_data.append({
                            "Time": activity.get("time", "N/A"),
                            "Activity": activity.get("activity", "N/A"),
                            "Duration": activity.get("duration", "N/A")
                        })
                    st.dataframe(activities_data, width='stretch', hide_index=True)
                
                # Meals
                if "meals" in day_plan and isinstance(day_plan["meals"], dict):
                    st.write("**Meals:**")
                    meals = day_plan["meals"]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"🌅 Breakfast: {meals.get('breakfast', 'TBD')}")
                    with col2:
                        st.write(f"🌤️ Lunch: {meals.get('lunch', 'TBD')}")
                    with col3:
                        st.write(f"🌙 Dinner: {meals.get('dinner', 'TBD')}")
                
                # Notes
                if day_plan.get("notes"):
                    st.write(f"**Notes:** {day_plan['notes']}")
    else:
        st.info("No itinerary created")
    
    # Transportation section
    st.subheader("🚗 Transportation Options")
    if "transportation" in transport and transport["transportation"]:
        trans_data = []
        for method in transport["transportation"]:
            trans_data.append({
                "Method": method.get("method", "N/A"),
                "Description": method.get("description", "N/A"),
                "Cost": method.get("cost_estimate", "N/A"),
                "Recommended For": method.get("recommended_for", "N/A")
            })
        st.dataframe(trans_data, width='stretch', hide_index=True)
    else:
        st.info("No transportation options fetched")
    
    st.success("✨ Have a great trip!")
