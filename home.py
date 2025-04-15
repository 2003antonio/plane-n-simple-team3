import streamlit as st
import os
import pandas as pd
import pydeck as pdk

def main():
    # Use image from web_images directory
    image_path = os.path.join("web_images", "home_banner.jpg")
    st.image(image_path)

    st.markdown("<h1 style='text-align: center; color: #1E90FF;'>Plane N Simple ✈️</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Find airports and book flights with ease!</h3>", unsafe_allow_html=True)

    st.write("### Welcome to Plane N Simple!")

    st.write("""
    Plane N Simple is a streamlined travel assistant designed to help users search and compare real-time flights across thousands of global airports using **Amadeus API** data. It provides a user-friendly interface for planning air travel, discovering airport information, and exploring entertainment options around your destination.

    We also use the **Geoapify Places API** to retrieve **Points of Interest (POIs)** — such as restaurants, entertainment venues, and attractions — located near the user’s selected airport or city.

    #### 🧠 Project Overview
    This web-based application was developed with modern frontend and backend technologies to simulate a real-world travel planning platform. It enables the user to interact with live APIs, sort through useful data efficiently, and navigate a seamless interface. The goal was to design a scalable, intuitive, and robust travel planner that incorporates both functionality and aesthetics.

    #### 🚀 Key Features
    - 🔍 **Flight Search**: Look up flights by selecting departure and arrival airports and choosing a travel date.
    - ⚙️ **Flight Sorting**: Sort results by price (low-high, high-low), departure time, arrival time, or airline name.
    - 📍 **Airport Map**: View a full map of supported airports with hoverable locations using PyDeck.
    - ✅ **Strict Match**: Filter only flights that strictly match the selected origin and destination.
    - 🗺️ **POI Search (via Geoapify API)**: Discover nearby attractions and services near your destination airport.
    - 🔐 **Reset Password**: Forgot your password? No problem — users can securely reset it through the profile page.
    - 🛠️ **Admin Panel** *(for authorized users)*: Access backend functions for managing analytics and user settings.

    #### 👨‍💻 Meet the Developers
    - **Joshua Rios** implemented the **flight sorting & filtering** feature and polished Flight Search and the Home page for smooth and intuitive interactions.
    - **Barbara Garcia** integrated the **Amadeus Flight API** and managed API authentication and error handling for Flight Search.
    - **Nicholas Juman** developed the **POI Search** functionality using **Geoapify** for location-based results.
    - **Danielle Maki** implemented the **Admin Control functionality** and conducted **database research** for future scalability and data persistence.
    - **Antonio Martinez** lead developer and architect behind the Plane N Simple App. Contributed to Firebase integration, login, logout, feature testing, website deployment, and overall UI design to ensure the site is functional and intuitive.

    We built this project as part of **Team 3 - CEN 4010 Software Engineering**, aiming to model a professional-grade web application with clear documentation, modular code, and thoughtful user-centered design.
    """)

    try:
        csv_file = "airports.csv"
        df = pd.read_csv(csv_file)

        with st.expander("📍 All Airlines Supported by Us!"):
            st.write("Hover over a point to see the airport name.")

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position=["longitude", "latitude"],
                get_color=[255, 0, 0, 150],
                get_radius=20000,
                pickable=True,
            )

            tooltip = {
                "html": "<b>{name}</b><br/><b>{iata_code}</b><br/><b>{latitude}, {longitude}</b>",
                "style": {"backgroundColor": "white", "color": "#404040", "border-radius": "10px", "padding": "10px 15px"},
            }

            map = pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state=pdk.ViewState(
                    latitude=df["latitude"].mean(),
                    longitude=df["longitude"].mean(),
                    zoom=3,
                    pitch=0,
                ),
                layers=[layer],
                tooltip=tooltip,
            )

            st.pydeck_chart(map)

    except Exception as e:
        st.warning(f"⚠️ Unable to load airport map: {e}")

if __name__ == "__main__":
    main()
