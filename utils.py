import requests
import os

API_KEY = os.getenv("OPENWEATHER_API_KEY")

GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

TIMEOUT = 10


# -------------------------------------------------
# Get coordinates from City + Country
# -------------------------------------------------
def get_coordinates(city, country=None):
    query = f"{city},{country}" if country else city
    params = {
        "q": query,
        "limit": 1,
        "appid": API_KEY
    }

    try:
        res = requests.get(GEO_URL, params=params, timeout=TIMEOUT).json()
        if not res:
            return None

        return {
            "lat": res[0]["lat"],
            "lon": res[0]["lon"],
            "location": f'{res[0]["name"]}, {res[0]["country"]}'
        }
    except Exception:
        return None


# -------------------------------------------------
# Auto Detect Location using IP
# -------------------------------------------------
def detect_location_by_ip():
    try:
        data = requests.get("https://ipapi.co/json/", timeout=5).json()
        return {
            "lat": data.get("latitude"),
            "lon": data.get("longitude"),
            "label": f'{data.get("city")}, {data.get("country_code")}'
        }
    except Exception:
        return None


# -------------------------------------------------
# Weather using Coordinates
# -------------------------------------------------
def get_weather_by_coords(lat, lon, units="metric"):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": units
    }
    return requests.get(WEATHER_URL, params=params, timeout=TIMEOUT).json()


def get_forecast_by_coords(lat, lon, units="metric"):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": units
    }
    return requests.get(FORECAST_URL, params=params, timeout=TIMEOUT).json()


# -------------------------------------------------
# Weather Icons
# -------------------------------------------------
def weather_icon(condition):
    icons = {
        "Clear": "☀️",
        "Clouds": "☁️",
        "Rain": "🌧",
        "Drizzle": "🌦",
        "Thunderstorm": "⛈",
        "Snow": "❄️",
        "Mist": "🌫",
        "Haze": "🌫",
        "Fog": "🌁"
    }
    return icons.get(condition, "🌍")


# -------------------------------------------------
# Smart Weather Advice
# -------------------------------------------------
def weather_advice(temp, humidity=None, wind=None):
    advice = []

    if temp >= 38:
        advice.append("🔥 Extreme heat — stay hydrated.")
    elif temp >= 30:
        advice.append("🌞 Hot weather — drink more water.")
    elif temp <= 8:
        advice.append("❄ Very cold — wear warm clothes.")
    else:
        advice.append("🌤 Pleasant weather.")

    if humidity and humidity >= 80:
        advice.append("💧 High humidity.")

    if wind and wind >= 10:
        advice.append("🌬 Strong winds.")

    return " ".join(advice)
