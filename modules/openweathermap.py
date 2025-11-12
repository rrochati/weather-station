import time
import sys, os
import logging
import requests

LOG_FILE=os.getenv('LOG_FILE', '/home/rrocha/logs/weather_station.log')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),  # This ensures output goes to stdout
        logging.FileHandler(LOG_FILE, mode='a') # Send logs to file
    ]
)
logger = logging.getLogger(__name__)

def get_current_sea_level_pressure(api_key, lat, lon):
    """Get current sea level pressure from OpenWeatherMap API"""
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    try:
        response = requests.get(url, timeout=20)
        data = response.json()
        # Pressure is in hPa
        return data['main']['sea_level'] if 'sea_level' in data['main'] else data['main']['pressure']
    except Exception as e:
        print(f"Error fetching sea level pressure: {e}")
        logger.error(f"Error fetching sea level pressure: {e}")
        return 1013.25  # Fallback to standard pressure

def get_detailed_weather_data(api_key, lat, lon):
    """Get comprehensive weather data from OpenWeatherMap API"""
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"

    try:
        response = requests.get(url, timeout=20)
        data = response.json()

        weather_info = {
            'location': data['name'],
            'country': data['sys']['country'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'sea_level_pressure': data['main'].get('sea_level', data['main']['pressure']),
            'ground_level_pressure': data['main'].get('grnd_level', data['main']['pressure']),
            'visibility': data.get('visibility', 0) / 1000,  # Convert to km
            'wind_speed': data['wind']['speed'],
            'wind_direction': data['wind'].get('deg', 0),
            'cloudiness': data['clouds']['all'],
            'weather_description': data['weather'][0]['description'],
            'sunrise': time.ctime(data['sys']['sunrise']),
            'sunset': time.ctime(data['sys']['sunset']),
            'timezone_offset': data['timezone'] / 3600  # Convert to hours
        }

        return weather_info

    except Exception as e:
        print(f"Error fetching weather data: {e}")
        logger.error(f"Error fetching weather data: {e}")
        return None

def get_air_quality(api_key, lat, lon):
    """Get air quality index and pollutant levels"""
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"

    try:
        response = requests.get(url, timeout=20)
        data = response.json()

        aqi_levels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}

        return {
            'air_quality_index': aqi_levels[data['list'][0]['main']['aqi']],
            'co': data['list'][0]['components']['co'],
            'no2': data['list'][0]['components']['no2'],
            'o3': data['list'][0]['components']['o3'],
            'pm2_5': data['list'][0]['components']['pm2_5'],
            'pm10': data['list'][0]['components']['pm10']
        }

    except Exception as e:
        print(f"Error fetching air quality data: {e}")
        logger.error(f"Error fetching air quality data: {e}")
        return None

def print_detailed_weather_data(weather):
    print("=== LOCATION INFO ===")
    print(f"Location: {weather['location']}, {weather['country']}")
    print(f"Timezone offset: {weather['timezone_offset']:.1f} hours from UTC")

    print("\n=== TEMPERATURE ===")
    print(f"Temperature: {weather['temperature']:.1f}°C")
    print(f"Feels like: {weather['feels_like']:.1f}°C")

    print("\n=== PRESSURE & ALTITUDE ===")
    print(f"Sea level pressure: {weather['sea_level_pressure']:.2f} hPa")
    print(f"Ground level pressure: {weather['ground_level_pressure']:.2f} hPa")

    print("\n=== HUMIDITY ===")
    print(f"API Humidity: {weather['humidity']}%")

    print("\n=== WEATHER CONDITIONS ===")
    print(f"Description: {weather['weather_description'].title()}")
    print(f"Cloudiness: {weather['cloudiness']}%")
    print(f"Visibility: {weather['visibility']:.1f} km")

    print("\n=== WIND ===")
    print(f"Wind Speed: {weather['wind_speed']:.1f} m/s")
    print(f"Wind Direction: {weather['wind_direction']}°")

    print("\n=== SUN TIMES ===")
    print(f"Sunrise: {weather['sunrise']}")
    print(f"Sunset: {weather['sunset']}")

    print("------")

def print_air_quality(air_quality):
    print("\n=== Air Quality ===")
    print(f"Air Quality Index: {air_quality['air_quality_index']}")
    print(f"CO: {air_quality['co']}")
    print(f"NO2: {air_quality['no2']}")
    print(f"O3: {air_quality['o3']}")
    print(f"pm2.5: {air_quality['pm2_5']}")
    print(f"pm10: {air_quality['pm10']}")
    print("------")
