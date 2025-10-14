import time
import csv
from datetime import datetime
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280
from libs.openweathermap import *

# Your location coordinates
latitude = 38.683822  # Replace with your latitude
longitude = -9.149931  # Replace with your longitude
api_key = "12a5ff2b1dcb41f0d1ee2c301244ad6d"  # API key from OpenWeatherMap

current_slp = get_current_sea_level_pressure(api_key, latitude, longitude)
weather = get_detailed_weather_data(api_key, latitude, longitude)
air_quality = get_air_quality(api_key, latitude, longitude)

# CSV file setup
CSV_FILE = "../weather_log.csv"

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
            with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, temperature, humidity, pressure, round(altitude, 1)])
                #writer.writerow([timestamp, temperature, humidity, pressure,
                #                speed, direction, v, rain, altitude])
            
            if weather:
                print_detailed_weather_data(weather)
            
            if air_quality:
                print_air_quality(air_quality)

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
