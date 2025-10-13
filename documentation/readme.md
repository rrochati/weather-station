# DFRobot BME280 I²C (temp/pressure/humidity) setup

---

## Board Overview
Num	Label	Description
1	+	3.3~5V
2	-	GND
3	C	SCL
4	D	SDA

---

## ⚙️ Hardware and Wiring
⚡ Wiring the BME280 (I²C Mode)

Here’s the correct wiring for Raspberry Pi 5 (or 4, same pinout):

BME280 Pin	Raspberry Pi Pin	GPIO #	Notes
VIN	3.3V (pin 1)	–	Power
GND	GND (pin 6)	–	Ground
SCL	SCL (pin 5)	GPIO3	Clock
SDA	SDA (pin 3)	GPIO2	Data

🧠 Important:
Use the 3.3V pin, not 5V — the BME280 is a 3.3 V device.
Use Dupont jumper wires (female–female if using header pins).
Double-check orientation: GND next to VIN is a good sanity check.

---

📚 References
- [Gravity: I2C BME280 Environmental Sensor product page] (https://www.dfrobot.com/product-1606.html?srsltid=AfmBOoqBBbryo_8s4nCuDduqtIjZssJWkl8rQ9-llZ0v9O4pBimLCSLX)
- [Product wiki] (https://wiki.dfrobot.com/Gravity__I2C_BME280_Environmental_Sensor__Temperature,_Humidity,_Barometer__SKU__SEN0236)
- [DFRobot_BME280 git (for arduino] (https://github.com/DFRobot/DFRobot_BME280/)
- [BME280 Final data sheet (PDF)] (https://dfimg.dfrobot.com/nobody/wiki/08b27f9827b4182a692b7069958dc81f.pdf)
