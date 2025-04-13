import streamlit as st
import pandas as pd
import requests
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


def get_amadeus_token():
    client_id = st.secrets["amadeus"]["client_id"]
    client_secret = st.secrets["amadeus"]["client_secret"]

    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    res = requests.post(url, data=payload)

    if res.status_code == 200:
        return res.json()["access_token"]
    else:
        st.error("❌ Failed to fetch Amadeus token")
        return None


def search_amadeus_flights(origin_code, dest_code, travel_date):
    token = get_amadeus_token()
    if not token:
        return []

    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "originLocationCode": origin_code,
        "destinationLocationCode": dest_code,
        "departureDate": travel_date.strftime("%Y-%m-%d"),
        "adults": 1,
        "currencyCode": "USD",
        "travelClass": "ECONOMY"
    }

    res = requests.get(url, headers=headers, params=params)

    if res.status_code == 200:
        return res.json().get("data", [])
    else:
        st.error(f"❌ Flight search failed: {res.status_code}")
        return []


def main():
    st.title("✈️ Plane N Simple: Flight Search")
    st.write("🎯 App loaded")  # Confirms rendering is working

    try:
        airports_df = load_airports()
        st.markdown("## 🔍 Select Your Route")
    except Exception as e:
        st.error("⚠️ Failed to load airports.csv")
        st.exception(e)
        return


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

        
        flights = search_amadeus_flights(origin_code, dest_code, travel_date)

        
        if not flights:
            st.info("No live flights found. Showing sample flights instead (demo mode).")
            flights = get_mock_flights(origin_display, destination_display, travel_date)

        
        for offer in flights:
            itinerary = offer["itineraries"][0]
            segment = itinerary["segments"][0]

            dep_code = segment["departure"]["iataCode"]
            arr_code = segment["arrival"]["iataCode"]
            dep_time = segment["departure"]["at"]
            arr_time = segment["arrival"]["at"]
            airline = segment.get("carrierCode", "Unknown")
            duration = segment.get("duration", "N/A")
            aircraft = segment.get("aircraft", {}).get("code", "N/A")
            price = offer["price"]["total"]
            currency = offer["price"]["currency"]

            st.markdown(f"""
            **Airline:** {airline}  
            **From:** {dep_code}  
            **To:** {arr_code}  
            **Departure:** {dep_time}  
            **Arrival:** {arr_time}  
            **Flight Duration:** {duration}  
            **Aircraft:** {aircraft}  
            **Price:** {price} {currency}  
            ---
            """)
            

if __name__ == "__main__":
    main()

