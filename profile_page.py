import streamlit as st
import json
import os

def main():
    st.title("👤 User Profile")

    username = st.session_state.get("username")
    if not username:
        st.warning("No user logged in.")
        return

    # Load user data from secrets.json
    user_data_path = "_secret_auth_.json"  # Update path if needed
    if not os.path.exists(user_data_path):
        st.error("User data not found.")
        return

    with open(user_data_path, "r") as f:
        users = json.load(f)

    # Find current user
    user = next((u for u in users if u["username"] == username), None)
    if not user:
        st.error("User not found in database.")
        return

    # Show user data (except password)
    full_name = st.text_input("Full Name", value=user.get("name", ""))
    email = st.text_input("Email", value=user.get("email", ""), disabled=True)
    phone = st.text_input("Phone Number", value=st.session_state.get("phone", ""))  # Optional

    st.file_uploader("Upload Profile Picture", type=["jpg", "png"])

    if st.button("Save Changes"):
        st.session_state["phone"] = phone
        st.session_state["name"] = full_name
        st.success("Profile updated successfully!")
