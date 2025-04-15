import streamlit as st
import requests
import math
import pydeck as pdk

def get_city_coordinates(city, api_key):
    try:
        url = f"https://api.geoapify.com/v1/geocode/search?text={city}&apiKey={api_key}"
        response = requests.get(url)
        if response.status_code != 200:
            st.warning("⚠️ Failed to get city coordinates. Geoapify may be unavailable.")
            return None, None
        data = response.json()
        lat = data["features"][0]["properties"]["lat"]
        lon = data["features"][0]["properties"]["lon"]
        return lat, lon
    except Exception as e:
        st.warning(f"⚠️ Error fetching coordinates: {e}")
        return None, None

def get_pois(lat, lon, radius_meters, api_key, selected_categories):
    try:
        categories = ",".join(selected_categories) if selected_categories else \
            "catering,entertainment,tourism,accommodation.hotel,accommodation.hostel,accommodation.motel,activity,commercial,leisure,national_park"
        url = (
            f"https://api.geoapify.com/v2/places"
            f"?categories={categories}"
            f"&filter=circle:{lon},{lat},{radius_meters}"
            f"&limit=20"
            f"&apiKey={api_key}"
        )
        response = requests.get(url)
        if response.status_code != 200:
            st.warning("⚠️ Failed to retrieve POIs from Geoapify.")
            return {}
        return response.json()
    except Exception as e:
        st.warning(f"⚠️ Error fetching POIs: {e}")
        return {}

def main():
    st.title("📍 Plane N Simple: POI Search")
    st.markdown("Find cool places near your destination using Geoapify APIs!")

    try:
        GEOAPIFY_API_KEY = st.secrets["geoapify"]["api_key"]
    except Exception as e:
        st.warning(f"⚠️ Geoapify API key not found or misconfigured: {e}")
        return

    st.markdown("## 🔍 Select Points of Interest")

    # Category mappings

    categories = {
        "accommodation": {
        "accommodation.hotel": "Hotel",
        "accommodation.hostel": "Hostel",
        "accommodation.motel": "Motel"
        },
        "entertainment": {
            "catering": "Catering",
            "entertainment": "Entertainment"
        },
        "tourism": {
            "tourism": "Tourism",
            "activity": "Activity",
            "leisure": "Leisure"
        },
        "commercial": {
            "commercial": "Commercial"
        },
        "parks": {
            "national_park": "National Park"
        }
    }

    # Category group selector (outside form so it refreshes)
    prev_selection = st.session_state.get("category_group", None)
    category_group = st.radio(
        "Select a category group",
        ("All", "Accommodation", "Entertainment", "Tourism", "Commercial", "Parks"),
        key="category_group"
    )

    if prev_selection is not None and category_group != prev_selection:
        st.rerun()

    if category_group == "All":
        selected_categories = None
    else:
        selected = st.multiselect(f"Select {category_group} Types", list(categories[category_group.lower()].values()))
        selected_categories = [k for k, v in categories[category_group.lower()].items() if v in selected] if len(selected) > 0 else [k for k, v in categories[category_group.lower()].items() if True]

    # Form for city and radius input
    with st.form("poi_search_form"):
        city = st.text_input("Enter a city (e.g., Miami)")
        radius_miles = st.selectbox("Search radius (miles)", [5, 10, 20, 50], index=1)
        filter_button = st.form_submit_button("Filter")

    if filter_button:
        if not city:
            st.warning("Please enter a city name.")
            return

        st.info(f"📍 Looking up coordinates for **{city}**...")
        lat, lon = get_city_coordinates(city, GEOAPIFY_API_KEY)
        if lat is None or lon is None:
            st.warning(f"⚠️ Could not find coordinates for {city}.")
            return

        st.success(f"Coordinates for {city}: ({lat}, {lon})")
        st.info("📡 Searching for nearby points of interest...")

        radius_meters = radius_miles * 1609.34
        pois_response = get_pois(lat, lon, radius_meters, GEOAPIFY_API_KEY, selected_categories)
        pois = pois_response.get("features", [])

        if not pois:
            st.warning("No POIs found for this location.")
            return

        st.markdown(f"### 🧭 Points of Interest near {city}:")
        for poi in pois:
            props = poi.get("properties", {})
            name = props.get("name", "Unnamed Place")
            category = props.get("categories", ["Unknown"])[0].split("/")[-1]
            st.markdown(f"- **{name}** ({category})")

        with st.expander("🗺️ View POIs on Map"):
            try:
                map_df = [{
                    "name": poi["properties"].get("name", "Unnamed"),
                    "lat": poi["properties"]["lat"],
                    "lon": poi["properties"]["lon"]
                } for poi in pois if "lat" in poi["properties"] and "lon" in poi["properties"]]

                if map_df:
                    layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=map_df,
                        get_position='[lon, lat]',
                        get_radius=300,
                        get_color=[0, 100, 255, 160],
                        pickable=True
                    )

                    view = pdk.ViewState(
                        latitude=lat,
                        longitude=lon,
                        zoom=10,
                        pitch=0
                    )

                    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, tooltip={"text": "{name}"}))
                else:
                    st.warning("Map data not available for these POIs.")
            except Exception as e:
                st.warning(f"⚠️ Error displaying map: {e}")

if __name__ == "__main__":
    main()