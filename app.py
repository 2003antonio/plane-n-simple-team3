import streamlit as st
from streamlit_option_menu import option_menu
import requests
import firebase_admin
from firebase_admin import credentials, db as realtimedb
import pandas as pd
import pyotp
import qrcode
from io import BytesIO
import base64

# Internal modules
import home
import flight_search
import profile_page
import poi_search
import travel_plans

# Page config with tab title, emoji, and wide layout
st.set_page_config(
    page_title="plane-n-simple",
    layout="wide",
    page_icon="✈️",
    initial_sidebar_state="auto"
)

if "show_2fa_qr" not in st.session_state:
    st.session_state.show_2fa_qr = False
if "twofa_secret" not in st.session_state:
    st.session_state.twofa_secret = None
if "new_user_email" not in st.session_state:
    st.session_state.new_user_email = ""
if "show_2fa_login" not in st.session_state:
    st.session_state.show_2fa_login = False
if "pending_uid" not in st.session_state:
    st.session_state.pending_uid = None
if "pending_email" not in st.session_state:
    st.session_state.pending_email = ""
if "setup_2fa_login" not in st.session_state:
    st.session_state.setup_2fa_login = False
if "temp_twofa_secret" not in st.session_state:
    st.session_state.temp_twofa_secret = None


# Safe Firebase config handling
try:
    firebase_config = st.secrets["firebase"]
    FIREBASE_API_KEY = firebase_config["apiKey"]
    FIREBASE_DB_URL = firebase_config["databaseURL"]

    if not firebase_admin._apps:
        cred = credentials.Certificate({
            "type": firebase_config["type"],
            "project_id": firebase_config["project_id"],
            "private_key_id": firebase_config["private_key_id"],
            "private_key": firebase_config["private_key"],
            "client_email": firebase_config["client_email"],
            "auth_uri": firebase_config["auth_uri"],
            "token_uri": firebase_config["token_uri"],
            "auth_provider_x509_cert_url": firebase_config["auth_provider_x509_cert_url"],
            "client_x509_cert_url": firebase_config["client_x509_cert_url"]
        })
        firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_DB_URL
        })

except Exception as e:
    st.error("🚨 Critical error: Firebase secrets are missing or misconfigured.")
    st.stop()

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

def firebase_reset_password(email):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
    payload = {"requestType": "PASSWORD_RESET", "email": email}
    res = requests.post(url, json=payload)
    return res.json()

# Session state
if "login" not in st.session_state:
    st.session_state.login = False

# Login Form
def login_form():
    if not st.session_state.get("show_2fa_login") and not st.session_state.get("setup_2fa_login"):
        with st.form("Login"):
            st.subheader("🔐 Login")
            email = st.text_input("Email", value="weakspicedev@gmail.com")
            password = st.text_input("Password", type="password", value="Cipher1$")
            col1, col2 = st.columns([1, 1])
            with col1:
                login = st.form_submit_button("Login")
            with col2:
                reset = st.form_submit_button("Forgot Password")

        if login:
            result = firebase_login(email, password)
            if "idToken" in result:
                uid = result["localId"]
                user_info = realtimedb.reference(f"users/{uid}").get()

                if not user_info or "twofa_secret" not in user_info:
                    st.session_state.pending_uid = uid
                    st.session_state.pending_email = email
                    st.session_state.temp_twofa_secret = pyotp.random_base32()
                    st.session_state.setup_2fa_login = True
                    st.rerun()
                else:
                    st.session_state.pending_uid = uid
                    st.session_state.pending_email = email
                    st.session_state.twofa_secret = user_info["twofa_secret"]
                    st.session_state.show_2fa_login = True
                    st.rerun()
            else:
                st.error(result.get("error", {}).get("message", "Login failed"))

        if reset:
            users_ref = realtimedb.reference("users")
            users_data = users_ref.get()
            email_exists = any(user.get("email") == email for user in users_data.values()) if users_data else False

            if email_exists:
                result = firebase_reset_password(email)
                if "email" in result:
                    st.success(f"Password reset email sent to {email}!")
                else:
                    st.error(result.get("error", {}).get("message", "Password reset failed"))
            else:
                st.error("❌ This email is not registered in our system.")

    elif st.session_state.get("show_2fa_login"):
        st.warning("🔐 Two-Factor Authentication Required")

        with st.form("2FA Verify Login"):
            token = st.text_input("Enter 6-digit code from your Authenticator app")
            verify_btn = st.form_submit_button("Verify Code")

        if verify_btn:
            totp = pyotp.TOTP(st.session_state.twofa_secret)
            if totp.verify(token):
                st.session_state.login = True
                st.session_state.email = st.session_state.pending_email
                st.session_state.uid = st.session_state.pending_uid

                for key in ["show_2fa_login", "pending_uid", "pending_email", "twofa_secret"]:
                    st.session_state.pop(key, None)

                st.success("✅ 2FA Verified! Please click 'Run' or refresh manually.")
                st.rerun()
            else:
                st.error("❌ Invalid 2FA code. Please try again.")

    elif st.session_state.get("setup_2fa_login"):
        st.warning("🚨 2FA is not set up for this account. Let's fix that.")

        totp = pyotp.TOTP(st.session_state.temp_twofa_secret)
        uri = totp.provisioning_uri(name=st.session_state.pending_email, issuer_name="Plane N Simple")

        qr = qrcode.make(uri)
        buf = BytesIO()
        qr.save(buf)
        b64_qr = base64.b64encode(buf.getvalue()).decode()

        st.markdown("### 🔐 Set Up 2FA Now")
        st.image(f"data:image/png;base64,{b64_qr}")
        st.markdown("Scan this QR code with Google Authenticator or Authy.")
        st.markdown("Then enter the 6-digit code below:")

        with st.form("2FA First-Time Setup During Login"):
            token = st.text_input("Enter the 6-digit code")
            verify_btn = st.form_submit_button("Enable and Login")

        if verify_btn:
            if totp.verify(token):
                realtimedb.reference(f"users/{st.session_state.pending_uid}/twofa_secret").set(st.session_state.temp_twofa_secret)
                st.session_state.login = True
                st.session_state.email = st.session_state.pending_email
                st.session_state.uid = st.session_state.pending_uid

                # Cleanup
                for key in ["setup_2fa_login", "temp_twofa_secret", "pending_uid", "pending_email"]:
                    st.session_state.pop(key, None)

                st.success("✅ 2FA setup complete. You're now logged in!")
                st.rerun()
            else:
                st.error("❌ Invalid 2FA code. Please try again.")


# Signup Form
def signup_form():
    if not st.session_state.show_2fa_qr:
        with st.form("Sign Up"):
            st.subheader("🆕 Create Account")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            full_name = st.text_input("Full Name")
            phone = st.text_input("Phone Number")
            signup_btn = st.form_submit_button("Sign Up")

        if signup_btn:
            result = firebase_signup(email, password)
            if "localId" in result:
                uid = result["localId"]
                twofa_secret = pyotp.random_base32()

                realtimedb.reference(f"users/{uid}").set({
                    "email": email,
                    "full_name": full_name,
                    "phone": phone,
                    "admin": False,
                    "twofa_secret": twofa_secret
                })

                st.session_state.show_2fa_qr = True
                st.session_state.twofa_secret = twofa_secret
                st.session_state.new_user_email = email
                st.rerun()
            else:
                st.error(result.get("error", {}).get("message", "Signup failed"))

    else:
        st.success("✅ Account created successfully!")

        totp = pyotp.TOTP(st.session_state.twofa_secret)
        uri = totp.provisioning_uri(name=st.session_state.new_user_email, issuer_name="Plane N Simple")

        qr = qrcode.make(uri)
        buf = BytesIO()
        qr.save(buf)
        b64_qr = base64.b64encode(buf.getvalue()).decode()

        st.markdown("### 🔐 Scan this QR code with Google Authenticator or Authy:")
        st.image(f"data:image/png;base64,{b64_qr}")
        st.markdown("Then enter the 6-digit code to test if setup works:")

        with st.form("Verify 2FA Setup"):
            token = st.text_input("Enter 6-digit code")
            verify_btn = st.form_submit_button("Verify Code")

        if verify_btn:
            if totp.verify(token):
                st.success("🎉 2FA code verified successfully! You can now log in.")
                st.session_state.show_2fa_qr = False
                st.session_state.twofa_secret = None
                st.session_state.new_user_email = ""
            else:
                st.error("❌ Invalid 2FA code. Double-check your app and try again.")


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
        is_admin = user_data.get("admin", False) if user_data else False
        st.write(f"Logged in as: {name}")

    if user_data and "twofa_secret" not in user_data:
        st.warning("🚨 You have not enabled Two-Factor Authentication (2FA).")

        if "twofa_setup_secret" not in st.session_state:
            st.session_state.twofa_setup_secret = pyotp.random_base32()

        totp = pyotp.TOTP(st.session_state.twofa_setup_secret)
        uri = totp.provisioning_uri(name=st.session_state.email, issuer_name="Plane N Simple")

        # Generate QR Code
        qr = qrcode.make(uri)
        buf = BytesIO()
        qr.save(buf)
        b64_qr = base64.b64encode(buf.getvalue()).decode()

        st.markdown("### 🔐 Set Up 2FA Now")
        st.image(f"data:image/png;base64,{b64_qr}")
        st.markdown("Scan the QR code above with Google Authenticator or Authy.")

        with st.form("Enable 2FA Now"):
            token = st.text_input("Enter the 6-digit code to confirm setup")
            verify_2fa = st.form_submit_button("Enable 2FA")

        if verify_2fa:
            if totp.verify(token):
                realtimedb.reference(f"users/{uid}/twofa_secret").set(st.session_state.twofa_setup_secret)
                st.success("✅ 2FA is now enabled on your account.")
                del st.session_state.twofa_setup_secret
                st.rerun()
            else:
                st.error("❌ Invalid 2FA code. Please try again.")

    with st.sidebar:
        if st.button("Logout of Account 🚪"):
            for key in ["login", "email", "uid"]:
                st.session_state.pop(key, None)
            st.rerun()

        # Adjust menu dynamically
        menu_options = ["Home", "Travel Plans", "Flight Search", "POI Search", "Profile"]
        menu_icons = ["house", "search", "map", "book", "person-circle"]

        if is_admin:
            menu_options.append("Admin")
            menu_icons.append("shield-lock")

        selected = option_menu(
            menu_title="Plane N Simple",
            options=menu_options,
            icons=menu_icons,
            menu_icon="airplane",
            default_index=0,
        )

    # Page Routing
    if selected == "Home":
        home.main()
    elif selected == "Flight Search":
        flight_search.main()
    elif selected == "POI Search":
        poi_search.main()
    elif selected == "Profile":
        profile_page.main()
    elif selected == "Admin":
        import admin_page
        admin_page.main()
    elif selected == "Travel Plans":
        travel_plans.main()
