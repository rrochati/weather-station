#!/usr/bin/env python3
"""
GPIO Pull-up Test Script
Tests if internal pull-up is working correctly on GPIO17
"""

import lgpio
import time
import signal
import sys

ANEMO_PIN = 17
gpio_handle = None

def signal_handler(sig, frame):
    print("\n🛑 Test stopped by user")
    cleanup_and_exit()

def cleanup_and_exit():
    global gpio_handle
    print("🧹 Cleaning up GPIO...")
    if gpio_handle is not None:
        lgpio.gpiochip_close(gpio_handle)
    print("✅ Test completed!")
    sys.exit(0)

def test_pullup_modes():
    global gpio_handle
    
    print("🔧 GPIO PULL-UP VERIFICATION TEST")
    print("="*50)
    
    try:
        gpio_handle = lgpio.gpiochip_open(0)
        
        print("📝 Test 1: GPIO with NO pull-up (floating)")
        print("   Expected: Should read random/unstable values when disconnected")
        
        # Test without pull-up
        lgpio.gpio_claim_input(gpio_handle, ANEMO_PIN)  # No pull-up
        
        print("   Readings (floating input):")
        readings = []
        for i in range(10):
            level = lgpio.gpio_read(gpio_handle, ANEMO_PIN)
            readings.append(level)
            print(f"     Reading {i+1}: {level}")
            time.sleep(0.2)
        
        # Analyze readings
        if all(r == readings[0] for r in readings):
            print(f"   📊 Result: All readings are {readings[0]} (stable)")
            if readings[0] == 1:
                print("   ⚠️  WARNING: Even without pull-up, reads HIGH")
                print("        This suggests external pull-up or connection issue")
        else:
            print("   📊 Result: Readings vary (normal for floating input)")
        
        # Release pin
        lgpio.gpio_free(gpio_handle, ANEMO_PIN)
        time.sleep(0.5)
        
        print("\n📝 Test 2: GPIO with INTERNAL pull-up")
        print("   Expected: Should read HIGH (1) consistently")
        
        # Test with pull-up
        lgpio.gpio_claim_input(gpio_handle, ANEMO_PIN, lgpio.SET_PULL_UP)
        
        print("   Readings (with internal pull-up):")
        for i in range(10):
            level = lgpio.gpio_read(gpio_handle, ANEMO_PIN)
            print(f"     Reading {i+1}: {level}")
            time.sleep(0.2)
        
        print("\n📝 Test 3: Manual connection test")
        print("   Instructions:")
        print("   1. Keep pin disconnected - should read HIGH")
        print("   2. Connect GPIO17 to GND directly - should read LOW")
        print("   3. Disconnect again - should read HIGH")
        print()
        print("   Press Enter when ready to start live monitoring...")
        input()
        
        print("🎯 Live monitoring (touch GPIO17 to GND to test):")
        print("   Press Ctrl+C to stop")
        
        last_level = -1
        for i in range(300):  # 30 seconds
            current_level = lgpio.gpio_read(gpio_handle, ANEMO_PIN)
            
            if current_level != last_level:
                timestamp = time.strftime("%H:%M:%S")
                change_desc = "GND connected" if current_level == 0 else "GND disconnected"
                print(f"   [{timestamp}] Change: {last_level} → {current_level} ({change_desc})")
                last_level = current_level
            
            time.sleep(0.1)
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🔍 TESTING GPIO PULL-UP FUNCTIONALITY")
    print("="*50)
    print("This test will verify if internal pull-ups work correctly")
    print("Make sure GPIO17 (Pin 11) is DISCONNECTED for accurate testing")
    print()
    
    response = input("Is GPIO17 (Pin 11) disconnected? (y/n): ").lower().strip()
    if response != 'y':
        print("❌ Please disconnect GPIO17 and run test again")
        return
    
    try:
        test_pullup_modes()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        cleanup_and_exit()

if __name__ == "__main__":
    main()