import streamlit as st
import firebase_admin
from firebase_admin import db as realtimedb

def main():
    uid = st.session_state.get("uid", None)
    if not uid:
        st.error("You are not logged in.")
        return

    # Check user data for admin flag
    user_data = realtimedb.reference(f"users/{uid}").get()
    is_admin = user_data.get("admin", False) if user_data else False

    if is_admin:
        st.title("🛠️ Admin Dashboard")
        st.success("You have admin access.")
        st.write("Welcome to your travel control center, captain. ✈️")
        st.warning("🚧 This admin page is still under construction. Expect turbulence and missing features.")

        # 🎛️ Admin Control Panel
        st.subheader("🗺️ Travel Planner Admin Controls")

        # Fun travel-planner-style toggles
        spotlight_destination = st.toggle("🎯 Spotlight Featured Destination")
        hotel_sync = st.toggle("🏨 Refresh Hotel Listings")
        calendar_force_sync = st.toggle("📆 Force Calendar Sync")
        poi_reveal = st.toggle("🔍 Reveal Hidden POIs")
        magic_getaway = st.toggle("✨ Promote a Magical Getaway")

        # Collect status messages based on what's toggled
        status_messages = []

        if spotlight_destination:
            status_messages.append("🎯 Destination of the day is now highlighted across the site!")

        if hotel_sync:
            status_messages.append("🏨 Hotel listings synced with external APIs.")

        if calendar_force_sync:
            status_messages.append("📆 Travel calendars are now in perfect harmony.")

        if poi_reveal:
            status_messages.append("🔍 Secret points of interest revealed to VIP users.")

        if magic_getaway:
            status_messages.append("✨ One lucky location now has the best deals. Almost too good to be true, a bit sus, kind of deals.")

        # Display results
        if status_messages:
            st.success("Admin Actions Executed:")
            for msg in status_messages:
                st.write(msg)
        else:
            st.info("🌍 No actions taken yet. Flip a few switches to make the magic happen.")


    else:
        st.error("🚫 Sorry, you do not have permission to view this page. You must have admin privileges.")

