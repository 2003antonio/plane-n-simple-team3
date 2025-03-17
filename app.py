import streamlit as st
import pandas as pd
import pydeck as pdk

# load data from CSV
csv_file = "airports.csv"  # update with your file path
df = pd.read_csv(csv_file, header=None, names=["name", "latitude", "longitude"])

# add custom styling for title and search bar
st.markdown(
    """
    <style>
        .title {
            font-size: 40px;
            font-weight: bold;
            text-align: center;
            color: #1E90FF;
        }
        .subtitle {
            text-align: center;
            font-size: 20px;
            color: #333;
        }
        .search-container {
            text-align: center;
            margin-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# display the main title and subtitle
st.markdown('<p class="title">Plane N Simple ✈️</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Find airports and book flights with ease!</p>', unsafe_allow_html=True)

# search bar for filtering airports
st.markdown('<div class="search-container">', unsafe_allow_html=True)
search_query = st.text_input("🔍 Search for an airport", placeholder="Type airport name here...")
st.markdown("</div>", unsafe_allow_html=True)

# show filtered results based on search query
if search_query:
    filtered_df = df[df["name"].str.contains(search_query, case=False, na=False)]
    if not filtered_df.empty:
        st.write("### Search Results:")
        st.dataframe(filtered_df)
    else:
        st.write("No results found.")

# expandable section for airport map
with st.expander("📍 All Airlines Supported by Us!"):
    st.write("Hover over a point to see the airport name.")

    # create a layer for airport markers
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_color=[255, 0, 0, 150],  # red color with transparency
        get_radius=20000,  # adjust size
        pickable=True,  # enables tooltips
    )

    # define tooltip to show airport names
    tooltip = {"html": "<b>{name}</b>", "style": {"backgroundColor": "white", "color": "black"}}

    # create the interactive map
    map = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=df["latitude"].mean(),
            longitude=df["longitude"].mean(),
            zoom=3,
            pitch=0,
        ),
        layers=[layer],
        tooltip=tooltip,
    )

    # display the map in Streamlit
    st.pydeck_chart(map)
