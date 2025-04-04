import streamlit as st

def main():
    st.title("👤 User Profile")
    
    st.text_input("Full Name", placeholder="Enter your full name")
    st.text_input("Email", placeholder="Enter your email address")
    st.text_input("Phone Number", placeholder="Enter your phone number")
    
    st.file_uploader("Upload Profile Picture", type=["jpg", "png"])
    
    st.button("Save Changes")
    
if __name__ == "__main__":
    main()