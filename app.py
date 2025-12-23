import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils import (
    get_coordinates,
    get_weather_by_coords,
    get_forecast_by_coords,
    weather_icon,
    weather_advice,
    detect_location_by_ip
)

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Smart Weather Dashboard",
    page_icon="🌦",
    layout="wide"
)

# -------------------------------------------------
# Custom CSS (ENHANCED UI)
# -------------------------------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(180deg, #020617, #0f172a);
}

.weather-card {
    background: rgba(28, 31, 38, 0.85);
    backdrop-filter: blur(10px);
    padding: 22px;
    border-radius: 18px;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}

.metric-card {
    background: linear-gradient(145deg, #1f2937, #111827);
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    transition: transform 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-6px);
}

.metric-value {
    font-size: 30px;
    font-weight: bold;
    color: #f9fafb;
}
.metric-label {
    color: #9ca3af;
    font-size: 14px;
}

.title-text {
    font-size: 40px;
    font-weight: 800;
}
.subtitle {
    color: #9ca3af;
    margin-bottom: 10px;
}

.footer {
    text-align: center;
    color: #9ca3af;
    margin-top: 50px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown("<div class='title-text'>🌦 Smart Weather Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Real-time weather • Auto location • Alerts • Forecast</div>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------------------------------
# Sidebar – Location Controls
# -------------------------------------------------
st.sidebar.header("📍 Location")

if "location" not in st.session_state:
    st.session_state.location = None

if st.sidebar.button("📡 Auto Detect My Location"):
    detected = detect_location_by_ip()
    if detected:
        st.session_state.location = detected
        st.sidebar.success("Location detected!")
    else:
        st.sidebar.error("Unable to detect location.")

city = st.sidebar.text_input("City", "Mumbai")
country = st.sidebar.text_input("Country Code", "IN")

unit = st.sidebar.radio("Temperature Unit", ["Celsius", "Fahrenheit"])
units = "metric" if unit == "Celsius" else "imperial"

# -------------------------------------------------
# Resolve Location → Coordinates
# -------------------------------------------------
if st.session_state.location:
    lat = st.session_state.location["lat"]
    lon = st.session_state.location["lon"]
    location_label = st.session_state.location["label"]
else:
    coords = get_coordinates(city, country)
    if not coords:
        st.error("❌ Location not found.")
        st.stop()
    lat, lon = coords["lat"], coords["lon"]
    location_label = coords["location"]

# -------------------------------------------------
# Fetch Weather
# -------------------------------------------------
with st.spinner("🌍 Fetching latest weather data..."):
    weather = get_weather_by_coords(lat, lon, units)
    forecast = get_forecast_by_coords(lat, lon, units)

if "weather" not in weather:
    st.error("⚠ Unable to fetch weather data.")
    st.stop()

# -------------------------------------------------
# Extract Weather
# -------------------------------------------------
condition = weather["weather"][0]["main"]
icon = weather_icon(condition)

temp = weather["main"]["temp"]
feels_like = weather["main"]["feels_like"]
humidity = weather["main"]["humidity"]
wind = weather["wind"]["speed"]

# -------------------------------------------------
# CURRENT WEATHER UI
# -------------------------------------------------
st.markdown("<div class='weather-card'>", unsafe_allow_html=True)
st.subheader(f"{icon} Current Weather — {location_label}")

c1, c2, c3, c4 = st.columns(4)

def metric(label, value):
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

c1.markdown(metric("🌡 Temperature", f"{temp}°"), unsafe_allow_html=True)
c2.markdown(metric("🤗 Feels Like", f"{feels_like}°"), unsafe_allow_html=True)
c3.markdown(metric("💧 Humidity", f"{humidity}%"), unsafe_allow_html=True)
c4.markdown(metric("🌬 Wind", f"{wind} m/s"), unsafe_allow_html=True)

st.info(weather_advice(temp, humidity, wind))
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# 🔔 WEATHER ALERTS (UI PANEL)
# -------------------------------------------------
st.markdown("<div class='weather-card'>", unsafe_allow_html=True)
st.subheader("🔔 Weather Alerts")

alerts = []
cond = condition.lower()

if cond in ["rain", "drizzle", "thunderstorm"]:
    alerts.append("🌧 Rain or storm expected. Carry an umbrella.")
if temp >= 38:
    alerts.append("🔥 Extreme heat warning. Stay hydrated.")
if temp <= 5:
    alerts.append("❄ Cold wave conditions. Wear warm clothes.")
if wind >= 10:
    alerts.append("🌬 Strong winds. Be cautious outdoors.")

if alerts:
    for a in alerts:
        st.warning(a)
else:
    st.success("✅ No severe weather alerts")

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# 📅 5-Day Forecast UI
# -------------------------------------------------
st.markdown("<div class='weather-card'>", unsafe_allow_html=True)
st.subheader("📅 5-Day Temperature Forecast")

daily = {}
for item in forecast["list"]:
    date, time = item["dt_txt"].split(" ")
    if time == "12:00:00" and date not in daily:
        daily[date] = item["main"]["temp"]

df = pd.DataFrame({
    "Date": list(daily.keys()),
    "Temperature": list(daily.values())
})

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["Date"], df["Temperature"], marker="o", linewidth=2)
ax.grid(alpha=0.3)
ax.set_ylabel("Temperature")

st.pyplot(fig)

# Day cards
cols = st.columns(len(df))
for i, row in df.iterrows():
    cols[i].markdown(metric(row["Date"], f"{row['Temperature']}°"), unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown("""
<div class="footer">
    © 2025 Smart Weather Dashboard<br>
    Built with Python • Streamlit • OpenWeather API
</div>
""", unsafe_allow_html=True)
