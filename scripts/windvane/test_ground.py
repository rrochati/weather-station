import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import time

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
ads.gain = 1
chan = AnalogIn(ads, 0)

print("🌬️  Testing wind vane after ground fix\n")
print("Slowly rotate the vane through all positions...\n")

voltages = []
for i in range(20):
    v = chan.voltage
    voltages.append(v)
    print(f"Reading {i+1:2d}: {v:.3f}V")
    time.sleep(1)

print(f"\n📊 Results:")
print(f"   Min voltage: {min(voltages):.3f}V (expected: ~0.252V)")
print(f"   Max voltage: {max(voltages):.3f}V (expected: ~2.973V)")
print(f"   Range: {max(voltages) - min(voltages):.3f}V")

if min(voltages) < 0.5 and max(voltages) > 2.5:
    print("   ✅ Wind vane is working correctly!")
else:
    print("   ⚠️  Still having issues - check Yellow wire ground connection")
