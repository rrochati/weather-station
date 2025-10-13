import time
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280
from collections import deque
import statistics

class CalibratedBME280Reader:
    def __init__(self, samples=10, floor_level=16, building_ground_altitude=0):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c)
        
        # Calibration parameters
        self.floor_level = floor_level
        self.meters_per_floor = 2.8  # My floor height
        self.actual_altitude_above_ground = floor_level * self.meters_per_floor
        self.building_ground_altitude = building_ground_altitude  # Above sea level
        self.actual_altitude_above_sea_level = building_ground_altitude + self.actual_altitude_above_ground
        
        # Calculate what sea level pressure should be based on your actual altitude
        # Pressure drops ~12 hPa per 100m
        self.calculated_sea_level_pressure = None
        
        # Store recent readings for averaging
        self.samples = samples
        self.temp_readings = deque(maxlen=samples)
        self.humidity_readings = deque(maxlen=samples)
        self.pressure_readings = deque(maxlen=samples)
        
    def calibrate_sea_level_pressure(self, current_pressure):
        """Calculate sea level pressure based on known altitude"""
        # Pressure increases by ~12 hPa per 100m as you go down
        pressure_correction = (self.actual_altitude_above_sea_level / 100) * 12
        self.calculated_sea_level_pressure = current_pressure + pressure_correction
        self.bme280.sea_level_pressure = self.calculated_sea_level_pressure
        
        print(f"🏢 Building info:")
        print(f"   Floor: {self.floor_level}")
        print(f"   Estimated height above ground: {self.actual_altitude_above_ground:.1f}m")
        print(f"   Estimated altitude above sea level: {self.actual_altitude_above_sea_level:.1f}m")
        print(f"   Calculated sea level pressure: {self.calculated_sea_level_pressure:.2f} hPa")
        print()
        
    def get_reading(self):
        # Take readings
        temp = self.bme280.temperature
        humidity = self.bme280.humidity
        pressure = self.bme280.pressure
        altitude = self.bme280.altitude
        
        # Add to deques for averaging
        self.temp_readings.append(temp)
        self.humidity_readings.append(humidity)
        self.pressure_readings.append(pressure)
        
        # Calculate averages if we have enough samples
        if len(self.temp_readings) >= self.samples:
            avg_temp = statistics.mean(self.temp_readings)
            avg_humidity = statistics.mean(self.humidity_readings)
            avg_pressure = statistics.mean(self.pressure_readings)
        else:
            avg_temp = temp
            avg_humidity = humidity
            avg_pressure = pressure
            
        # Calculate relative altitude (height above ground)
        relative_altitude = altitude - self.building_ground_altitude if self.calculated_sea_level_pressure else altitude
        
        return {
            'temperature': avg_temp,
            'humidity': avg_humidity,
            'pressure': avg_pressure,
            'altitude_above_sea_level': altitude,
            'altitude_above_ground': relative_altitude,
            'raw_pressure': pressure,
            'sea_level_pressure': self.calculated_sea_level_pressure or self.bme280.sea_level_pressure
        }

try:
    print("🌡️ Initializing BME280 for 16th floor readings...")
    
    # Initialize sensor (adjust building_ground_altitude if you know your city's elevation)
    sensor = CalibratedBME280Reader(
        samples=10, 
        floor_level=16,
        building_ground_altitude=0  # Change this if you know your city's elevation above sea level
    )
    
    print("📊 Taking initial readings for calibration...")
    
    # Take a few readings to calibrate
    initial_readings = []
    for i in range(5):
        temp = sensor.bme280.temperature
        pressure = sensor.bme280.pressure
        initial_readings.append(pressure)
        time.sleep(1)
    
    avg_initial_pressure = statistics.mean(initial_readings)
    sensor.calibrate_sea_level_pressure(avg_initial_pressure)
    
    print("🚀 Starting calibrated readings...\n")
    
    while True:
        try:
            reading = sensor.get_reading()
            
            print(f"🌡️  Temperature: {reading['temperature']:.2f} °C")
            print(f"💧 Humidity: {reading['humidity']:.2f} %")
            print(f"🌊 Pressure: {reading['pressure']:.2f} hPa (raw: {reading['raw_pressure']:.2f})")
            print(f"🏔️  Altitude above sea level: {reading['altitude_above_sea_level']:.1f} m")
            print(f"🏢 Height above ground: {reading['altitude_above_ground']:.1f} m")
            print(f"🌍 Sea level pressure: {reading['sea_level_pressure']:.2f} hPa")
            print("------")
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n⏹️ Stopping readings...")
            break
        except Exception as e:
            print(f"❌ Error reading sensor: {e}")
            time.sleep(1)

except Exception as e:
    print(f"❌ Error initializing BME280: {e}")
