# New wiring

## Pre requisites
- Digital multimeter
- Solder iron and flux
- Soldering supports

## ⚙️ Hardware and Wiring

***SparkFun Weather Meter Kit Anemometer Wiring***

### **What You Need:**

### Hardware:
- Anemometer and wind vane from your SparkFun kit
- 5 RJ45 breakouts (i used simple ones for breakout test and 1, and Goobay Keystone Module RJ45 CAT 6 for 2-4)
- A peace of CAT6 cable without the connectors
- An CAT6 extention
- Opitional: 2 Waterproof junction boxes

### Top level wiring
**This guide will alse include wiring for the rain bucket:**
- RJ45 breakout 1   ---> Breadboard/Pi
- RJ45 breakout 1   ---> CAT 6 extension
- CAT 6 extension   ---> RJ45 breakout 2 (inside waterproof junction box 1)
- RJ45 breakout 2   ---> CAT6 Cable (inside waterproof junction box 1)
- CAT6 Cable        ---> RJ45 breakout 3 (Anemometer/Vane) (inside waterproof junction box 2)
- CAT6 Cable        ---> RJ45 breakout 4 (Rain bucket) (inside waterproof junction box 2)
- Wind Vane RJ 11   ---> RJ45 breakout 3 (inside waterproof junction box 2)
- Rain bucket RJ 11 ---> RJ45 breakout 4 (inside waterproof junction box 2)
- Anemometer RJ 11  ---> Wind Vane RJ11 female

### Identify connections
This RJ11 to RJ45 is tricky. My suggestion, bring the whole kit mounted inside (including the stand), next to you work bench and test with the multimeter.
Check ANEMO_VANE_README.md for details

### Procedure
#### For each connection, test continuity using the multimeter
Trust me, it will save you a lot of troubleshoot time

#### RJ45 breakout 1   ---> Breadboard/Pi
    | RJ45 breakout pin| DuPont Cable | Function      | Connect to   |
    |------------------|--------------| ------------- | ------------ |
    | Pin 1	           | Red          | Power         | Power Rail 2 |
    | Pin 2	           | Black        | GND           | GND Rail 2   |
    | Pin 3	           | Blue         | GPIO3 (Clock) | 2B           |
    | Pin 4	           | Green        | GPIO2 (Data)  | 4B           |
    | Pin 5	           | Purple       | Vane Signal   | 20A/D        |
    | Pin 6	           | Orange       |               |              |
    | Pin 7	           | White        | Anemo Signal  | 14D          |
    | Pin 8	           | Brown        | Rain Signal   |              |

#### RJ45 breakout 2   ---> CAT6 Cable
    | RJ45 breakout pin| CAT6 Color   | Function      | Extension*   | Connect to |
    |------------------|--------------| ------------- | ------------ |----------- |
    | Pin 1	           | White/Orange | Power         | DuPont Red   | BME280 +   |
    | Pin 2	           | Orange       | GND           | DuPont Black | BME280 +   |
    | Pin 3	           | White/Green  | GPIO3 (Clock) | DuPont Blue  | BME280 SCL |
    | Pin 4	           | Blue         | GPIO2 (Data)  | DuPont Green | BME280 SDA |
    | Pin 5	           | White/Blue   | Vane Signal   | DuPont Purple| DFR0553 A0 |
    | Pin 6	           | Green        | Not in use    | DuPont Orange|            |
    | Pin 7	           | White/Brown  | Anemo Signal  | DuPont White | GPIO17     |
    | Pin 8	           | Brown        | Rain Signal   | DuPont Brown |            |
     * You will need to iron sold these


#### RJ45 breakout 3 (Anemometer/Vane)
**SparkFun Weather Meter RJ11 Connector Pinout**
The Connector Pinout is different from the RJ11 standard. Check Check ANEMO_VANE_README.md for details

When looking at the contact part of the connector: Green, Yellow, Red, Black (pins 1-4)

    | RJ11 Pin | Wire Color | Function           | RJ45 Pin | CAT6 Color   | Notes                      |
    |----------|------------|--------------------|----------|--------------|----------------------------|
    | Pin 1    | Green      | Ground (GND)       | Pin 3    | Orange       | Shared ground              |
    | Pin 2    | Yellow     | Anemometer Signal  | Pin 4    | White/Brown  | Reed switch, to GPIO17     |
    | Pin 3    | Red        | Power (3.3V)       | Pin 5    | White/Orange | Powers resistors           |
    | Pin 4    | Black      | Wind Vane Signal   | Pin 6    | White/Blue   | Analog voltage, To DFR0553 |

 Wind Vane Signal   

During this set up I had a few conectivity problems. The last one is about grounding.
The continuity test from CAT6 GND wire (Orange) to breadboard is fine.
This raises questions about Breaktou 3 connections to Orange wire.
To dimiss this doubt I got a peace of RJ11 cable (about 20 cm) with 4 wires and connector. Decaped a good part of rubber nad a part of each wire.
Connect it to Breakout 3 and test continuity.

    | RJ11 Pin | Wire Color | RJ11 wire| Color  |
    |----------|------------|----------|--------|
    | Pin 1    | Green      | Pin 1    | Yellow |
    | Pin 2    | Yellow     | Pin 2    | Blue   |
    | Pin 3    | Red        | Pin 3    | Rosé   |
    | Pin 4    | Black      | Pin 4    | White  |

All have continuity, but the vane does not work.
Cry in your bed

#### RJ45 breakout 4 (Rain Bucket)
    | RJ45 breakout pin| CAT6 Color   | Function    | Notes           |
    |------------------|--------------| ------------| --------------- |
    | Pin 1	           |              |             |                 |
    | Pin 2	           |              |             |                 |
    | Pin 3	           |              |             |                 |
    | Pin 4	           | Orange*      | GND         | From breakout 3 |
    | Pin 5	           | Brown*       | Rain Signal |                 |
    | Pin 6	           |              |             |                 |
    | Pin 7	           |              |             |                 |
    | Pin 8	           |              |             |                 |
    * Decap a long peace from CAT6 cable or iron sold an extension here

## Anemometer and wind vane split
As wind vane is not working although wiring seams right and have continity, I will split anemometer from if and troubleshoot further later.
This sections describes the changes made.

- Disconect anemo from vane
- Connect anemo to a RJ45/RJ11 splice
- Connect a RJ11 cable to other end of splice
- Iron sold the connections

Anemo connecter have 2 wires in the middle: green and red. These are ground and anemo signal as we learned before.
The RJ11 cable I'm using have 4 cables: Yellow, Blue, Rosé, White.
I tested continuity on Blue + Rosé and I have the expected intermitent beep.

So, let's test it on Pi
First, make sure the GPIO is working:

```bash
~/weather-station/scripts/anemo $ python3 1-gpio_test.py 
🔍 TESTING GPIO PULL-UP FUNCTIONALITY
==================================================
This test will verify if internal pull-ups work correctly
Make sure GPIO17 (Pin 11) is DISCONNECTED for accurate testing

Is GPIO17 (Pin 11) disconnected? (y/n): y
🔧 GPIO PULL-UP VERIFICATION TEST
==================================================
📝 Test 1: GPIO with NO pull-up (floating)
   Expected: Should read random/unstable values when disconnected
   Readings (floating input):
     Reading 1: 0
     Reading 2: 0
     Reading 3: 0
     Reading 4: 0
     Reading 5: 0
     Reading 6: 0
     Reading 7: 0
     Reading 8: 0
     Reading 9: 0
     Reading 10: 0
   📊 Result: All readings are 0 (stable)

📝 Test 2: GPIO with INTERNAL pull-up
   Expected: Should read HIGH (1) consistently
   Readings (with internal pull-up):
     Reading 1: 1
     Reading 2: 1
     Reading 3: 1
     Reading 4: 1
     Reading 5: 1
     Reading 6: 1
     Reading 7: 1
     Reading 8: 1
     Reading 9: 1
     Reading 10: 1

📝 Test 3: Manual connection test
   Instructions:
   1. Keep pin disconnected - should read HIGH
   2. Connect GPIO17 to GND directly - should read LOW
   3. Disconnect again - should read HIGH

   Press Enter when ready to start live monitoring...

🎯 Live monitoring (touch GPIO17 to GND to test):
   Press Ctrl+C to stop
   [13:21:29] Change: -1 → 1 (GND disconnected)
   [13:21:37] Change: 1 → 0 (GND connected)
   [13:21:37] Change: 0 → 1 (GND disconnected)
   [13:21:38] Change: 1 → 0 (GND connected)
   [13:21:38] Change: 0 → 1 (GND disconnected)
   [13:21:38] Change: 1 → 0 (GND connected)
   [13:21:38] Change: 0 → 1 (GND disconnected)
   [13:21:38] Change: 1 → 0 (GND connected)
   [13:21:38] Change: 0 → 1 (GND disconnected)
   [13:21:38] Change: 1 → 0 (GND connected)
   [13:21:39] Change: 0 → 1 (GND disconnected)
   [13:21:39] Change: 1 → 0 (GND connected)
   [13:21:39] Change: 0 → 1 (GND disconnected)
   [13:21:39] Change: 1 → 0 (GND connected)
   [13:21:39] Change: 0 → 1 (GND disconnected)
   [13:21:39] Change: 1 → 0 (GND connected)
   [13:21:39] Change: 0 → 1 (GND disconnected)
   [13:21:39] Change: 1 → 0 (GND connected)
   [13:21:39] Change: 0 → 1 (GND disconnected)
   [13:21:40] Change: 1 → 0 (GND connected)
   [13:21:40] Change: 0 → 1 (GND disconnected)
   [13:21:40] Change: 1 → 0 (GND connected)
   [13:21:40] Change: 0 → 1 (GND disconnected)
   [13:21:40] Change: 1 → 0 (GND connected)
   [13:21:40] Change: 0 → 1 (GND disconnected)
   [13:21:41] Change: 1 → 0 (GND connected)
   [13:21:41] Change: 0 → 1 (GND disconnected)
   [13:21:41] Change: 1 → 0 (GND connected)
   [13:21:41] Change: 0 → 1 (GND disconnected)
   [13:21:42] Change: 1 → 0 (GND connected)
   [13:21:42] Change: 0 → 1 (GND disconnected)
   [13:21:42] Change: 1 → 0 (GND connected)
   [13:21:42] Change: 0 → 1 (GND disconnected)
ç^C
🛑 Test stopped by user
🧹 Cleaning up GPIO...
✅ Test completed!
🧹 Cleaning up GPIO...
```

The test the anemo itself:
```bash
~/weather-station/scripts/anemo $ python3 3-anemo_quick_test.py 
🔧 Anemometer Quick Diagnostic Test
============================================================
✅ GPIO chip opened
✅ GPIO17 claimed as input

📍 Current GPIO17 state: 0
   0 = LOW (ground), 1 = HIGH (3.3V/pull-up)
   ⚠️  Pin is LOW - this suggests:
      - Reed switch might be closed (magnet nearby), OR
      - Signal wire shorted to ground, OR
      - No pull-up resistance

============================================================
🔄 Monitoring for state changes...
   Spin the anemometer and watch for transitions
   Press Ctrl+C to stop
============================================================
⬆️  [1.712s] RISING edge (0→1) - Pulse #1
⬇️  [1.966s] FALLING edge (1→0)
⬆️  [2.520s] RISING edge (0→1) - Pulse #2
⬇️  [2.838s] FALLING edge (1→0)
⬆️  [3.371s] RISING edge (0→1) - Pulse #3
⬇️  [3.793s] FALLING edge (1→0)
⬆️  [3.892s] RISING edge (0→1) - Pulse #4
⬇️  [3.942s] FALLING edge (1→0)
⬆️  [4.031s] RISING edge (0→1) - Pulse #5
⬇️  [4.076s] FALLING edge (1→0)
⬆️  [4.180s] RISING edge (0→1) - Pulse #6
⬇️  [4.237s] FALLING edge (1→0)
⬆️  [4.337s] RISING edge (0→1) - Pulse #7
⬇️  [4.389s] FALLING edge (1→0)
⬆️  [4.506s] RISING edge (0→1) - Pulse #8
⬇️  [4.571s] FALLING edge (1→0)
⬆️  [4.683s] RISING edge (0→1) - Pulse #9
⬇️  [4.742s] FALLING edge (1→0)
⬆️  [4.873s] RISING edge (0→1) - Pulse #10
⬇️  [4.947s] FALLING edge (1→0)
⬆️  [5.074s] RISING edge (0→1) - Pulse #11
⬇️  [5.140s] FALLING edge (1→0)
⬆️  [5.290s] RISING edge (0→1) - Pulse #12
⬇️  [5.372s] FALLING edge (1→0)
⬆️  [5.517s] RISING edge (0→1) - Pulse #13
⬇️  [5.592s] FALLING edge (1→0)
⬆️  [5.761s] RISING edge (0→1) - Pulse #14
⬇️  [5.856s] FALLING edge (1→0)
⬆️  [6.020s] RISING edge (0→1) - Pulse #15
⬇️  [6.106s] FALLING edge (1→0)
⬆️  [6.299s] RISING edge (0→1) - Pulse #16
⬇️  [6.407s] FALLING edge (1→0)
^C

🛑 Test stopped by user

📊 Results:
   Total pulses: 16
   Test duration: 6.5s
   Pulse rate: 2.45 pulses/sec
   Estimated RPM: 146.7
   Wind speed: 1.63 m/s (5.9 km/h)
🔧 GPIO cleaned up
```

In my tests there were no difference between connecting Blue cable to GND and Rosé to anemo signal or vice-versa. So let's procced with this combination: Blue to GND and Rosé to signal.