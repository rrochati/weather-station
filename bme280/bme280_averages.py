import time
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280
from collections import deque
import statistics

class BME280Reader:
    def __init__(self, samples=5):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c)
        self.bme280.sea_level_pressure = 1013.25
        
        # Store recent readings for averaging
        self.samples = samples
        self.temp_readings = deque(maxlen=samples)
        self.humidity_readings = deque(maxlen=samples)
        self.pressure_readings = deque(maxlen=samples)
        self.altitude_readings = deque(maxlen=samples)
        
    def get_averaged_reading(self):
        # Take a reading
        temp = self.bme280.temperature
        humidity = self.bme280.humidity
        pressure = self.bme280.pressure
        altitude = self.bme280.altitude
        
        # Add to deques
        self.temp_readings.append(temp)
        self.humidity_readings.append(humidity)
        self.pressure_readings.append(pressure)
        self.altitude_readings.append(altitude)
        
        # Return averages if we have enough samples
        if len(self.temp_readings) >= self.samples:
            return {
                'temperature': statistics.mean(self.temp_readings),
                'humidity': statistics.mean(self.humidity_readings),
                'pressure': statistics.mean(self.pressure_readings),
                'altitude': statistics.mean(self.altitude_readings),
                'raw_temp': temp,
                'raw_pressure': pressure
            }
        else:
            return {
                'temperature': temp,
                'humidity': humidity,
                'pressure': pressure,
                'altitude': altitude,
                'raw_temp': temp,
                'raw_pressure': pressure
            }

try:
    print("Initializing BME280 with averaging...")
    sensor = BME280Reader(samples=10)  # Average over 10 readings
    
    print("Starting readings with 10-sample averaging...\n")
    
    while True:
        try:
            reading = sensor.get_averaged_reading()
            
            print(f"Temperature: {reading['temperature']:.2f} °C")
            print(f"Humidity: {reading['humidity']:.2f} %")
            print(f"Pressure: {reading['pressure']:.2f} hPa (raw: {reading['raw_pressure']:.2f})")
            print(f"Altitude: {reading['altitude']:.2f} m")
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
