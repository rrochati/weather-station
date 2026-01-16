#!/usr/bin/env python3
"""
Basic ADS1115 (DFR0553) Test
Tests all 4 channels to verify the ADC is working
"""
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import time

print("🔬 ADS1115 (DFR0553) Basic Test")
print("=" * 70)

# Initialize I2C
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    print("✅ I2C bus initialized")
except Exception as e:
    print(f"❌ I2C initialization failed: {e}")
    exit(1)

# Initialize ADS1115
try:
    ads = ADS1115(i2c)
    print("✅ ADS1115 found at address 0x48")
except Exception as e:
    print(f"❌ ADS1115 initialization failed: {e}")
    print("   Run: i2cdetect -y 1")
    exit(1)

# Set gain (±4.096V range)
ads.gain = 1
print("✅ Gain set to 1 (±4.096V range)")

print("\n" + "=" * 70)
print("📊 Testing All 4 Channels")
print("=" * 70)

# Test all channels
channels = [
    (0, "A0 (Wind Vane)"),
    (1, "A1"),
    (2, "A2"),
    (3, "A3")
]

print("\n⚠️  Disconnect wind vane for baseline test")
input("Press Enter to continue...")

print("\n🔍 Channel readings (should all be near 0V when nothing connected):\n")

for channel_num, channel_name in channels:
    try:
        chan = AnalogIn(ads, channel_num)
        readings = []
        
        # Take 5 readings
        for _ in range(5):
            readings.append(chan.voltage)
            time.sleep(0.1)
        
        avg = sum(readings) / len(readings)
        min_v = min(readings)
        max_v = max(readings)
        
        print(f"   {channel_name}:")
        print(f"      Average: {avg:+.4f}V")
        print(f"      Range: {min_v:+.4f}V to {max_v:+.4f}V")
        
        if abs(avg) < 0.01:
            print(f"      ✅ Normal (near 0V)")
        else:
            print(f"      ⚠️  Unexpected voltage")
        print()
        
    except Exception as e:
        print(f"   ❌ Channel {channel_num} error: {e}\n")

print("=" * 70)
print("🧪 Test A0 with External Voltage")
print("=" * 70)

print("\n📋 Connect test voltages to A0 and verify readings:")
print("   • Connect A0 to GND → Should read ~0V")
print("   • Connect A0 to 3.3V → Should read ~3.3V")
print("   • Connect wind vane → Should vary 0.25V-3.0V when rotated")

print("\n1️⃣  Connect A0 to GND")
input("   Press Enter when ready...")

#chan0 = AnalogIn(ads, 0)
chan0 = AnalogIn(ads, 1)
readings = []
for i in range(5):
    v = chan0.voltage
    readings.append(v)
    print(f"   Reading {i+1}: {v:.4f}V")
    time.sleep(0.2)

avg_gnd = sum(readings) / len(readings)
print(f"\n   Average: {avg_gnd:.4f}V")
if abs(avg_gnd) < 0.05:
    print("   ✅ Good - reads near 0V when grounded")
else:
    print(f"   ❌ Problem - should be near 0V, got {avg_gnd:.4f}V")

print("\n2️⃣  Connect A0 to 3.3V power rail")
input("   Press Enter when ready...")

readings = []
for i in range(5):
    v = chan0.voltage
    readings.append(v)
    print(f"   Reading {i+1}: {v:.4f}V")
    time.sleep(0.2)

avg_3v3 = sum(readings) / len(readings)
print(f"\n   Average: {avg_3v3:.4f}V")
if 3.2 < avg_3v3 < 3.4:
    print("   ✅ Good - reads ~3.3V when connected to power")
else:
    print(f"   ❌ Problem - should be ~3.3V, got {avg_3v3:.4f}V")

print("\n3️⃣  Connect wind vane and rotate it")
input("   Press Enter when ready...")

print("\n🔄 Rotate the vane slowly...\n")
readings = []
for i in range(20):
    v = chan0.voltage
    readings.append(v)
    bar = "█" * int(v * 10) if v > 0 else ""
    print(f"   Reading {i+1:2d}: {v:.3f}V {bar}")
    time.sleep(0.5)

min_v = min(readings)
max_v = max(readings)
print(f"\n   Range: {min_v:.3f}V to {max_v:.3f}V")
if max_v > 0.25:
    print("   ✅ Wind vane is producing voltage!")
else:
    print("   ❌ Still reading near 0V - vane not powered or not connected")

print("\n" + "=" * 70)
print("📋 SUMMARY")
print("=" * 70)
print(f"\n   A0 → GND test: {avg_gnd:.4f}V {'✅' if abs(avg_gnd) < 0.05 else '❌'}")
print(f"   A0 → 3.3V test: {avg_3v3:.4f}V {'✅' if 3.2 < avg_3v3 < 3.4 else '❌'}")
print(f"   Wind vane range: {min_v:.3f}V - {max_v:.3f}V {'✅' if max_v > 0.25 else '❌'}")

if abs(avg_gnd) < 0.05 and 3.2 < avg_3v3 < 3.4:
    print("\n✅ ADS1115 A0 channel is working correctly!")
    if max_v < 0.25:
        print("\n⚠️  But wind vane shows no voltage:")
        print("   → Check wind vane power (Black wire should be 3.3V)")
        print("   → Check wind vane signal (Green wire to A0)")
        print("   → Verify voltage divider circuit (10kΩ resistor + 100nF cap)")
else:
    print("\n❌ ADS1115 A0 channel has issues - check connections")

print("\n" + "=" * 70)
