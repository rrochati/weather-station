#!/usr/bin/env python3
"""
Rain bucket test script for SparkFun Weather Meter Kit
"""

import sys
import os
import time

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.rain_bucket import RainBucket

def test_rain_bucket_basic():
    """Test basic rain bucket functionality"""
    print("🌧️ RAIN BUCKET TEST")
    print("="*50)
    
    # Initialize rain bucket
    print("📍 Initializing rain bucket on GPIO27...")
    rain_bucket = RainBucket(pin=27)
    rain_bucket.setup()
    
    print("\n💧 Rain bucket monitoring test:")
    print("   - Manually tip the rain bucket or simulate rainfall")
    print("   - Each tip should register as 0.2794mm")
    print("   - Test runs for 60 seconds")
    print("   - Press Ctrl+C to stop early")
    
    try:
        start_time = time.time()
        last_tips = 0
        
        while (time.time() - start_time) < 60:
            # Get current data (but don't reset counter yet)
            data = rain_bucket.get_data(reset_counter=False)
            
            # Report new tips
            if data['interval_tips'] > last_tips:
                new_tips = data['interval_tips'] - last_tips
                print(f"   ✅ New rain detected: +{new_tips} tip(s) = +{new_tips * rain_bucket.mm_per_tip:.3f}mm")
                print(f"      Total this interval: {data['interval_mm']:.3f}mm ({data['interval_tips']} tips)")
                print(f"      Daily total: {data['daily_mm']:.3f}mm ({data['daily_tips']} tips)")
                last_tips = data['interval_tips']
            
            time.sleep(0.1)  # Check every 100ms for better responsiveness
        
        # Final summary
        final_data = rain_bucket.get_data(reset_counter=True)
        print(f"\n📊 TEST SUMMARY:")
        print(f"   Interval rainfall: {final_data['interval_mm']:.3f}mm ({final_data['interval_tips']} tips)")
        print(f"   Daily total: {final_data['daily_mm']:.3f}mm ({final_data['daily_tips']} tips)")
        
        if final_data['interval_tips'] > 0:
            print(f"   ✅ Rain bucket is working correctly!")
            rate = (final_data['interval_mm'] / 60) * 60  # mm/hour
            print(f"   📈 Calculated rate: {rate:.2f}mm/hour")
        else:
            print(f"   ❌ No rain detected. Check:")
            print(f"      - Wiring (GPIO27 to rain bucket signal)")
            print(f"      - Ground connection")
            print(f"      - Rain bucket mechanism")
        
    except KeyboardInterrupt:
        print(f"\n🛑 Test stopped by user")
        final_data = rain_bucket.get_data(reset_counter=True)
        print(f"   Final: {final_data['interval_mm']:.3f}mm ({final_data['interval_tips']} tips)")
    
    finally:
        rain_bucket.cleanup()
        print("✅ Rain bucket test completed")

def test_rain_bucket_wiring():
    """Test rain bucket GPIO wiring"""
    import lgpio
    
    print("\n🔧 RAIN BUCKET WIRING TEST")
    print("="*40)
    
    PIN = 27
    
    try:
        # Test GPIO access
        gpio_handle = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(gpio_handle, PIN, lgpio.SET_PULL_UP)
        
        print(f"📊 Testing GPIO{PIN} state:")
        print("   Expected: HIGH (1) when reed switch is open")
        print("   Expected: LOW (0) when reed switch is closed")
        
        for i in range(10):
            level = lgpio.gpio_read(gpio_handle, PIN)
            print(f"   Reading {i+1}: GPIO{PIN} = {level} {'(HIGH/Open)' if level == 1 else '(LOW/Closed)'}")
            time.sleep(0.5)
        
        print(f"\n🎯 Manual test:")
        print("   Try manually triggering the rain bucket while watching for changes...")
        print("   Monitoring for 30 seconds...")
        
        last_level = -1
        changes = 0
        
        for i in range(60):  # 30 seconds at 0.5s intervals
            current_level = lgpio.gpio_read(gpio_handle, PIN)
            
            if current_level != last_level and last_level != -1:
                changes += 1
                timestamp = time.strftime("%H:%M:%S")
                print(f"   [{timestamp}] Change #{changes}: {last_level} → {current_level}")
            
            last_level = current_level
            time.sleep(0.5)
        
        print(f"\n📈 Wiring test results:")
        if changes == 0:
            print("   ❌ No state changes detected")
            print("   Check:")
            print("   - Rain bucket signal wire to GPIO27")
            print("   - Ground connection")
            print("   - Rain bucket reed switch operation")
        else:
            print(f"   ✅ Detected {changes} state changes - wiring looks good!")
        
        lgpio.gpiochip_close(gpio_handle)
        
    except Exception as e:
        print(f"   ❌ Error testing GPIO: {e}")

def main():
    print("🌧️ RAIN BUCKET DIAGNOSTIC TOOL")
    print("="*50)
    
    print("\nSelect test:")
    print("1. Wiring test (GPIO state monitoring)")
    print("2. Full rain bucket test (tip counting)")
    print("3. Both tests")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice in ['1', '3']:
        test_rain_bucket_wiring()
    
    if choice in ['2', '3']:
        test_rain_bucket_basic()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()