#!/usr/bin/env python3
"""
Wind Vane Test Script for SparkFun Weather Kit
Tests the voltage divider circuit and direction mapping

Hardware Requirements:
- Raspberry Pi 5
- DFR0553 (ADS1115) module connected via I2C
- Wind vane connected to A0 with 10kΩ voltage divider
- 100nF filter capacitor

Usage: python3 wind_vane_test.py
"""

import time
import board
import busio
try:
    # Try newer CircuitPython library first
    from adafruit_ads1x15.ads1115 import ADS1115
    from adafruit_ads1x15.analog_in import AnalogIn
    USE_CIRCUITPYTHON = True
except ImportError:
    # Fall back to older library
    import Adafruit_ADS1x15
    USE_CIRCUITPYTHON = False

# -------------------------------------------------
# Configuration
# -------------------------------------------------

# Voltage tolerance for direction matching (volts)
TOLERANCE = 0.08

# Wind direction mapping based on your actual hardware calibration
# Custom calibrated values from your SparkFun Weather Kit + 10kΩ voltage divider
# Note: Some adjacent directions have identical voltages - hardware limitation
VOLTAGE_TO_DIR = {
    0.252: 202.5,  # SSW
    0.254: 180.0,  # S
    0.441: 225.0,  # SW
#    0.441: 247.5,  # WSW (Note: identical voltage to SW)
    0.763: 270.0,  # W
#    0.763: 292.5,  # WNW (Note: identical voltage to W)
    1.260: 135.0,  # SE
    1.261: 157.5,  # SSE
    1.802: 315.0,  # NW
#    1.802: 337.5,  # NNW (Note: identical voltage to NW)
    2.355: 67.5,   # ENE
    2.356: 90.0,   # E
#    2.356: 112.5,  # ESE (Note: very close voltage to E)
#    2.681: 22.5,   # NNE (Note: identical voltage to NE)
    2.681: 45.0,   # NE
    2.973: 0.0,    # N
}
# Direction names for easy reading
DIR_NAMES = {
    0.0: "N", 22.5: "NNE", 45.0: "NE", 67.5: "ENE",
    90.0: "E", 112.5: "ESE", 135.0: "SE", 157.5: "SSE",
    180.0: "S", 202.5: "SSW", 225.0: "SW", 247.5: "WSW",
    270.0: "W", 292.5: "WNW", 315.0: "NW", 337.5: "NNW"
}

def setup_ads1115():
    """Initialize ADS1115 for wind vane readings"""
    try:
        print("🔧 Setting up I2C and ADS1115...")
        
        if USE_CIRCUITPYTHON:
            # I2C setup
            i2c = busio.I2C(board.SCL, board.SDA)
            
            # ADS1115 setup
            ads = ADS1115(i2c)
            ads.gain = 1  # ±4.096V range (suitable for 3.3V system)
            
            # Wind vane on A0 (channel 0)
            wind_vane = AnalogIn(ads, 0)  # Channel 0 = A0
            
            print("✅ ADS1115 initialized successfully (CircuitPython)")
            print(f"✅ Wind vane connected to A0")
            print(f"✅ Voltage range: ±4.096V")
            
        else:
            # Older library setup
            ads = Adafruit_ADS1x15.ADS1115()
            wind_vane = ads
            
            print("✅ ADS1115 initialized successfully (Legacy)")
            print(f"✅ Wind vane connected to A0")
            print(f"✅ Voltage range: ±4.096V")
        
        return wind_vane, ads if USE_CIRCUITPYTHON else wind_vane
        
    except Exception as e:
        print(f"❌ Error setting up ADS1115: {e}")
        return None, None

def read_wind_direction(wind_vane):
    """Read voltage and convert to compass direction"""
    try:
        # Read voltage
        if USE_CIRCUITPYTHON:
            voltage = wind_vane.voltage
        else:
            # Channel 0, gain=1 (±4.096V), sample rate=860 samples/second
            raw_value = wind_vane.read_adc(0, gain=1)
            # Convert to voltage (16-bit ADC with ±4.096V range)
            voltage = raw_value * 4.096 / 32767.0
        
        # Find closest voltage match
        closest_voltage = min(VOLTAGE_TO_DIR.keys(), key=lambda x: abs(x - voltage))
        voltage_diff = abs(closest_voltage - voltage)
        
        if voltage_diff <= TOLERANCE:
            direction = VOLTAGE_TO_DIR[closest_voltage]
            direction_name = DIR_NAMES.get(direction, f"{direction}°")
            confidence = "HIGH"
        else:
            # Interpolate between two closest values if outside tolerance
            direction = None
            direction_name = "UNKNOWN"
            confidence = "LOW"
            
        return voltage, direction, direction_name, confidence, voltage_diff
        
    except Exception as e:
        print(f"❌ Error reading wind vane: {e}")
        return None, None, None, None, None

def test_voltage_readings():
    """Test and display voltage readings continuously"""
    wind_vane, ads = setup_ads1115()
    
    if wind_vane is None:
        return
    
    print("\n" + "="*60)
    print("🌬️  WIND VANE VOLTAGE TEST")
    print("="*60)
    print("🔄 Manually rotate your wind vane to test all directions")
    print("📊 Readings every 2 seconds. Press Ctrl+C to stop.")
    print("\n📋 Expected voltage ranges:")
    
    # Show expected voltages sorted
    sorted_voltages = sorted(VOLTAGE_TO_DIR.items(), key=lambda x: x[0])
    for voltage, direction in sorted_voltages:
        dir_name = DIR_NAMES.get(direction, f"{direction}°")
        print(f"   {voltage:.3f}V → {direction:5.1f}° ({dir_name})")
    
    print("\n" + "="*60)
    print("🔴 Live Readings:")
    print("="*60)
    
    try:
        reading_count = 0
        while True:
            voltage, direction, direction_name, confidence, voltage_diff = read_wind_direction(wind_vane)
            
            if voltage is not None:
                reading_count += 1
                
                # Format output
                status_icon = "✅" if confidence == "HIGH" else "⚠️"
                
                print(f"{status_icon} Reading #{reading_count:3d}: "
                      f"Voltage: {voltage:6.3f}V | "
                      f"Direction: {direction_name:4s} | "
                      f"Confidence: {confidence:4s} | "
                      f"Error: {voltage_diff:.3f}V")
                
                # Show calibration suggestions for unknown readings
                if confidence == "LOW":
                    closest_voltage = min(VOLTAGE_TO_DIR.keys(), key=lambda x: abs(x - voltage))
                    expected_dir = VOLTAGE_TO_DIR[closest_voltage]
                    expected_name = DIR_NAMES.get(expected_dir, f"{expected_dir}°")
                    print(f"   💡 Closest match: {closest_voltage:.3f}V ({expected_name}) - "
                          f"Diff: {voltage_diff:.3f}V")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Test stopped. Total readings: {reading_count}")
        print("="*60)

def test_i2c_devices():
    """Test if I2C devices are detected"""
    print("🔍 Checking I2C devices...")
    
    try:
        # This will help identify what devices are on the bus
        import subprocess
        result = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)
        
        print("I2C Device Scan:")
        print(result.stdout)
        
        if "48" in result.stdout:
            print("✅ ADS1115 (DFR0553) detected at address 0x48")
        else:
            print("❌ ADS1115 (DFR0553) NOT detected at address 0x48")
            
        if "77" in result.stdout or "76" in result.stdout:
            print("✅ BME280 detected")
        else:
            print("ℹ️  BME280 not detected (this is OK for wind vane testing)")
            
    except Exception as e:
        print(f"⚠️  Could not run i2cdetect: {e}")

def voltage_calibration_helper():
    """Help calibrate voltage readings"""
    print("\n" + "="*60)
    print("🎯 VOLTAGE CALIBRATION HELPER")
    print("="*60)
    print("This will help you create a custom voltage mapping")
    print("Manually point your wind vane to each direction and record voltages")
    print()
    
    wind_vane, ads = setup_ads1115()
    if wind_vane is None:
        return
    
    calibration_data = {}
    # All 16 compass directions (every 22.5°)
    directions = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5]
    dir_names_simple = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    
    for i, (direction, name) in enumerate(zip(directions, dir_names_simple)):
        input(f"\n👉 Point wind vane to {direction}° ({name}) and press Enter...")
        
        # Take multiple readings for accuracy
        voltages = []
        print("   Taking 10 readings...")
        for j in range(10):
            if USE_CIRCUITPYTHON:
                voltage = wind_vane.voltage
            else:
                raw_value = wind_vane.read_adc(0, gain=1)
                voltage = raw_value * 4.096 / 32767.0
            voltages.append(voltage)
            print(f"   Reading {j+1}: {voltage:.4f}V")
            time.sleep(0.5)
        
        avg_voltage = sum(voltages) / len(voltages)
        calibration_data[avg_voltage] = direction
        
        print(f"   ✅ Average: {avg_voltage:.4f}V for {direction}° ({name})")
    
    print("\n" + "="*60)
    print("📋 CALIBRATION RESULTS:")
    print("="*60)
    print("Copy this dictionary to your code:")
    print()
    print("VOLTAGE_TO_DIR = {")
    for voltage, direction in sorted(calibration_data.items()):
        print(f"    {voltage:.3f}: {direction:.1f},")
    print("}")

def main():
    """Main test menu"""
    print("🌬️  SparkFun Wind Vane Test Script")
    print("="*60)
    print("Choose a test option:")
    print("1. I2C Device Scan")
    print("2. Live Voltage Readings")
    print("3. Voltage Calibration Helper")
    print("4. All Tests")
    print()
    
    try:
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            test_i2c_devices()
        elif choice == "2":
            test_voltage_readings()
        elif choice == "3":
            voltage_calibration_helper()
        elif choice == "4":
            test_i2c_devices()
            print("\nPress Enter to continue to voltage readings...")
            input()
            test_voltage_readings()
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()