import streamlit as st
import requests
import time

st.set_page_config(
    page_title="Live Traffic Tracker",
    page_icon="🚗",
    layout="centered"
)

# क्रिकेट स्कोअरकार्डसारखी स्टाईल (CSS)
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
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .details {
        font-size: 16px;
        color: #e5e7eb;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚗 Live Commute Scorecard")

# इनपुट बॉक्स
col1, col2 = st.columns(2)
with col1:
    origin_name = st.text_input("📍 मूळ स्थान (Origin):", value="Mangaon, Maharashtra")
with col2:
    dest_name = st.text_input("🏁 गंतव्य स्थान (Destination):", value="Indapur, Raigad")

# पत्त्यावरून अचूक अक्षांश-रेखांश शोधणे (OpenStreetMap Geocoding)
@st.cache_data(ttl=3600)
def get_coordinates(place_name):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": place_name.strip(),
            "format": "json",
            "limit": 1,
            "countrycodes": "in"  # फक्त भारतात शोधण्यासाठी
        }
        headers = {"User-Agent": "StreamlitTrafficTrackerApp/2.0"}
        res = requests.get(url, params=params, headers=headers, timeout=10).json()
        if res and len(res) > 0:
            return float(res[0]['lon']), float(res[0]['lat']), res[0].get('display_name', place_name)
    except Exception as e:
        pass
    return None, None, None

# OSRM द्वारे अंतर आणि वेळ काढणे
def get_route_info(orig_lon, orig_lat, dest_lon, dest_lat):
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{orig_lon},{orig_lat};{dest_lon},{dest_lat}?overview=false"
        res = requests.get(url, timeout=10).json()
        if res.get('routes') and len(res['routes']) > 0:
            duration_sec = res['routes'][0]['duration']
            distance_km = res['routes'][0]['distance'] / 1000
            mins = int(duration_sec // 60)
            return mins, round(distance_km, 1)
    except Exception as e:
        pass
    return None, None

# सर्च आणि स्कोअरकार्ड डिस्प्ले
if origin_name and dest_name:
    with st.spinner("रूट आणि ट्रॅफिक वेळ तपासत आहे..."):
        o_lon, o_lat, o_full = get_coordinates(origin_name)
        d_lon, d_lat, d_full = get_coordinates(dest_name)

    if o_lon is None:
        st.error(f"❌ मूळ स्थान सापडले नाही: '{origin_name}'. कृपया तालुक्याचे किंवा जिल्ह्याचे नाव जोडून पहा (उदा. Mangaon, Raigad).")
    elif d_lon is None:
        st.error(f"❌ गंतव्य स्थान सापडले नाही: '{dest_name}'. कृपया तालुक्याचे किंवा जिल्ह्याचे नाव जोडून पहा (उदा. Indapur, Raigad).")
    else:
        mins, dist_km = get_route_info(o_lon, o_lat, d_lon, d_lat)
        
        if mins is not None:
            # वेळ तास आणि मिनिटांत रूपांतरित करणे
            if mins >= 60:
                hours = mins // 60
                rem_mins = mins % 60
                time_display = f"{hours} तास {rem_mins} मिनिटे"
            else:
                time_display = f"{mins} MINS"

            st.markdown(f"""
                <div class="scorecard">
                    <div class="route-title">📍 {origin_name} ➔ 🏁 {dest_name}</div>
                    <div class="travel-time">⏱️ {time_display}</div>
                    <div class="details">एकूण अंतर: <b>{dist_km} किमी</b> • सध्याची अंदाजे वेळ</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("या दोन ठिकाणांमधील थेट रस्ता सापडला नाही.")

# ऑटो रिफ्रेश टॉगल
st.divider()
auto_refresh = st.checkbox("दर ६० सेकंदांनी डेटा आपोआप अपडेट करा", value=False)
if auto_refresh:
    time.sleep(60)
    st.rerun()
