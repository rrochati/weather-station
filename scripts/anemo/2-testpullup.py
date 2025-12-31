import lgpio
gpio_handle = lgpio.gpiochip_open(0)
lgpio.gpio_claim_input(gpio_handle, 17, lgpio.SET_PULL_UP)
state = lgpio.gpio_read(gpio_handle, 17)
print(f"GPIO17 with pull-up enabled: {state}")
print("Expected: 1 (HIGH)")
if state == 1:
    print("✅ Pull-up is working! Reconnect the Red wire and test.")
lgpio.gpiochip_close(gpio_handle)
