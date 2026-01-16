#!/usr/bin/env python3
"""
Wind Vane Circuit Diagnostic
Helps identify wiring/circuit issues

The problem: Pi reads 3.29V (full power rail) instead of 0.25V-2.97V
This means the voltage divider is not working.
"""

import time
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

print("=" * 70)
print("🔧 WIND VANE CIRCUIT DIAGNOSTIC")
print("=" * 70)
print()
print("Problem identified: Pi reads 3.29V (power rail) instead of variable voltage")
print("Expected: 0.25V - 2.97V varying with wind vane rotation")
print()

# Initialize
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
ads.gain = 1
#chan0 = AnalogIn(ads, 0)
chan0 = AnalogIn(ads, 1)

print("=" * 70)
print("TEST 1: Baseline Reading (with everything connected)")
print("=" * 70)
print()

readings = []
for i in range(10):
    v = chan0.voltage
    readings.append(v)
    print(f"Reading {i+1}: {v:.4f}V")
    time.sleep(0.3)

avg = sum(readings) / len(readings)
print(f"\nAverage: {avg:.4f}V")

if avg > 3.2:
    print("❌ CONFIRMED: Reading full 3.3V power rail")
    print()
    print("This means the 10kΩ voltage divider is NOT working.")
    print()
else:
    print("✅ Voltage is in expected range")

print()
print("=" * 70)
print("TEST 2: Physical Connection Check")
print("=" * 70)
print()
print("Please verify your breadboard connections:")
print()
print("Circuit should be:")
print("  3.3V Power → 10kΩ resistor → Junction (A) → 100nF cap → GND")
print("                                    ↓")
print("                              Wind Vane Signal")
print("                                    ↓")
print("                               ADS1115 A0")
print()
print("Current wiring according to your docs:")
print("  • Power Rail → Row 17A (10kΩ leg 1)")
print("  • Row 17B (10kΩ leg 2) → Row 20B (junction)")
print("  • Row 20C (100nF leg 1) → ADS1115 A0 (20D)")
print("  • Row 20A → Wind Vane Orange wire")
print()

input("Press Enter to continue to disconnection tests...")

print()
print("=" * 70)
print("TEST 3: Disconnect Wind Vane Signal")
print("=" * 70)
print()
print("👉 Physically DISCONNECT the Orange wire (wind vane signal) from Row 20A")
print("   (Leave everything else connected)")
print()
input("Press Enter when disconnected...")

readings = []
for i in range(5):
    v = chan0.voltage
    readings.append(v)
    print(f"Reading {i+1}: {v:.4f}V")
    time.sleep(0.3)

avg_disconnected = sum(readings) / len(readings)
print(f"\nAverage: {avg_disconnected:.4f}V")

if avg_disconnected > 3.2:
    print("❌ Still reading 3.3V with vane disconnected!")
    print()
    print("This means the problem is NOT the wind vane.")
    print("The issue is in your voltage divider circuit itself.")
    print()
    print("LIKELY CAUSES:")
    print("  1. 10kΩ resistor is not actually connected")
    print("  2. Wire from Row 17B to Row 20B is missing/loose")
    print("  3. ADS1115 A0 is connected to wrong row (directly to power)")
    print()
else:
    print("✅ Voltage dropped when vane disconnected - good!")
    print("   Problem is in the wind vane signal connection")

print()
print("=" * 70)
print("TEST 4: Check Power Rail Connection")
print("=" * 70)
print()
print("👉 Keep wind vane disconnected")
print("👉 DISCONNECT the 10kΩ resistor from the 3.3V power rail (Row 17A)")
print()
input("Press Enter when disconnected...")

readings = []
for i in range(5):
    v = chan0.voltage
    readings.append(v)
    print(f"Reading {i+1}: {v:.4f}V")
    time.sleep(0.3)

avg_no_power = sum(readings) / len(readings)
print(f"\nAverage: {avg_no_power:.4f}V")

if abs(avg_no_power) < 0.1:
    print("✅ Voltage near 0V - good! This is correct behavior.")
else:
    print(f"⚠️  Unexpected voltage: {avg_no_power:.4f}V")

print()
print("=" * 70)
print("DIAGNOSTIC SUMMARY")
print("=" * 70)
print()
print(f"With everything connected:     {avg:.4f}V {'❌ TOO HIGH' if avg > 3.2 else '✅ OK'}")
print(f"With vane disconnected:        {avg_disconnected:.4f}V {'❌ STILL HIGH' if avg_disconnected > 3.2 else '✅ OK'}")
print(f"With power disconnected:       {avg_no_power:.4f}V {'✅ OK' if abs(avg_no_power) < 0.1 else '⚠️  UNEXPECTED'}")
print()

if avg > 3.2 and avg_disconnected > 3.2:
    print("🔍 DIAGNOSIS:")
    print()
    print("The ADS1115 A0 is somehow connected DIRECTLY to the 3.3V power rail,")
    print("bypassing the 10kΩ voltage divider completely.")
    print()
    print("SOLUTION - Check these connections carefully:")
    print()
    print("1. Verify 10kΩ resistor is actually in the circuit:")
    print("   • One leg in Row 17A (connected to 3.3V power rail)")
    print("   • Other leg in Row 17B")
    print()
    print("2. Verify Row 17B connects to Row 20B:")
    print("   • Use a jumper wire from 17B to 20B")
    print()
    print("3. Verify ADS1115 A0 pin connects to Row 20D:")
    print("   • This is the same row as the junction point (20A/B/C/D/E)")
    print()
    print("4. Verify 100nF capacitor:")
    print("   • One leg in Row 20C (same junction)")
    print("   • Other leg in Row 21C")
    print("   • Row 21C connected to GND rail")
    print()
    print("5. Wind vane Orange wire goes to Row 20A")
    print("   • Same junction as everything else on row 20")
    print()
    print("The key: Row 20 is the JUNCTION where:")
    print("  • 10kΩ resistor (from power) meets")
    print("  • Wind vane signal (Orange wire) meets")
    print("  • 100nF cap (to ground) meets")
    print("  • ADS1115 A0 input meets")
    print()
    print("Currently, it appears A0 is seeing 3.3V directly, which means")
    print("it's connected before the 10kΩ resistor, not after it.")

print()
print("=" * 70)
print("👉 RECONNECT everything before running tests again")
print("=" * 70)
