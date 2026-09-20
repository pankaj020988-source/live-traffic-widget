import streamlit as st
import requests
import time

# पेज सेटिंग - कॉम्पॅक्ट आणि क्लीन दिसण्यासाठी
st.set_page_config(
    page_title="Live Traffic Scorecard",
    page_icon="🚗",
    layout="centered"
)

# कस्टम CSS - अगदी क्रिकेट स्कोअर पट्टीसारखा लूक देण्यासाठी
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e1e1e;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 1px solid #333;
    }
    .traffic-time {
        font-size: 32px;
        font-weight: bold;
        color: #00ffcc;
        margin: 5px 0;
    }
    .traffic-sub {
        font-size: 14px;
        color: #aaaaaa;
    }
    </style>
""", unsafe_allow_html=True)

# मूळ आणि गंतव्य स्थानाचे अक्षांश-रेखांश (उदा. मुंबई ते ठाणे)
ORIGIN_LON, ORIGIN_LAT = 72.8777, 19.0760
DEST_LON, DEST_LAT = 72.9781, 19.2183

def fetch_traffic_data():
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{ORIGIN_LON},{ORIGIN_LAT};{DEST_LON},{DEST_LAT}?overview=false"
        res = requests.get(url, timeout=5).json()
        duration_sec = res['routes'][0]['duration']
        distance_km = res['routes'][0]['distance'] / 1000
        mins = int(duration_sec // 60)
        return mins, round(distance_km, 1)
    except Exception:
        return None, None

mins, distance = fetch_traffic_data()

# स्कोअरकार्ड डिस्प्ले
if mins is not None:
    st.markdown(f"""
        <div class="metric-card">
            <div class="traffic-sub">📍 HOME ➔ OFFICE</div>
            <div class="traffic-time">🚗 {mins} MINS</div>
            <div class="traffic-sub">अंतर: {distance} किमी • लाइव्ह अपडेट</div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error("डेटा फेच करताना अडचण येत आहे. कृपया पुन्हा प्रयत्न करा.")

# दर ६० सेकंदांनी पेज आपोआप रीलोड होईल
time.sleep(60)
st.rerun()
