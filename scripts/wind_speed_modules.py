#!/usr/bin/env python3
import time
import board
import busio
import sys, os
# Add the modules directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'modules'))
from windvane import *


# -------------------------------------------------
# Main loop
# -------------------------------------------------
try:
    print("Starting wind speed measurement... Press Ctrl+C to stop.")
    # I2C setup
    i2c = busio.I2C(board.SCL, board.SDA)
    start_gpio()
    print(f"Measuring wind speed at {time.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    while True:
        
        # Measure wind
        speed, cps = measure_wind_speed(60)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        # Print summary
        print(f"Timestamp: {timestamp}")
        print(f"Wind: {speed:.2f} m/s ({speed*3.6:.1f} km/h), {speed*2.237:.1f} mph), Pulses: {cps*5:.0f} in last 5s")
        print("-" * 30)

except KeyboardInterrupt:
    print("Stopping wind speed measurement...")
finally:
    GPIO.cleanup()
