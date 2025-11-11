#!/usr/bin/env python3
import time
import board
import busio
import sys, os
# Add the modules directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'modules'))
from anemometer import *


# -------------------------------------------------
# Main loop
# -------------------------------------------------
try:
    print("Starting wind speed measurement... Press Ctrl+C to stop.")
    # I2C setup
    i2c = busio.I2C(board.SCL, board.SDA)
    start_gpio()
    print(f"Measuring wind speed at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
    while True:
        interval = 60  # seconds
        # Measure wind
        speed, total_pulses = measure_wind_speed(interval)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        # Print summary
        print(f"Timestamp: {timestamp}")
        print(f"Wind: {speed:.2f} m/s ({speed*3.6:.1f} km/h, {speed*2.237:.1f} mph, {speed*1.944:.1f} knots), Pulses: {total_pulses} in last interval")
        print(f"pulses: {total_pulses} pulses/second")
        print(f"pulses: {total_pulses/interval} pulses/interval")
        print("-" * 30)

except KeyboardInterrupt:
    print("Stopping wind speed measurement...")
finally:
    GPIO.cleanup()
