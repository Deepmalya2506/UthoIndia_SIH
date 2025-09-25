import streamlit as st
import pandas as pd
import json
import time
import os

# --- Page Config ---
st.set_page_config(page_title="UthoIndia - Visual Walkthrough", page_icon="🌊", layout="wide")

# --- Data Files ---
TWEET_FILE = "my_collected_tweets.json"
MAP_FILE = "disaster_hotspot_map_interactive.html"

# --- Custom CSS ---
st.markdown("""
<style>
.stage {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 50px 0;
}
.icon {
    font-size: 60px;
    margin: 0 20px;
    animation: fadeIn 1s ease-in-out;
}
.label {
    font-size: 22px;
    font-weight: bold;
    text-align: center;
    margin-top: 10px;
}
.connector {
    width: 140px;
    height: 4px;
    background: linear-gradient(to right, #3498db, #85c1e9);
    border-radius: 2px;
    margin: 0 20px;
    animation: pulseLine 2s infinite;
}
.pulse {
    margin: 20px auto;
    width: 20px;
    height: 20px;
    background: #3498db;
    border-radius: 50%;
    box-shadow: 0 0 0 rgba(52, 152, 219, 0.7);
    animation: pulseGlow 2s infinite;
}
@keyframes fadeIn {
    from { opacity: 0; transform: scale(0.8); }
    to { opacity: 1; transform: scale(1); }
}
@keyframes pulseLine {
    0% { opacity: 0.4; }
    50% { opacity: 1; }
    100% { opacity: 0.4; }
}
@keyframes pulseGlow {
    0% {
        box-shadow: 0 0 0 0 rgba(52, 152, 219, 0.7);
    }
    70% {
        box-shadow: 0 0 0 20px rgba(52, 152, 219, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(52, 152, 219, 0);
    }
}
</style>
""", unsafe_allow_html=True)

def show_stage(icon1, icon2, label, delay=6):
    with st.container():
        st.markdown(f'<div class="stage"><div class="icon">{icon1}</div><div class="connector"></div><div class="icon">{icon2}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="label">{label}</div>', unsafe_allow_html=True)
        st.markdown('<div class="pulse"></div>', unsafe_allow_html=True)
        time.sleep(delay)

def show_not_found(message="The data you're looking for isn't available."):
    st.markdown(f"""
    <div style="text-align:center; padding:30px;">
        <div style="font-size:50px; color:#ff6f61;">🔍</div>
        <p style="font-size:20px; color:#888;">{message}</p>
    </div>
    """, unsafe_allow_html=True)

# --- Header ---
st.title("🌊 UthoIndia - Visual AI Pipeline")
st.markdown("A cinematic walkthrough of the disaster detection workflow powered by social sensing and geospatial intelligence.")

# --- Stage Animations with Unique Delays ---
show_stage("📄", "📁", "Chapter 1: Voices of Twitter", delay=6)
show_stage("📁", "🤖", "Chapter 2: Transformer distill noise into meaning", delay=9)
show_stage("🤖", "📁✅", "Chapter 3: Authenticity pass", delay=5)
show_stage("📁", "🌍", "Chapter 4: NER + Geocoder ", delay=8)
show_stage("🌍", "🏢", "Chapter 5: Earth tessellates into H3 hexagons", delay=7)
show_stage("🏢", "🗺️", "Chapter 6: Hotspots Canvass", delay=6)

# --- Load Data ---
def load_tweets():
    try:
        with open(TWEET_FILE, "r", encoding="utf-8") as f:
            return pd.DataFrame(json.load(f))
    except Exception:
        return None

def load_map_html():
    try:
        with open(MAP_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None

# --- Node Explorer (only 3 dropdowns retained) ---
st.subheader("🧭 Explore Available Stages")
selected_node = st.selectbox("Choose a stage to inspect:", [
    "Collecting Tweets",
    "Semantic Filtering",
    "Hotspot Map"
])

# --- Stage Details ---
if selected_node == "Collecting Tweets":
    st.markdown("### 📡 Tweets Collected via Twitter API")
    df_tweets = load_tweets()
    if df_tweets is not None and not df_tweets.empty:
        st.dataframe(df_tweets.head(10), use_container_width=True)
    else:
        show_not_found("Tweet data could not be loaded or is empty.")

elif selected_node == "Semantic Filtering":
    st.markdown("### 🤖 Gemini Semantic Filtering")
    st.markdown("✅ Example 1: `Huge number of fans flooded streets of Ranchi for MSD` → **Not a disaster** (Score: 0.18)")
    st.markdown("✅ Example 2: `The streets of Kolkata are flooded before Puja due to the cloud burst` → **Likely disaster** (Score: 0.92)")

elif selected_node == "Hotspot Map":
    st.markdown("### 🗺️ Interactive Hotspot Map")
    map_html = load_map_html()
    if map_html:
        st.components.v1.html(map_html, height=600)
    else:
        show_not_found("Map file could not be loaded.")

# --- Footer ---
st.markdown("---")
st.markdown("Built by **Data Dolphins** | Designed for Emergency , powered by AI 🚀")
