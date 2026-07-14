# flow-tap interposer — KiCad project

Buffers the stock GICAR flow-meter pulse into ito, in-line and reversible. Design rationale +
install steps are in the project doc: [06-015](../../06-015-gicar-flow-tap-interposer.md). Topology
picture: [flow-interposer.svg](flow-interposer.svg).

**Status (2026-07-13): routed + DRC-clean, fab-ready.** The board is generated headlessly
(`generate_pcb.py`, kiutils) and validated with `kicad-cli` (DRC: **0 violations, 0 unconnected**).
Gerbers/drill are exported in [`flow-tap-gerbers.zip`](flow-tap-gerbers.zip); a top render is
[`flow-tap-top.png`](flow-tap-top.png). Board size ≈ **23.1 × 19.8 mm**, 2-layer.

> Open `flow-tap.kicad_pcb` in KiCad for a final eyeball before ordering (mains-adjacent signal).
> The placement is functional but roomy — you may want to compact it and/or swap the vertical XH
> headers for right-angle (`S…-XH-A`) so the cables exit the board edges.

## Connectors (resolved)

All three ports are **JST XH, 2.5 mm** (the GICAR board connector measures 2.0 mm _between_ pins →
2.5 mm pitch; ito's IMPULSE side is XH too).

| Ref  | Footprint                               | Pinout                                                           |
| ---- | --------------------------------------- | ---------------------------------------------------------------- |
| `J1` | `JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical` | 1 key/blank · 2 +14.3 V (red) · 3 GND (black) · 4 signal (white) |
| `J2` | `JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical` | mirrors `J1` (to Vivaldi, pass-through)                          |
| `J3` | `JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical` | 1 GND · 2 OUT (buffered) · 3 +5 V — matches ito IMPULSE          |

The +14.3 V (`J1.2`/`J2.2`) passes `J1→J2` only and never reaches `J3`. `J3` taps `J1.4/J2.4`
(signal) buffered through `U1`, referenced to the shared GND.

## Components

| Ref | Value / Part                        | Footprint                       | Notes                                          |
| --- | ----------------------------------- | ------------------------------- | ---------------------------------------------- |
| U1  | **74LVC1G17** (SN74LVC1G17DBVR, TI) | `SOT-23-5`                      | single Schmitt buffer, non-inverting. JLC SMT. |
| C1  | **0.1 µF** X7R 50 V                 | `C_0603_1608Metric`             | decoupling at U1 VCC/GND. JLC SMT.             |
| J1  | GICAR meter (in)                    | `JST_XH_B4B-XH-A_1x04` vertical | hand-solder.                                   |
| J2  | to Vivaldi                          | `JST_XH_B4B-XH-A_1x04` vertical | hand-solder.                                   |
| J3  | to ito                              | `JST_XH_B3B-XH-A_1x03` vertical | hand-solder.                                   |

`U1` (SN74LVC1G17, DBV/SOT-23-5) pins: **1 NC · 2 A(in) · 3 GND · 4 Y(out) · 5 VCC** (per the TI
datasheet).

## Nets

```text
  N_PLUS (14.3 V) : J1.2 — J2.2                              [pass-through ONLY]
  GND             : J1.3 — J2.3 — J3.1 — U1.3 — C1.2         [B.Cu network]
  N_O    (pulse)  : J1.4 — J2.4 — U1.2 (A input)
  V5     (ito 5V) : J3.3 — U1.5 (VCC) — C1.1
  N_OUT  (buffer) : U1.4 (Y) — J3.2
```

Signals route on **F.Cu**; GND routes on **B.Cu** (own layer → never crosses a signal). No copper
pour is used, so there is no zone-fill step.

## Regenerate / validate / fab (headless)

```sh
# 1. generate the board (native, no KiCad needed)
python3 generate_pcb.py footprints flow-tap.kicad_pcb

# 2. validate + export with kicad-cli (KiCad 9; on Apple Silicon use the amd64 image)
docker run --rm --platform linux/amd64 -v "$PWD:/w" -w /w kicad/kicad:9.0 sh -c '
  kicad-cli pcb drc flow-tap.kicad_pcb
  kicad-cli pcb export gerbers -o gerbers/ flow-tap.kicad_pcb
  kicad-cli pcb export drill   -o gerbers/ flow-tap.kicad_pcb
  kicad-cli pcb render --side top -o flow-tap-top.png flow-tap.kicad_pcb'
```

`footprints/` holds the four KiCad-9 footprints the generator places (so it runs without a local
KiCad install).

> Note: `pcbnew` Python scripting crashes under amd64 emulation on Apple Silicon
> (`malloc(): unaligned tcache chunk`), so this project generates with **kiutils** (pure Python,
> native) and only uses the compiled `kicad-cli` for DRC/export/render.

## Order (JLC/PCBWay)

1. Upload [`flow-tap-gerbers.zip`](flow-tap-gerbers.zip).
2. Enable **SMT assembly for U1 + C1** only (LCSC parts); hand-solder `J1/J2/J3`.
3. Piggyback on the plumb-in bracket order.
