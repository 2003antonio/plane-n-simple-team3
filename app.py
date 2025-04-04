# app.py
import streamlit as st
from streamlit_option_menu import option_menu

# Import the page modules
import home
import flight_search
import profile_page

# Page config
st.set_page_config(page_title="Plane N Simple", layout="wide")

# Sidebar navigation
with st.sidebar:
    selected = option_menu(
        menu_title="Plane N Simple",
        options=["Home", "Flight Search", "Profile"],
        icons=["house", "search", "person-circle"],
        menu_icon="airplane",
        default_index=0,
    )

# Route to appropriate page
if selected == "Home":
    home.main()
elif selected == "Flight Search":
    flight_search.main()
elif selected == "Profile":
    profile_page.main()
