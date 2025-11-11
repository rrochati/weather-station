#!/usr/bin/env python3
"""
Improved Anemometer Test Script (using lgpio)
Tests SparkFun Weather Meter Kit anemometer on GPIO17
- Detects BOTH rising and falling edges
- Better debouncing
- More detailed pulse analysis
"""

import lgpio
import time
import signal
import sys
from datetime import datetime

# Configuration
ANEMO_PIN = 17  # GPIO17 (Pin 11)
SPEED_CONV = 0.6667  # m/s per pulse/sec (SparkFun specification)
DEBOUNCE_TIME = 0.01  # 10ms debounce time

# Global variables
pulse_count = 0
test_start_time = None
last_pulse_time = None
last_edge_time = None
gpio_handle = None
edge_transitions = []

def signal_handler(sig, frame):
    """Clean exit on Ctrl+C"""
    print("\n\n🛑 Test stopped by user")
    show_final_results()
    cleanup_and_exit()

def anemo_pulse_callback(gpio, level, tick):
    """Callback function for each anemometer edge transition"""
    global pulse_count, last_pulse_time, last_edge_time, edge_transitions
    
    current_time = time.time()
    
    # Debounce: ignore edges too close together
    if last_edge_time and (current_time - last_edge_time) < DEBOUNCE_TIME:
        return
    
    # Record edge transition
    edge_type = "FALLING" if level == 0 else "RISING"
    timestamp = time.strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
    
    print(f"⚡ [{timestamp}] {edge_type} edge detected (level={level})")
    
    # Count complete pulses (falling edges for reed switch)
    if level == 0:  # Falling edge (switch closes)
        pulse_count += 1
        
        # Calculate time since last complete pulse
        if pulse_count > 1 and last_pulse_time:
            time_diff = current_time - last_pulse_time
            freq = 1.0 / time_diff if time_diff > 0 else 0
            print(f"💨 Pulse #{pulse_count} (gap: {time_diff:.3f}s, freq: {freq:.2f}Hz)")
        else:
            print(f"💨 First complete pulse detected!")
        
        last_pulse_time = current_time
    
    # Store transition for analysis
    edge_transitions.append({
        'time': current_time,
        'level': level,
        'type': edge_type
    })
    
    last_edge_time = current_time

def calculate_wind_speed(pulses, time_period):
    """Calculate wind speed from pulse count and time"""
    if time_period <= 0:
        return 0, 0
    
    pulses_per_second = pulses / time_period
    speed_ms = pulses_per_second * SPEED_CONV  # m/s
    speed_kmh = speed_ms * 3.6  # km/h
    
    return speed_ms, speed_kmh

def show_final_results():
    """Show detailed analysis of the test session"""
    if not test_start_time:
        return
    
    total_time = time.time() - test_start_time
    
    print("\n" + "="*60)
    print("📊 FINAL TEST RESULTS")
    print("="*60)
    print(f"🕐 Test duration: {total_time:.1f} seconds")
    print(f"⚡ Total edge transitions: {len(edge_transitions)}")
    print(f"💨 Complete pulses (falling edges): {pulse_count}")
    
    if pulse_count > 0:
        speed_ms, speed_kmh = calculate_wind_speed(pulse_count, total_time)
        avg_pulse_rate = pulse_count / total_time
        
        print(f"📈 Average pulse rate: {avg_pulse_rate:.2f} pulses/sec")
        print(f"🌬️  Calculated wind speed: {speed_ms:.2f} m/s ({speed_kmh:.1f} km/h)")
        
        # Analyze edge patterns
        falling_edges = sum(1 for e in edge_transitions if e['level'] == 0)
        rising_edges = sum(1 for e in edge_transitions if e['level'] == 1)
        
        print(f"📊 Edge analysis:")
        print(f"   Rising edges (switch opens): {rising_edges}")
        print(f"   Falling edges (switch closes): {falling_edges}")
        
        if falling_edges != rising_edges:
            print("   ⚠️  Unequal edge counts - possible bounce or missed edges")
    else:
        print("❌ No complete pulses detected")
        
        if len(edge_transitions) > 0:
            print("💡 Edge transitions detected but no complete pulses:")
            print("   - Try spinning faster or more consistently")
            print("   - Check mechanical connection in reed switch")
        else:
            print("❌ No edge transitions at all - check wiring")
    
    print("="*60)

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
    print("🌬️  IMPROVED ANEMOMETER TEST (lgpio version)")
    print("=" * 60)
    print(f"📍 GPIO Pin: {ANEMO_PIN} (Physical Pin 11)")
    print(f"🔧 Conversion: {SPEED_CONV} m/s per pulse/sec")
    print(f"⚡ Pull-up: Internal (enabled)")
    print(f"🕐 Debounce: {DEBOUNCE_TIME*1000:.0f}ms software debounce")
    print(f"📊 Detection: Both RISING and FALLING edges")
    print("=" * 60)
    print("📋 Instructions:")
    print("   1. Spin anemometer by hand (try different speeds)")
    print("   2. Watch real-time edge detection")
    print("   3. Press Ctrl+C to stop and see detailed results")
    print("=" * 60)
    print()

def main():
    global test_start_time, pulse_count, gpio_handle
    
    # Set up signal handler for clean exit
    signal.signal(signal.SIGINT, signal_handler)
    
    print_test_header()
    
    try:
        # Setup GPIO
        print("🔧 Setting up GPIO with lgpio...")
        
        # Open GPIO chip
        gpio_handle = lgpio.gpiochip_open(0)
        
        # Set pin as input with pull-up
        lgpio.gpio_claim_input(gpio_handle, ANEMO_PIN, lgpio.SET_PULL_UP)
        
        # Set up callback for BOTH edges (rising and falling)
        callback = lgpio.callback(gpio_handle, ANEMO_PIN, lgpio.BOTH_EDGES, anemo_pulse_callback)
        
        print("✅ GPIO setup complete!")
        print("🎯 Waiting for anemometer activity... (spin it!)")
        print("💡 You should see edge transitions immediately when spinning")
        print()
        
        test_start_time = time.time()
        
        # Main test loop - print status every 10 seconds
        while True:
            time.sleep(10)
            
            current_time = time.time()
            elapsed_time = current_time - test_start_time
            
            # Calculate current stats
            print(f"\n📊 Status after {elapsed_time:.1f}s:")
            print(f"   Edge transitions: {len(edge_transitions)}")
            print(f"   Complete pulses: {pulse_count}")
            
            if pulse_count > 0:
                speed_ms, speed_kmh = calculate_wind_speed(pulse_count, elapsed_time)
                avg_pulse_rate = pulse_count / elapsed_time
                
                print(f"   Avg rate: {avg_pulse_rate:.2f} pulses/sec")
                print(f"   Wind speed: {speed_ms:.2f} m/s ({speed_kmh:.1f} km/h)")
                
                # Time since last pulse
                if last_pulse_time:
                    time_since_last = current_time - last_pulse_time
                    if time_since_last > 5:
                        print(f"   ⏰ No pulses for {time_since_last:.1f}s")
            else:
                print("   ⏳ No complete pulses yet...")
                if len(edge_transitions) > 0:
                    print(f"   💡 {len(edge_transitions)} edge transitions detected - keep spinning!")
            print()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        show_final_results()
        cleanup_and_exit()

if __name__ == "__main__":
    main()