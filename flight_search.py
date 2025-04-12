import streamlit as st
import pandas as pd
from datetime import date

def load_airports():
    df = pd.read_csv("airports.csv")
    df = df.dropna(subset=["iata_code"])
    df["display_name"] = df["iata_code"].str.upper() + " - " + df["name"].str.strip()
    df = df.drop_duplicates(subset=["display_name"])
    return df

def get_mock_flights(origin, destination, travel_date):
    return [
        {
            "flight": {"iata": "PS123"},
            "airline": {"name": "Plane N Simple Airlines"},
            "departure": {"airport": origin, "scheduled": f"{travel_date}T12:30:00"},
            "arrival": {"airport": destination, "scheduled": f"{travel_date}T15:45:00"},
            "flight_status": "scheduled"
        },
        {
            "flight": {"iata": "PS456"},
            "airline": {"name": "Demo Jetways"},
            "departure": {"airport": origin, "scheduled": f"{travel_date}T18:00:00"},
            "arrival": {"airport": destination, "scheduled": f"{travel_date}T21:05:00"},
            "flight_status": "scheduled"
        }
    ]

def main():
    st.title("✈️ Plane N Simple: Flight Search")

    airports_df = load_airports()
    st.markdown("## 🔍 Select Your Route")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        origin_display = st.selectbox("Departure Airport", airports_df["display_name"])
    with col3:
        travel_date = st.date_input("Select Travel Date", min_value=date.today())
    with col2:
        destination_display = st.selectbox("Destination Airport", airports_df["display_name"])
        search_clicked = st.button("Search Flights", use_container_width=True)

    if search_clicked:
        origin_row = airports_df[airports_df["display_name"] == origin_display].iloc[0]
        dest_row = airports_df[airports_df["display_name"] == destination_display].iloc[0]
        origin_code = origin_row["iata_code"]
        dest_code = dest_row["iata_code"]

        st.markdown(f"#### Results for {travel_date.strftime('%m/%d/%Y')}")

        mock_flights = get_mock_flights(origin_display, destination_display, travel_date)

        for flight in mock_flights:
            flight_code = flight.get("flight", {}).get("iata", "N/A")
            airline = flight.get("airline", {}).get("name", "Unknown Airline")
            dep_airport = flight.get("departure", {}).get("airport", "Unknown")
            arr_airport = flight.get("arrival", {}).get("airport", "Unknown")
            dep_time = flight.get("departure", {}).get("scheduled", "N/A")
            arr_time = flight.get("arrival", {}).get("scheduled", "N/A")
            status = flight.get("flight_status", "N/A")

            st.markdown(f"""
            **Flight:** {flight_code}  
            **Airline:** {airline}  
            **From:** {dep_airport}  
            **To:** {arr_airport}  
            **Departure:** {dep_time}  
            **Arrival:** {arr_time}  
            **Status:** {status}  
            ---  
            """)

if __name__ == "__main__":
    main()
