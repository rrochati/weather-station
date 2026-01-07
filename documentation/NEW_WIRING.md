# New wiring

## ⚙️ Hardware and Wiring

***SparkFun Weather Meter Kit Anemometer Wiring***

As the wind vane setup is more complex, let's begin with anemometer.

## 🎯 **Anemometer-Only Setup (Minimal Start):**

### **What You Need:**

### Hardware:
- Anemometer and wind vane from your SparkFun kit
- 4 RJ45 breakouts (i used  a simple one for breakout 2 and Goobay Keystone Module RJ45 CAT 6 for 2-4)
- A peace of CAT6 cable without the connectors
- An CAT6 extention
- Opitional: 2 Waterproof junction boxes


### Top level wiring
**This guide will alse include wiring for the rain bucket:**
- RJ45 breakout 1   ---> Breadboard/Pi
- RJ45 breakout 1   ---> CAT 6 extension
- CAT 6 extension   ---> RJ45 breakout 2 (inside waterproof junction box 1)
- RJ45 breakout 2   ---> CAT6 Cable (inside  waterproof junction box 1)
- CAT6 Cable        ---> RJ45 breakout 3 (Anemometer/Vane) (inside waterproof junction box 2)
- CAT6 Cable        ---> RJ45 breakout 4 (Rain bucket) (inside waterproof junction box 2)
- Wind Vane RJ 11   ---> RJ45 breakout 3 (inside waterproof junction box 2)
- Rain bucket RJ 11 ---> RJ45 breakout 4 (inside waterproof junction box 2)
- Anemometer RJ 11  ---> Wind Vane RJ11 female

#### RJ45 breakout 1   ---> Breadboard/Pi
    | RJ45 breakout pin| DuPont Cable | Function      | Connect to   |
    |------------------|--------------| ------------- | ------------ |
    | Pin 1	           | Red          | Power         | Power Rail 2 |
    | Pin 2	           | Black        | GND           | GND Rail 13  |
    | Pin 3	           | Blue         | GPIO3 (Clock) | 2A           |
    | Pin 4	           | Green        | GPIO2 (Data)  | 4A           |
    | Pin 5	           | Green        | Vane Signal   | 20A          |
    | Pin 6	           | N/A          |               |              |
    | Pin 7	           | Red          | Anemo Signal  | 14D          |
    | Pin 8	           | TBD          | Rain Signal   |              |

#### RJ45 breakout 2   ---> CAT6 Cable
    | RJ45 breakout pin| CAT6 Color   | Function      | Extension    | Connect to |
    |------------------|--------------| ------------- | ------------ |----------- |
    | Pin 1	           | White/Orange | Power         | DuPont Red   | BME280 +   |
    | Pin 2	           | Orange       | GND           | DuPont Black | BME280 +   |
    | Pin 3	           | White/Green  | GPIO3 (Clock) | DuPont Blue  | BME280 SCL |
    | Pin 4	           | Blue         | GPIO2 (Data)  | DuPont Green | BME280 SDA |
    | Pin 5	           | White/Blue   | Vane Signal   |     ---      | DFR0553 A0 |
    | Pin 6	           | Green        | Not in use    |     ---      |            |
    | Pin 7	           | White/Brown  | Anemo Signal  |     ---      | GPIO17     |
    | Pin 8	           | Brown        | Rain Signal   |     ---      |            |

#### RJ45 breakout 3 (Anemometer/Vane)
    ***SparkFun Weather Meter RJ11 Connector Pinout***
    The Connector Pinout is different from the RJ11 standard:
    
    ![alt text](images/rj11-pinout-diagram.jpg)

    When looking at the contact part of the connector: Green, Yellow, Red, Black (pins 1-4)

    **RJ11 to RJ45 Mapping:**
    | RJ11 Pin | Wire Color | Function           | → | RJ45 Pin | CAT6 Color   | Notes                         |
    |----------|------------|--------------------|---|----------|--------------|-------------------------------|
    | Pin 1    | Green      | Wind Vane Signal   | → | Pin 3    | White/Blue   | Analog voltage, To DFR0553 A0 |
    | Pin 2    | Yellow     | Ground (GND)       | → | Pin 4    | Orange       | Shared ground                 |
    | Pin 3    | Red        | Anemometer Signal  | → | Pin 5    | White/Brown* | Reed switch, To Pi GPIO17     |
    | Pin 4    | Black      | Power (3.3V)       | → | Pin 6    | White/Orange | Powers resistors              |
    * It should have be the green, but it is not working


#### RJ45 breakout 4 (Rain Bucket) (tbd)
    | RJ45 breakout pin| CAT6 Color   | Function    | Notes.          |
    |------------------|--------------| ------------| --------------- |
    | Pin 1	           |              |             |                 |
    | Pin 2	           |              |             |                 |
    | Pin 3	           |              |             |                 |
    | Pin 4	           | Brown        | Rain Signal |                 |
    | Pin 5	           | Orange       | GND         | From breakout 3 |
    | Pin 6	           |              |             |                 |
    | Pin 7	           |              |             |                 |
    | Pin 8	           |              |             |                 |




--------
#### Dump o temp text
#### Wind Vane RJ 11 ---> RJ45 breakout 1 ####
    | RJ11 Pin| Wire Color | Function                | Connection                     | RJ45 breakout pin | CAT6 wire color |
    |---------|------------|-------------------------| ------------------------------ | ----------------- | --------------- |
    | Pin 1	  | Black      | VCC (Power)             | Connect to 3.3V                | Pin 3	          | White/Green     |
    | Pin 2	  | Red        | Wind Speed (Anemometer) | Connect to Pi Pin 11 (GPIO 17) | Pin 4	          | Green           |
    | Pin 3	  | Yellow     | Ground                  | Connect to GND                 | Pin 5             | Blue            |
    | Pin 4	  | Green	   | Wind Vane Signal        | Connect to DFR0553 A0          | Pin 6             | White/Blue      |


#### Rain bucket RJ 11 ---> RJ45 breakout 2 #### 
    | RJ11 Pin | Wire Color | Function    | Pi Connection     | RJ45 breakout pin | CAT6 wire color |
    |----------|------------|-------------|-------------------| ----------------- | --------------- |
    | Pin 2    | Red        | Rain Signal | Pi Pin 13 (GPIO27)| Pin 4	          | Orange          |
    | Pin 3    | Yellow     | Ground      | Pi Pin 6 (GND)    | Pin 5	          | White/Orange    |

#### CAT6 Cable ---> RJ45 breakout 3
    | CAT6 wire color | RJ45 breakout pin |
    |-----------------|-------------------|
    | White/Orange    | Pin 1	          |
    | Orange          | Pin 2	          |
    | White/Green     | Pin 3	          |
    | Green           | Pin 4	          |
    | Blue            | Pin 5	          |
    | White/Blue      | Pin 6	          |
    | N/A             | Pin 7	          |
    | N/A             | Pin 8	          |

#### CAT6 extension collor pattern
    | Extension pin | CAT6 wire color | 
    |---------------|-----------------|
    | Pin 1	        | White/Orange    |
    | Pin 2	        | Orange          |
    | Pin 3	        | White/Green     |
    | Pin 4	        | Green           |
    | Pin 5	        | Blue            |
    | Pin 6	        | White/Blue      |
    | Pin 7	        | White/Brown     |
    | Pin 8	        | Bronw           |

