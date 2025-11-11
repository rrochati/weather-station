#!/usr/bin/env python3
"""
SparkFun Anemometer Wire Identification Test
Helps identify which wires from the 4-wire wind vane connector carry the anemometer signal
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
    if gpio_handle is not None:
        lgpio.gpiochip_close(gpio_handle)
    sys.exit(0)

def test_wire_combination(wire1_name, wire2_name):
    """Test a specific wire combination for anemometer signals"""
    print(f"\n🔧 Testing: {wire1_name} + {wire2_name}")
    print("-" * 40)
    print(f"Connect: {wire1_name} → GPIO17, {wire2_name} → GND")
    print("Press Enter when connected and ready to test...")
    input()
    
    # Test baseline
    baseline_level = lgpio.gpio_read(gpio_handle, ANEMO_PIN)
    print(f"Baseline reading: {baseline_level}")
    
    print("\n🎯 Spin anemometer now! (15 second test)")
    changes = 0
    last_level = baseline_level
    
    for i in range(150):  # 15 seconds
        current_level = lgpio.gpio_read(gpio_handle, ANEMO_PIN)
        
        if current_level != last_level:
            changes += 1
            timestamp = time.strftime("%H:%M:%S")
            print(f"   [{timestamp}] Change #{changes}: {last_level} → {current_level}")
            last_level = current_level
        
        time.sleep(0.1)
    
    print(f"\n📊 Result: {changes} signal changes detected")
    
    if changes > 0:
        print("✅ SUCCESS! This wire combination works!")
        print(f"   {wire1_name} = Signal wire (to GPIO17)")
        print(f"   {wire2_name} = Ground wire (to GND)")
        return True
    else:
        print("❌ No signals detected with this combination")
        return False

def main():
    global gpio_handle
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🔍 SPARKFUN ANEMOMETER WIRE IDENTIFICATION")
    print("=" * 60)
    print("According to SparkFun documentation:")
    print("- Anemometer (2 wires) plugs into Wind Vane (4 wires)")
    print("- We need to find which 2 of the 4 wind vane wires carry anemometer signal")
    print("- Wind vane has: Black, Red, Yellow, Green wires")
    print()
    print("⚠️  IMPORTANT: Make sure anemometer is plugged INTO wind vane!")
    print()
    
    # Verify setup
    response = input("Is anemometer connected to wind vane? (y/n): ").lower().strip()
    if response != 'y':
        print("❌ Please connect anemometer to wind vane first!")
        return
    
    try:
        # Setup GPIO
        gpio_handle = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(gpio_handle, ANEMO_PIN)
        
        print("\n🎯 SYSTEMATIC WIRE TESTING")
        print("We'll test each possible combination of 2 wires from the 4-wire wind vane")
        print()
        
        # Based on SparkFun docs, anemometer likely uses center pins (pins 2&3)
        # These often correspond to specific colors in RJ11
        
        wire_combinations = [
            ("RED", "GREEN"),      # Most likely - center pins
            ("BLACK", "YELLOW"),   # Outer pins  
            ("RED", "BLACK"),      # Mixed combinations
            ("RED", "YELLOW"),
            ("GREEN", "BLACK"),
            ("GREEN", "YELLOW")
        ]
        
        successful_combo = None
        
        for wire1, wire2 in wire_combinations:
            if test_wire_combination(wire1, wire2):
                successful_combo = (wire1, wire2)
                break
                
            # Ask if user wants to continue
            print(f"\nTry next combination? (y/n): ", end="")
            response = input().lower().strip()
            if response != 'y':
                break
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 FINAL RESULTS")
        print("=" * 60)
        
        if successful_combo:
            wire1, wire2 = successful_combo
            print(f"✅ FOUND WORKING COMBINATION:")
            print(f"   Signal: {wire1} wire → Pi GPIO17 (Pin 11)")
            print(f"   Ground: {wire2} wire → Pi GND (Pin 6)")
            print()
            print("🔧 UPDATE YOUR WIRING:")
            print(f"   1. Connect wind vane {wire1} wire to your extension cable signal wire")
            print(f"   2. Connect wind vane {wire2} wire to your extension cable ground wire")
            print(f"   3. Your extension cable should go: Signal→GPIO17, Ground→GND")
        else:
            print("❌ No working combination found")
            print("   Possible issues:")
            print("   - Anemometer not connected to wind vane")
            print("   - Faulty anemometer or wind vane")
            print("   - Wrong extension cable connections")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cleanup_and_exit()

if __name__ == "__main__":
    main()