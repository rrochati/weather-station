#!/usr/bin/env python3
"""
GPIO Diagnostic Script for Anemometer Troubleshooting
Tests GPIO17 setup and reads current state
"""

import lgpio
import time
import signal
import sys

# Configuration
ANEMO_PIN = 17  # GPIO17 (Pin 11)

gpio_handle = None

def signal_handler(sig, frame):
    """Clean exit on Ctrl+C"""
    print("\n🛑 Diagnostic stopped by user")
    cleanup_and_exit()

def cleanup_and_exit():
    """Clean up GPIO and exit"""
    global gpio_handle
    print("🧹 Cleaning up GPIO...")
    if gpio_handle is not None:
        lgpio.gpiochip_close(gpio_handle)
    print("✅ Diagnostic completed!")
    sys.exit(0)

def test_gpio_basic():
    """Test basic GPIO functionality"""
    global gpio_handle
    
    print("🔧 Testing basic GPIO setup...")
    
    try:
        # Open GPIO chip
        gpio_handle = lgpio.gpiochip_open(0)
        print("✅ GPIO chip opened successfully")
        
        # Claim pin as input with pull-up
        lgpio.gpio_claim_input(gpio_handle, ANEMO_PIN)
        print(f"✅ GPIO{ANEMO_PIN} claimed as input")
        
        # Test reading GPIO state
        print("\n📊 GPIO State Test (10 readings over 5 seconds):")
        print("   This will show if the pin is properly connected and reading logic levels")
        print("   Expected: Should read HIGH (1) when switch is open, LOW (0) when closed")
        print()
        
        for i in range(10):
            level = lgpio.gpio_read(gpio_handle, ANEMO_PIN)
            print(f"   Reading {i+1}: GPIO{ANEMO_PIN} = {level} {'(HIGH/Open)' if level == 1 else '(LOW/Closed)'}")
            time.sleep(0.5)
        
        print("\n🔍 Manual Test Instructions:")
        print("   1. If all readings show HIGH (1): Wiring might be correct, reed switch is open")
        print("   2. If all readings show LOW (0): Check if pull-up is working or switch is stuck closed")
        print("   3. If readings fluctuate: Good! The switch is working")
        print("   4. Try manually spinning anemometer during next test...")
        
        print("\n🎯 Live GPIO monitoring (spin anemometer now!)...")
        print("   Press Ctrl+C to stop")
        
        last_level = -1
        changes = 0
        
        for i in range(120):  # Monitor for 120 seconds
            current_level = lgpio.gpio_read(gpio_handle, ANEMO_PIN)
            
            if current_level != last_level:
                changes += 1
                timestamp = time.strftime("%H:%M:%S")
                print(f"   [{timestamp}] Change #{changes}: {last_level} → {current_level}")
                last_level = current_level
            
            time.sleep(0.1)  # Check every 100ms
        
        print(f"\n📈 Summary: Detected {changes} state changes in 60 seconds")
        if changes == 0:
            print("❌ No state changes detected - possible wiring issue")
        else:
            print("✅ State changes detected - anemometer is working!")
            
    except Exception as e:
        print(f"❌ Error during GPIO test: {e}")

def test_wiring_verification():
    """Help verify correct wiring based on documentation"""
    print("\n" + "="*60)
    print("🔌 WIRING VERIFICATION GUIDE")
    print("="*60)
    print("Based on your documentation, you should have:")
    print()
    print("🎯 ANEMOMETER TO RJ45 CONNECTOR:")
    print("   RJ11 Red (RJ45 Pin 4) - Anemometer Signal")
    print("   RJ11 Yellow (RJ45 Pin 5) - GND)")
    print()
    print("🎯 RJ45 CONNECTOR TO Pi:")
    print("   Pin 4 Purple DuPont → Pi Pin 11 (GPIO17) - SIGNAL (via breadboard)")
    print("   Pin 5 Black DuPont → Pi Pin 6 (GND) - GROUND (via breadboard)")
    print()
    print("❗ CRITICAL CHECK:")
    print("   1. Is your signal wire (from anemometer RED) going to GPIO17?")
    print("   2. Is your ground wire (from anemometer YELLOW) going to Pi GND?")
    print()
    print("="*60)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🔍 GPIO DIAGNOSTIC TOOL FOR ANEMOMETER")
    print("="*60)
    
    test_wiring_verification()
    
    try:
        test_gpio_basic()
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        cleanup_and_exit()

if __name__ == "__main__":
    main()
