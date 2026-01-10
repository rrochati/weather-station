# Troubleshoot steps

## For the vane:
The wiring sucks. Make shure it is wright:

#### Wind Vane RJ 11 ---> RJ45 breakout ####
    | RJ11 Pin| Wire Color | Function                | Connection *        | RJ45 breakout pin | Dupont color |
    |---------|------------|-------------------------| ------------------- | ----------------- | ------------ |
    | Pin 1	  | Black      | VCC (Power)             | 3.3V                | Pin 3	           | Red          |
    | Pin 2	  | Red        | Wind Speed (Anemometer) | Pi Pin 11 (GPIO 17) | Pin 4	           | Purple       |
    | Pin 3	  | Yellow     | Ground                  | GND                 | Pin 5             | Black        |
    | Pin 4	  | Green	   | Wind Vane Signal        | DFR0553 A0          | Pin 6             | Orange       |
***Check detailed instructions for connections***

The last problem with anemo was the pull-up that was not enabled
```python
        # Claim pin as input with pull-up
        lgpio.gpio_claim_input(gpio_handle, ANEMO_PIN, lgpio.SET_PULL_UP)
        lgpio.gpio_set_debounce_micros(gpio_handle, ANEMO_PIN, 10000)
        logger.info(f"✅ GPIO{ANEMO_PIN} claimed as input with pull-up enabled")
```

### New wiring
The new wiring introduced a lot of new problems.
It is documented under the wiring section.