import streamlit as st
import requests
import math

def get_city_coordinates(city, api_key):
    """Convert a city name to coordinates using Geoapify's geocoding API"""
    url = f"https://api.geoapify.com/v1/geocode/search?text={city}&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
    try:
        lat = data["features"][0]["properties"]["lat"]
        lon = data["features"][0]["properties"]["lon"]
        return lat, lon
    except (KeyError, IndexError):
        return None, None

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points on the earth in miles"""
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Radius of the earth in miles
    R = 3958.8
    distance = R * c  # Distance in miles
    return distance

def get_pois(lat, lon, radius_meters, api_key, selected_categories):
    """Fetch POIs near given coordinates using Geoapify Places API"""
    categories = ",".join(selected_categories) if selected_categories else "catering,entertainment,tourism,accommodation.hotel,accommodation.hostel,accommodation.motel,activity,commercial,leisure,national_park"
    url = (
        f"https://api.geoapify.com/v2/places"
        f"?categories={categories}"
        f"&filter=circle:{lon},{lat},{radius_meters}"
        f"&limit=20"
        f"&apiKey={api_key}"
    )
    response = requests.get(url)
    return response.json()

def sort_pois(pois, sort_by, lat, lon):
    """Sort POIs based on selected criteria (name or distance)"""
    if sort_by == "Distance":
        # Calculate distance for each POI and add it as a field
        for poi in pois:
            props = poi.get("properties", {})
            poi_lat = props.get("lat", lat)
            poi_lon = props.get("lon", lon)
            poi['distance_miles'] = haversine(lat, lon, poi_lat, poi_lon)
        # Sort by the calculated distance in miles
        return sorted(pois, key=lambda x: x.get("distance_miles", float('inf')))
    elif sort_by == "Name":
        return sorted(pois, key=lambda x: x["properties"].get("name", "").lower())
    return pois

def main():
    st.title("📍 Plane N Simple: POI Search")
    st.markdown("Find cool places near your destination using Geoapify APIs!")

    st.markdown("## 🔍 Select Points of Interest")
    with st.form("poi_search_form"):
        city = st.text_input("Enter a city (e.g., Miami)")
        radius_miles = st.selectbox("Search radius (miles)", [5, 10, 20, 50], index=1)

        # Define the mapping between API category names and user-friendly names
        accommodation = {
            "accommodation.hotel": "Hotel",
            "accommodation.hostel": "Hostel",
            "accommodation.motel": "Motel"
        }
        entertainment = {
            "catering": "Catering",
            "entertainment": "Entertainment"
        }
        tourism = {
            "tourism": "Tourism",
            "activity": "Activity",
            "leisure": "Leisure"
        }
        commercial = {
            "commercial": "Commercial"
        }
        parks = {
            "national_park": "National Park"
        }

        # Grouped categories for display
        category_group = st.radio(
            "Select a category group",
            ("Accommodation", "Entertainment", "Tourism", "Commercial", "Parks")
        )

        # Display the multiselect widget with user-friendly names
        if category_group == "Accommodation":
            selected_categories_display = st.multiselect(
                "Select Accommodation Types", 
                list(accommodation.values()), 
                default=list(accommodation.values())
            )
            selected_categories = [key for key, value in accommodation.items() if value in selected_categories_display]

        elif category_group == "Entertainment":
            selected_categories_display = st.multiselect(
                "Select Entertainment Types", 
                list(entertainment.values()), 
                default=list(entertainment.values())
            )
            selected_categories = [key for key, value in entertainment.items() if value in selected_categories_display]

        elif category_group == "Tourism":
            selected_categories_display = st.multiselect(
                "Select Tourism Activities", 
                list(tourism.values()), 
                default=list(tourism.values())
            )
            selected_categories = [key for key, value in tourism.items() if value in selected_categories_display]

        elif category_group == "Commercial":
            selected_categories_display = st.multiselect(
                "Select Commercial Types", 
                list(commercial.values()), 
                default=list(commercial.values())
            )
            selected_categories = [key for key, value in commercial.items() if value in selected_categories_display]

        elif category_group == "Parks":
            selected_categories_display = st.multiselect(
                "Select Parks", 
                list(parks.values()), 
                default=list(parks.values())
            )
            selected_categories = [key for key, value in parks.items() if value in selected_categories_display]

        filter_button = st.form_submit_button("Filter")

    sort_by = st.selectbox("Sort by", ["Distance", "Name"])

    GEOAPIFY_API_KEY = st.secrets["geoapify"]["api_key"]

    if filter_button:
        if not city:
            st.error("Please enter a city name.")
            return

        st.info(f"📍 Looking up coordinates for **{city}**...")
        lat, lon = get_city_coordinates(city, GEOAPIFY_API_KEY)
        if lat is None or lon is None:
            st.error(f"Could not find coordinates for {city}.")
            return

        st.success(f"Coordinates for {city}: ({lat}, {lon})")
        st.info("📡 Searching for nearby points of interest...")

        radius_meters = radius_miles * 1609.34
        pois_response = get_pois(lat, lon, radius_meters, GEOAPIFY_API_KEY, selected_categories)
        pois = pois_response.get("features", [])

        if not pois:
            st.warning("No POIs found for this location.")
            return

        # Sort POIs based on user selection
        sorted_pois = sort_pois(pois, sort_by, lat, lon)

        st.markdown(f"### 🧭 Points of Interest near {city}:")
        for poi in sorted_pois:
            props = poi.get("properties", {})
            name = props.get("name", "Unnamed Place")
            category = props.get("categories", ["Unknown"])[0].split("/")[-1]
            # Get the distance from the city center using Haversine formula
            distance_miles = poi.get('distance_miles', 0)
            st.markdown(f"- **{name}** ({category}) — `{distance_miles:.2f} miles` away")

if __name__ == "__main__":
    main()
