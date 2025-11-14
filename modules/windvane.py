#!/usr/bin/env python3
"""
Wind Vane Test Module for SparkFun Weather Kit
Tests the voltage divider circuit and direction mapping

Hardware Requirements:
- Raspberry Pi 5
- DFR0553 (ADS1115) module connected via I2C
- Wind vane connected to A0 with 10kΩ voltage divider
- 100nF filter capacitor
"""

import time
import board
import busio
import os
import sys
import logging
try:
    # Try newer CircuitPython library first
    from adafruit_ads1x15.ads1115 import ADS1115
    from adafruit_ads1x15.analog_in import AnalogIn
    USE_CIRCUITPYTHON = True
except ImportError:
    # Fall back to older library
    import Adafruit_ADS1x15
    USE_CIRCUITPYTHON = False


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


# -------------------------------------------------
# Configuration
# -------------------------------------------------

# Voltage tolerance for direction matching (volts)
TOLERANCE = 0.05

# Wind direction mapping based on your actual hardware calibration
# Custom calibrated values from your SparkFun Weather Kit + 10kΩ voltage divider
# Note: Some adjacent directions have identical voltages - hardware limitation
VOLTAGE_TO_DIR = {
    0.252: 202.5,  # SSW
    0.254: 180.0,  # S
    0.441: 225.0,  # SW
    0.602: 247.5,  # WSW (Note: very close voltage voltage to SW)
    0.763: 270.0,  # W
    1.043: 292.5,  # WNW (Note: very close voltage voltage to W)
    1.260: 135.0,  # SE
    1.261: 157.5,  # SSE
    1.802: 315.0,  # NW
    1.974: 337.5,  # NNW
    2.255: 67.5,   # ENE
    2.356: 90.0,   # E
    2.437: 112.5,  # ESE (Note: very close voltage to E)
    2.681: 45.0,   # NE
    2.858: 22.5,   # NNE
    2.973: 0.0,    # N
}

# Direction names for easy reading
DIR_NAMES = {
    0.0: "N", 22.5: "NNE", 45.0: "NE", 67.5: "ENE",
    90.0: "E", 112.5: "ESE", 135.0: "SE", 157.5: "SSE",
    180.0: "S", 202.5: "SSW", 225.0: "SW", 247.5: "WSW",
    270.0: "W", 292.5: "WNW", 315.0: "NW", 337.5: "NNW"
}

class WindVane:
    def __init__(self, tolerance: float = TOLERANCE, voltage_to_dir: dict = VOLTAGE_TO_DIR, dir_names: dict = DIR_NAMES):
        self.tolerance = tolerance
        self.voltage_to_dir = voltage_to_dir
        self.dir_names = dir_names
        self.wind_vane = None
        self.ads = None

    def setup_ads1115(self):
        """Initialize ADS1115 for wind vane readings"""
        try:
            logger.info("🔧 Setting up I2C and ADS1115...")
            
            if USE_CIRCUITPYTHON:
                # I2C setup
                i2c = busio.I2C(board.SCL, board.SDA)
                
                # ADS1115 setup
                self.ads = ADS1115(i2c)
                self.ads.gain = 1  # ±4.096V range (suitable for 3.3V system)
                
                # Wind vane on A0 (channel 0)
                self.wind_vane = AnalogIn(self.ads, 0)  # Channel 0 = A0
                
                logger.info("✅ ADS1115 initialized successfully (CircuitPython)")
                logger.info(f"✅ Wind vane connected to A0")
                logger.info(f"✅ Voltage range: ±4.096V")
                
            else:
                # Older library setup
                self.ads = Adafruit_ADS1x15.ADS1115()
                self.wind_vane = self.ads
                
                logger.info("✅ ADS1115 initialized successfully (Legacy)")
                logger.info(f"✅ Wind vane connected to A0")
                logger.info(f"✅ Voltage range: ±4.096V")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up ADS1115: {e}")
            return False

    def read_wind_direction(self):
        """
        Read voltage and convert to compass direction
        """
        try:
            # Check if ADS1115 is initialized
            if self.wind_vane is None:
                logger.warning("ADS1115 not initialized. Call setup_ads1115() first.")
                return None, None, None, None, None
                
            # Read voltage
            if USE_CIRCUITPYTHON:
                voltage = self.wind_vane.voltage
            else:
                # Channel 0, gain=1 (±4.096V), sample rate=860 samples/second
                raw_value = self.wind_vane.read_adc(0, gain=1)
                # Convert to voltage (16-bit ADC with ±4.096V range)
                voltage = raw_value * 4.096 / 32767.0
            
            # Find closest voltage match
            closest_voltage = min(self.voltage_to_dir.keys(), key=lambda x: abs(x - voltage))
            voltage_diff = abs(closest_voltage - voltage)
            
            if voltage_diff <= self.tolerance:
                direction = self.voltage_to_dir[closest_voltage]
                direction_name = self.dir_names.get(direction, f"{direction}°")
                confidence = "HIGH"
                logger.info(f"Wind Vane Reading: {voltage:.3f} V -> {direction_name} ({confidence} confidence)")
            else:
                # Interpolate between two closest values if outside tolerance
                direction = None
                direction_name = "UNKNOWN"
                confidence = "LOW"
                logger.info(f"Wind Vane Reading: {voltage:.3f} V -> {direction_name} ({confidence} confidence)")
            
            return voltage, direction, direction_name, confidence, voltage_diff
            
        except Exception as e:
            logger.error(f"❌ Error reading wind vane: {e}")
            return None, None, None, None, None