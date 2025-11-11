#!/usr/bin/env python3
"""
Anemometer Signal Analysis Script
Analyzes anemometer signals accounting for external pull-up on GPIO17
"""

import lgpio
import time
import signal
import sys

ANEMO_PIN = 17
gpio_handle = None
signal_events = []

def signal_handler(sig, frame):
    print("\n🛑 Test stopped by user")
    analyze_results()
    cleanup_and_exit()

def cleanup_and_exit():
    global gpio_handle
    print("🧹 Cleaning up GPIO...")
    if gpio_handle is not None:
        lgpio.gpiochip_close(gpio_handle)
    print("✅ Test completed!")
    sys.exit(0)

def edge_callback(gpio, level, tick):
    """Record all edge transitions"""
    current_time = time.time()
    edge_type = "RISING" if level == 1 else "FALLING"
    timestamp = time.strftime("%H:%M:%S.%f")[:-3]
    
    print(f"⚡ [{timestamp}] {edge_type} edge: {1-level} → {level}")
    
    signal_events.append({
        'time': current_time,
        'level': level,
        'type': edge_type
    })

def analyze_results():
    """Analyze the collected signal data"""
    if not signal_events:
        print("\n❌ No signal events detected")
        return
    
    print(f"\n📊 SIGNAL ANALYSIS")
    print("="*50)
    print(f"Total events: {len(signal_events)}")
    
    rising_count = sum(1 for e in signal_events if e['level'] == 1)
    falling_count = sum(1 for e in signal_events if e['level'] == 0)
    
    print(f"Rising edges (0→1): {rising_count}")
    print(f"Falling edges (1→0): {falling_count}")
    
    # Calculate timing patterns
    if len(signal_events) >= 2:
        intervals = []
        for i in range(1, len(signal_events)):
            interval = signal_events[i]['time'] - signal_events[i-1]['time']
            intervals.append(interval)
        
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            min_interval = min(intervals)
            max_interval = max(intervals)
            
            print(f"Average interval: {avg_interval:.3f}s")
            print(f"Min interval: {min_interval:.3f}s") 
            print(f"Max interval: {max_interval:.3f}s")
            
            # Estimate frequency
            if rising_count > 0:
                test_duration = signal_events[-1]['time'] - signal_events[0]['time']
                frequency = rising_count / test_duration if test_duration > 0 else 0
                print(f"Estimated frequency: {frequency:.2f} Hz")
    
    print("\n🔍 RECOMMENDATIONS:")
    if rising_count > 0 or falling_count > 0:
        print("✅ Anemometer IS generating signals!")
        print("💡 Your anemometer is working - the original script just wasn't detecting it properly")
        
        if rising_count > falling_count:
            print("📈 More rising edges detected - consider using RISING edge triggers")
        elif falling_count > rising_count:
            print("📉 More falling edges detected - consider using FALLING edge triggers")
        else:
            print("⚖️ Equal edges - both rising and falling triggers should work")
    else:
        print("❌ Still no signals - check anemometer mechanical operation")

def main():
    global gpio_handle
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🌪️ ANEMOMETER SIGNAL ANALYSIS")
    print("="*50)
    print("This will capture and analyze ALL signal transitions")
    print("from your anemometer to understand the signal pattern")
    print()
    print("🔧 Setup:")
    print("   - GPIO17 has external pull-up (confirmed)")
    print("   - Monitoring both rising and falling edges")
    print("   - Recording timing and patterns")
    print()
    
    try:
        # Setup GPIO
        gpio_handle = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(gpio_handle, ANEMO_PIN)  # No internal pull-up needed
        
        # Monitor both edges
        callback = lgpio.callback(gpio_handle, ANEMO_PIN, lgpio.BOTH_EDGES, edge_callback)
        
        print("✅ GPIO monitoring started")
        print("🎯 Spin the anemometer now and watch for signal patterns...")
        print("   Press Ctrl+C when done to see analysis")
        print()
        
        # Monitor current GPIO state
        start_time = time.time()
        last_status_time = start_time
        
        while True:
            current_time = time.time()
            
            # Show status every 10 seconds
            if current_time - last_status_time >= 10:
                elapsed = current_time - start_time
                current_level = lgpio.gpio_read(gpio_handle, ANEMO_PIN)
                
                print(f"⏰ Status after {elapsed:.0f}s: Current level={current_level}, Events={len(signal_events)}")
                last_status_time = current_time
            
            time.sleep(0.1)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        analyze_results()
        cleanup_and_exit()

if __name__ == "__main__":
    main()