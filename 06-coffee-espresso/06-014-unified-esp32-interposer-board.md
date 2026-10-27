---
title: 'Unified ESP32 Interposer Board (Mini V2 → Home Assistant)'
number: '06-014'
category: 'coffee-espresso'
difficulty: 'Hard'
time_commitment: '1-4 weeks'
target_skills:
  'ESP32 / ESPHome, PCB Design (KiCad), Analog Front-Ends, Signal Interposing, Home Assistant'
status: 'In Progress'
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

**Measure first. These gate layout; details are in the plan's "Open facts" table:**

- [ ] **M1** Control-board low-voltage GND isolated from mains? _(gates everything)_
- [ ] **M2** `S1`/`S2` connector type + pin count at the control board
- [ ] **M3** `S1`/`S2` node voltage range + bias (cold / at temp), cold NTC resistance
- [ ] **M4** `SB` boiler-level sensing method + excitation _(optional for rev A)_
- [ ] **M5** `SL` tank-level method + connector _(optional for rev A)_
- [ ] **M6** ito `ENC` plug: Molex KK 254 4-pin + pin order confirmed
- [ ] **M7** Encoder rest state at a detent + ito pull-up level
- [ ] **M8** Panel ⇄ board link: serial `SER` vs 16-pin ribbon vs discrete pins _(optional for rev
      A)_
- [ ] **M9** GICAR `+` ≈ 14.3 V and `o` pulled to 5 V (re-check)
- [ ] **M10** Physical envelope: mount point, cable lengths, max board size

**Then build:**

- [x] Rev A scope decided (everything but `SER`)
- [x] Plan written
      ([`docs/plans/2026-10-27-unified-esp32-interposer-rev-a-plan.md`](../docs/plans/2026-10-27-unified-esp32-interposer-rev-a-plan.md))
- [ ] Schematic + headless KiCad layout (DRC-clean; grep for bare `(remove_unused_layers)`)
- [ ] Order from JLC (SMT top; hand-solder XH/KK/SH connectors)
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
