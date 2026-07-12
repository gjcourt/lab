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

| Ref  | Role                     | Pins               | Match to…                                                   |
| ---- | ------------------------ | ------------------ | ----------------------------------------------------------- |
| `J1` | GICAR meter in           | `+`, `−`, `o`      | the **GICAR flow-meter connector** (receptacle)             |
| `J2` | to Vivaldi (passthrough) | `+`, `−`, `o`      | the **Vivaldi flow socket** (plug identical to the meter's) |
| `J3` | to ito                   | `OUT`, `5V`, `GND` | **Dietmar's ito flow-meter cable** connector                |

> ⚠️ **Connector choice is pending two photos** — the GICAR meter connector and ito's flow cable
> connector (type + pin pitch, 2.0 mm vs 2.54 mm). If matching either is impractical, fall back to
> **JST-XH 2.54 mm** on all three ports + two short adapter pigtails (universal, slightly less
> tidy).

## Schematic / netlist

One buffer, one decoupling cap, three connectors. Full netlist + BoM live in the KiCad project
README: [`_reference/flow-tap-pcb/`](_reference/flow-tap-pcb/README.md).

```text
  N_PLUS (14.3 V):  J1.+ ── J2.+                       (pass-through ONLY — not to U1 or J3)
  GND:              J1.− ── J2.− ── J3.GND ── U1.GND ── C1
  N_O   (pulse):    J1.o ── J2.o ── U1.A(in)
  V5    (ito 5 V):  J3.5V ── U1.VCC ── C1
  N_OUT (buffered): U1.Y(out) ── J3.OUT
```

- **U1** — 74LVC1G17 single Schmitt buffer (SOT-23-5). (Non-inverting; `74LVC1G14` = inverting equiv
  if preferred.)
- **C1** — 0.1 µF X7R, close to U1's VCC/GND.
- **R1** _(optional)_ — ~100 Ω in series at `U1.A` for input protection; omit for simplicity.

## Fabrication + assembly (JLC/PCBWay)

- **2-layer, ~20 × 20 mm.** Export Gerbers + BoM + CPL from KiCad.
- **SMT-assemble only U1 + C1** (the fiddly SMD). Use **through-hole connectors** for `J1/J2/J3` and
  hand-solder them — cheap, and lets you pick the exact housings once the photos land.
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
- [ ] Identify `J1/J2` (GICAR) + `J3` (ito) connectors from photos → finalize connector BoM
- [ ] Draw schematic in KiCad, assign footprints, lay out (~20 × 20 mm, 2-layer)
- [ ] Export Gerbers/BoM/CPL → order JLC/PCBWay (SMT U1+C1, TH connectors)
- [ ] Assemble, bench-verify pulse pass-through + buffered output into ito
- [ ] Install in-line; confirm machine still doses/autofills and ito reads flow

## Sources

- [Mini V2 control-board wiring reference](_reference/mini-v2-control-board-wiring.md) — GICAR
  pinout, blondica vs sandc taps, buffer part options.
- [06-001 — ito + `leva!` profiling](06-001-lucca-a53-mini-leva-firmware-integration.md).
