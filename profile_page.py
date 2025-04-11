# profile_page.py
import streamlit as st
import firebase_admin
from firebase_admin import db as realtimedb
import urllib.parse

def main():
    st.markdown("<h1 style='text-align: center;'>👤 User Profile</h1>", unsafe_allow_html=True)

    uid = st.session_state.get("uid")
    if not uid:
        st.warning("No user is currently logged in.")
        return

    user_ref = realtimedb.reference(f"users/{uid}")
    user_data = user_ref.get()

    if not user_data:
        st.error("User data could not be loaded.")
        return

    full_name = user_data.get("full_name", "User")
    phone = user_data.get("phone", "")
    email = user_data.get("email", "Not provided")

    initials = "".join([part[0] for part in full_name.split() if part]).upper()
    encoded_initials = urllib.parse.quote_plus(initials)

    # Always use fallback avatar based on initials
    avatar_src = f"https://ui-avatars.com/api/?name={encoded_initials}&size=200&background=cccccc&color=555555&rounded=true"

    # Show avatar
    st.markdown(f"""
        <style>
            .avatar-container {{
                display: flex;
                justify-content: center;
                margin-bottom: 20px;
            }}
            .avatar-img {{
                width: 200px;
                height: 200px;
                object-fit: cover;
                border-radius: 50%;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }}
        </style>
        <div class="avatar-container">
            <img src="{avatar_src}" class="avatar-img" />
        </div>
    """, unsafe_allow_html=True)

    # Show read-only and editable fields
    st.text_input("Email", value=email, disabled=True)
    updated_name = st.text_input("Full Name", value=full_name)
    updated_phone = st.text_input("Phone Number", value=phone)

    if st.button("Save Changes"):
        user_ref.update({
            "full_name": updated_name,
            "phone": updated_phone
        })
        st.success("Profile updated in our database!")

if __name__ == "__main__":
    main()
