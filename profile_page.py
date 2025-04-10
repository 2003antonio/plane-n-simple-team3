# profile_page.py
import streamlit as st
import firebase_admin
from firebase_admin import db as realtimedb
from PIL import Image
import base64
import io

# Show user profile

def main():
    st.title("👤 User Profile")

    uid = st.session_state.get("uid")
    if not uid:
        st.warning("No user is currently logged in.")
        return

    user_ref = realtimedb.reference(f"users/{uid}")
    user_data = user_ref.get()

    if not user_data:
        st.error("User data could not be loaded.")
        return

    # Display profile picture from session or firebase
    profile_pic_bytes = st.session_state.get("profile_pic")
    if profile_pic_bytes:
        b64 = base64.b64encode(profile_pic_bytes).decode()
        st.markdown(f"""
        <div style='display: flex; justify-content: center;'>
            <img src='data:image/jpeg;base64,{b64}' style='width: 200px; height: 200px; object-fit: cover; border-radius: 50%;' />
        </div>
        """, unsafe_allow_html=True)
    elif user_data.get("photo_url"):
        st.markdown(f"""
        <div style='display: flex; justify-content: center;'>
            <img src='{user_data['photo_url']}' style='width: 200px; height: 200px; object-fit: cover; border-radius: 50%;' />
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No profile picture uploaded.")

    # Display and edit user info
    full_name = st.text_input("Full Name", value=user_data.get("full_name", ""))
    phone = st.text_input("Phone Number", value=user_data.get("phone", ""))

    uploaded_file = st.file_uploader("Upload New Profile Picture", type=["png", "jpg", "jpeg"])

    if st.button("Save Changes"):
        update_data = {
            "full_name": full_name,
            "phone": phone
        }

        if uploaded_file:
            bytes_data = uploaded_file.read()
            st.session_state["profile_pic"] = bytes_data
            update_data["photo_url"] = "local-uploaded"

        user_ref.update(update_data)
        st.success("Profile updated in our database!")

if __name__ == "__main__":
    main()