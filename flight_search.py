import streamlit as st

def main():
    st.title("🔍 Flight Search")
    
    origin = st.text_input("Departure Airport", placeholder="Enter airport name or code...")
    destination = st.text_input("Destination Airport", placeholder="Enter airport name or code...")
    date = st.date_input("Select Travel Date")
    
    search_btn = st.button("Search Flights")
    
    if search_btn:
        st.write("### Available Flights")
        st.write("(Flight search results will be displayed here)")
    
if __name__ == "__main__":
    main()