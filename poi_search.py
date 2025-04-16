import streamlit as st
import requests
import math
import pydeck as pdk
from firebase_admin import db
import json

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

    uid = st.session_state.get("uid")
    travel_plans = db.reference(f"travel_plans/{uid}").get() or {}
    plan_names = list(travel_plans.keys())

    try:
        GEOAPIFY_API_KEY = st.secrets["geoapify"]["api_key"]
    except Exception as e:
        st.warning(f"⚠️ Geoapify API key not found or misconfigured: {e}")
        return

    st.markdown("## 🔍 Select Points of Interest")

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

    category_group = st.radio(
        "Select a category group",
        ("All", "Accommodation", "Entertainment", "Tourism", "Commercial", "Parks"),
        key="category_group"
    )

    if category_group == "All":
        selected_categories = None
    else:
        selected = st.multiselect(f"Select {category_group} Types", list(categories[category_group.lower()].values()))
        selected_categories = [k for k, v in categories[category_group.lower()].items() if v in selected] if selected else list(categories[category_group.lower()].keys())

    with st.form("poi_search_form"):
        city = st.text_input("Enter a city (e.g., Miami)")
        radius_miles = st.selectbox("Search radius (miles)", [5, 10, 20, 50], index=1)
        filter_button = st.form_submit_button("Filter")

    if filter_button:
        lat, lon = get_city_coordinates(city, GEOAPIFY_API_KEY)
        if lat is None or lon is None:
            return

        radius_meters = radius_miles * 1609.34
        response = get_pois(lat, lon, radius_meters, GEOAPIFY_API_KEY, selected_categories)
        pois = response.get("features", [])

        st.session_state.pois = pois
        st.session_state.city = city
        st.session_state.lat = lat
        st.session_state.lon = lon

    added_plan_feedback = {}

    if "pending_poi_add" in st.session_state:
        data = st.session_state.pop("pending_poi_add")
        plan_ref = db.reference(f"travel_plans/{uid}/{data['plan']}")
        raw_plan = plan_ref.get()

        try:
            plan = json.loads(raw_plan) if isinstance(raw_plan, str) else raw_plan
        except Exception:
            plan = {"flights": [], "pois": []}

        plan["pois"].append({
            "name": data["name"],
            "category": data["category"]
        })

        plan_ref.set(json.dumps(plan))
        added_plan_feedback[data["name"] + data["category"]] = data["plan"]

    if "pois" in st.session_state:
        pois = st.session_state.pois
        city = st.session_state.city
        lat = st.session_state.lat
        lon = st.session_state.lon

        st.markdown(f"### 🧭 Points of Interest near {city}:")
        for idx, poi in enumerate(pois):
            props = poi.get("properties", {})
            name = props.get("name", "Unnamed Place")
            category = props.get("categories", ["Unknown"])[0].split("/")[-1]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"- **{name}** ({category})")
            with col3:
                with st.expander("➕ Add to Travel Plan"):
                    plan_key = f"plan_select_{idx}"
                    if plan_key not in st.session_state:
                        st.session_state[plan_key] = plan_names[0] if plan_names else None

                    selected_plan = st.selectbox("Select a Plan", plan_names, key=plan_key)

                    if st.button("Add to Plan", key=f"add_btn_{idx}"):
                        st.session_state["pending_poi_add"] = {
                            "name": name,
                            "category": category,
                            "plan": selected_plan
                        }

                        st.rerun()

                    key = name + category
                    if key in added_plan_feedback:
                        st.success(f"✅ POI added to '{added_plan_feedback[key]}'!")

        with st.expander("🗺️ View POIs on Map"):
            try:
                map_df = [{
                    "name": poi["properties"].get("name", "Unnamed"),
                    "address": poi["properties"].get("address_line2", ""),
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

                    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, tooltip={"html": "{name}<br/>{address}"}))
                else:
                    st.warning("Map data not available for these POIs.")
            except Exception as e:
                st.warning(f"⚠️ Error displaying map: {e}")

if __name__ == "__main__":
    main()