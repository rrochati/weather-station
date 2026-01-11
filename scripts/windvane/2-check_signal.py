import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import time

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
ads.gain = 1

# Test different channels to see what we're getting
print("Testing all ADS1115 channels:\n")

chan0 = AnalogIn(ads, 0)  # A0
chan1 = AnalogIn(ads, 1)  # A1
chan2 = AnalogIn(ads, 2)  # A2
chan3 = AnalogIn(ads, 3)  # A3

for i in range(5):
    print(f"Reading {i+1}:")
    print(f"  A0: {chan0.voltage:6.3f}V")
    print(f"  A1: {chan1.voltage:6.3f}V")
    print(f"  A2: {chan2.voltage:6.3f}V")
    print(f"  A3: {chan3.voltage:6.3f}V")
    print()
    time.sleep(1)

print("If A0 is stuck at 3.3V, the vane signal isn't connected properly")
