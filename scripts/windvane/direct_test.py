#!/usr/bin/env python3
"""
Direct test with new RJ45 breakout
Tests wind vane connected directly to test breakout with proper circuit
"""
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import time

print("🔧 Direct Wind Vane Test - Using Test Breakout")
print("=" * 70)
print("\n📌 Expected RJ11 → Test Breakout Wiring:")
print("   RJ11 Pin 1 (Green - Vane Signal)  → RJ45 Pin 3 → White → A0")
print("   RJ11 Pin 2 (Yellow - Ground)      → RJ45 Pin 4 → Black → GND")
print("   RJ11 Pin 3 (Red - Anemo Signal)   → RJ45 Pin 5 → White → GPIO17")
print("   RJ11 Pin 4 (Black - Power 3.3V)   → RJ45 Pin 6 → Red → Power rail")
print("=" * 70)

# Initialize I2C and ADS1115
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS1115(i2c)
    ads.gain = 1  # ±4.096V range
    chan = AnalogIn(ads, 0)  # A0 channel
    print("\n✅ ADS1115 initialized successfully")
except Exception as e:
    print(f"\n❌ Error initializing ADS1115: {e}")
    exit(1)

print("\n" + "=" * 70)
print("🔍 STEP 1: Power Check (Vane Disconnected)")
print("=" * 70)
input("\n⚠️  Disconnect the wind vane RJ11. Press Enter when ready...")

readings = []
for i in range(5):
    v = chan.voltage
    readings.append(v)
    print(f"   Reading {i+1}: {v:.3f}V")
    time.sleep(0.3)

disconnected_avg = sum(readings) / len(readings)
print(f"\n   Average: {disconnected_avg:.3f}V")

if abs(disconnected_avg) < 0.05:
    print("   ✅ Good - no signal when disconnected")
elif abs(disconnected_avg) > 0.1:
    print(f"   ⚠️  Unexpected voltage ({disconnected_avg:.3f}V) - may indicate:")
    print("      • Floating input (normal with high-impedance circuit)")
    print("      • Or signal wire shorted to power")

print("\n" + "=" * 70)
print("🔍 STEP 2: Wind Vane Connected Test")
print("=" * 70)
input("\n✅ Connect the wind vane RJ11 to test breakout. Press Enter when ready...")

time.sleep(1)
print("\n🔄 Reading voltage while you rotate the vane...")
print("   Rotate SLOWLY through all 16 positions\n")

readings = []
directions_seen = set()

for i in range(30):
    v = chan.voltage
    readings.append(v)
    
    # Show voltage with simple bar graph
    bar_length = int(v * 10) if v > 0 else 0
    bar = "█" * bar_length
    
    print(f"   Reading {i+1:2d}: {v:.3f}V {bar}")
    time.sleep(0.5)

print("\n" + "=" * 70)
print("📊 ANALYSIS")
print("=" * 70)

min_v = min(readings)
max_v = max(readings)
avg_v = sum(readings) / len(readings)

print(f"\n   Minimum voltage: {min_v:.3f}V")
print(f"   Maximum voltage: {max_v:.3f}V")
print(f"   Average voltage: {avg_v:.3f}V")
print(f"   Range: {max_v - min_v:.3f}V")

print("\n   Expected ranges:")
print("   • Minimum: ~0.25V (SSW position)")
print("   • Maximum: ~3.00V (N position)")
print("   • Range: ~2.75V")

print("\n" + "=" * 70)
print("🎯 DIAGNOSIS")
print("=" * 70)

if max_v < 0.1:
    print("\n❌ PROBLEM: Still reading near 0V")
    print("\n   Possible causes:")
    print("   1. Wind vane NOT getting 3.3V power")
    print("      → Check Red dupont (Pin 6) is on powered rail")
    print("      → Verify RJ11 Pin 4 (Black wire) → RJ45 Pin 6")
    print()
    print("   2. Wind vane signal not reaching A0")
    print("      → Check White dupont (Pin 3) connects to A0")
    print("      → Verify RJ11 Pin 1 (Green wire) → RJ45 Pin 3")
    print()
    print("   3. Bad ground connection")
    print("      → Check Black dupont (Pin 4) to GND rail")
    print("      → Verify RJ11 Pin 2 (Yellow wire) → RJ45 Pin 4")
    print()
    print("   4. Faulty wind vane")
    print("      → Test with multimeter: Black wire should be 3.3V")
    print("      → Green wire should vary 0.25V-3.0V when rotated")

elif min_v < 0.2 or max_v < 2.5:
    print("\n⚠️  PARTIAL: Getting voltage but range is low")
    print(f"   Expected 0.25V-3.00V, got {min_v:.3f}V-{max_v:.3f}V")
    print("\n   Possible causes:")
    print("   1. Weak power supply - check 3.3V rail voltage")
    print("   2. High resistance in wiring")
    print("   3. Wrong resistor value in voltage divider")
    print("      → Should be 10kΩ between signal and A0")

elif min_v >= 0.2 and max_v >= 2.5:
    print("\n✅ SUCCESS: Wind vane is working correctly!")
    print(f"\n   Voltage range: {min_v:.3f}V - {max_v:.3f}V")
    print("   This is within expected parameters.")
    print("\n   Next steps:")
    print("   1. If this works but your main wiring doesn't,")
    print("      the problem is in the CAT6 cable path")
    print("   2. Check continuity of each wire in the CAT6")
    print("   3. Verify RJ45 breakout 2 connections")

else:
    print(f"\n⚠️  UNCLEAR: Unexpected results")
    print(f"   min={min_v:.3f}V, max={max_v:.3f}V, avg={avg_v:.3f}V")

print("\n" + "=" * 70)
