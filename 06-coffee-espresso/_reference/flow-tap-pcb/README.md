# flow-tap interposer — KiCad project

Buffers the stock GICAR flow-meter pulse into ito, in-line and reversible. Design rationale +
install steps are in the project doc: [06-015](../../06-015-gicar-flow-tap-interposer.md). Topology
picture: [flow-interposer.svg](flow-interposer.svg).

> **No KiCad on the authoring machine to validate a `.kicad_sch`**, so this ships as a project stub
> (`flow-tap.kicad_pro`) + the exact netlist/BoM below. It's five parts — drawing it in KiCad on
> Windows is ~10 minutes. Open the `.kicad_pro`, draw the schematic from the netlist, assign the
> footprints, lay out (~20 × 20 mm, 2-layer), and export Gerbers/BoM/CPL.

## Components

| Ref | Value / Part                        | Footprint                         | Notes                                               |
| --- | ----------------------------------- | --------------------------------- | --------------------------------------------------- |
| U1  | **74LVC1G17** (SN74LVC1G17DBVR, TI) | `Package_TO_SOT_SMD:SOT-23-5`     | single Schmitt buffer, non-inverting. JLC-assemble. |
| C1  | **0.1 µF** X7R 50 V                 | `Capacitor_SMD:C_0603_1608Metric` | decoupling, close to U1 VCC/GND. JLC-assemble.      |
| R1  | _(optional)_ 100 Ω                  | `Resistor_SMD:R_0603_1608Metric`  | series at U1 input for protection; omit if unsure.  |
| J1  | Conn 1×3 — GICAR meter              | _TBD (match meter connector)_     | receptacle the meter plugs into.                    |
| J2  | Conn 1×3 — to Vivaldi               | _TBD (match Vivaldi socket)_      | plug identical to the meter's, into the Vivaldi.    |
| J3  | Conn 1×3 — to ito                   | _TBD (match ito flow cable)_      | fallback `Connector_JST:JST_XH_B3B-XH-A_1x03`.      |

Connector footprints stay TBD until the GICAR + ito connector photos land; JST-XH 2.54 mm is the
universal fallback for all three (+ two adapter pigtails).

## Netlist (draw these nets)

```text
  N_PLUS  (14.3 V) : J1.1(+) — J2.1(+)                              [pass-through ONLY]
  GND              : J1.2(−) — J2.2(−) — J3.3(GND) — U1.GND — C1.b [— R1? no]
  N_O     (pulse)  : J1.3(o) — J2.3(o) — U1.A(in)   [via R1 if fitted]
  V5      (ito 5V) : J3.2(5V) — U1.VCC — C1.a
  N_OUT   (buffer) : U1.Y(out) — J3.1(OUT)
```

- `U1` pin functions: **VCC, GND, A (input), Y (output), NC** — confirm the SOT-23-5 pin numbers
  against the SN74LVC1G17 datasheet when you place the symbol (they vary by vendor/package).
- **`+` (14.3 V) touches only J1↔J2** — never U1 or J3. That isolation is the safety feature; keep
  it.

## Order (JLC/PCBWay)

1. Export Gerbers, BoM (`U1`, `C1`, optional `R1` with LCSC part numbers), and CPL/centroid.
2. Enable **SMT assembly for U1 + C1** only; leave `J1/J2/J3` as hand-soldered through-hole.
3. Piggyback on the plumb-in bracket order.
