---
title: 'GICAR Flow-Tap Interposer PCB (stock meter → ito)'
number: '06-015'
category: 'coffee-espresso'
difficulty: 'Medium'
time_commitment: '1-2 days (design + order + assemble)'
target_skills: 'PCB Design (KiCad), SMT Assembly, Connectors, Signal Buffering'
status: 'In Progress'
depends_on:
  - hardware/lucca-a53
  - hardware/ito-module
---

# GICAR Flow-Tap Interposer PCB (stock meter → ito)

A small, JLC/PCBWay-assembled interposer PCB that lets
[ito + `leva!`](06-001-lucca-a53-mini-leva-firmware-integration.md) read the **stock GICAR flow
meter in parallel** — no inline Digmesa (avoids the ~10% flow restriction), no soldering into the
machine or ito, and fully reversible. It buffers the meter's 5 V open-collector pulse into ito
through a **74LVC1G17 Schmitt gate**, and its connector layout makes the 14.3 V rail physically
unable to reach ito.

Grounded in the [control-board wiring reference](_reference/mini-v2-control-board-wiring.md) — read
that first for the GICAR pinout, the buffer rationale (blondica vs sandc), and why the buffer runs
at 5 V.

## Why an interposer (not a flying-lead buffer)

The board sits **in-line between the GICAR meter and the Vivaldi**, passing all three meter pins
straight through so the machine is untouched, and breaking out only what ito needs. See
[flow-interposer.svg](_reference/flow-tap-pcb/flow-interposer.svg).

- **Reversible:** unplug the board, plug the meter back into the Vivaldi → stock. `J1↔J2` is a
  straight pass-through; the machine never knows it was there.
- **Safe by construction:** the +14.3 V rail only bridges `J1→J2`. There is **no `+` pin on `J3`**,
  so 14.3 V cannot physically reach ito (whose input is 5 V + 0.5 V absolute max).
- **Clean signal:** the Schmitt input adds hysteresis → squares up the coarse ~2 pulse/mL edges and
  rejects noise; its high-impedance input never loads the line the machine uses for dosing/autofill.

## Connectors — three ports

All three ports are **JST XH, 2.5 mm pitch** — confirmed 2026-07-13. The GICAR board connector
measures **2.0 mm _between_ pins**, which with the 0.5 mm posts = 2.5 mm pitch (XH, not the 2.0 mm
PH it superficially resembles). ito's IMPULSE side is XH too, so one connector family + one crimp
tool covers the whole board.

| Ref  | Role                     | Connector         | Pinout (numbered from the key/latch end)                                  |
| ---- | ------------------------ | ----------------- | ------------------------------------------------------------------------- |
| `J1` | GICAR meter in           | JST XH, **4-pin** | 1 = **key/blank**, 2 = +14.3 V (red), 3 = GND (black), 4 = signal (white) |
| `J2` | to Vivaldi (passthrough) | JST XH, **4-pin** | mirrors `J1` — 1 blank, 2 +14.3 V, 3 GND, 4 signal                        |
| `J3` | to ito                   | JST XH, **3-pin** | 1 = GND, 2 = OUT (buffered signal), 3 = +5 V — matches ito IMPULSE        |

> ✅ **Connector question resolved.** GICAR flow-meter plug = JST XH **4-pin** housing with
> **position 1 left blank as a key** (3 wires on 4 pins). ito IMPULSE = JST XH **3-pin**
> (`1 GND / 2 signal / 3 +5 V`, metered earlier). Pin 2's +14.3 V passes `J1→J2` only and never
> reaches `J3`; `J3` taps **pin 4 (white/signal)** buffered, referenced to the shared **pin 3 GND**.

**Connector BoM (all JST XH 2.5 mm):**

- **Cable plugs:** `XHP-4` (J1/J2 side) + `XHP-3` (ito) housings with `SXH-001T-P0.6` crimps — or
  pre-crimped XH pigtails to skip the crimp tool.
- **PCB headers (through-hole):** `B4B-XH-A` ×2 (`J1`, `J2`) + `B3B-XH-A` (`J3`); swap to `S…-XH-A`
  right-angle if it lays out cleaner.
- **`J2`→Vivaldi:** a short XH 4-wire jumper (`XHP-4` both ends) or a `J2` pigtail — the Vivaldi
  board header natively mates the meter's plug, so the interposer presents a plug back to it.

## Schematic / netlist

One buffer, one decoupling cap, three connectors. Full netlist + BoM live in the KiCad project
README: [`_reference/flow-tap-pcb/`](_reference/flow-tap-pcb/README.md).

```text
  (J1.1 / J2.1 = keyed blank — no connection)
  N_PLUS (14.3 V):  J1.2 ── J2.2                       (pass-through ONLY — not to U1 or J3)
  GND:              J1.3 ── J2.3 ── J3.1 ── U1.GND ── C1
  N_O   (pulse):    J1.4 ── J2.4 ── U1.A(in)
  V5    (ito 5 V):  J3.3 ── U1.VCC ── C1
  N_OUT (buffered): U1.Y(out) ── J3.2
```

- **U1** — 74LVC1G17 single Schmitt buffer (SOT-23-5). (Non-inverting; `74LVC1G14` = inverting equiv
  if preferred.)
- **C1** — 0.1 µF X7R, close to U1's VCC/GND.
- **R1** _(optional)_ — ~100 Ω in series at `U1.A` for input protection; omit for simplicity.

## Fabrication + assembly (JLC/PCBWay)

- **2-layer, ~20 × 20 mm.** Export Gerbers + BoM + CPL from KiCad.
- **SMT-assemble only U1 + C1** (the fiddly SMD). Hand-solder the **through-hole JST XH headers**
  for `J1/J2/J3` (`B4B-XH-A` ×2 + `B3B-XH-A`) — cheap, and keeps the connector footprints trivial.
- Piggyback this on the plumb-in bracket order (both fab houses take it in one cart).

## Integration (3 plugs, reversible)

1. Unplug the GICAR flow meter from the Vivaldi.
2. Meter → `J1`.
3. `J2` → the Vivaldi's now-empty flow socket.
4. ito flow cable → `J3`.

To revert: pull the board, plug the meter back into the Vivaldi.

## Exit Criteria

- [ ] Board fabricated + assembled (U1 + C1 SMT, connectors soldered).
- [ ] Bench: `J1→J2` passes all three meter pins through unchanged (machine-side pulses intact).
- [ ] Bench: a pulse injected on `o` appears cleanly at `J3.OUT` (0↔5 V), and **no continuity**
      exists between the 14.3 V (`+`) net and any `J3` pin.
- [ ] Installed in-line: machine still doses + autofills normally, and ito reads live flow.
- [ ] Fully reversible verified: removing the board and re-plugging the meter restores stock
      behaviour.

## Progress

- [x] Topology chosen: in-line interposer, Schmitt-buffered, `+` isolated from ito by construction
- [x] Schematic + netlist + BoM drafted (KiCad project scaffolded)
- [x] Identify `J1/J2` (GICAR) + `J3` (ito) connectors → **JST XH 2.5 mm**: GICAR = 4-pin (pos 1
      key-blank; 2 +14.3 V/red, 3 GND/black, 4 signal/white), ito = 3-pin (1 GND, 2 signal, 3 +5 V)
- [ ] Draw schematic in KiCad, assign footprints (XH-4/XH-3), lay out (~20 × 20 mm, 2-layer)
- [ ] Export Gerbers/BoM/CPL → order JLC/PCBWay (SMT U1+C1, TH connectors)
- [ ] Assemble, bench-verify pulse pass-through + buffered output into ito
- [ ] Install in-line; confirm machine still doses/autofills and ito reads flow

## Sources

- [Mini V2 control-board wiring reference](_reference/mini-v2-control-board-wiring.md) — GICAR
  pinout, blondica vs sandc taps, buffer part options.
- [06-001 — ito + `leva!` profiling](06-001-lucca-a53-mini-leva-firmware-integration.md).
