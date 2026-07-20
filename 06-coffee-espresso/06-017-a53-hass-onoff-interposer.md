---
title: 'A53 Mini HASS On/Off Interposer (ESP32 / ESPHome)'
number: '06-017'
category: 'coffee-espresso'
difficulty: 'Medium'
time_commitment: '1-2 days'
target_skills: 'ESP32 / ESPHome, Optocoupler Interfacing, Home Assistant, Mains-Adjacent Safety'
status: 'Not Started'
depends_on:
  - hardware/lucca-a53
---

# A53 Mini HASS On/Off Interposer (ESP32 / ESPHome)

The concrete **v1 on/off build** of the general button sidecar
([06-014](06-014-esp32-button-automation-sidecar.md)), and the first step of machine control (Phase
4 of the Vibrato shot-feedback-loop roadmap, which lives in the `vibrato` repo). Give the LUCCA A53
Mini (= La Spaziale S1 Mini Vivaldi II) a **Home Assistant power switch** by simulating its front
**ON/OFF button** — an ESP32 running ESPHome closes an isolated contact across the button's two pins
for ~3 s, exactly like a finger press. It talks to **Home Assistant** directly (not to Vibrato).

> ⚠️ **Safety.** The button lines are **low-voltage logic** (safe to interpose), but they live
> inside a **mains + dual-boiler (~15 A) + water** machine. **Unplug the machine before opening or
> wiring.** Only bridge the two ON/OFF pins on the low-voltage panel connector — never the mains,
> heater, or relay-board terminals. Remote-ON heats the boilers **unattended** → confirm the tank
> has water, and add an auto-off automation + a leak sensor in HASS. The machine's klixons (TSB/TSC)
> are backstops, not primary interlocks.

## How it works

The A53 is **soft power**: plugged in it sits in **Stand-by**; **shorting front-connector pins 1
(GND) & 6 (ON/OFF) for ~3 s** boots it and starts heating (community-documented — s1cafe t=261). We
drive that short with an **opto-isolated output** from an ESP32 so the microcontroller is
galvanically separate from the machine, and expose it to HASS.

> **Pin-numbering gotcha (verify before you cut).** The forum's "pin 6" is numbered off the
> **control-panel picture** (top row counts 1, 3, 5, 7, 9, 11), so panel-"pin 6" is **connector pin
> 11**. Numbering schemes differ between the connector and the diagram — **confirm with a
> multimeter**: with the machine unplugged, find the two pins that read continuity **only while the
> physical ON/OFF button is held.** Those are your two wires.
>
> **Duration nuance (from the s1cafe record).** The press length is semantic: **~1 s ≈ a clean
> on/off toggle; ≥3 s can drop the board into a configuration mode.** The robust shipped builds send
> a short double-pulse "reset" then the hold, to guard against landing in programming mode. The 3.2
> s hold below is on the edge — start at ~1 s if a clean toggle is all you want.

## Bill of materials

| Part                 | Notes                                                                                                                                                                                                                                            |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ESP32 dev board      | Any — e.g. Seeed XIAO ESP32-C3, ESP32-C3-DevKitM, or a **Shelly Plus 1** (ESPHome-flashable, has a built-in isolated dry contact — skips the opto).                                                                                              |
| Opto-isolated output | A **PC817** optocoupler **or** an opto-MOSFET (e.g. **TLP222A**, no polarity, ideal for a logic-level dry contact) **or** a small reed relay. Skip if using a Shelly's dry contact.                                                              |
| Resistor             | ~220–330 Ω for the opto LED from the ESP32 GPIO (PC817).                                                                                                                                                                                         |
| Wire + tap           | Dupont/JST pigtail onto the two verified panel-connector pins (T-tap or a splice).                                                                                                                                                               |
| 5 V USB supply       | Power the ESP32 separately — keeps it isolated via the opto.                                                                                                                                                                                     |
| _(optional, v1.1)_   | An **LDR or a second opto** on the front **power LED "D"** for real on/off state feedback. The s1cafe builds tap an **always-on** LED (e.g. "Econ") and read **duty cycle** — the LEDs are PWM'd/ground-multiplexed, so a static level won't do. |

## Wiring

```text
ESP32 GPIO ──[330Ω]──▶│ PC817 LED        (opto input, driven by ESPHome)
                        PC817 transistor ── collector ─▶ panel pin 6 (ON/OFF)
                                          └ emitter    ─▶ panel pin 1 (GND)
ESP32 5V/GND ◀── separate USB supply (isolated from the machine via the opto)
```

- **GPIO high → opto conducts → pin 6 shorted to pin 1 (GND) = button pressed.** Hold ~1–3 s,
  release.
- With an **opto-MOSFET (TLP222) or reed relay**, the output is a bare dry contact — wire it
  straight across pins 1 & 6 (no polarity concern), driven from the GPIO.
- **Shelly Plus 1**: wire its **O/I dry-contact output** across pins 1 & 6; flash ESPHome; no opto
  needed.

## ESPHome config

`a53-power.yaml` (fill secrets in `secrets.yaml`; the `button` is the guaranteed-working v1, the
`switch` is the stateful upgrade once you add LED feedback):

```yaml
esphome:
  name: a53-power

esp32:
  board: esp32-c3-devkitm-1 # match your board

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api: # native Home Assistant API
  encryption:
    key: !secret api_key
ota:
  - platform: esphome
logger:

# The isolated output that shorts pins 1 & 6 (opto/relay input).
output:
  - platform: gpio
    pin: GPIO4
    id: onoff_contact

# One "button press" = close the contact for ~3 s, then open.
script:
  - id: press_power
    then:
      - output.turn_on: onoff_contact
      - delay: 3.2s # a touch over the ~3 s hold; drop toward ~1 s for a plain toggle
      - output.turn_off: onoff_contact

# v1 — always-works primitive: a HASS button that mimics a finger press.
button:
  - platform: template
    name: 'A53 Power button (3 s hold)'
    on_press:
      - script.execute: press_power

# v1.1 — a real on/off SWITCH (needs the LED-state sensor below).
# The A53 ON/OFF is a toggle, so only press when the state actually needs to flip —
# otherwise a stale HASS state would toggle you the wrong way.
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO5
      mode: INPUT_PULLDOWN
    name: 'A53 power state'
    id: a53_on
    filters:
      - delayed_on: 300ms # power LED "D" is solid when ON, flashing in standby;
      - delayed_off: 2s #   the delays debounce the standby flash to read as OFF

switch:
  - platform: template
    name: 'A53 Power'
    lambda: 'return id(a53_on).state;' # reflect the machine's real state
    turn_on:
      - if:
          condition:
            binary_sensor.is_off: a53_on
          then:
            - script.execute: press_power
    turn_off:
      - if:
          condition:
            binary_sensor.is_on: a53_on
          then:
            - script.execute: press_power
```

## Bring-up & test (do it in this order)

1. **Bench-test the opto/relay alone** — flash the firmware, press the HASS button, and watch a
   multimeter (continuity) or an LED across the opto output pulse closed for ~3 s. **Prove it works
   before it's anywhere near the machine.**
2. **Verify the pins (machine unplugged):** multimeter continuity → the two panel-connector pins
   that close **only while the physical ON/OFF button is held.** Those are pins 1 & 6.
3. **Wire** the opto output across those two pins; keep the ESP32 on its own USB supply.
4. **Plug in, fire the button** from HASS → the machine should boot and heat (LED "D" goes solid).
   If nothing happens, re-check the pins and the hold length (try ~1 s for a clean toggle, up to 3.5
   s).

## Exit Criteria

- [ ] Opto/relay bench-verified: HASS button pulses the contact closed for the set hold, open
      otherwise — proven off-machine.
- [ ] ON/OFF pins confirmed by continuity (close **only** while the physical button is held).
- [ ] Installed: the HASS `button` boots the machine (LED "D" solid) and toggles it off, mirroring a
      finger press.
- [ ] Hold length tuned so a single press is a clean on/off toggle (not a drop into config mode).
- [ ] _(v1.1)_ Power-LED state sensor added (always-on LED, duty-cycle read) so the HASS entity is a
      true stateful **switch**, not just a momentary press.
- [ ] Auto-off automation + tank-water/leak safety interlock present before any unattended
      remote-ON.

## Follow-ups

- **v1.1 state feedback:** tap an **always-on** power LED (LDR or opto) into `GPIO5` so the HASS
  entity is a true on/off switch, not just a momentary press. The LEDs are PWM'd/ground-multiplexed
  — read **duty cycle**, and tune the `delayed_on/off` filters to the standby-flash rate.
- **Full button control ([06-014](06-014-esp32-button-automation-sidecar.md)):** the other buttons
  (Single / Double / Hot-water / Boiler) are the same low-voltage membrane contacts — the full
  16-pin ribbon matrix is mapped (s1cafe t=2629); add an opto/MOSFET per button-pin-pair and expose
  them in this same ESPHome config.
- **Deep RE ([06-016](06-016-a53-control-board-reverse-engineering.md)):** the bench-board project
  characterizes the keypad matrix, timer bus, and firmware for anything past button emulation.
- **Deploy:** once proven, this ESPHome device graduates to the homelab repo (where the ESPHome/HASS
  configs live) for managed deployment.

## Sources

- On/off recipe + pin-numbering nuance + duration semantics: s1cafe "HOWTO: Installing a power-on
  timer" (t=261), the full ribbon button/LED map (t=2629), and an alternative timer (t=1784) —
  **Cloudflare-blocks bots; read in a browser or via the local KB, and verify pins by continuity
  before cutting.**
- Wiring / keyboard diagrams: the A53 Mini manual and the S1 Mini Vivaldi II owner's manual PDF
  (static PDFs on s1cafe.com **are** fetchable), plus the
  [control-board wiring reference](_reference/mini-v2-control-board-wiring.md).
- Parent / related: [06-014](06-014-esp32-button-automation-sidecar.md) (general button sidecar),
  [06-016](06-016-a53-control-board-reverse-engineering.md) (bench-board RE). Umbrella: the Vibrato
  shot-feedback-loop roadmap, Phase 4 (in the `vibrato` repo).
