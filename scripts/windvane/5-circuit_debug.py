import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
ads.gain = 1
#chan = AnalogIn(ads, 0)
chan = AnalogIn(ads, 1)

print("IMPORTANT TEST:")
print("===============")
print(f"Current A0 reading: {chan.voltage:.3f}V\n")

print("Now DISCONNECT the Green wire from the wind vane")
print("(leave everything else connected)")
print()
input("Press Enter after you've disconnected the Green wire...")

print(f"A0 with Green disconnected: {chan.voltage:.3f}V")
print()
print("If voltage stays at 3.3V → 10kΩ resistor is pulling it high")
print("If voltage drops to 0V → Problem is elsewhere")
print()
print("Now RECONNECT the Green wire")
input("Press Enter after reconnecting...")
print(f"A0 with Green reconnected: {chan.voltage:.3f}V")
