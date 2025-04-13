import streamlit as st
import requests
import pydeck as pdk

API_KEY = "e3ecac128a684aec8e024128789e6d83"

def get_city_coordinates(city_name):
    """Geocode city to lat/lon using Geoapify."""
    url = f"https://api.geoapify.com/v1/geocode/search?text={city_name}&limit=1&apiKey={API_KEY}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        feature = res.json()["features"][0]
        lon, lat = feature["geometry"]["coordinates"]
        return lat, lon
    except Exception as e:
        st.error(f"Geocoding failed: {e}")
        return None, None

def get_pois(lat, lon, radius_m):
    """Query Geoapify Places API with circle filter and broad category."""
    url = (
        "https://api.geoapify.com/v2/places"
        f"?categories=commercial"
        f"&filter=circle:{lon},{lat},{radius_m}"
        f"&limit=50&apiKey={API_KEY}"
    )
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json().get("features", [])
    except Exception as e:
        st.error(f"POI search failed: {e}")
        return []

def main():
    st.title("📍 Plane N Simple: POI Explorer")
    st.markdown("Just enter a city and radius. See places on the map — no categories needed!")

    with st.form("poi_form"):
        city = st.text_input("Enter a city (e.g., Miami)")
        radius_km = st.slider("Search radius (km)", 1, 20, 5)
        submitted = st.form_submit_button("Search")

    if not submitted or not city:
        return

    st.info("📍 Geocoding city...")
    lat, lon = get_city_coordinates(city)
    if not lat:
        return

    st.success(f"Coordinates: ({lat:.5f}, {lon:.5f})")

    st.info("🔎 Getting places nearby...")
    radius_m = int(radius_km * 1000)
    pois = get_pois(lat, lon, radius_m)

    if not pois:
        st.warning("No POIs found. Try a broader city or increase the radius.")
        return

    st.success(f"Found {len(pois)} places.")

    poi_data = [{
        "name": poi["properties"].get("name", "Unnamed"),
        "lat": poi["geometry"]["coordinates"][1],
        "lon": poi["geometry"]["coordinates"][0],
    } for poi in pois]

    poi_layer = pdk.Layer(
        "ScatterplotLayer",
        data=poi_data,
        get_position=["lon", "lat"],
        get_fill_color=[0, 0, 255, 160],
        get_radius=60,
        pickable=True
    )

    circle_layer = pdk.Layer(
        "ScatterplotLayer",
        data=[{"lon": lon, "lat": lat}],
        get_position=["lon", "lat"],
        get_radius=radius_m,
        get_fill_color=[100, 200, 255, 40],
        pickable=False
    )

    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=12),
        layers=[circle_layer, poi_layer],
        tooltip={"text": "{name}"},
        map_style="mapbox://styles/mapbox/light-v9"
    ))

if __name__ == "__main__":
    main()
