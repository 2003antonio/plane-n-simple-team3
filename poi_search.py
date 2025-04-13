import streamlit as st
import requests

def get_access_token(api_key, api_secret):
    """Obtain an OAuth2 token from Amadeus"""
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": api_secret,
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")


def get_city_coordinates(city, token):
    """Convert a city name to coordinates using Amadeus location API"""
    url = f"https://test.api.amadeus.com/v1/reference-data/locations?keyword={city}&subType=CITY"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    try:
        lat = data["data"][0]["geoCode"]["latitude"]
        lon = data["data"][0]["geoCode"]["longitude"]
        return lat, lon
    except (KeyError, IndexError):
        return None, None


def get_pois(lat, lon, radius, token):
    """Fetch POIs near given coordinates"""
    url = (
        f"https://test.api.amadeus.com/v1/reference-data/locations/pois?"
        f"latitude={lat}&longitude={lon}&radius={radius}"
    )
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json()


def main():
    st.title("📍 Plane N Simple: POI Search")
    st.markdown("Find cool places near your destination using Amadeus APIs!")

    st.markdown("## 🔍 Select Points of Interest")
    with st.form("poi_search_form"):
        st.subheader("Search Your City")
        city = st.text_input("Enter a city (e.g., Miami)")
        radius = st.selectbox("Search radius (miles)", [5, 10, 20, 50], index=1)
        submit = st.form_submit_button("Search")

    # Your Amadeus API Credentials
    AMADEUS_API_KEY = "mHKnOUJ9Jya2vg2QYAJ6HGThcR7LxkcJ"
    AMADEUS_API_SECRET = "XyO7mWlttW7YE1d6"

    if submit:
        if not city:
            st.error("Please enter a city name.")
            return

        st.info(f"🔄 Getting access token...")
        token = get_access_token(AMADEUS_API_KEY, AMADEUS_API_SECRET)
        if not token:
            st.error("Failed to get access token from Amadeus.")
            return

        st.info(f"📍 Looking up coordinates for **{city}**...")
        lat, lon = get_city_coordinates(city, token)
        if lat is None or lon is None:
            st.error(f"Could not find coordinates for {city}.")
            return

        st.success(f"Coordinates for {city}: ({lat}, {lon})")
        st.info("📡 Searching for nearby points of interest...")

        pois_response = get_pois(lat, lon, radius * 1.60934, token)  # 🔁 convert mi → km
        pois = pois_response.get("data", [])

        if not pois:
            st.warning("No POIs found for this location.")
            return


        st.markdown(f"### 🧭 Points of Interest near {city}:")
        for poi in pois:
            name = poi.get("name", "Unnamed Place")
            category = poi.get("category", "Unknown")
            dist = poi.get("distance", "N/A")
            st.markdown(f"- **{name}** ({category}) — `{dist} meters` away")

# Run the app
if __name__ == "__main__":
    main()
