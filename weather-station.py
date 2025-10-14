import time
import csv
from datetime import datetime
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280
import requests


def get_current_sea_level_pressure(api_key, lat, lon):
    """Get current sea level pressure from OpenWeatherMap API"""
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        # Pressure is in hPa
        return data['main']['sea_level'] if 'sea_level' in data['main'] else data['main']['pressure']
    except:
        return 1013.25  # Fallback to standard pressure

def get_detailed_weather_data(api_key, lat, lon):
    """Get comprehensive weather data from OpenWeatherMap API"""
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
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
        return None

def get_air_quality(api_key, lat, lon):
    """Get air quality index and pollutant levels"""
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    
    try:
        response = requests.get(url)
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
        return None

# Your location coordinates
latitude = 38.683822  # Replace with your latitude
longitude = -9.149931  # Replace with your longitude
api_key = "12a5ff2b1dcb41f0d1ee2c301244ad6d"  # API key from OpenWeatherMap

current_slp = get_current_sea_level_pressure(api_key, latitude, longitude)
weather = get_detailed_weather_data(api_key, latitude, longitude)
air_quality = get_air_quality(api_key, latitude, longitude)

# CSV file setup
CSV_FILE = "weather_log.csv"

# Initialize file with headers (if new)
with open(CSV_FILE, "a", newline="") as f:
    writer = csv.writer(f)
    if f.tell() == 0:  # file empty
        writer.writerow([
            "timestamp", "temperature_C", "humidity_%", "pressure_hPa",
            "altitude", 
            "wind_speed_m_s", "wind_dir_deg", "wind_vane_voltage_V",
            "rain_interval_mm"
        ])

try:
    # I2C setup
    print("Initializing I2C...")
    i2c = busio.I2C(board.SCL, board.SDA)
    
    print("Connecting to BME280...")
    # Correct class name for the newer library version
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    
    # Update sea level pressure
    bme280.sea_level_pressure = current_slp
    
    print(f"Current sea level pressure: {current_slp:.4f} hPa")
    
    print("BME280 initialized successfully!")
    print("Starting readings...\n")
    
    while True:
        try:
            temperature = bme280.temperature
            humidity = bme280.humidity
            pressure = bme280.pressure
            altitude = bme280.altitude
            
            # Write to CSV
            timestamp = datetime.now().isoformat(timespec='seconds')
            with open(CSV_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, temperature, humidity, pressure, altitude])
                #writer.writerow([timestamp, temperature, humidity, pressure,
                #                speed, direction, v, rain, altitude])
            
            if weather:
                print("=== LOCATION INFO ===")
                print(f"Location: {weather['location']}, {weather['country']}")
                print(f"Timezone offset: {weather['timezone_offset']:.1f} hours from UTC")
                
                print("\n=== TEMPERATURE ===")
                print(f"Temperature: {weather['temperature']:.1f}°C")
                print(f"Feels like: {weather['feels_like']:.1f}°C")
                print(f"BME280 Temperature: {bme280.temperature:.1f}°C")
                
                print("\n=== PRESSURE & ALTITUDE ===")
                print(f"Sea level pressure: {weather['sea_level_pressure']:.2f} hPa")
                print(f"Ground level pressure: {weather['ground_level_pressure']:.2f} hPa")
                print(f"BME280 Pressure: {bme280.pressure:.2f} hPa")
                
                # Set accurate sea level pressure for altitude calculation
                print(f"Corrected Altitude: {bme280.altitude:.2f} meters")
    
                print("\n=== HUMIDITY ===")
                print(f"API Humidity: {weather['humidity']}%")
                print(f"BME280 Humidity: {bme280.relative_humidity:.1f}%")
                
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
            
                print(f"Temperature: {temperature:.2f} °C")
                print(f"Humidity: {humidity:.2f} %")
                print(f"Pressure: {pressure:.4f} hPa")
                print(f"Altitude: {altitude:.0f} m")
                print("------")
            
            if air_quality:
                print("\n=== Air Quality ===")
                print(f"Air Quality Index: {air_quality['air_quality_index']}")
                print(f"CO: {air_quality['co']}")
                print(f"NO2: {air_quality['no2']}")
                print(f"O3: {air_quality['o3']}%")
                print(f"pm2.5: {air_quality['pm2_5']}")
                print(f"pm10: {air_quality['pm10']}%")
            
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\nStopping readings...")
            break
        except Exception as e:
            print(f"Error reading sensor: {e}")
            time.sleep(1)

except Exception as e:
    print(f"Error initializing BME280: {e}")
    print("\nTroubleshooting tips:")
    print("1. Check I2C wiring")
    print("2. Run 'i2cdetect -y 1' to verify sensor is detected")
    print("3. Make sure I2C is enabled in raspi-config")

