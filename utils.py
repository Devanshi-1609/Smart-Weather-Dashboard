import requests
import os

# -------------------------------------------------
# Load Environment Variables
# -------------------------------------------------

API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
BASE_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"

TIMEOUT = 10  # seconds

# -------------------------------------------------
# Internal helper for API calls
# -------------------------------------------------
def _call_api(url, params):
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
        return response.json()
    except requests.exceptions.Timeout:
        return {"cod": 408, "message": "Request timeout"}
    except requests.exceptions.ConnectionError:
        return {"cod": 503, "message": "Network connection error"}
    except requests.exceptions.RequestException as e:
        return {"cod": 500, "message": str(e)}

# -------------------------------------------------
# Current Weather
# -------------------------------------------------
def get_weather(city, units="metric"):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": units
    }
    return _call_api(BASE_WEATHER_URL, params)

# -------------------------------------------------
# 5-Day Forecast
# -------------------------------------------------
def get_forecast(city, units="metric"):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": units
    }
    return _call_api(BASE_FORECAST_URL, params)

# -------------------------------------------------
# Geo API – Get State & Country from City
# -------------------------------------------------
def get_location_details(city, country=None):
    """
    Uses OpenWeather Geo API to fetch latitude, longitude, state, country
    """
    query = city if not country else f"{city},{country}"
    params = {
        "q": query,
        "limit": 1,
        "appid": API_KEY
    }

    try:
        response = requests.get(GEO_URL, params=params, timeout=TIMEOUT)
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            return {
                "lat": data[0].get("lat"),
                "lon": data[0].get("lon"),
                "state": data[0].get("state"),
                "country": data[0].get("country")
            }
    except Exception:
        pass

    return None

# -------------------------------------------------
# Auto Detect Location using IP
# -------------------------------------------------
def detect_location_by_ip():
    """
    Detects user's city, state, country using IP
    """
    try:
        response = requests.get("https://ipapi.co/json/", timeout=5)
        data = response.json()

        return {
            "city": data.get("city"),
            "state": data.get("region_code"),
            "country": data.get("country_code")
        }
    except Exception:
        return None

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
        "Fog": "🌁",
        "Smoke": "💨",
        "Dust": "🌪",
        "Sand": "🌪",
        "Ash": "🌋",
        "Squall": "💨",
        "Tornado": "🌪"
    }
    return icons.get(condition, "🌍")

# -------------------------------------------------
# Smart Weather Advice
# -------------------------------------------------
def weather_advice(temp, humidity=None, wind=None):
    advice = []

    if temp is not None:
        if temp >= 38:
            advice.append("🔥 Extreme heat — stay hydrated and avoid going out.")
        elif temp >= 30:
            advice.append("🌞 Hot weather — drink plenty of water.")
        elif temp <= 8:
            advice.append("❄ Very cold — wear warm clothes.")
        elif temp <= 15:
            advice.append("🧥 Cool weather — light jacket recommended.")
        else:
            advice.append("🌤 Pleasant temperature.")

    if humidity is not None:
        if humidity >= 80:
            advice.append("💧 High humidity — you may feel sticky.")
        elif humidity <= 30:
            advice.append("🏜 Low humidity — keep your skin hydrated.")

    if wind is not None and wind >= 10:
        advice.append("🌬 Strong winds — be cautious outdoors.")

    return " ".join(advice)
