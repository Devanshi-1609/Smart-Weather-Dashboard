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
# Custom CSS
# -------------------------------------------------
st.markdown("""
<style>
.main { background-color: #0f1117; }
.weather-card {
    background: #1c1f26;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}
.title-text { font-size: 36px; font-weight: bold; }
.subtitle { color: #b0b0b0; }
.footer {
    text-align: center;
    color: gray;
    margin-top: 40px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown("<div class='title-text'>🌦 Smart Weather Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Auto location detection with 5-day forecast</div>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------------------------------
# Sidebar – Location Controls
# -------------------------------------------------
st.sidebar.header("📍 Location")

if "location" not in st.session_state:
    st.session_state.location = None

# Auto detect
if st.sidebar.button("📡 Auto Detect My Location"):
    detected = detect_location_by_ip()
    if detected:
        st.session_state.location = detected
        st.sidebar.success("Location detected!")
    else:
        st.sidebar.error("Unable to detect location.")

city = st.sidebar.text_input("City", "Ahmedabad")
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
        st.error("❌ Location not found. Please check city/country.")
        st.stop()
    lat = coords["lat"]
    lon = coords["lon"]
    location_label = coords["location"]

# -------------------------------------------------
# Fetch Weather (USING COORDS)
# -------------------------------------------------
weather = get_weather_by_coords(lat, lon, units)
forecast = get_forecast_by_coords(lat, lon, units)

# -------------------------------------------------
# Current Weather
# -------------------------------------------------
# -------------------------------------------------
# Validate API Response
# -------------------------------------------------
if "weather" not in weather or "main" not in weather:
    st.error("⚠ Unable to fetch weather data right now. Please try again.")
    st.stop()

condition = weather["weather"][0]["main"]
icon = weather_icon(condition)

temp = weather["main"]["temp"]
feels_like = weather["main"]["feels_like"]
humidity = weather["main"]["humidity"]
wind = weather["wind"]["speed"]

st.markdown("<div class='weather-card'>", unsafe_allow_html=True)
st.subheader(f"{icon} Current Weather in {location_label}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("🌡 Temperature", f"{temp}°")
col2.metric("🤗 Feels Like", f"{feels_like}°")
col3.metric("💧 Humidity", f"{humidity}%")
col4.metric("🌬 Wind", f"{wind} m/s")

st.info(weather_advice(temp, humidity, wind))
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# 5-Day Forecast (Daily)
# -------------------------------------------------
st.markdown("<div class='weather-card'>", unsafe_allow_html=True)
st.subheader("📅 5-Day Temperature Forecast")

daily_forecast = {}

for item in forecast["list"]:
    date = item["dt_txt"].split(" ")[0]
    time = item["dt_txt"].split(" ")[1]

    # Pick midday forecast for each day
    if time == "12:00:00" and date not in daily_forecast:
        daily_forecast[date] = item["main"]["temp"]

# Convert to DataFrame
df = pd.DataFrame({
    "Date": list(daily_forecast.keys()),
    "Temperature": list(daily_forecast.values())
})

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["Date"], df["Temperature"], marker="o", linewidth=2)
ax.set_xlabel("Date")
ax.set_ylabel("Temperature")
ax.set_title("Next 5 Days Forecast")
ax.grid(alpha=0.3)

st.pyplot(fig)
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown("""
<div class="footer">
    Built with ❤️ using Python & Streamlit<br>
    Smart Weather Dashboard
</div>
""", unsafe_allow_html=True)
