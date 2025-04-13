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

def get_sort_key(option):
    def sort_key(offer):
        segment = offer["itineraries"][0]["segments"][0]
        if option == "Price: Low to High" or option == "Price: High to Low":
            return float(offer["price"]["total"])
        elif option.startswith("Departure"):
            return segment["departure"]["at"]
        elif option.startswith("Arrival"):
            return segment["arrival"]["at"]
        elif option == "Airline Name":
            return segment.get("carrierCode", "")
    return sort_key

def main():
    st.title("✈️ Plane N Simple: Flight Search")
    st.markdown("Search and compare real-time flights via Amadeus API")

    try:
        airports_df = load_airports()
    except Exception as e:
        st.error("⚠️ Failed to load airports.csv")
        st.exception(e)
        return

    with st.container():
        st.subheader("🔍 Select Your Route")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            origin_display = st.selectbox("Departure Airport", airports_df["display_name"])
        with col2:
            destination_display = st.selectbox("Destination Airport", airports_df["display_name"])
        with col3:
            travel_date = st.date_input("Travel Date", min_value=date.today())

        sort_option = st.selectbox("Sort By", ["Select", "Price: Low to High", "Price: High to Low", "Departure: Earliest", "Departure: Latest", "Arrival: Earliest", "Arrival: Latest", "Airline Name"])
        strict_match = st.checkbox("Enable Strict Match", value=True)

        if st.button("🔎 Search Flights", use_container_width=True):
            origin_row = airports_df[airports_df["display_name"] == origin_display].iloc[0]
            origin_code = origin_row["iata_code"]
            dest_code = "ZZZ" if not strict_match else airports_df[airports_df["display_name"] == destination_display].iloc[0]["iata_code"]

            flights = search_amadeus_flights(origin_code, dest_code, travel_date)

            if not flights:
                st.warning("⚠️ No flights found for the selected route and date. Please try a different departure, destination, or travel date.")
                return

            if strict_match:
                flights = [
                    offer for offer in flights
                    if offer["itineraries"][0]["segments"][0]["departure"]["iataCode"] == origin_code and
                       offer["itineraries"][0]["segments"][0]["arrival"]["iataCode"] == dest_code
                ]
            else:
                flights = [
                    offer for offer in flights
                    if offer["itineraries"][0]["segments"][0]["departure"]["iataCode"] == origin_code
                ]

            if not flights:
                st.warning("⚠️ No matching flights found based on your selection.")
                return

            st.session_state.flights = flights
            st.session_state.origin_code = origin_code
            st.session_state.dest_code = dest_code
            st.session_state.travel_date = travel_date

    if "flights" in st.session_state:
        flights = st.session_state.flights
        origin_code = st.session_state.origin_code
        dest_code = st.session_state.dest_code
        travel_date = st.session_state.travel_date

        st.markdown(f"### ✈️ Results for {travel_date.strftime('%b %d, %Y')} from *{origin_code}*")

        if sort_option != "Select":
            reverse = sort_option in ["Price: High to Low", "Departure: Latest", "Arrival: Latest"]
            flights.sort(key=get_sort_key(sort_option), reverse=reverse)

        for offer in flights:
            segment = offer["itineraries"][0]["segments"][0]
            dep_code = segment["departure"]["iataCode"]
            arr_code = segment["arrival"]["iataCode"]
            dep_time = segment["departure"]["at"]
            arr_time = segment["arrival"]["at"]
            airline = segment.get("carrierCode", "Unknown Airline")
            duration = segment.get("duration", "N/A")
            aircraft = segment.get("aircraft", {}).get("code", "N/A")
            price = offer["price"]["total"]
            currency = offer["price"]["currency"]

            with st.container():
                st.markdown(f"""
                <div style=\"border: 1px solid #ccc; border-radius: 12px; padding: 15px; margin-bottom: 10px; background-color: #f9f9f9;\">
                    <h4 style=\"margin: 0;\">🛫 {dep_code} → 🛬 {arr_code}</h4>
                    <p style=\"margin: 5px 0;\"><strong>Airline:</strong> {airline} &nbsp; | &nbsp; <strong>Aircraft:</strong> {aircraft}</p>
                    <p style=\"margin: 5px 0;\"><strong>Departure:</strong> {dep_time} &nbsp; | &nbsp; <strong>Arrival:</strong> {arr_time}</p>
                    <p style=\"margin: 5px 0;\"><strong>Duration:</strong> {duration}</p>
                    <p style=\"margin: 5px 0; font-size: 1.2em;\"><strong>💲Price:</strong> {price} {currency}</p>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
