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

    | RJ11 Pin | Wire Color | Function           | RJ45 Pin | CAT6 Color   | Notes                         |
    |----------|------------|--------------------|----------|--------------|-------------------------------|
    | Pin 1    | Green      | Wind Vane Signal   | Pin 3    | White/Blue   | Analog voltage, To DFR0553 A0 |
    | Pin 2    | Yellow     | Ground (GND)       | Pin 4    | Orange       | Shared ground                 |
    | Pin 3    | Red        | Anemometer Signal  | Pin 5    | White/Brown* | Reed switch, to GPIO17        |
    | Pin 4    | Black      | Power (3.3V)       | Pin 6    | White/Orange | Powers resistors              |
    * It should have be the green, but it is not working

During this set up I had a few conectivity problems. The last one is about grounding.
The continuity test from CAT6 GND wire (Orange) to protoboard is fine.
This raises questions about Breaktou 3 connections to Orange wire.
To dimiss this doubt I got a peace of RJ11 cable (about 20 cm) with 4 wires and connector. Decaped a good part of rubber nad a part of each wire.
Connect it to Breakout 3 and test continuity.

    | RJ11 Pin | Wire Color | Function           | RJ11 wire| Color  |
    |----------|------------|--------------------|----------|--------|
    | Pin 1    | Green      | Wind Vane Signal   | Pin 1    | Yellow |
    | Pin 2    | Yellow     | Ground (GND)       | Pin 2    | Blue   |
    | Pin 3    | Red        | Anemometer Signal  | Pin 3    | Rosé   |
    | Pin 4    | Black      | Power (3.3V)       | Pin 4    | White  |

All have continuity.
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