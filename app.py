import streamlit as st
import pandas as pd
import os
from PIL import Image
from typing import Optional
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Risks With Mining", layout="wide")
BASE_PATH = "data"

def clean_name(name: str) -> str:
    return name.replace("data_", "").replace("_", " ").strip()

def cover_path(folder: str) -> Optional[str]:
    base = folder.replace("data_", "")
    path = os.path.join(BASE_PATH, folder, f"{base}_Satellite_2024_After.png")
    return path if os.path.exists(path) else None

# Theme
st.markdown("""
<style>
.stApp {
    background: #e9f5e1;
    color: #1c1c1c;
    font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3, h4 {
    color: #205522;
}
.stButton button {
    background: #2e7d32;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    padding: 0.4em 1.2em;
}
.stButton button:hover {
    background: #1b5e20;
}
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    text-align: center;
    padding: 0.6em;
    font-size: 0.9em;
    color: #1c1c1c;
    background: #d6eada;
    border-top: 1px solid #a5c7a5;
}
</style>
""", unsafe_allow_html=True)

# Session states
for key in ("open_folder", "main_open", "viz_open", "search_open", "selected_image"):
    st.session_state.setdefault(key, None)

# Home page
if not any([st.session_state.main_open, st.session_state.viz_open, st.session_state.search_open]):
    st.markdown("<h1 style='text-align:center;'>Research Analysis of Indian Mining Zones</h1>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        st.subheader("Satellite Changes")
        cover = Image.open("satellite_cover.png")
        h = 180
        w = int(cover.width * h / cover.height)
        st.image(cover.resize((w, h)))
        if st.button("Open Mining Regions"):
            st.session_state.main_open = True
            st.rerun()

    with right:
        st.subheader("Visualisations")
        st.markdown("Explore forest loss, NO₂ levels, and feature relationships.")
        if st.button("Open Charts"):
            st.session_state.viz_open = True
            st.rerun()

        st.subheader("Mine Data Explorer")
        st.markdown("Search any mining zone and review its risk profile.")
        if st.button("Open Mine Explorer"):
            st.session_state.search_open = True
            st.rerun()

# Satellite Changes: Folder Grid
elif st.session_state.main_open and st.session_state.open_folder is None:
    st.title("Satellite Changes")
    if st.button("Back to Home"):
        st.session_state.main_open = False
        st.rerun()

    folders = sorted(f for f in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, f)))
    cols = st.columns(3)
    for idx, folder in enumerate(folders):
        with cols[idx % 3]:
            thumb = cover_path(folder)
            st.image(thumb if thumb else " ", use_container_width=True)
            st.caption(clean_name(folder))
            if st.button("Open", key=f"open_{folder}"):
                st.session_state.open_folder = folder
                st.rerun()

# Satellite Changes: Folder Content
elif st.session_state.open_folder:
    folder = st.session_state.open_folder
    path = os.path.join(BASE_PATH, folder)

    if st.session_state.selected_image:
        if st.button("Back to Folder"):
            st.session_state.selected_image = None
            st.rerun()
        img = Image.open(st.session_state.selected_image)
        h = 600
        w = int(img.width * h / img.height)
        st.image(img.resize((w, h)))
    else:
        if st.button("Back to Mining Regions"):
            st.session_state.open_folder = None
            st.rerun()
        st.header(clean_name(folder))
        imgs = sorted(f for f in os.listdir(path) if f.lower().endswith((".png", ".jpg", ".jpeg")))
        cols = st.columns(4)
        for idx, im in enumerate(imgs):
            with cols[idx % 4]:
                ip = os.path.join(path, im)
                st.image(ip, use_container_width=True)
                if st.button("View", key=f"view_{im}"):
                    st.session_state.selected_image = ip
                    st.rerun()

# Visualisations
elif st.session_state.viz_open:
    st.title("Visualisations")
    if st.button("Back to Home"):
        st.session_state.viz_open = False
        st.rerun()

    df = pd.read_csv("zone_features.csv").dropna(subset=["Zone"])

    def plot_mines_and_forests():
        fig, ax = plt.subplots(figsize=(4, 3.5))
        ax.scatter(df["Long"], df["Lat"], c="red", label="Mine", s=50)
        ax.scatter(df["ForestLon"], df["ForestLat"], c="green", label="Forest", s=50)
        for i in range(len(df)):
            ax.plot([df["Long"].iloc[i], df["ForestLon"].iloc[i]],
                    [df["Lat"].iloc[i], df["ForestLat"].iloc[i]], "gray", alpha=0.4)
        ax.set_title("Mine and Forest Locations")
        ax.legend()
        st.pyplot(fig, use_container_width=False)

    def plot_correlation():
        fig, ax = plt.subplots(figsize=(4, 3.5))
        corr = df[["ForestLossPct", "DistanceToForest", "UrbanGrowth",
                   "LanduseChange", "NO2_Mine", "NO2_Forest"]].astype(float).corr()
        sns.heatmap(corr, annot=True, cmap="YlGnBu", ax=ax)
        ax.set_title("Correlation Between Features")
        st.pyplot(fig, use_container_width=False)

    def plot_no2_levels():
        fig, ax = plt.subplots(figsize=(4, 3.5))
        zones = df["Zone"].str.replace("_", " ")
        ax.bar(zones, df["NO2_Mine"], label="Mine", color="crimson")
        ax.bar(zones, df["NO2_Forest"], label="Forest", color="seagreen", alpha=0.7)
        ax.set_title("NO₂ Concentration")
        ax.tick_params(axis="x", rotation=90, labelsize=7)
        ax.legend()
        st.pyplot(fig, use_container_width=False)

    plot_mines_and_forests()
    plot_correlation()
    plot_no2_levels()

# Mine Data Explorer
elif st.session_state.search_open:
    st.title("Mine Data Explorer")
    if st.button("Back to Home"):
        st.session_state.search_open = False
        st.rerun()

    df = pd.read_csv("zone_features.csv").dropna(subset=["Zone"])
    zone = st.selectbox("Search Mining Zone", sorted(df["Zone"].unique()))

    if zone:
        row = df[df["Zone"] == zone].iloc[0]
        st.subheader(zone.replace("_", " "))
        st.markdown(f"""
        - **Latitude / Longitude:** {row['Lat']} / {row['Long']}
        - **Forest Loss %:** {row['ForestLossPct'] if pd.notna(row['ForestLossPct']) else 'N/A'}
        - **Distance to Forest:** {row['DistanceToForest']} km
        - **Urban Growth Index:** {row['UrbanGrowth']}
        - **Land-Use Change:** {row['LanduseChange']}
        - **Nearest Forest:** {row['ForestName']}
        - **NO₂ Near Mine:** {row['NO2_Mine']}
        - **NO₂ Near Forest:** {row['NO2_Forest']}
        - **Risk Level:** {"High" if row['Risks'] == 1 else "Low"}
        """)

        folder_name = f"data_{zone}"
        folder_path = os.path.join(BASE_PATH, folder_name)
        if os.path.isdir(folder_path):
            if st.button("View Satellite Images"):
                st.session_state.main_open = True
                st.session_state.open_folder = folder_name
                st.session_state.search_open = False
                st.rerun()
        else:
            st.info("No satellite images found for this mine.")

# Footer
st.markdown("<div class='footer'><strong>EnvironmentSummer Organisation</strong></div>", unsafe_allow_html=True)
