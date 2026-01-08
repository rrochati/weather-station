#!/usr/bin/env python3
"""
Quick test to verify wind vane power connection
Measures voltage with vane disconnected vs connected
"""
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import time

print("🔌 Wind Vane Power Connection Test")
print("=" * 60)

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
ads.gain = 1  # ±4.096V range
chan = AnalogIn(ads, 0)  # A0 channel

print("\n📋 This test helps identify if the wind vane is getting power")
print("   Expected behavior:")
print("   • With vane DISCONNECTED: Should read ~0V")
print("   • With vane CONNECTED: Should read 0.2V - 3.0V (varies by position)")
print("\n" + "=" * 60)

print("\n⚠️  STEP 1: DISCONNECT the wind vane RJ11 connector")
input("   Press Enter when disconnected...")

readings = []
for i in range(5):
    v = chan.voltage
    readings.append(v)
    print(f"   Reading {i+1}: {v:.3f}V")
    time.sleep(0.5)

disconnected_avg = sum(readings) / len(readings)
print(f"\n   Average with vane disconnected: {disconnected_avg:.3f}V")

print("\n✅ STEP 2: RECONNECT the wind vane RJ11 connector")
print("   (Make sure it's fully seated)")
input("   Press Enter when connected...")

print("\n🔄 Rotate the vane slowly through different positions...")
time.sleep(2)

readings = []
for i in range(10):
    v = chan.voltage
    readings.append(v)
    print(f"   Reading {i+1}: {v:.3f}V")
    time.sleep(0.5)

connected_min = min(readings)
connected_max = max(readings)
connected_avg = sum(readings) / len(readings)

print("\n" + "=" * 60)
print("📊 RESULTS:")
print(f"   Disconnected average: {disconnected_avg:.3f}V")
print(f"   Connected range: {connected_min:.3f}V to {connected_max:.3f}V")
print(f"   Connected average: {connected_avg:.3f}V")
print("=" * 60)

# Diagnosis
if abs(disconnected_avg) < 0.1 and abs(connected_avg) < 0.1:
    print("\n❌ PROBLEM: Both readings are ~0V")
    print("\n🔍 Likely causes:")
    print("   1. Wind vane NOT POWERED - Check 3.3V connection to RJ11 Pin 4 (Black wire)")
    print("   2. At RJ45 breakout 3: Verify Black wire → White/Orange CAT6")
    print("   3. Trace White/Orange back to power source")
    print("   4. Use multimeter to verify 3.3V on wind vane Black wire")
    
elif abs(disconnected_avg) < 0.1 and connected_avg > 0.2:
    print("\n✅ GOOD: Wind vane is powered and working!")
    print(f"   Voltage range is normal ({connected_min:.3f}V - {connected_max:.3f}V)")
    
elif disconnected_avg > 0.1:
    print("\n⚠️  WARNING: Reading voltage when disconnected")
    print("   This suggests:")
    print("   - Floating input (add pull-down resistor)")
    print("   - Or interference on the signal line")

else:
    print("\n⚠️  UNCLEAR: Mixed results")
    print("   Check all connections and try again")
