import streamlit as st
import requests
import time

st.set_page_config(
    page_title="Live Traffic Tracker",
    page_icon="🚗",
    layout="centered"
)

# तुमची TomTom API Key इथे टाका
TOMTOM_API_KEY = "YOUR_TOMTOM_API_KEY_HERE"

st.markdown("""
    <style>
    .scorecard {
        background: linear-gradient(135deg, #111827, #1f2937);
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        border: 2px solid #374151;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        margin-top: 20px;
    }
    .route-title {
        font-size: 15px;
        color: #9ca3af;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .travel-time {
        font-size: 42px;
        font-weight: 800;
        color: #00ffcc;
        margin: 6px 0;
    }
    .traffic-delay {
        font-size: 14px;
        color: #f87171;
        font-weight: bold;
    }
    .details {
        font-size: 16px;
        color: #e5e7eb;
        margin-top: 6px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚗 Live Commute Scorecard")

col1, col2 = st.columns(2)
with col1:
    origin_name = st.text_input("📍 मूळ स्थान (Origin):", value="Mangaon, Maharashtra")
with col2:
    dest_name = st.text_input("🏁 गंतव्य स्थान (Destination):", value="Indapur, Raigad")

# TomTom Geocoding (अचूक शहर शोधण्यासाठी)
@st.cache_data(ttl=3600)
def get_coordinates_tomtom(place_name, api_key):
    try:
        url = f"https://api.tomtom.com/search/2/geocode/{place_name}.json"
        params = {"key": api_key, "limit": 1, "countrySet": "IN"}
        res = requests.get(url, params=params, timeout=10).json()
        if res.get('results'):
            pos = res['results'][0]['position']
            return pos['lat'], pos['lon']
    except Exception:
        pass
    return None, None

# TomTom द्वारे लाइव्ह ट्रॅफिकसह वेळ काढणे
def get_live_traffic_route(o_lat, o_lon, d_lat, d_lon, api_key):
    try:
        url = f"https://api.tomtom.com/routing/1/calculateRoute/{o_lat},{o_lon}:{d_lat},{d_lon}/json"
        params = {
            "key": api_key,
            "traffic": "true",           # लाइव्ह ट्रॅफिक चालू करतो
            "departAt": "now"             # आत्ता निघाल्यास लागणारा वेळ
        }
        res = requests.get(url, params=params, timeout=10).json()
        if res.get('routes'):
            summary = res['routes'][0]['summary']
            travel_time_mins = int(summary['travelTimeInSeconds'] // 60)
            traffic_delay_mins = int(summary.get('trafficDelayInSeconds', 0) // 60)
            distance_km = round(summary['lengthInMeters'] / 1000, 1)
            return travel_time_mins, traffic_delay_mins, distance_km
    except Exception:
        pass
    return None, None, None

if origin_name and dest_name:
    if TOMTOM_API_KEY == "YOUR_TOMTOM_API_KEY_HERE":
        st.warning("⚠️ कृपया कोडमध्ये तुमची मोफत TomTom API Key टाका.")
    else:
        with st.spinner("लाइव्ह ट्रॅफिक मोजत आहे..."):
            o_lat, o_lon = get_coordinates_tomtom(origin_name, TOMTOM_API_KEY)
            d_lat, d_lon = get_coordinates_tomtom(dest_name, TOMTOM_API_KEY)

        if o_lat is None or d_lat is None:
            st.error("❌ ठिकाण शोधता आले नाही. कृपया नावाचे स्पेलिंग तपासा.")
        else:
            mins, delay, dist_km = get_live_traffic_route(o_lat, o_lon, d_lat, d_lon, TOMTOM_API_KEY)
            
            if mins is not None:
                delay_text = f"⚠️ ट्रॅफिक जॅममुळे {delay} मिनिटे उशीर" if delay > 0 else "🟢 रस्ता सुरळीत आहे (No Delay)"
                
                st.markdown(f"""
                    <div class="scorecard">
                        <div class="route-title">📍 {origin_name} ➔ 🏁 {dest_name}</div>
                        <div class="travel-time">⏱️ {mins} MINS</div>
                        <div class="traffic-delay">{delay_text}</div>
                        <div class="details">एकूण अंतर: <b>{dist_km} किमी</b> • लाइव्ह ट्रॅफिक अपडेट</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.error("रूट डेटा फेच करताना अडचण आली.")

st.divider()
auto_refresh = st.checkbox("दर ६० सेकंदांनी डेटा आपोआप अपडेट करा", value=False)
if auto_refresh:
    time.sleep(60)
    st.rerun()
