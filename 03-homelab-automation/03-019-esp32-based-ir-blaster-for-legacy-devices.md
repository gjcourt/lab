---
title: 'ESP32-based IR Blaster for Legacy Devices'
number: '03-019'
category: 'homelab-automation'
difficulty: 'Easy'
time_commitment: '1-2 days'
target_skills: 'IR LEDs/Receivers, Signal Decoding, ESPHome'
status: 'In Progress'
depends_on:
  - hardware/esp32
  - homelab/home-assistant
---

# ESP32-based IR Blaster for Legacy Devices

## Description

Build a device that can record and transmit infrared (IR) signals. Use it to integrate legacy
devices (like an old TV, amplifier, or portable AC unit) into your Home Assistant automations.

**Concrete goal (2026-06):** replace the pile of cheap audio-gear remotes with one generalized
controller, surfaced in Home Assistant (phone, dashboards, automations). Confirmed the remotes
are **mainly IR**, not RF — so this is an IR-blaster job, not an SDR/RF job (no SDR can learn or
transmit IR).

## Approach (decided after RF-landscape research)

**Step 0 — per-remote IR vs RF check.** Point each remote at a phone's **front/selfie camera**
and press a button → flashing light = IR. (Use the *front* camera: many modern rear cameras have
IR-cut filters and show nothing even for real IR.) Anything that shows no flash *and* works
through walls / off-axis is 433 MHz RF — handle those separately (below).

**Primary build — ESP32 + ESPHome IR transceiver (~$15, local-first, best homelab fit):**
- ESP32 dev board running ESPHome `remote_receiver` (TSOP38238-class IR receiver) to *learn*
  codes, and `remote_transmitter` (IR LED) to *send* them. Native, fully-local HA integration —
  no cloud, no lock-in.
- ⚠️ Drive the IR LED through an **NPN transistor** (e.g. 2N2222) + current-limit resistor, never
  straight off a GPIO — direct-drive range is inches. With a transistor you get whole-room range.
- Learn each remote's codes from the ESPHome receiver logs (or capture with a Flipper), paste the
  protocol/code into YAML as HA buttons.
- No-solder option: **Athom** sells a pre-built ESPHome RF433+IR unit if you'd rather not build.

**Quick alternative — Broadlink RM4 Pro (~$40, plug-and-play):** IR *and* 433 MHz RF in one box,
native HA `broadlink` integration that can run fully local. Setup gotcha: it's cloud-capable — set
Wi-Fi in the Broadlink app, then **quit the app and configure in HA** to avoid cloud mode; a
firmware update can re-assert cloud, which the ESP32 route avoids entirely.

**For any 433 MHz RF stragglers:** the same Broadlink RM4 Pro absorbs 433 learn/replay, or go
local with a Sonoff RF Bridge R2 + Tasmota + Portisch → MQTT → HA. (Do NOT expect RTL-SDR to
control anything — it's receive-only.)

## Exit Criteria

- [ ] Every audio-gear remote inventoried + tagged IR or RF (front-camera test)
- [ ] One ESP32+ESPHome blaster flashed and adopted in Home Assistant
- [ ] Each target device controllable from HA (power, volume, input) at whole-room range
- [ ] HA dashboard/remote card (and at least one automation) replacing the physical remotes
- [ ] Fully local — no cloud dependency

## Bill of materials (~$10–15 beyond the dev board)

Already have: **ESP32 / Seeed XIAO ESP32-C3 dev board + USB-C cable** (brains, WiFi, power, flashing).

| Part | Qty | ~Price | Purpose |
|---|---|---|---|
| **IR receiver — TSOP38238** (or VS1838B / TSOP4838) | 1 | ~$1.50 | Demodulates 38 kHz IR → clean envelope for **capture** (and optional physical-remote→HA input) |
| **IR LED, 940 nm** (5 mm) | 1–3 | ~$0.20 ea | Transmitter; extras = more range / aim at multiple devices |
| **NPN transistor — 2N2222** (or 2N3904 / S8050 / BC337) | 1 | ~$0.10 | Drives the IR LED at ~100 mA+ pulsed — the GPIO can't. **The #1 part for range** |
| **Resistor ~470 Ω–1 kΩ** | 1 | ~$0.02 | Transistor *base* resistor (GPIO → base) |
| **Resistor ~33–100 Ω** | 1 | ~$0.02 | IR LED *current-limit* (start ~100 Ω; drop toward 33 Ω for more range) |
| **Breadboard + jumpers** | 1 | ~$6 | Prototyping (or perfboard + solder for permanent) |

Recommended extras (good practice, often skipped): a **0.1 µF cap** across the TSOP VS↔GND + a **~100 Ω** resistor in its supply line (datasheet supply filtering). Internal pull-up means a 10 kΩ on the TSOP output is usually unnecessary.

**Sourcing — Mouser (all in stock):**

| Item | Mouser part | Pick / note |
|---|---|---|
| IR receiver | Vishay **TSOP38238** | exact part |
| IR LED 940 nm | Vishay **TSAL6400** | **6400 over 6200** — higher output = range; buy ~10 (spares + makes shipping worth it) |
| NPN transistor | onsemi **PN2222A** (or 2N3904) | **prefer PN2222A** (~800 mA vs 2N3904's ~200 mA — more headroom pulsing the LED) |
| Resistors | a **through-hole resistor kit** | covers 470 Ω–1 kΩ base + 33–100 Ω LED; reusable |

Links: [TSOP38238](https://www.mouser.com/ProductDetail/Vishay-Semiconductors/TSOP38238?qs=RzxYCzJDjPVjpHVZS582Ng%3D%3D) · [TSAL6400](https://www.mouser.com/ProductDetail/Vishay-Semiconductors/TSAL6400/?qs=oSAwVt7aKTHCOCv1ythi7g%3D%3D) · [2N3904](https://www.mouser.com/ProductDetail/Diotec-Semiconductor/2N3904?qs=OlC7AqGiEDlYMySw5i2rlg%3D%3D) · [resistor kits](https://www.mouser.com/c/passive-components/resistors/resistor-kits/) · [breadboards](https://www.mouser.com/new/bps/bps-breadboards/) · [jumper wires](https://www.mouser.com/c/tools-supplies/prototyping-products/jumper-wires/)

**Paste-able for the Mouser BOM Tool** (Account → BOMs → Import, or quick-add by part #; format = `Part #, Qty`):
```
TSOP38238,2
TSAL6400,10
PN2222ABU,5
CFR-25JB-52-1K0,10
CFR-25JB-52-100R,10
CFR-25JB-52-47R,10
```
(CFR-25JB-52-* are Yageo ¼ W carbon-film: 1K0 = 1 kΩ base, 100R / 47R = LED current-limit. Verify each
line resolves, or swap the three resistor lines for one resistor-assortment-kit SKU.)

**Breadboard + jumpers — from SparkFun** (cheaper than Mouser à-la-carte):
- Jumper wires: SparkFun **PRT-12795** — Jumper Wires, Connected 6", M/M (20-pack)
- Breadboard: SparkFun **PRT-12002** — Breadboard, Self-Adhesive (full-size)

Caveats: parts total only a few $, so **pad the Mouser order** (qtys above) so shipping is worth it — chips from Mouser + the SparkFun breadboard/jumpers still lands **<$25 total**.

**Circuit:** TSOP `OUT→GPIO`, `GND→GND`, `VS→3.3V`. LED driver: `GPIO→470Ω–1kΩ→transistor base`; `emitter→GND`; `IR LED anode→33–100Ω→5V` (use the board's 5V/VBUS for range); `LED cathode→collector`. Logic stays 3.3 V; LED runs off 5 V via the transistor (no transistor = ~6-inch range).

**Tools:** phone **front camera** to confirm the LED fires (IR shows faint purple; rear cams have IR-cut filters). Soldering iron only if going permanent; multimeter handy.

**Shortcuts:** KY-022 receiver module (fine, no resistors) — but the common **KY-005 transmitter module has no driver transistor**, so its range is weak; build the transistor circuit instead. Or buy the fully-prebuilt **Athom ESPHome IR+RF433 unit (~$15–20)** — LED+driver+receiver wired, ships with ESPHome, zero soldering. (Or **Broadlink RM4 Pro ~$40** for instant non-DIY.)

## Ready-to-flash ESPHome configs

Two-phase: flash `learn.yaml` to capture codes, then move them into `blaster.yaml` to transmit.
Needs a `secrets.yaml` next to them with `wifi_ssid` / `wifi_password`. When actually built, these
should live in **`~/src/homelab/firmware/esphome/ir-blaster/`** (same convention as the mmwave
nodes — secrets.yaml gitignored; flash USB first, then OTA). Wiring: TSOP `OUT→GPIO14` (VS→3.3V,
GND→GND); IR LED on `GPIO4` **through an NPN transistor** (GPIO→1kΩ→base; LED+resistor on a 5V
collector path) — never straight off the GPIO, or range is inches.

### learn.yaml (capture phase)
```yaml
# Flash, open the logs, point each remote at the TSOP and press buttons.
# ESPHome prints the decoded protocol + code (or raw timings). Record each into
# your code book, then move them into blaster.yaml.
substitutions:
  name: ir-blaster
  recv_pin: GPIO14            # TSOP38238 OUT (adjust per board)

esphome:
  name: ${name}
  friendly_name: IR Blaster (learning)
esp32:
  board: esp32dev            # Seeed XIAO ESP32-C3: board: seeed_xiao_esp32c3
logger:
  level: DEBUG               # IR dumps print at DEBUG
api:
ota:
  platform: esphome
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

remote_receiver:
  pin:
    number: ${recv_pin}
    inverted: true           # TSOP idles HIGH, pulls LOW on a mark
    mode: { input: true, pullup: true }
  dump: all                  # try every decoder (use `raw` to see timings)
  tolerance: 25%
  idle: 25ms
```

### blaster.yaml (transmit phase)
```yaml
# Fill in the codes captured with learn.yaml. Each button becomes a HA entity
# (button.ir_blaster_*); pressing it fires the IR LED. Receiver kept so a
# physical remote can also trigger HA automations.
substitutions:
  name: ir-blaster
  tx_pin: GPIO4              # IR LED via NPN transistor (NOT direct!)
  recv_pin: GPIO14          # optional: physical-remote → HA input

esphome:
  name: ${name}
  friendly_name: IR Blaster
esp32:
  board: esp32dev           # Seeed XIAO ESP32-C3: board: seeed_xiao_esp32c3
logger:
api:
ota:
  platform: esphome
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

remote_transmitter:
  pin: ${tx_pin}
  carrier_duty_percent: 50%  # standard for a 38 kHz carrier

remote_receiver:             # optional input; set dump:all to re-learn
  pin:
    number: ${recv_pin}
    inverted: true
    mode: { input: true, pullup: true }
  dump: []

button:
  # --- replace address/command with YOUR captured codes ---
  - platform: template
    name: "Amp Power"
    on_press:
      - remote_transmitter.transmit_nec: { address: 0x10, command: 0x21 }

  - platform: template
    name: "Amp Volume Up"
    on_press:
      - remote_transmitter.transmit_nec: { address: 0x10, command: 0x22 }
      # hold-to-repeat feel: wrap with repeat: { times: 3, wait_time: 40ms }

  # Sony uses a different action (12/15/20-bit):
  # - platform: template
  #   name: "TV Power (Sony)"
  #   on_press:
  #     - remote_transmitter.transmit_sony: { data: 0xA90, nbits: 12 }

  # A code that only decoded as RAW:
  # - platform: template
  #   name: "CD Play (raw)"
  #   on_press:
  #     - remote_transmitter.transmit_raw:
  #         carrier_frequency: 38kHz
  #         code: [9000, -4500, 560, -560, 560, -1690]
```

> Per-protocol transmit actions: `transmit_nec`, `transmit_sony`, `transmit_rc5`, `transmit_samsung`,
> `transmit_panasonic`, `transmit_pronto` (for Pronto hex from online DBs), `transmit_raw` (fallback).
> Match the action to whatever `dump: all` reported for that button.

## Progress

- [x] Research: IR vs RF, tool landscape, approach decided (2026-06-27)
- [ ] Inventory + IR/RF test all remotes
- [ ] Build/flash ESP32 ESPHome blaster
- [ ] Learn codes + HA entities
- [ ] Documentation
