#!/usr/bin/env python3
import time
import board
import busio
#import adafruit_ads1x15.ads1115 as ADS
#from adafruit_ads1x15.analog_in import AnalogIn
#import RPi.GPIO as GPIO
import lgpio
import csv
from datetime import datetime

# -------------------------------------------------
# Configuration
# -------------------------------------------------

# GPIO pins (BCM numbering)
ANEMO_PIN = 17       # Anemometer reed switch
gpio_handle = None

# Conversion constants
SPEED_CONV = 0.6667      # m/s per pulse/sec (SparkFun)

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)

# -------------------------------------------------
# Global counters
# -------------------------------------------------
anemo_pulses = 0

# -------------------------------------------------
# Helper functions
# -------------------------------------------------

def anemo_callback(channel):
    global anemo_pulses
    anemo_pulses += 1

def start_gpio():
    """Initialize GPIO"""
    global gpio_handle
    
    print("🔧 Starting GPIO...")
    
    try:
        # Open GPIO chip
        gpio_handle = lgpio.gpiochip_open(0)
        print("✅ GPIO chip opened successfully")
        
        # Claim pin as input with pull-up
        lgpio.gpio_claim_input(gpio_handle, ANEMO_PIN)
        lgpio.gpio_set_debounce_micros(gpio_handle, ANEMO_PIN, 1000)
        print(f"✅ GPIO{ANEMO_PIN} claimed as input")

    except Exception as e:
        print(f"❌ Error during GPIO test: {e}")

    #try:
    #    GPIO.setmode(GPIO.BCM)
    #    GPIO.setup(ANEMO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #    GPIO.add_event_detect(ANEMO_PIN, GPIO.FALLING, callback=anemo_callback, bouncetime=10)
    #    print(f"✅ GPIO{ANEMO_PIN} event detection set up")
    #except Exception as e:
    #    print(f"❌ Error during GPIO test: {e}")

def measure_wind_speed(interval=5):
    global anemo_pulses
    anemo_pulses = 0
    last_level = 0
    changes = 0
    start_time = time.time()
    
    for i in range(int(interval)):
        current_level = lgpio.gpio_read(gpio_handle, ANEMO_PIN)
                
        if current_level != last_level:
            changes += 1
            timestamp = time.strftime("%H:%M:%S")
            print(f"   [{timestamp}] Change #{changes}: {last_level} → {current_level}")
            last_level = current_level
                
        time.sleep(0.1)  # Check every 100ms
    
    cps = anemo_pulses / interval
    speed = cps * SPEED_CONV  # m/s
    return speed, cps

# -------------------------------------------------
# Main loop
# -------------------------------------------------
try:
    print("Starting wind speed measurement... Press Ctrl+C to stop.")
    start_gpio()
    print(f"Measuring wind speed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    while True:
        
        # Measure wind
        speed, cps = measure_wind_speed(5)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Print summary
        print(f"Timestamp: {timestamp}")
        print(f"Wind: {speed:.2f} m/s ({speed*3.6:.1f} km/h), {speed*2.237:.1f} mph), Pulses: {cps*5:.0f} in last 5s")
        print("-" * 30)

except KeyboardInterrupt:
    print("Stopping wind speed measurement...")
finally:
    GPIO.cleanup()