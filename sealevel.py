import requests
import board
from adafruit_bme280 import basic as adafruit_bme280
import time
import busio

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

# Setup sensor
#i2c = board.I2C()
i2c = busio.I2C(board.SCL, board.SDA)
#bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# Your location coordinates
latitude = 38.683822  # Replace with your latitude
longitude = -9.149931  # Replace with your longitude
api_key = "12a5ff2b1dcb41f0d1ee2c301244ad6d"  # Get free API key from OpenWeatherMap

# Update sea level pressure
current_slp = get_current_sea_level_pressure(api_key, latitude, longitude)
bme280.sea_level_pressure = current_slp

while True:
    try:
        bme280.sea_level_pressure = current_slp
        print(f"Current sea level pressure: {current_slp:.4f} hPa")
        print(f"Pressure: {bme280.pressure:.4f} hPa") 
        print(f"Altitude: {bme280.altitude:.4f} meters")
        time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping readings...")
        break
    except Exception as e:
        print(f"Error reading sensor: {e}")
        time.sleep(1)
