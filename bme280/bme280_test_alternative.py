import time
import board
import busio
import adafruit_bme280.basic as bme280

try:
    # I2C setup
    print("Initializing I2C...")
    i2c = busio.I2C(board.SCL, board.SDA)
    
    print("Connecting to BME280...")
    sensor = bme280.Adafruit_BME280_I2C(i2c)
    
    print("BME280 initialized successfully!")
    print("Starting readings...\n")
    
    while True:
        try:
            print(f"Temperature: {sensor.temperature:.2f} °C")
            print(f"Humidity: {sensor.humidity:.2f} %")
            print(f"Pressure: {sensor.pressure:.2f} hPa")
            print(f"Altitude: {sensor.altitude:.2f} m")
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
