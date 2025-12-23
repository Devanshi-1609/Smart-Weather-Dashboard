import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils import (
    get_weather,
    get_forecast,
    weather_icon,
    weather_advice,
    get_location_details,
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

# Session defaults
if "city" not in st.session_state:
    st.session_state.city = "Ahmedabad"
    st.session_state.state = ""
    st.session_state.country = "IN"

# Auto-detect button
if st.sidebar.button("📡 Auto Detect My Location"):
    detected = detect_location_by_ip()
    if detected:
        st.session_state.city = detected.get("city", "")
        st.session_state.state = detected.get("state", "")
        st.session_state.country = detected.get("country", "")
        st.sidebar.success("Location detected!")
    else:
        st.sidebar.error("Unable to detect location.")

city = st.sidebar.text_input("City", st.session_state.city)
state = st.sidebar.text_input("State Code (optional)", st.session_state.state)
country = st.sidebar.text_input("Country Code", st.session_state.country)

st.sidebar.caption("Example: Ahmedabad, GJ, IN")

unit = st.sidebar.radio("Temperature Unit", ["Celsius", "Fahrenheit"])
units = "metric" if unit == "Celsius" else "imperial"

# -------------------------------------------------
# Build Location Query
# -------------------------------------------------
location_parts = [city]
if state:
    location_parts.append(state)
if country:
    location_parts.append(country)

query = ",".join(location_parts)

# -------------------------------------------------
# Search History
# -------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------------------------------
# Fetch Weather
# -------------------------------------------------
weather = get_weather(query, units)

if weather.get("cod") != 200:
    st.error("❌ City not found or API error.")
    st.stop()

forecast = get_forecast(query, units)

# Save history
location_label = f"{city}, {state}, {country}".strip(", ")
if location_label not in st.session_state.history:
    st.session_state.history.append(location_label)
    st.session_state.history = st.session_state.history[-5:]

# -------------------------------------------------
# Resolve State & Country via Geo API
# -------------------------------------------------
geo = get_location_details(city, country)

if geo:
    st.caption(f"📍 Detected Location: {geo.get('state', '')}, {geo.get('country', '')}")

# -------------------------------------------------
# Current Weather
# -------------------------------------------------
condition = weather["weather"][0]["main"]
icon = weather_icon(condition)

temp = weather["main"]["temp"]
feels_like = weather["main"]["feels_like"]
temp_min = weather["main"]["temp_min"]
temp_max = weather["main"]["temp_max"]
humidity = weather["main"]["humidity"]
pressure = weather["main"]["pressure"]
wind = weather["wind"]["speed"]

st.markdown("<div class='weather-card'>", unsafe_allow_html=True)
st.subheader(f"{icon} Current Weather in {city.title()}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("🌡 Temperature", f"{temp}°")
col2.metric("🤗 Feels Like", f"{feels_like}°")
col3.metric("💧 Humidity", f"{humidity}%")
col4.metric("🌬 Wind", f"{wind} m/s")

st.write(f"🔻 Min: {temp_min}° | 🔺 Max: {temp_max}° | 🌡 Pressure: {pressure} hPa")
st.info(weather_advice(temp, humidity, wind))
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Forecast Chart
# -------------------------------------------------
st.markdown("<div class='weather-card'>", unsafe_allow_html=True)
st.subheader("📈 5-Day Temperature Forecast")

dates = [item["dt_txt"] for item in forecast["list"]]
temps = [item["main"]["temp"] for item in forecast["list"]]

df = pd.DataFrame({"Date": dates, "Temperature": temps})

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["Date"], df["Temperature"], linewidth=2)
ax.set_xlabel("Date")
ax.set_ylabel("Temperature")
ax.set_title("Temperature Trend")
ax.tick_params(axis="x", rotation=45)
ax.grid(alpha=0.3)

st.pyplot(fig)
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Recent Searches
# -------------------------------------------------
st.markdown("<div class='weather-card'>", unsafe_allow_html=True)
st.subheader("🕒 Recent Searches")

for c in st.session_state.history:
    st.write("•", c)

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
