import time
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280
from collections import deque
import statistics
import json
import os

class FlexibleBME280Reader:
    def __init__(self, samples=10, floor_level=16, floor_height=2.8, pole_height=0, building_ground_altitude=0, config_file="sensor_config.json"):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c)
        
        # Configuration parameters
        self.config_file = config_file
        self.floor_level = floor_level
        self.floor_height = floor_height  # Your 2.8m floor height
        self.pole_height = pole_height   # Additional height from pole/mounting
        self.building_ground_altitude = building_ground_altitude
        
        # Calculate total altitude above ground and sea level
        self.floor_altitude_above_ground = floor_level * floor_height
        self.total_altitude_above_ground = self.floor_altitude_above_ground + pole_height
        self.total_altitude_above_sea_level = building_ground_altitude + self.total_altitude_above_ground
        
        # Load or create configuration
        self.load_or_create_config()
        
        # Calibration
        self.calculated_sea_level_pressure = None
        
        # Store recent readings for averaging
        self.samples = samples
        self.temp_readings = deque(maxlen=samples)
        self.humidity_readings = deque(maxlen=samples)
        self.pressure_readings = deque(maxlen=samples)
    
    def load_or_create_config(self):
        """Load existing configuration or create new one"""
        config = {
            'floor_level': self.floor_level,
            'floor_height': self.floor_height,
            'pole_height': self.pole_height,
            'building_ground_altitude': self.building_ground_altitude,
            'total_altitude_above_ground': self.total_altitude_above_ground,
            'total_altitude_above_sea_level': self.total_altitude_above_sea_level,
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save configuration
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"📝 Configuration saved to {self.config_file}")
    
    def update_pole_height(self, new_pole_height):
        """Update pole height when sensor is moved"""
        self.pole_height = new_pole_height
        self.total_altitude_above_ground = self.floor_altitude_above_ground + new_pole_height
        self.total_altitude_above_sea_level = self.building_ground_altitude + self.total_altitude_above_ground
        
        # Update configuration file
        self.load_or_create_config()
        
        # Recalibrate
        print(f"🔄 Updated pole height to {new_pole_height}m")
        print(f"📏 New total height above ground: {self.total_altitude_above_ground:.1f}m")
        
    def calibrate_sea_level_pressure(self, current_pressure):
        """Calculate sea level pressure based on known altitude"""
        # Pressure increases by ~12 hPa per 100m as you go down
        pressure_correction = (self.total_altitude_above_sea_level / 100) * 12
        self.calculated_sea_level_pressure = current_pressure + pressure_correction
        self.bme280.sea_level_pressure = self.calculated_sea_level_pressure
        
        print(f"🏢 Sensor Location Info:")
        print(f"   Floor: {self.floor_level} (@ {self.floor_height}m per floor)")
        print(f"   Floor height above ground: {self.floor_altitude_above_ground:.1f}m")
        print(f"   Additional pole height: {self.pole_height:.1f}m")
        print(f"   📏 Total height above ground: {self.total_altitude_above_ground:.1f}m")
        print(f"   🌍 Total altitude above sea level: {self.total_altitude_above_sea_level:.1f}m")
        print(f"   🌊 Calculated sea level pressure: {self.calculated_sea_level_pressure:.2f} hPa")
        print()
        
    def get_reading(self):
        """Get averaged sensor readings"""
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
            'expected_height_above_ground': self.total_altitude_above_ground,
            'raw_pressure': pressure,
            'sea_level_pressure': self.calculated_sea_level_pressure or self.bme280.sea_level_pressure,
            'pole_height': self.pole_height
        }

def interactive_setup():
    """Interactive setup for sensor configuration"""
    print("🔧 BME280 Sensor Setup")
    print("=" * 40)
    
    # Get current configuration
    floor = int(input("Enter floor level (default 16): ") or "16")
    floor_height = float(input("Enter floor height in meters (default 2.8): ") or "2.8")
    pole_height = float(input("Enter pole/mounting height in meters (default 0): ") or "0")
    building_altitude = float(input("Enter building ground altitude above sea level (default 0): ") or "0")
    
    print(f"\n📍 Configuration Summary:")
    print(f"   Floor: {floor}")
    print(f"   Floor height: {floor_height}m")
    print(f"   Pole height: {pole_height}m")
    print(f"   Building ground altitude: {building_altitude}m")
    print(f"   Total sensor height: {(floor * floor_height) + pole_height:.1f}m above ground")
    
    confirm = input("\nIs this correct? (y/n): ").lower().strip()
    if confirm != 'y':
        print("Setup cancelled.")
        return None
    
    return {
        'floor_level': floor,
        'floor_height': floor_height,
        'pole_height': pole_height,
        'building_ground_altitude': building_altitude
    }

def main():
    print("🌡️ Flexible BME280 Reader")
    print("=" * 40)
    
    # Check if we want to reconfigure
    if os.path.exists("sensor_config.json"):
        reconfigure = input("Configuration exists. Reconfigure? (y/n): ").lower().strip()
        if reconfigure == 'y':
            config = interactive_setup()
            if not config:
                return
        else:
            # Use existing configuration
            with open("sensor_config.json", 'r') as f:
                saved_config = json.load(f)
            config = {
                'floor_level': saved_config['floor_level'],
                'floor_height': saved_config['floor_height'],
                'pole_height': saved_config['pole_height'],
                'building_ground_altitude': saved_config['building_ground_altitude']
            }
    else:
        config = interactive_setup()
        if not config:
            return
    
    try:
        # Initialize sensor with configuration
        sensor = FlexibleBME280Reader(
            samples=10,
            floor_level=config['floor_level'],
            floor_height=config['floor_height'],
            pole_height=config['pole_height'],
            building_ground_altitude=config['building_ground_altitude']
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
                print(f"🏢 Measured height above ground: {reading['altitude_above_ground']:.1f} m")
                print(f"📏 Expected height above ground: {reading['expected_height_above_ground']:.1f} m")
                if reading['pole_height'] > 0:
                    print(f"🎯 Pole height: {reading['pole_height']:.1f} m")
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

if __name__ == "__main__":
    main()
