#!/usr/bin/env python3
"""
Simple Anemometer Test Script (using lgpio)
Tests SparkFun Weather Meter Kit anemometer on GPIO17
"""

import lgpio
import time
import signal
import sys
import board # pyright: ignore[reportMissingImports]
import busio # pyright: ignore[reportMissingImports]
from datetime import datetime

# Configuration
ANEMO_PIN = 17  # GPIO17 (Pin 11)
SPEED_CONV = 0.6667  # m/s per pulse/sec (SparkFun specification)

# Global variables
pulse_count = 0
test_start_time = None
last_pulse_time = None
gpio_handle = None

def signal_handler(sig, frame):
    """Clean exit on Ctrl+C"""
    print("\n\n🛑 Test stopped by user")
    cleanup_and_exit()

def anemo_pulse_callback(gpio, level, tick):
    """Callback function for each anemometer pulse"""
    global pulse_count, last_pulse_time
    
    if level == 0:  # Falling edge (switch closes)
        current_time = time.time()
        pulse_count += 1
        
        # Calculate time since last pulse (for debugging)
        if pulse_count > 1 and last_pulse_time:
            time_diff = current_time - last_pulse_time
            print(f"💨 Pulse #{pulse_count} (gap: {time_diff:.3f}s)")
        else:
            print(f"💨 First pulse detected!")
        
        last_pulse_time = current_time

def calculate_wind_speed(pulses, time_period):
    """Calculate wind speed from pulse count and time"""
    if time_period <= 0:
        return 0, 0
    
    pulses_per_second = pulses / time_period
    speed_ms = pulses_per_second * SPEED_CONV  # m/s
    speed_kmh = speed_ms * 3.6  # km/h
    
    return speed_ms, speed_kmh

def cleanup_and_exit():
    """Clean up GPIO and exit"""
    global gpio_handle
    print("🧹 Cleaning up GPIO...")
    if gpio_handle is not None:
        lgpio.gpiochip_close(gpio_handle)
    print("✅ Test completed!")
    sys.exit(0)

def print_test_header():
    """Print test information"""
    print("=" * 60)
    print("🌬️  ANEMOMETER BENCH TEST (lgpio version)")
    print("=" * 60)
    print(f"📍 GPIO Pin: {ANEMO_PIN} (Physical Pin 11)")
    print(f"🔧 Conversion: {SPEED_CONV} m/s per pulse/sec")
    print(f"⚡ Pull-up: Internal (enabled)")
    print(f"🕐 Debounce: Hardware + software")
    print("=" * 60)
    print("📋 Instructions:")
    print("   1. Spin anemometer by hand")
    print("   2. Watch pulse counting in real-time")
    print("   3. Press Ctrl+C to stop and see results")
    print("=" * 60)
    print()

def main():
    global test_start_time, pulse_count, gpio_handle
    
    # Set up signal handler for clean exit
    signal.signal(signal.SIGINT, signal_handler)
    
    print_test_header()
    
    try:
        #logger.info("Initializing I2C...")
        print("Initializing I2C...")
        i2c = busio.I2C(board.SCL, board.SDA)
        
        # Setup GPIO
        print("🔧 Setting up GPIO with lgpio...")
        
        # Open GPIO chip
        gpio_handle = lgpio.gpiochip_open(0)
        
        # Set pin as input with pull-up
        lgpio.gpio_claim_input(gpio_handle, ANEMO_PIN) #, lgpio.SET_PULL_UP)
        
        # Set up callback for falling edge
        callback = lgpio.callback(gpio_handle, ANEMO_PIN, lgpio.FALLING_EDGE, anemo_pulse_callback)
        
        print("✅ GPIO setup complete!")
        print("🎯 Waiting for anemometer pulses... (spin it!)")
        print()
        
        test_start_time = time.time()
        
        # Main test loop - print status every 5 seconds
        while True:
            time.sleep(5)
            
            current_time = time.time()
            elapsed_time = current_time - test_start_time
            
            # Calculate current stats
            if pulse_count > 0:
                speed_ms, speed_kmh = calculate_wind_speed(pulse_count, elapsed_time)
                avg_pulse_rate = pulse_count / elapsed_time
                
                print(f"📊 Status after {elapsed_time:.1f}s:")
                print(f"   Pulses: {pulse_count}")
                print(f"   Avg rate: {avg_pulse_rate:.2f} pulses/sec")
                print(f"   Wind speed: {speed_ms:.2f} m/s ({speed_kmh:.1f} km/h)")
                
                # Time since last pulse (detect if stopped)
                if last_pulse_time:
                    time_since_last = current_time - last_pulse_time
                    if time_since_last > 10:
                        print(f"   ⏰ No pulses for {time_since_last:.1f}s (stopped?)")
                print()
            else:
                print(f"⏳ Still waiting for first pulse... ({elapsed_time:.1f}s elapsed)")
                print("   💡 Try spinning the anemometer manually")
                print()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        cleanup_and_exit()

if __name__ == "__main__":
    main()
