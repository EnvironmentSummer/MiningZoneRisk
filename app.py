import streamlit as st
import pandas as pd
import os
from PIL import Image
from typing import Optional
import matplotlib.pyplot as plt
import seaborn as sns
import random

FUN_FACTS = [
    "India is the second-largest producer of coal in the world.",
    "Mining contributes about 2.5% to India's GDP.",
    "Some abandoned mines have become biodiversity hotspots.",
    "Satellite imagery can reveal forest loss near mining zones.",
    "Excess NO₂ levels near mines affect both vegetation and human health.",
    "Open-pit mining causes large-scale landscape changes visible from space.",
    "Illegal mining is a major contributor to environmental degradation in India.",
]


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
.stApp {background:#e9f5e1;color:#1c1c1c;font-family:'Segoe UI',sans-serif;}
h1,h2,h3,h4 {color:#205522;}
.stButton button{background:#2e7d32;color:#fff;font-weight:bold;border-radius:8px;padding:.4em 1.2em;}
.stButton button:hover{background:#1b5e20;}
.footer{position:fixed;bottom:0;left:0;right:0;text-align:center;padding:.6em;font-size:.9em;
        color:#1c1c1c;background:#d6eada;border-top:1px solid #a5c7a5;}
</style>
""", unsafe_allow_html=True)

for key in (
    "open_folder", "main_open", "viz_open", "search_open",
    "selected_image", "return_to_search", "selected_zone",
    "mine_chart_open"   # ← add this
):
    st.session_state.setdefault(key, None)


# ───────────────────────── Home ─────────────────────────
if not any([st.session_state.main_open,
            st.session_state.viz_open,
            st.session_state.search_open]):
    st.markdown("<h1 style='text-align:center;'>Research Analysis of Indian Mining Zones</h1>",
                unsafe_allow_html=True)

    left, right = st.columns(2)
    

    with left:
        st.subheader("Satellite Changes")
        cover = Image.open("Satellite_Cover.png")
        h = 180
        w = int(cover.width * h / cover.height)
        st.image(cover.resize((w, h)))
        if st.button("Open Mining Regions"):
            st.session_state.main_open = True
            st.rerun()

    with right:
        st.subheader("Visualisations")
        st.markdown("Explore forest loss, NO₂ levels, and correlations.")
        if st.button("Open Charts"):
            st.session_state.viz_open = True
            st.rerun()

        st.subheader("Mine Data Explorer")
        st.markdown("Search any mining zone and review its risk profile.")
        if st.button("Open Mine Explorer"):
            st.session_state.search_open = True
            st.rerun()

    st.markdown("---")
    fact = random.choice(FUN_FACTS)
    st.markdown("""
        <h3 style="color:#205522;">💡 Did You Know?</h3>
        <div style="background-color:#d6eada;padding:1em;border-radius:8px;
                    border:1px solid #a5c7a5;color:#1c4411;">
            <strong>{}</strong>
        </div>
    """.format(fact), unsafe_allow_html=True)



# ─────────────────── Satellite Folder Grid ───────────────────
elif st.session_state.main_open and st.session_state.open_folder is None:
    st.title("Satellite Changes")
    if st.button("Back to Home"):
        st.session_state.main_open = False
        st.rerun()

    folders = sorted(f for f in os.listdir(BASE_PATH)
                     if os.path.isdir(os.path.join(BASE_PATH, f)))
    cols = st.columns(3)
    for idx, folder in enumerate(folders):
        with cols[idx % 3]:
            st.image(cover_path(folder) or " ", use_container_width=True)
            st.caption(clean_name(folder))
            if st.button("Open", key=f"open_{folder}"):
                st.session_state.open_folder = folder
                st.rerun()

# ──────────────── Satellite Folder Content ────────────────
elif st.session_state.open_folder:
    folder = st.session_state.open_folder
    path   = os.path.join(BASE_PATH, folder)

    if st.session_state.selected_image:
        if st.button("Back to Folder"):
            st.session_state.selected_image = None
            st.rerun()
        img = Image.open(st.session_state.selected_image)
        h   = 600
        w   = int(img.width * h / img.height)
        st.image(img.resize((w, h)))
    else:
        back_label = (
            "Back to Mine Explorer"
            if st.session_state.return_to_search else
            "Back to Mining Regions"
        )
        if st.button(back_label):
            st.session_state.open_folder = None
            if st.session_state.return_to_search:
                st.session_state.search_open      = True
                st.session_state.main_open        = None
                st.session_state.return_to_search = None
            st.rerun()

        st.header(clean_name(folder))
        imgs = sorted(
            f for f in os.listdir(path)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        )
        cols = st.columns(4)
        for idx, im in enumerate(imgs):
            with cols[idx % 4]:
                ip = os.path.join(path, im)
                st.image(ip, use_container_width=True)
                if st.button("View", key=f"view_{im}"):
                    st.session_state.selected_image = ip
                    st.rerun()

# ───────────────────── Visualisations ─────────────────────
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
        corr = df[[
            "ForestLossPct", "DistanceToForest", "UrbanGrowth",
            "LanduseChange", "NO2_Mine", "NO2_Forest"
        ]].astype(float).corr()
        sns.heatmap(corr, annot=True, cmap="YlGnBu", ax=ax)
        ax.set_title("Feature Correlation")
        st.pyplot(fig, use_container_width=False)

    def plot_no2_levels():
        fig, ax = plt.subplots(figsize=(4, 3.5))
        zones = df["Zone"].str.replace("_", " ")
        ax.bar(zones, df["NO2_Mine"], label="Mine",   color="crimson")
        ax.bar(zones, df["NO2_Forest"], label="Forest", color="seagreen", alpha=0.7)
        ax.set_title("NO₂ Concentration")
        ax.tick_params(axis="x", rotation=90, labelsize=7)
        ax.legend()
        st.pyplot(fig, use_container_width=False)

    plot_mines_and_forests()
    plot_correlation()
    plot_no2_levels()

# ────────────────── Mine Data Explorer ──────────────────
# ────────────────── Mine Data Explorer ──────────────────
elif st.session_state.search_open:
    st.title("Mine Data Explorer")

    if st.button("Back to Home"):
        st.session_state.search_open = False
        st.rerun()

    df = pd.read_csv("zone_features.csv").dropna(subset=["Zone"])
    zones = sorted(df["Zone"].unique())
    idx = zones.index(st.session_state.selected_zone) if st.session_state.selected_zone in zones else 0
    zone = st.selectbox("Search Mining Zone", zones, index=idx)
    st.session_state.selected_zone = zone

    if zone:
        row = df[df["Zone"] == zone].iloc[0]
        folder = f"data_{zone}"
        img_name = f"{zone}_Satellite_2024_After.png"
        img_path = os.path.join(BASE_PATH, folder, img_name)
        img_ok = os.path.isfile(img_path)
        lat, lon = row["Lat"], row["Long"]
        gmaps = f"https://www.google.com/maps/@{lat},{lon},17z"

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
                - **NO₂ Near Mine:** {row['NO2_Mine']}
                - **NO₂ Near Forest:** {row['NO2_Forest']}
                - **Risk Level:** {"High" if row['Risks'] == 1 else "Low"}
                """
            )

            # 1) View Satellite Images (now first)
            if img_ok and st.button("View Satellite Images"):
                st.session_state.main_open        = True
                st.session_state.open_folder      = folder
                st.session_state.return_to_search = True
                st.session_state.search_open      = False
                st.rerun()

            # 2) Google-Maps link (now below)
            st.link_button("Open in Google Maps", gmaps)

            # 3) Chart toggle
            if st.button("View Charts for this Mine"):
                st.session_state.mine_chart_open = not st.session_state.get("mine_chart_open", False)

            if st.session_state.get("mine_chart_open", False):
                c1, c2 = st.columns(2)
                with c1:
                    fig1, ax1 = plt.subplots(figsize=(3.2, 2.5))
                    ax1.bar(["Mine", "Forest"], [row["NO2_Mine"], row["NO2_Forest"]],
                            color=["crimson", "seagreen"])
                    ax1.set_ylabel("NO₂ Level")
                    ax1.set_title("NO₂ Comparison")
                    st.pyplot(fig1)
                with c2:
                    fig2, ax2 = plt.subplots(figsize=(3.2, 0.6))
                    ax2.barh([0], [1], color="#ddd")
                    ax2.barh([0], [0.5 if row['Risks'] == 0 else 1],
                             color="orange" if row['Risks'] == 1 else "green")
                    ax2.set_xlim(0, 1)
                    ax2.set_xticks([]); ax2.set_yticks([])
                    ax2.set_title("Risk Level")
                    st.pyplot(fig2)

        with right:
            if img_ok:
                st.image(img_path, caption="Satellite 2024 – After", use_container_width=True)
            else:
                st.info("Satellite image not found.")





# Footer
st.markdown(
    "<div class='footer'><strong>EnvironmentSummer Organisation</strong></div>",
    unsafe_allow_html=True
)
