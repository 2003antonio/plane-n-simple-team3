import streamlit as st
import requests

def main():
    st.title("📍 POI Search")
    st.markdown("Find cool places near your destination using Amadeus APIs!")

    
   ## USE YOUR API STUFF HERE (-Antonio)
    AMADEUS_API_KEY = "your_amadeus_api_key_here"
    AMADEUS_API_SECRET = "your_amadeus_api_secret_here"

    if AMADEUS_API_KEY == "your_amadeus_api_key_here":
        st.warning("Replace the placeholder API key and secret with your actual Amadeus credentials.")
        return


    #generated these using AI so that you can get ideas and how to lay out user input specifications 
    # and layout of data pulled from API
    # ================================
    # 📍 Search Input
    # ================================
    with st.form("poi_search_form"):
        st.subheader("Search Points of Interest")
        city = st.text_input("Enter a city (e.g., Miami)")
        latitude = st.text_input("Latitude (optional)")
        longitude = st.text_input("Longitude (optional)")
        radius = st.slider("Search radius (km)", 1, 50, 10)

        submit = st.form_submit_button("Search")

    # ================================
    # 🚀 Sample Response Placeholder
    # ================================
    if submit and city:
        st.info(f"🔍 Searching POIs around **{city}**...")

        # TODO: Replace this block with Amadeus token + POI API call
        st.code("""
# Example API Call Structure:
# Step 1: Get access token from Amadeus
# Step 2: Use token to query POIs near coordinates

# Endpoint (OAuth2): https://test.api.amadeus.com/v1/security/oauth2/token
# Endpoint (POIs):   https://test.api.amadeus.com/v1/reference-data/locations/pois

# Include city-to-coordinates lookup if using just city names
        """, language="python")

        st.warning("This is just a skeleton. Actual Amadeus API calls will be handled here.")

    elif submit and not city:
        st.error("Please enter a city name to begin your search.")
