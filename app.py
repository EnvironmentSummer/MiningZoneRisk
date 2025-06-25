import streamlit as st
import pandas as pd
import os
from PIL import Image
from typing import Optional
import matplotlib.pyplot as plt
import seaborn as sns
import random

st.set_page_config(page_title="Risky Mines", layout="wide")
BASE_PATH = "data"

def clean_name(name: str) -> str:
    return name.replace("data_", "").replace("_", " ").strip()

def cover_path(folder: str) -> Optional[str]:
    base = folder.replace("data_", "")
    p = os.path.join(BASE_PATH, folder, f"{base}_Satellite_2024_After.png")
    return p if os.path.exists(p) else None

def parse_water_level(val):
    try:
        if isinstance(val, str) and "-" in val:
            low, high = map(float, val.split("-"))
            return (low + high) / 2
        return float(val)
    except Exception:
        return None

st.markdown(
    """
    <style>
    .stApp{background:#f4faef;color:#1c1c1c;font-family:'Segoe UI',sans-serif;}
    h1,h2,h3{color:#205522;}
    .stButton button{background:#2e7d32;color:#fff;border-radius:8px;padding:.5em 1.4em;font-weight:700;}
    .stButton button:hover{background:#1b5e20;}
    .banner{background:#ffeb3b;padding:.7em 1em;border-radius:8px;font-weight:bold;color:#a30000;text-align:center;margin-bottom:1.5em;}
    .footer{position:fixed;bottom:0;left:0;right:0;text-align:center;padding:.6em;font-size:.9em;color:#1c1c1c;background:#d6eada;border-top:1px solid #a5c7a5;}
    </style>
    """,
    unsafe_allow_html=True,
)

for k in (
    "open_folder", "main_open", "viz_open", "search_open",
    "selected_image", "return_to_search", "selected_zone", "mine_chart_open"
):
    st.session_state.setdefault(k, None)

df = pd.read_csv("zone_features.csv").dropna(subset=["Zone"])
df["Water Levels"] = df["Water Levels"].apply(parse_water_level)

if not any([st.session_state.main_open, st.session_state.viz_open, st.session_state.search_open]):
    top_zone = df.sort_values("Risk", ascending=False).iloc[0]["Zone"].replace("_", " ")
    st.markdown(f"<div class='banner'>Today’s Top Risk Zone: <u>{top_zone}</u></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Research on Indian Mining Zones</h1>", unsafe_allow_html=True)

    cards = st.columns(3)

    with cards[0]:
        st.subheader("Satellite Changes")
        st.image(Image.open("satellite_cover.png").resize((300, 180)))
        if st.button("Open Mining Regions"):
            st.session_state.main_open = True
            st.rerun()

    with cards[1]:
        st.subheader("Visualisations")
        st.image(Image.open("visualisation.png").resize((300, 180)))
        if st.button("Open Charts"):
            st.session_state.viz_open = True
            st.rerun()

    with cards[2]:
        st.subheader("Mine Explorer")
        st.image(Image.open("Explorer.png").resize((300, 180)))
        if st.button("Open Explorer"):
            st.session_state.search_open = True
            st.rerun()

    spacer_left, center_col, spacer_right = st.columns([1, 1, 1])
    with center_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Surprise Me with a Random Mine"):
            st.session_state.selected_zone = random.choice(sorted(df["Zone"].unique()))
            st.session_state.search_open = True
            st.rerun()

elif st.session_state.main_open and st.session_state.open_folder is None:
    st.title("Satellite Changes")
    if st.button("Back to Home"):
        st.session_state.main_open = False
        st.rerun()
    folders = sorted(f for f in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, f)))
    cols = st.columns(3)
    for idx, folder in enumerate(folders):
        with cols[idx % 3]:
            img = cover_path(folder)
            if img:
                st.image(img, use_container_width=True)
            st.caption(clean_name(folder))
            if st.button("Open", key=f"open_{folder}"):
                st.session_state.open_folder = folder
                st.rerun()

elif st.session_state.open_folder:
    folder = st.session_state.open_folder
    path = os.path.join(BASE_PATH, folder)
    if st.session_state.selected_image:
        if st.button("Back to Folder"):
            st.session_state.selected_image = None
            st.rerun()
        img = Image.open(st.session_state.selected_image)
        w, h = img.size
        st.image(img.resize((int(w * 600 / h), 600)))
    else:
        back_lbl = "Back to Mine Explorer" if st.session_state.return_to_search else "Back to Mining Regions"
        if st.button(back_lbl):
            st.session_state.open_folder = None
            if st.session_state.return_to_search:
                st.session_state.search_open = True
                st.session_state.return_to_search = None
            st.rerun()
        st.header(clean_name(folder))
        imgs = [f for f in sorted(os.listdir(path)) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        cols = st.columns(4)
        for idx, im in enumerate(imgs):
            with cols[idx % 4]:
                ip = os.path.join(path, im)
                st.image(ip, use_container_width=True)
                if st.button("View", key=f"view_{im}"):
                    st.session_state.selected_image = ip
                    st.rerun()

elif st.session_state.viz_open:
    st.title("Visualisations")
    if st.button("Back to Home"):
        st.session_state.viz_open = False
        st.rerun()

    def feature_vs_risk():
        features = [
            "ForestLossPct", "DistanceToForest", "UrbanGrowth",
            "LanduseChange", "NO2_Mine", "NO2_Forest", "Water Levels"
        ]
        st.subheader("Feature vs Risk")
        cols = st.columns(3)
        for i, feat in enumerate(features):
            with cols[i % 3]:
                fig, ax = plt.subplots(figsize=(2.8, 2.2))
                ax.scatter(df[feat], df["Risk"], alpha=0.6, color="#2e7d32")
                ax.set_xlabel(feat, fontsize=5)
                ax.set_ylabel("Risk", fontsize=5)
                ax.tick_params(labelsize=5)
                st.pyplot(fig, use_container_width=True)

    feature_vs_risk()

elif st.session_state.search_open:
    st.title("Mine Explorer")
    if st.button("Back to Home"):
        st.session_state.search_open = False
        st.rerun()

    zones = sorted(df["Zone"].unique())
    idx = zones.index(st.session_state.selected_zone) if st.session_state.selected_zone in zones else 0
    zone = st.selectbox("Search a Zone", zones, index=idx)
    st.session_state.selected_zone = zone

    if zone:
        row = df[df["Zone"] == zone].iloc[0]
        folder = f"data_{zone}"
        img_path = os.path.join(BASE_PATH, folder, f"{zone}_Satellite_2024_After.png")
        img_ok = os.path.isfile(img_path)
        lat, lon = row["Lat"], row["Long"]
        gmaps = f"https://www.google.com/maps/@{lat},{lon},16z"

        left, right = st.columns([2, 1])

        with left:
            st.subheader(zone.replace("_", " "))
            st.markdown(
                f"""
                - **Latitude / Longitude:** {lat} / {lon}  
                - **Forest Loss %:** {row['ForestLossPct'] if pd.notna(row['ForestLossPct']) else 'N/A'}  
                - **Distance to Forest:** {row['DistanceToForest']} km  
                - **Urban Growth Index:** {row['UrbanGrowth']}  
                - **Land-Use Change:** {row['LanduseChange']}  
                - **Nearest Forest:** {row['ForestName']}  
                - **NO₂ Near Mine / Forest:** {row['NO2_Mine']} / {row['NO2_Forest']}  
                - **Water Level (avg):** {row['Water Levels']}  
                - **Risk Level:** {'High' if row['Risk']==1 else 'Low'}
                """
            )

            if img_ok and st.button("View Satellite Images"):
                st.session_state.main_open = True
                st.session_state.open_folder = folder
                st.session_state.return_to_search = True
                st.session_state.search_open = False
                st.rerun()

            st.link_button("Open in Google Maps", gmaps)

            if st.button("View Charts for this Zone"):
                st.session_state.mine_chart_open = not st.session_state.get("mine_chart_open", False)

            if st.session_state.get("mine_chart_open", False):
                feat_cols = [
                    "ForestLossPct", "DistanceToForest", "UrbanGrowth",
                    "LanduseChange", "NO2_Mine", "NO2_Forest", "Water Levels"
                ]
                med_vals = df[feat_cols].median()
                cols = st.columns(2)
                for i, feat in enumerate(feat_cols):
                    with cols[i % 2]:
                        q1 = df[feat].quantile(0.30)
                        q3 = df[feat].quantile(0.70)
                        mine_val = row[feat]
                        bars = ["30% (Min)", "Median", "70% (Max)", "This Mine"]
                        vals = [q1, med_vals[feat], q3, mine_val]
                        colors = ["#dcedc8", "#b0bec5", "#90caf9", "#2e7d32"]

                        fig, ax = plt.subplots(figsize=(3.3, 2.3))
                        ax.bar(bars, vals, color=colors)
                        ax.set_title(feat, fontsize=7)
                        ax.set_ylabel("Value", fontsize=6)
                        ax.tick_params(labelsize=5)
                        fig.tight_layout()
                        st.pyplot(fig)

        with right:
            if img_ok:
                st.image(img_path, caption="Satellite 2024 – After", use_container_width=True)
            else:
                st.info("No satellite image available.")

st.markdown("<div class='footer'><strong>EnvironmentSummer Organisation</strong></div>", unsafe_allow_html=True)
