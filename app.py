import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import h3
from pathlib import Path
from PIL import Image
import spacy
from core import get_media_visuals
import requests
from streamlit_lottie import st_lottie
import time

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="🌍 UthoIndia", layout="wide")
MEDIA_DIR = Path("media")
LOCAL_VIDEO_PATH = MEDIA_DIR / "heygen_kolkata.mp4"

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "chapter" not in st.session_state:
    st.session_state.chapter = 0

# -----------------------------
# LOTTIE UTILS
# -----------------------------
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# -----------------------------
# CHAPTER FUNCTION
# -----------------------------
def cinematic_chapter(title, desc, icon, author):
    st.empty()  # Ensure fresh container
    container = st.container()
    # Title fade-in
    container.markdown(f"<h1 style='text-align:center'>{title}</h1>", unsafe_allow_html=True)
    # Lottie animation
    lottie_json = load_lottie_url(icon)
    if lottie_json:
        st_lottie(lottie_json, height=200)
    # Description
    container.markdown(f"<p style='font-size:18px'>{desc}</p>", unsafe_allow_html=True)
    # Author
    container.markdown(f"<p style='font-style:italic'>{author}</p>", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("final_geocoded_reports.csv")

df = load_data()

# -----------------------------
# SPACY LOCATION & CONTEXT
# -----------------------------
nlp = spacy.load("en_core_web_sm")
def extract_location_and_context(row):
    geo = row.get("tweet_geo")
    if pd.notna(geo) and geo != "nan":
        try:
            import ast
            geo_dict = ast.literal_eval(geo)
            if "coordinates" in geo_dict:
                location_name = f"{geo_dict['coordinates'][0]},{geo_dict['coordinates'][1]}"
            else:
                location_name = row.get("author_profile_location", "Unknown")
        except Exception:
            location_name = row.get("author_profile_location", "Unknown")
    else:
        doc = nlp(str(row.get("text", "")))
        loc_entities = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
        location_name = loc_entities[0] if loc_entities else row.get("author_profile_location", "Unknown")

    disaster_keywords = ["flood", "rain", "cloud burst", "cyclone", "storm", "landslide",
                         "tsunami", "earthquake", "fire", "high wave", "storm surge"]
    text = str(row.get("text", "")).lower()
    context_terms = [kw for kw in disaster_keywords if kw in text]
    disaster_context = ", ".join(context_terms) if context_terms else row.get("text", "General disaster")
    return location_name, disaster_context

# -----------------------------
# MAP PREP
# -----------------------------
H3_RESOLUTION = 7
df["h3_index"] = df.apply(lambda row: h3.latlng_to_cell(row["latitude"], row["longitude"], H3_RESOLUTION), axis=1)
report_density = df["h3_index"].value_counts().reset_index()
report_density.columns = ["h3_index", "report_count"]
hotspot_centers = {row["h3_index"]: h3.cell_to_latlng(row["h3_index"]) for _, row in report_density.iterrows()}

def create_hotspot_map(selected_h3=None):
    center = [df["latitude"].mean(), df["longitude"].mean()]
    zoom = 7
    if selected_h3:
        center = hotspot_centers[selected_h3]
        zoom = 12
    hotspot_map = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")
    for _, row in report_density.iterrows():
        hex_coords = [[lon, lat] for lat, lon in h3.cell_to_boundary(row["h3_index"])]
        folium.GeoJson(
            {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [hex_coords]}},
            style_function=lambda feature, h3_idx=row["h3_index"]: {
                "fillColor": "red" if h3_idx == selected_h3 else "orange",
                "color": "black",
                "weight": 2,
                "fillOpacity": 0.6
            },
            tooltip=f"🔥 Reports: {row['report_count']}<br>H3 Index: {row['h3_index']}"
        ).add_to(hotspot_map)
    return hotspot_map

# -----------------------------
# STORY CHAPTERS SEQUENCE
# -----------------------------
chapters = [
    {"title":"Chapter 01 – Data Collection", "desc":"Collecting social media posts from Twitter as initial data source.", 
     "icon":"https://assets9.lottiefiles.com/packages/lf20_iwmd6pyr.json", "author":"Authored by: You"},
    {"title":"Chapter 02 – Disaster Classification", "desc":"AI models classify posts as disaster-related or general content.", 
     "icon":"https://assets9.lottiefiles.com/packages/lf20_tutvdkg0.json", "author":"Authored by: You"},
    {"title":"Chapter 03 – Hotspot Mapping", "desc":"Reports are geocoded and aggregated into H3 hexagonal hotspots.", 
     "icon":"https://assets9.lottiefiles.com/packages/lf20_xdfeea13.json", "author":"Authored by: You"},
    {"title":"Chapter 04 – Media & AI Reports", "desc":"Visuals and AI-generated videos provide contextual disaster awareness.", 
     "icon":"https://assets9.lottiefiles.com/packages/lf20_5ngs2ksb.json", "author":"Authored by: You"},
    {"title":"Chapter 05 – Insights & Trends", "desc":"Analyze top disaster types and hotspot statistics for actionable insights.", 
     "icon":"https://assets9.lottiefiles.com/packages/lf20_c9py7q7h.json", "author":"Authored by: You"}
]

# -----------------------------
# RENDER CHAPTER BASED ON SESSION STATE
# -----------------------------
current = st.session_state.chapter

if current < len(chapters)-1:
    cinematic_chapter(**chapters[current])
    if st.button("➡️ Next Chapter"):
        st.session_state.chapter += 1
        st.rerun()
else:
    # Final chapter: Map with visuals & AI report
    cinematic_chapter(**chapters[-1])
    col1, col2 = st.columns([2,1])
    with col2:
        selected_h3 = st.selectbox(
            "Select a hotspot",
            report_density["h3_index"].tolist(),
            format_func=lambda x: f"{x} ({report_density.loc[report_density['h3_index']==x,'report_count'].iloc[0]} reports)"
        )
    with col1:
        hotspot_map = create_hotspot_map(selected_h3)
        map_data = st_folium(hotspot_map, height=600, width=800, returned_objects=["last_clicked"])

    hotspot_points = df[df["h3_index"] == selected_h3]
    nearest_point = hotspot_points.iloc[0] if not hotspot_points.empty else df.iloc[0]
    location_name, disaster_context = extract_location_and_context(nearest_point)

    tab1, tab2 = st.tabs(["🖼️ Contextual Visuals", "🎥 AI News Report"])
    with tab1:
        visuals = get_media_visuals(keywords=[disaster_context], location=location_name)
        if visuals:
            for i, img_path in enumerate(visuals):
                with st.expander(f"Page {i+1}"):
                    img = Image.open(img_path)
                    st.image(img, caption=Path(img_path).name, use_container_width=True)
        else:
            st.warning("No visuals found for this hotspot yet.")
    with tab2:
        if "kolkata" in str(location_name).lower() and any(
            kw in disaster_context.lower() for kw in ["rain", "cloud burst", "flood"]
        ):
            st.video(str(LOCAL_VIDEO_PATH))
        else:
            st.warning("🚧 AI news report not available for this hotspot.")
