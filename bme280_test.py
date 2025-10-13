import time
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280

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
            
            print(f"Temperature: {temperature:.2f} °C")
            print(f"Humidity: {humidity:.2f} %")
            print(f"Pressure: {pressure:.2f} hPa")
            print(f"Altitude: {altitude:.2f} m")
            print("------")
            time.sleep(2)
            
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
