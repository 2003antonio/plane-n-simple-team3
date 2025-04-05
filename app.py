# app.py
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_login_auth_ui.widgets import __login__

# Import the page modules
import home
import flight_search
import profile_page

# Page config
st.set_page_config(page_title="Plane N Simple", layout="wide")

if 'login' not in st.session_state:
    st.session_state.login = False

__login__obj = __login__(auth_token = "dk_prod_15C3N21B044K7TQ5C0WQK38N3BZH",
                    company_name = "Plane-n-Simple",
                    width = 200, height = 250,
                    logout_button_name = 'Logout', hide_menu_bool = False,
                    hide_footer_bool = False,
                    lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

st.session_state.login = __login__obj.build_login_ui()

if st.session_state.login:
    st.markdown("Welcome to Main page!")

    # Get the user name.
    fetched_cookies = __login__obj.cookies
    if '__streamlit_login_signup_ui_username__' in fetched_cookies:
        username = fetched_cookies['__streamlit_login_signup_ui_username__']
        st.session_state["username"] = username
        st.write(username)
    
    if '__streamlit_login_signup_ui_email__' in fetched_cookies:
        email = fetched_cookies['__streamlit_login_signup_ui_email__']
        st.session_state["email"] = email

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
