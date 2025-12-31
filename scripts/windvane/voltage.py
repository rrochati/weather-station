# Measure voltage directly with multimeter if available:
# Between Green wire and Yellow wire = should read 0.2V-3.0V

import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import time

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
ads.gain = 1  # ±4.096V range

chan0 = AnalogIn(ads, 0)  # A0

print('Testing wind vane voltage...')
print('Rotate vane slowly and watch for changes\n')

for i in range(10):
    voltage = chan0.voltage
    raw = chan0.value
    print(f'Reading {i+1}: {voltage:6.3f}V (raw: {raw:6d})')
    time.sleep(1)

print('\nExpected: 0.252V to 2.973V')
print('If still negative/zero, check ground connections!')
