---
title: 'XIAO ESP32-C3 IR + RF Blaster Carrier PCB'
number: '03-027'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-2 weeks'
target_skills: 'PCB design (KiCad), IR LED drivers, sub-GHz RF (CC1101), ESPHome, JLCPCB fab'
status: 'In Progress'
depends_on:
  - hardware/esp32
  - hardware/kicad
  - homelab/home-assistant
---

# XIAO ESP32-C3 IR + RF Blaster Carrier PCB

## Description

Productize the breadboard IR blaster from
[03-019](03-019-esp32-based-ir-blaster-for-legacy-devices.md) into a small custom PCB — a carrier
"hat" in the **Seeed XIAO 24GHz mmWave module** form factor. The XIAO ESP32-C3 sockets into 2×7
female headers; the board carries the payload. Then go one better than the breadboard: fold a
**sub-GHz RF transmitter** onto the same board so a single tiny package is a universal **IR + RF**
remote.

## Why a carrier board

The breadboard proved the circuit (2N2222 → MOSFET, dual/triple 940 nm LEDs, ~15 Ω current limit,
`power_save_mode: none` for MQTT latency). A carrier PCB makes it deployable: solid, aimable,
mountable, and repeatable. The XIAO stays socketed (removable/reflashable) and powers the board off
its own USB-C.

## Design summary

- **IR:** transmit-only, **3× 940 nm THT LEDs** (D3 optional/DNP), low-side **AO3400A** MOSFET on
  GPIO2 (D0; the 10 kΩ gate pulldown keeps it off through boot). LEDs off 5 V (VBUS).
- **RF:** transmit-only **CC1101** on a socketed **EBYTE E07-M1101D** module (SPI + GDO0), on the
  **back** with the SMA/antenna off the south edge. The CC1101 _chip_ is multi-band, but a physical
  _module_ is antenna-matched to one band — the E07-M1101D is **433 MHz** (covers ~387–464; the
  common US/EU fixed-code band). The 2×4 socket is **band-agnostic**, so a differently-tuned CC1101
  module (315 / 868 / 915) drops in without a board change. Codes are learned on the C3 learn rig,
  so the blaster needs no receiver. RF replay only works on **fixed-code** gear (outlets/fans/
  doorbells), not rolling-code.
- **Assembly:** JLCPCB SMT for the MOSFET + passives + CC1101; hand-solder the IR LEDs and the XIAO
  sockets.
- **Firmware:** ESPHome. IR is stock `remote_transmitter`; the CC1101 needs a community
  `external_component` (SPI init + GDO0 OOK bridge).

## Where the design lives

The buildable assets (KiCad project, `generate_pcb.py` generator, design doc, and the ESPHome
config) live in the homelab repo — this repo is the project-lifecycle writeup, not a binary/asset
store.

- `gjcourt/homelab` → `hardware/ir-rf-blaster-hat/` + `firmware/esphome/ir-rf-blaster-xiao-c3.yaml`
- Opened as homelab **PR #1044**.

## Exit Criteria

- A routed, DRC-clean 4-layer board using Seeed's official XIAO footprint, fabricated by JLCPCB.
- The assembled hat drives every captured IR device across the room from the socketed XIAO C3.
- The CC1101 transmits a learned fixed-code RF command that actuates a real device (outlet/fan).
- It drops into Home Assistant over MQTT as a replacement for the breadboard node — no regressions.

## Status & next steps

- [x] Requirements + schematic + BOM + pin map (no strapping pins) + floorplan
- [x] KiCad scaffold generated headless (18 footprints placed, nets, outline, mounting holes,
      antenna keepout) and round-trip-validated
- [x] **Routed as 4-layer** (F.Cu / In1 GND plane / In2 +5V plane / B.Cu) with real library
      footprints; SPI fans N-row-from-J1 / S-row-from-J2 so no trace clips the E07 pad block.
      **DRC-clean: 0 errors, 0 unconnected** (23 × 54 mm). Generated headless (kiutils), zone-filled
      via `pcbnew.LoadBoard`, validated with `kicad-cli`. Homelab PR #1120.
- [x] **Design-review re-layout**: XIAO rotated horizontal (USB-C off the WEST edge); CC1101 moved
      to a **swappable 2×4 female socket on the BACK** wired to the **fixed E07-M1101D datasheet
      pinout** (module plugs straight in), antenna off the south edge; **all-layer antenna keepout
      added**. Top/bottom renders + orientation diagram in the homelab dir.
- [x] **Official Seeed footprint**: swapped the provisional 1×7 sockets for Seeed's
      `XIAO-ESP32-C3-DIP` (15.24 mm row pitch, hybrid SMD+THT castellated pads, USB-C off the west
      edge); re-derived the fan around the real pad map (power on 12/13/14, strapping D0/D8/D9
      avoided). Standoff confirmed (E07 pins protrude ~1 mm, clears the socketed XIAO). DRC still
      0/0.
- [x] Export Gerbers/drill → `hardware/ir-rf-blaster-hat/ir-rf-gerbers.zip`
- [ ] Optional final 3D view before fab; then order (JLCPCB)
- [ ] CC1101 ESPHome external component + on-board RF bring-up
