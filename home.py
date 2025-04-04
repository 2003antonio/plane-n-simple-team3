import streamlit as st
import os
import pandas as pd
import pydeck as pdk

def main():
    # Use image from web_images directory
    image_path = os.path.join("web_images", "home_banner.jpg")
    st.image(image_path, use_container_width=True)

    st.markdown("<h1 style='text-align: center; color: #1E90FF;'>Plane N Simple ✈️</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Find airports and book flights with ease!</h3>", unsafe_allow_html=True)


    st.write("### Welcome to Plane N Simple!")
    st.write("Explore flights and entertainment easily! Use the navigation menu to access flight search and profile settings.")

    csv_file = "airports.csv"  # update with your file path
    df = pd.read_csv(csv_file, header=None, names=["name", "latitude", "longitude"])

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

if __name__ == "__main__":
    main()
