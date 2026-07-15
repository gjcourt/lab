# XIAO ESP32-C3 IR + RF blaster hat — KiCad project

A XIAO-carrier "hat": the XIAO ESP32-C3 sockets in horizontally (USB-C off the **west** edge), the
board carries a **triple-940 nm IR blaster** (MOSFET-driven) on the front, and an **E07-M1101D
(CC1101) sub-GHz module** rides a swappable 2×4 female socket flipped to the **back** with its
antenna off the **south** edge. Design rationale + build lifecycle are in the project doc:
[03-027](../../03-027-xiao-c3-ir-rf-blaster-carrier-pcb.md).

**Status (2026-07-14): routed + DRC-clean, fab-ready.** Generated headlessly (`generate_pcb.py`,
kiutils), zone-filled (`fill.py`, pcbnew), validated with `kicad-cli` (DRC: **0 violations, 0
unconnected**). Gerbers/drill are in [`xiao-c3-ir-rf-gerbers.zip`](xiao-c3-ir-rf-gerbers.zip);
renders are [`…-top.png`](xiao-c3-ir-rf-top.png) / [`…-bottom.png`](xiao-c3-ir-rf-bottom.png). Board
size **23 × 54 mm**, **4-layer**.

> Open `xiao-c3-ir-rf.kicad_pcb` in KiCad for a final eyeball before ordering. The E07 socket is on
> the back so the module tucks over the XIAO; confirm the module body clears the XIAO's USB-C shell.

## Stackup (4-layer)

| Layer    | Use                                             |
| -------- | ----------------------------------------------- |
| `F.Cu`   | parts + signal (IR front-end, XIAO fan-out)     |
| `In1.Cu` | **GND** plane                                   |
| `In2.Cu` | **+5 V** plane                                  |
| `B.Cu`   | signal + the E07 module socket (module on back) |

Every SMD GND pad stitches to `In1` and every SMD +5 V pad to `In2` with a via; the XIAO's power
pins are through-hole so they hit the planes directly.

## Floorplan (north → south)

1. **IR LEDs** (D1–D3, 940 nm THT 5 mm) across the north edge, aimed off-board.
2. **Current-limit R** (R1–R3, 15 Ω) then the **MOSFET gate cluster** (Q1 + R4/R5, C1/C2 bulk).
3. **XIAO ESP32-C3** (official Seeed DIP footprint, rotated 180° → USB-C exits the **west** edge).
4. **E07-M1101D** on a 2×4 female socket, flipped to the **back**, antenna off the **south** edge,
   with its 3V3 decaps (C3/C4) in the strip below the XIAO.

## Pin map (XIAO C3 — no strapping pins used)

| Net       | XIAO pin | GPIO | Use                                           |
| --------- | -------- | ---- | --------------------------------------------- |
| `IR_TX`   | D1       | 3    | MOSFET gate drive (IR LEDs)                   |
| `CC_CSN`  | D2       | 4    | CC1101 chip-select                            |
| `CC_MOSI` | D3       | 5    | SPI MOSI                                      |
| `CC_GDO2` | D4       | 6    | CC1101 aux (optional)                         |
| `CC_MISO` | D6       | 21   | SPI MISO                                      |
| `CC_SCK`  | D7       | 20   | SPI clock                                     |
| `CC_GDO0` | D10      | 10   | CC1101 OOK data (`remote_transmitter` drives) |

Strapping pins **D0/GPIO2, D8/GPIO8, D9/GPIO9** are left spare. `IR_TX` is on **D1/GPIO3** (not D0)
so the 10 kΩ gate pulldown can't drag a strap low at reset. **Power:** XIAO 3V3 → module VCC; **+5 V
(VBUS)** → IR LEDs; common GND.

> ⚠ **Firmware must match this pin map.** The ESPHome config
> (`gjcourt/homelab → firmware/esphome/ir-rf-blaster-xiao-c3.yaml`) predates this re-layout and used
> the older v0.2 assignment — align its GPIOs to the table above before flashing.

## Components

| Ref     | Value / Part                   | Footprint                         | Notes                              |
| ------- | ------------------------------ | --------------------------------- | ---------------------------------- |
| D1–D3   | 940 nm IR LED (e.g. TSAL6400)  | `LED_D5.0mm`                      | THT, hand-solder; D3 optional/DNP  |
| R1–R3   | 15 Ω                           | `R_0805_2012Metric`               | LED current limit. JLC SMT (Basic) |
| Q1      | **AO3400A** N-ch MOSFET        | `SOT-23`                          | low-side switch. JLC SMT           |
| R4      | 100 Ω                          | `R_0603_1608Metric`               | gate series. JLC SMT               |
| R5      | 10 kΩ                          | `R_0603_1608Metric`               | gate pulldown → GND. JLC SMT       |
| C1 / C2 | 100 nF / 22 µF                 | `C_0603` / `C_0805`               | 5 V decouple + bulk. JLC SMT       |
| C3 / C4 | 100 nF / 10 µF                 | `C_0603` / `C_0805`               | 3V3 decouple at module. JLC SMT    |
| A1      | **XIAO ESP32-C3**              | `XIAO-ESP32-C3-DIP`               | socketed (2×7 female headers)      |
| M1      | **E07-M1101D** (CC1101 module) | `PinSocket_2x04_P2.54mm_Vertical` | **back-mounted, swappable**        |

`M1` socket is on the **back** so the module is removable — swap E07 bands (315/433/868/915 MHz)
without re-spinning the board. E07-M1101D pinout (CDEBYTE fixed): **1 GND · 2 VCC(3V3) · 3 GDO0 · 4
CSN · 5 SCK · 6 MOSI · 7 MISO · 8 GDO2**.

## Regenerate / validate / fab (headless)

```sh
# 1. generate the board (native, no KiCad needed) — writes UNFILLED zones
python3 generate_pcb.py footprints xiao-c3-ir-rf.kicad_pcb

# 2. fill zones + validate + export with kicad-cli (KiCad 9; on Apple Silicon use the amd64 image)
docker run --rm --platform linux/amd64 -v "$PWD:/w" -w /w kicad/kicad:9.0 sh -c '
  python3 fill.py xiao-c3-ir-rf.kicad_pcb xiao-c3-ir-rf.kicad_pcb
  kicad-cli pcb drc xiao-c3-ir-rf.kicad_pcb
  kicad-cli pcb export gerbers -o gerbers/ xiao-c3-ir-rf.kicad_pcb
  kicad-cli pcb export drill   -o gerbers/ xiao-c3-ir-rf.kicad_pcb
  kicad-cli pcb export svg --layers "F.Cu,Edge.Cuts,F.Silkscreen" --page-size-mode 2 -o top.svg xiao-c3-ir-rf.kicad_pcb'
```

`footprints/` holds the eight KiCad-9 footprints the generator places (so it runs without a local
KiCad install). `fill.py` zone-fills via `pcbnew.ZONE_FILLER` — needed because the planes are
written unfilled.

> Note: `pcbnew`'s `FootprintLoad` crashes under amd64 emulation on Apple Silicon, so the board is
> **generated** with kiutils (pure Python, native) and only the compiled `kicad-cli` / `pcbnew`
> zone-filler run in the container.

## Order (JLC)

1. Upload [`xiao-c3-ir-rf-gerbers.zip`](xiao-c3-ir-rf-gerbers.zip). Select **4-layer**.
2. Enable **SMT assembly** (top side only) and upload the BOM + CPL:
   - BOM: [`xiao-c3-ir-rf-BOM.csv`](xiao-c3-ir-rf-BOM.csv)
   - CPL / pick-and-place: [`xiao-c3-ir-rf-CPL.csv`](xiao-c3-ir-rf-CPL.csv)
3. Hand-solder the 3 IR LEDs (`D1–D3`), the XIAO sockets (`A1`), and the E07 socket (`M1`) — they're
   not in the BOM/CPL.
4. The E07 module drops into its 2×4 socket on the back — leave it removable for band swaps.

### Assembly BOM (all JLC **Basic** — no extended-part fee)

| Designator | Value   | Package | LCSC   | Library |
| ---------- | ------- | ------- | ------ | ------- |
| R1,R2,R3   | 15 Ω    | 0805    | C17480 | Basic   |
| R4         | 100 Ω   | 0603    | C22775 | Basic   |
| R5         | 10 kΩ   | 0603    | C25804 | Basic   |
| C1,C3      | 100 nF  | 0603    | C14663 | Basic   |
| C2         | 22 µF   | 0805    | C45783 | Basic   |
| C4         | 10 µF   | 0805    | C15850 | Basic   |
| Q1         | AO3400A | SOT-23  | C20917 | Basic   |

> ⚠ **Verify rotations in JLC's CPL preview before ordering.** The CPL carries KiCad's rotations;
> chip R/C usually map 1:1, but **`Q1` (SOT-23) commonly needs a 180° flip** to line pin 1 up with
> JLC's part orientation. JLC's online viewer overlays each part on its footprint — spin any that
> look wrong there (it's non-destructive, and easier than second-guessing the CSV).
