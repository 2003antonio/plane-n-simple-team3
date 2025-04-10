# app.py
import streamlit as st
from streamlit_option_menu import option_menu
import requests
import firebase_admin
from firebase_admin import credentials, db as realtimedb
import home
import flight_search
import profile_page
import time
import os

# Firebase Config from Streamlit secrets
firebase_config = st.secrets["firebase"]
FIREBASE_API_KEY = firebase_config["apiKey"]
FIREBASE_DB_URL = firebase_config["databaseURL"]

# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": firebase_config["type"],
        "project_id": firebase_config["project_id"],
        "private_key_id": firebase_config["private_key_id"],
        "private_key": firebase_config["private_key"].replace('\n', '\n'),
        "client_email": firebase_config["client_email"],
        "auth_uri": firebase_config["auth_uri"],
        "token_uri": firebase_config["token_uri"],
        "auth_provider_x509_cert_url": firebase_config["auth_provider_x509_cert_url"],
        "client_x509_cert_url": firebase_config["client_x509_cert_url"]
    })
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_DB_URL
    })

# Firebase Auth API endpoints
def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    return res.json()

def firebase_signup(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    return res.json()

# Session state
if "login" not in st.session_state:
    st.session_state.login = False

# Login Form
def login_form():
    with st.form("Login"):
        st.subheader("🔐 Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            result = firebase_login(email, password)
            if "idToken" in result:
                st.session_state.login = True
                st.session_state.email = email
                st.session_state.uid = result["localId"]
                st.success("Logged in successfully! Please click 'Run' or refresh manually.")
                st.rerun()
                #st.stop()  # Ends the script run so the UI can reflect login state
            else:
                st.error(result.get("error", {}).get("message", "Login failed"))

# Signup Form
def signup_form():
    with st.form("Sign Up"):
        st.subheader("🆕 Create Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        full_name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        if st.form_submit_button("Sign Up"):
            result = firebase_signup(email, password)
            if "localId" in result:
                uid = result["localId"]
                realtimedb.reference(f"users/{uid}").set({
                    "email": email,
                    "full_name": full_name,
                    "phone": phone
                })
                st.success("Account created! You can log in now.")
            else:
                st.error(result.get("error", {}).get("message", "Signup failed"))

# Page config
st.set_page_config(page_title="Plane N Simple", layout="wide")

# Auth flow
if not st.session_state.login:
    tabs = st.tabs(["Login", "Sign Up"])
    with tabs[0]:
        login_form()
    with tabs[1]:
        signup_form()
else:
    st.markdown("### Welcome to Plane N Simple!")
    uid = st.session_state.get("uid")
    if uid:
        user_data = realtimedb.reference(f"users/{uid}").get()
        name = user_data.get("full_name", "User") if user_data else "User"
        st.write(f"Logged in as: {name}")

    with st.sidebar:
        selected = option_menu(
            menu_title="Plane N Simple",
            options=["Home", "Flight Search", "Profile"],
            icons=["house", "search", "person-circle"],
            menu_icon="airplane",
            default_index=0,
        )

    if selected == "Home":
        home.main()
    elif selected == "Flight Search":
        flight_search.main()
    elif selected == "Profile":
        profile_page.main()
