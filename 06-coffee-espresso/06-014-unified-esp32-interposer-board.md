---
title: 'Unified ESP32 Interposer Board (Mini V2 → Home Assistant)'
number: '06-014'
category: 'coffee-espresso'
difficulty: 'Hard'
time_commitment: '1-4 weeks'
target_skills:
  'ESP32 / ESPHome, PCB Design (KiCad), Analog Front-Ends, Signal Interposing, Home Assistant'
status: 'Not Started'
depends_on:
  - hardware/lucca-a53
  - hardware/ito-module
---

# Unified ESP32 Interposer Board (Mini V2 → Home Assistant)

## Description

One plug-in ESP32 board that brings **everything the Mini V2 knows into Home Assistant**: boiler and
group temperatures, derived steam pressure, water levels, and flow. It also drives ito's `leva!`
menus without loss through the `ENC` interposer, and later takes over the touchpad link for on/off,
temperature and mode. ito keeps the real-time profiling loop
([06-001](06-001-lucca-a53-mini-leva-firmware-integration.md)). This board owns the rest.

Every machine signal passes straight through the board on matching connectors, and the ESP32 only
listens at high impedance. The one exception is `ENC`, which can also pull low, exactly like the
real knob. Unplug the board and re-mate the original plugs, and the machine is stock again.

**Design + build plan (authoritative):**
[`docs/plans/2026-10-27-unified-esp32-interposer-rev-a-plan.md`](../docs/plans/2026-10-27-unified-esp32-interposer-rev-a-plan.md).
It holds the block diagram, the per-function interfaces, power and grounding, connectors, firmware
outline, fab plan, tests, and the measure-first list below.

## Rev A scope (decided 2026-10-26)

**Everything except the `SER` interposer:**

- **ESP32** (S3 class) on 5 V from an **off-board isolated supply**. There is no mains on the PCB.
- **ADS1115** taps on the `S1` (steam) and `S2` (group) NTCs, through buffers. Steam pressure is
  derived from `S1` in firmware.
- **`SB` / `SL` level taps.** They are populated only if the sensing method is confirmed. Otherwise
  the board ships pass-through connectors plus DNP footprints.
- **Flow:** [06-015](06-015-gicar-flow-tap-interposer.md)'s GICAR flow-tap circuit, merged in as is,
  plus a second buffer into the ESP32.
- **ito `ENC` interposer:** open-drain injection plus read-back, which makes menu stepping open-loop
  and lossless.
- **Shared I²C** header. The ESP32 is the master; ito `EXPANSION` sits behind DNP jumpers.
- **`SER`:** header and DNP footprints only. Rev B, after the Saleae capture.
- **M9 "RS232 serial" tap (added 2026-11-08):** a DNP EXCON 4-pin header to the control board's
  empty M9 header, broken out to a link field and a spare ESP32 UART, with DNP level-shift
  footprints. Pin roles and levels are unknown: scope before connecting.
- **Optional on/off:** a DNP dry contact using [06-017](06-017-a53-hass-onoff-interposer.md)'s
  recipe, as a stopgap until `SER` lands. It is populated only if the panel really has a closable
  ON/OFF pin pair.

## Relationship to other projects

- **[06-015 GICAR flow-tap interposer](06-015-gicar-flow-tap-interposer.md):** **absorbed** as this
  board's flow function. The standalone boards (in hand) stay valid as the fallback and for bench
  work.
- **[06-017 HASS on/off interposer](06-017-a53-hass-onoff-interposer.md):** the **optional on/off
  stopgap** (DNP on rev A) until rev B's `SER` interposer gives full control.
- **[06-016 control-board RE](06-016-a53-control-board-reverse-engineering.md):** the source of the
  open facts (NTC curve, panel and serial map). Rev A doesn't need the spare-board bench to ship;
  rev B does.
- **[06-012 leva! PID takeover](06-012-leva-pid-temperature-takeover.md):** still the only path to
  _arbitrary_ setpoints. Rev B's `SER` interposer can only select the board's own preset
  temperatures.
- **[06-001 ito + leva!](06-001-lucca-a53-mini-leva-firmware-integration.md):** unaffected. This
  board taps ito's `IMPULSE` and `ENC` without changing ito's wiring.

## History

- **v0 (this file before 2026-10-27):** "ESP32 button-automation sidecar". It put **one optocoupler
  across each front-panel button** (discrete or scanned matrix) to simulate presses.
- **Superseded** by the architecture reference (hestia `ARCHITECTURE.md` §4). The Mini V2 touchpad
  is an **intelligent serial peripheral** with its own MCU on `SER2`→`SER1`, not a button matrix. So
  full control means a **`SER` man-in-the-middle** (rev B), not per-button optos.
- The v0 goal (temp presets, hot water, standby → Home Assistant) carries forward unchanged.

## Exit Criteria

- [ ] Rev A installed in-line. The machine doses, autofills, heats and alarms exactly as stock, and
      ito still reads flow.
- [ ] Home Assistant shows `S1`/`S2` temperatures, derived steam pressure and flow (and levels, if
      populated). Missing or out-of-range data shows as **unavailable**, never 0.
- [ ] HA can step a `leva!` value through `ENC` injection by exactly N detents, with the physical
      knob still working alongside.
- [ ] Pulling the board and re-mating the plugs restores the stock machine.
- [ ] _(rev B)_ HA controls on/off, temperature preset and mode through the `SER` interposer, with
      state read-back.

## Progress

**Measure first. These gate layout; details are in the plan's "Open facts" table. George took M1–M10
on 2026-11-08 (bench page Tests 28–37):**

- [x] **M1** Control-board low-voltage GND isolated from mains? _(gates everything)_ Yes (Test 28):
      GND to N and to F open unplugged; GND to PE 2 mV AC, 0 V DC powered; PS1 is a Lauma SMR30.10,
      Class II. GND is also bonded to chassis earth through M3 pin 4 (the steam-level return to the
      boiler body, Test 30), so the interposer's GND is earth. Flash an installed board from a
      grounded or battery-powered laptop.
- [ ] **M2** `S1`/`S2` connector type + pin count at the control board. **Probable** (Test 29):
      EXCON 2547, 2.54 mm, black PBT (header 2547xxWV203, housing 2547xxHA203, terminal
      254700TC351/TC501). M2 2-pin = steam NTC (1 GND, 2 feed); M3 4-pin = 1 GND, 2 group NTC feed,
      3 steam level probe, 4 level return; M6 = flow; M10 = tank level; M9 = empty, "RS232 serial".
      Still to do: calipers on the 4-pin header (≈ 12.7 mm wide) before ordering.
- [ ] **M3** `S1`/`S2` node voltage range + bias (cold / at temp), cold NTC resistance. Resistance
      half done (Test 30): group 249 kΩ at 21 °C, 13.3 kΩ at 94 °C (β ≈ 4340 K, R25 ≈ 205 kΩ); steam
      201.7 kΩ at 21 °C, 6.8 kΩ hot (temperature unknown); feed pin to GND ≈ 15 / 16.5 kΩ on the
      unpowered board. **Decided (George):** "Measure 0–5.5 V, survive 24 V". Live node voltages
      wait for an EXCON extension lead.
- [ ] **M4** `SB` boiler-level sensing method + excitation _(optional for rev A; Test 31 not done)_
- [ ] **M5** `SL` tank-level method + connector _(optional for rev A; Test 32 not done)_
- [x] **M6** ito `ENC` plug: Molex KK 254 4-pin + pin order confirmed (Test 33). The cable carries
      SW / A / B in holes 2 / 3 / 4 (each through 4.7 kΩ on the display board); hole 1 is empty.
      ito's pin 1 is GND.
- [x] **M7** Encoder rest state at a detent + ito pull-up level (Test 34): SW, A, B idle at 5.05 V,
      A/B open at detents, SW pressed 0 V. Injection is pull-low only; nothing is masked at rest.
- [ ] **M8** Panel ⇄ board link: serial `SER` vs 16-pin ribbon vs discrete pins _(optional for rev
      A)_. Partial (Test 35): a 16-way ribbon on M1; the panel end isn't reached yet.
- [x] **M9** GICAR `+` and `o` (Test 36): `+` is **~3.3 V** on this machine (meter unplugged), not
      14.3 V; `o` idles at 4.9 V. Everything on M6 is ≤ 5 V.
- [ ] **M10** Physical envelope: mount sites measured (Test 37: 55 × 50 mm in the control-board box,
      70 × 50 mm beside the ito, ~130 × 120 mm opposite the tank); cable lengths not yet.

**Then build:**

- [x] Rev A scope decided (everything but `SER`)
- [x] Plan written
      ([`docs/plans/2026-10-27-unified-esp32-interposer-rev-a-plan.md`](../docs/plans/2026-10-27-unified-esp32-interposer-rev-a-plan.md))
- [x] Pre-measurement schematic draft
      ([`_reference/interposer-rev-a/`](_reference/interposer-rev-a/README.md)): netlist as data in
      `circuit.py`, ERC checker passing, every placeholder mapped to the measurement that closes it
- [x] Schematic updated with the 2026-11-08 measurements; EXCON 2547 2- and 4-pin footprints
      authored from the EXCON drawing
- [ ] Schematic + headless KiCad layout (DRC-clean; grep for bare `(remove_unused_layers)`)
- [ ] Order from JLC (SMT top; hand-solder EXCON/XH/KK/SH connectors)
- [ ] Bench tests T1–T7 (pass-through, rails, NTC emulation + loading, level, flow, `ENC` on a
      bench-powered ito)
- [ ] ESPHome firmware: ADS1115 + temperature fit, steam-pressure template, flow `pulse_counter`,
      `ENC` injector component
- [ ] Install in-line; T8 (stock behaviour preserved) + T9 (reversible)
- [ ] _(rev B)_ Saleae capture of `SER`; design the `SER` interposer

## Sources

- hestia `/mnt/main/family/projects/electronics/espresso/ARCHITECTURE.md` (§4 panel, §6 sensors, §10
  interpose points, §13 open RE items) + `AGENTS.md`.
- [Control-board wiring reference](_reference/mini-v2-control-board-wiring.md): M5 map, GICAR meter,
  the absence of a switched mains rail.
- ito Hardware Reference Manual (PCB 2.0) pp.58–70: `ENC`, `IMPULSE`, `EXPANSION`, electrical
  limits.
- [ESPHome](https://esphome.io/): firmware and Home Assistant integration.
