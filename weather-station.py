import time
import csv
from datetime import datetime
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280

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
    
    # Optional: set sea level pressure for accurate altitude
    bme280.sea_level_pressure = 1013.25
    
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
            
            print(f"Temperature: {temperature:.2f} °C")
            print(f"Humidity: {humidity:.2f} %")
            print(f"Pressure: {pressure:.2f} hPa")
            print(f"Altitude: {altitude:.2f} m")
            print("------")
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

