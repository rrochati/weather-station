# Weather station revival: Pi → breadboard → RJ45 breakout

Last updated: 2026-09-22

## Status at handover

**BME280 and anemometer: confirmed working by the user on 2026-09-22.** The indoor wiring map below remains unchanged. The user did not supply test commands, measured values, or logs; this is a user-reported functional confirmation, not an agent-run test or a calibration result.

**Rain bucket: connected but still unverified. Wind vane: out of scope.** The previously requested rail continuity result was not separately reported; do not let that historical pending check override the subsequent functional confirmation.

## Goal and scope

Revive a personal Raspberry Pi 5 weather station after a period offline. The Pi, breadboard, and RJ45 breakout are now mounted on an acrylic board. The goal is to reduce loose wiring by routing Pi connections through the breadboard to the breakout, using the breakout wire colours consistently.

The user says nothing from the Pi-side RJ45 breakout onward was changed. Preserve the existing outdoor cable and sensor-end wiring unless testing identifies a fault.

- BME280: confirmed working by the user.
- Anemometer: confirmed working by the user; wind-speed calculation accuracy remains to be verified.
- Wind vane: explicitly out of scope; previously not working.
- Rain bucket: brown signal connected through row 18; working condition remains unknown.

Work with the user **one small physical step at a time**. They explicitly asked to slow down. Record their actual placements rather than reverting to earlier proposed layouts. The user handles physical wiring; the agent guides and records it.

## Current connection map

All Pi pin numbers below are **physical 40-pin header numbers**, not BCM GPIO numbers. Breakout pin numbers refer to the **RJ45 breakout next to the breadboard**, called breakout 1 in NEW_WIRING.md. They must not be confused with terminals on the outdoor breakouts.

| Function | Wire colour | Pi physical pin → breadboard | Breadboard → RJ45 breakout |
|---|---|---|---|
| 3.3V | Red | 1 → positive rail, position 1 | Positive rail → breakout pin 1 |
| Ground | Black | 6 → ground rail, position 1 | Ground rail → breakout pin 2 |
| SDA / data / GPIO2 | Green | 3 → A1 | B1 → breakout pin 4 |
| SCL / clock / GPIO3 | Blue | 5 → A3 | B3 → breakout pin 3 |
| Anemometer signal / GPIO17 | White | 11 → A14 | C14 → breakout pin 7 |
| Rain-bucket signal / GPIO27 | Brown | 13 → A18 | B18 → breakout pin 8 |

The breadboard uses its dedicated positive and ground rails. On the A–E side, holes with the same row number are electrically connected. Thus A1/B1, A3/B3, A14/B14/C14, and A18/B18 form four separate signal nodes. Do not assume connections across the centre gap or across split power rails; verify continuity where necessary.

### Anemometer capacitor and pull-up

A **100nF ceramic capacitor** has been placed between:

- B14: anemometer signal, shared with A14 and C14.
- The ground rail connected to Pi physical pin 6.

The ceramic capacitor has no polarity. No external pull-up resistor was added. The intended pull-up is the Pi internal pull-up, which must be enabled in whichever test or application claims GPIO17. The reed switch closes the signal to common ground.

The 10kΩ resistor shown in the old workbook belongs to the wind-vane circuit. Do not add it merely because it appears in that historical layout.

### Rain-bucket connection

The brown wires connect Pi physical pin 13 (GPIO27) to A18, and breakout pin 8 to B18. The user moved both connections to **row 18**, superseding the proposed row 16. A18 and B18 share the same electrical node.

Each bucket tip should briefly close its reed switch between the signal and common ground. The software must enable the GPIO27 internal pull-up to 3.3V. No external resistor or capacitor has been added for rain. This connection is complete as reported by the user, but the switch, outdoor wiring, and rainfall measurements remain unverified.

### Connections left out

| Breakout pin | Colour | Current state |
|---|---|---|
| 5 | Purple | Disconnected; wind vane out of scope |
| 6 | Orange | Disconnected; unused |

Keep unused loose ends insulated. Pi physical pins 7, 8, and 9 are empty. Physical pin 13 / GPIO27 is now connected to the brown rain signal through row 18. The vane/ADS1115 circuit is excluded from the planned revival wiring; do not reconnect it for these tests.

## What was done in this session

1. Read the project README, wiring documents and diagrams, and relevant BME280, anemometer, rain, and station code. The repository was clean on branch dev at initial inspection.
2. Reviewed the user photo of the acrylic-mounted assembly and read the old wiring workbook. The photo could not establish electrical continuity or reliably verify all hidden terminal connections.
3. Agreed to retain dedicated power rails and use the breakout colours for the Pi-side wiring.
4. Corrected an initially reported white connection from Pi physical pin 9 to A1. Pin 9 is ground and would ground SDA at A1. The user subsequently confirmed the corrected connection: physical pin 11 to A14.
5. Recorded the user final clock placement as Pi physical pin 5 to A3, superseding earlier suggestions of A2. SDA remains physical pin 3 to A1.
6. Added the 100nF capacitor from B14 to ground.
7. Connected the breakout white signal to C14, black to ground, red to 3.3V, blue to B3, and green to B1. The user confirmed these steps.
8. Requested a power-off continuity check between 3.3V and ground. No result has been supplied.
9. Added the brown rain connection: Pi physical pin 13 → A18; breakout pin 8 → B18. The user confirmed moving the connections to row 18 after row 16 was initially proposed. Rain remains untested.

10. The user subsequently confirmed that the BME280 and anemometer are working. No test details or readings were provided. Rain remains unverified.

No sensor tests were run by the agent, no SSH connection was established by the agent, and no application or diagnostic code was changed by the agent during the session. This handover file is the documentation update requested by the user.

## Historical sources and conflicts

- `documentation/NEW_WIRING.md`: source of the Pi-side breakout mapping: 1 red power, 2 black ground, 3 blue SCL, 4 green SDA, 5 purple vane, 6 orange unused, 7 white anemometer, 8 brown rain.
- `documentation/BME280_README.md`: BME280 terminal mapping: + power, − ground, C clock, D data.
- `documentation/ANEMO_VANE_README.md` and `documentation/images/breadboard_wiring.png`: earlier circuitry, including anemometer filtering and the excluded vane circuit.
- `/Users/ricardorocha/Downloads/weather station wiring.xlsx`: historical workbook, sheet Breadboard. It describes the previous direct-sensor/vane layout and does not include the current RJ45 mapping. It was read, not edited.
- User supplied a photo in chat. Its temporary source path was `/var/folders/bj/nn8zmm9j2d99hdgj8cp93cz40000gn/T/codex-clipboard-ecd8176d-4ecf-451b-8a29-7e802ca03f78.png`; it may not persist. The photo predates the completed steps above.

Known documentation conflicts:

- NEW_WIRING.md lists breakout 2 ground as going to BME280 +. Ground must go to BME280 −; this appears to be a documentation typo.
- Older anemometer/vane connector tables use conflicting colours and pin numbering. Do not apply their sensor-end pin numbers to the Pi-side breakout.
- The latest historical notes say the anemometer was separated from the vane, with splice blue assigned ground and rosé assigned signal. These are sensor-side splice colours, distinct from the Pi-side white signal wire. Treat them as historical notes pending continuity verification.
- The rain documentation contains contradictory colour/function labels. Verify the switch pair before powering and testing the rebuilt circuit.

For the current indoor rebuild, the connection map above supersedes earlier proposed breadboard row numbers. Outdoor connections remain reported unchanged, not independently verified.

## Software findings to address before trusting measurements

These findings were identified by reading code; they have not been repaired or hardware-tested.

1. **Wind conversion is reversed.** In `modules/anemometer.py`, `SPEED_CONV = 0.6667` represents m/s per pulse/second, but `measure_wind_speed()` divides by it. The intended conversion is pulse frequency multiplied by 0.6667. The existing expression overstates speed by about 2.25 times for the same pulse count.
2. **The quick anemometer diagnostic omits the pull-up.** `scripts/anemo/3-anemo_quick_test.py` claims GPIO17 without `lgpio.SET_PULL_UP`. Correct or replace this diagnostic before relying on it with the current circuit, which has no external pull-up resistor.
3. **The main loop does not monitor wind and rain concurrently.** `weather_station.py` polls rain for roughly 59 seconds, then calls the blocking 60-second wind measurement. Rain is not polled during that wind measurement, and a nominal one-minute loop takes roughly two minutes. Do not use the full station as the initial hardware diagnostic.
4. **Existing rain diagnostics can miss short closures.** The wiring monitor sleeps 0.5 seconds between reads; the functional test polls at 0.1 seconds. A missed tip is not sufficient evidence of a broken switch.
5. **GPIO chip selection needs checking on the live Pi.** Existing code assumes gpiochip 0. Inspect the actual Pi configuration rather than changing this blindly.

Wind-vane use is already commented out in the main application. Rain initialization remains enabled there despite its unverified hardware state.

## Next steps — proceed individually

### Remaining work

Accept the user confirmation that BME280 and anemometer are working; do not restart their basic wiring checks without a new fault. The known software findings above remain unresolved in this session and are not disproved by functional sensor operation.

1. Investigate rain independently, one step at a time. Its brown signal is already connected through A18/B18 to Pi physical pin 13 / GPIO27. For a switch continuity test, unplug Pi power and isolate the switch wiring from the Pi electronics before manually tipping the bucket. Then use a powered GPIO diagnostic with the internal pull-up enabled. A lack of detected tips does not prove zero rainfall or a functioning bucket.
2. If agent-run diagnostics are needed, obtain the Pi SSH address or guide the user locally. No SSH address has been supplied. Before separate diagnostics, check for and stop any station process that would compete for GPIO/I2C access or log test data.
3. Fix and validate the wind conversion and combined acquisition timing before trusting normal logged measurements. Sensor operation does not establish wind-speed accuracy or reliable concurrent rain counting. Preserve the wind-vane exclusion.

Keep the user pace: give one step, wait for their result, and update this record. Any further physical wiring changes should be made with Pi power unplugged.

Use 3.3V for this circuit. The RJ45 cable carries custom sensor signals: it is not an Ethernet connection and must not be plugged into network equipment.

## External references checked during the session

- SparkFun Weather Meter Hookup Guide: https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide/all?print=1
- Raspberry Pi hardware documentation: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html

The SparkFun guide supports the passive switch model and nominal anemometer conversion of approximately 2.4 km/h per closure/second. Existing project rain calibration is 0.2794 mm/tip; actual rain operation and calibration remain unverified.
