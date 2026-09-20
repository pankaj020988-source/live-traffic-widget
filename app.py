import streamlit as st
import requests
import time

st.set_page_config(
    page_title="Live Traffic Tracker",
    page_icon="🚗",
    layout="centered"
)

# स्कोअरकार्डसारखा लूक देण्यासाठी कस्टम डिझाइन
st.markdown("""
    <style>
    .scorecard {
        background: linear-gradient(135deg, #1e1e1e, #2a2a2a);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #444;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        margin-top: 15px;
    }
    .travel-time {
        font-size: 38px;
        font-weight: bold;
        color: #00ffcc;
        margin: 5px 0;
    }
    .details {
        font-size: 15px;
        color: #d1d5db;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚗 Live Commute Scorecard")

# साइडबार किंवा वरच्या भागात इनपुट बॉक्स
col1, col2 = st.columns(2)
with col1:
    origin_name = st.text_input("📍 मूळ स्थान (Origin):", value="Dadar, Mumbai")
with col2:
    dest_name = st.text_input("🏁 गंतव्य स्थान (Destination):", value="Thane Station")

# पत्त्यावरून अक्षांश-रेखांश शोधण्याचे फंक्शन (Geocoding)
@st.cache_data(ttl=3600)
def get_coordinates(place_name):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": place_name, "format": "json", "limit": 1}
        headers = {"User-Agent": "StreamlitTrafficTrackerApp/1.0"}
        res = requests.get(url, params=params, headers=headers, timeout=5).json()
        if res:
            return float(res[0]['lon']), float(res[0]['lat'])
    except Exception:
        pass
    return None, None

# प्रवासाची वेळ आणि अंतर काढण्याचे फंक्शन (OSRM Routing)
def get_route_info(orig_lon, orig_lat, dest_lon, dest_lat):
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{orig_lon},{orig_lat};{dest_lon},{dest_lat}?overview=false"
        res = requests.get(url, timeout=5).json()
        if res.get('routes'):
            duration_sec = res['routes'][0]['duration']
            distance_km = res['routes'][0]['distance'] / 1000
            mins = int(duration_sec // 60)
            return mins, round(distance_km, 1)
    except Exception:
        pass
    return None, None

# डेटा फेच आणि स्कोअरकार्ड रेंडर
if origin_name and dest_name:
    o_lon, o_lat = get_coordinates(origin_name)
    d_lon, d_lat = get_coordinates(dest_name)

    if o_lon is not None and d_lon is not None:
        mins, dist_km = get_route_info(o_lon, o_lat, d_lon, d_lat)
        
        if mins is not None:
            st.markdown(f"""
                <div class="scorecard">
                    <div class="details">📍 {origin_name.upper()} ➔ 🏁 {dest_name.upper()}</div>
                    <div class="travel-time">⏱️ {mins} MINS</div>
                    <div class="details">एकूण अंतर: <b>{dist_km} किमी</b> • ड्रायव्हिंग वेळ</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("या दोन ठिकाणांमधील रस्ता सापडला नाही. कृपया ठिकाणाचे नाव तपासा.")
    else:
        st.error("दिलेले ठिकाण मॅपवर सापडले नाही. कृपया अधिक तपशीलवार नाव टाका (उदा. 'Dadar West, Mumbai').")

# ऑटो-रिफ्रेश पर्याय
auto_refresh = st.checkbox("दर ६० सेकंदांनी डेटा आपोआप अपडेट करा", value=False)
if auto_refresh:
    time.sleep(60)
    st.rerun()
