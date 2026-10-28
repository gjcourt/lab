# Unified ESP32 interposer, rev A: pre-measurement schematic

The schematic for [06-014](../../06-014-unified-esp32-interposer-board.md), drawn **before**
George's measurements M1–M10 come in, so layout can start the day they arrive. The design of record
is the [rev A plan](../../../docs/plans/2026-10-27-unified-esp32-interposer-rev-a-plan.md) (cited as
**plan §n**). The 06-015 flow tap it absorbs is in [`../flow-tap-pcb/`](../flow-tap-pcb/README.md).

**Status (2026-10-28): schematic as data, ERC-clean, not laid out.** Nothing here is a guess. Every
value that waits on a measurement is listed in [Placeholders](#placeholders-what-closes-each-one),
and every part number comes from a datasheet or a JLCPCB part page read on 2026-10-28.

| File                                   | What it is                                                                                                  |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| [`circuit.py`](circuit.py)             | **Single source of truth.** Parts, nets, NC pads, GPIO map, placeholders. Importable by a future generator. |
| [`check_circuit.py`](check_circuit.py) | ERC-style checker (10 checks). Exit 0 = pass.                                                               |
| [`footprints/`](footprints/)           | The 25 KiCad 9 footprints `circuit.py` names, copied from `kicad/kicad:9.0` (same pattern as 06-015).       |

```sh
cd 06-coffee-espresso/_reference/interposer-rev-a
python3 circuit.py              # part / net summary per function block
python3 check_circuit.py -v     # ERC; -v also prints the GPIO map
```

Output today: `116 parts (76 fitted, 40 DNP), 78 nets` and `ALL 10 CHECKS PASS`. Plain Python 3, no
dependencies. The checker reads pad names straight out of the vendored `.kicad_mod` files, so a typo
in a pin number fails C1.

**No KiCad schematic (`.kicad_sch`) in this rev.** kiutils can write one, but every one of the 116
parts would need a library symbol placed and wired or labelled by hand-written coordinates, and
`kicad-cli` has no headless netlist import to validate a `.net` file against. That is hours for a
drawing that adds nothing `circuit.py` + the checker don't already enforce. The layout generator
should read `circuit.py` directly (as 06-015's `generate_pcb.py` hard-codes its nets today), and DRC
on the generated board is the KiCad-side validation.

## What the checker enforces

| #   | Rule                                                                                                                                                     | Source                     |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| C1  | Every part has a vendored footprint; every `REF.pad` named exists in it                                                                                  | KiCad 9 library            |
| C2  | Every footprint pad is on a net or listed in `NC` with a reason                                                                                          | —                          |
| C3  | Every net ≥ 2 pins; no pin on two nets                                                                                                                   | —                          |
| C4  | `+14.3 V` (`N_PLUS`) touches only `J1.2` / `J2.2`                                                                                                        | 06-015, plan §3.4          |
| C5  | ito 5 V (`V5_ITO`, `ITO_EXP_5V`) never meets `+3V3` / `+5V` / `VA` / `VBUS`, directly or through any R, C, D, jumper or switch; U1 on ito 5 V, U2 on 3V3 | plan §3.4                  |
| C6  | Each GPIO used once and matches the GPIO table; no strapping, octal-PSRAM, UART0 or non-existent pin; USB only on GPIO19/20; analog nets on ADC1         | ESP32-S3-WROOM-1 DS v1.8   |
| C7  | `SB` / `SL` probe lines touch only the pass-through connectors and the series coupling cap; the aux pins are pure pass-through                           | plan §3.3                  |
| C8  | `S1` / `S2` lines touch only the pass-through connectors and one series R into a follower (no bias injected)                                             | plan §3.2                  |
| C9  | `ENC` lines touch only connectors, FET drains (source on GND, gate pulled down) and LVC inputs: pull-low only, no pull-ups, never driven high            | plan §3.5                  |
| C10 | IC power pins on the intended rails                                                                                                                      | each datasheet's pin table |

The checker was mutation-tested: putting a part on `N_PLUS`, a resistor on `SB_PROBE`, a pull-up on
`ENC_A`, GPIO3 on a signal, or `R39` from `V5_ITO` to 3V3 each fails the right check.

## Blocks

Pass-through copper is drawn `═══`. Every machine signal goes in on one connector and straight out
on its mate. Only `ENC` can pull low (plan §2 design invariant).

### F0 power, ESP32, USB

```text
 J4 XH-2 (5V in, our choice: 1 = +5V, 2 = GND) ──────────────┬── +5V ──┬── JP1.3 (VA option)
                                                             │         │
 J5 USB-C ── VBUS ──►|── D1 SS34 (VBUS → +5V only) ──────────┘   C3 10µ│
   CC1 ── R1 5k1 ── GND     CC2 ── R2 5k1 ── GND                       │
   D+ (A6,B6) ══ U3 USBLC6-2SC6 (1/6) ══ GPIO20                 U4 AMS1117-3.3 (VIN 3, GND 1, VOUT 2/tab)
   D- (A7,B7) ══ U3 (3/4) ═════════════ GPIO19                         │
   U3.5 VBUS, U3.2 GND                                         +3V3 ──┴── C4 22µ ── U5.2 3V3 (C5 22µ + C6 100n at pin)
 U5 ESP32-S3-WROOM-1-N8:  EN ── R3 10k ── 3V3, C7 1µ ── GND, SW1 ── GND   (DS v1.8 §9: R = 10k, C = 1µF)
                          GPIO0 ── R4 10k ── 3V3, SW2 (BOOT) ── GND
```

- **Never plug USB in while the machine is plugged in** (plan §3.1). D1 only stops the 5 V PSU
  back-feeding a USB host. It is not isolation.
- **USB headroom:** AMS1117 dropout is 1.3 V max at 0.8 A, so it wants ≥ 4.6 V in. USB through D1
  can sit just under that. Flashing works; Wi-Fi TX peaks on USB power may brown out. Use J4 for
  bench tests T2+.

### F1 / F2 `S1` / `S2` NTC taps (identical; 4 followers, one per NTC wire)

```text
 J6.1 (S1 probe) ═══════ S1_A ═══════ J7.1 (control board)        same for S1_B (J6.2/J7.2, R6, U6B),
                           │                                       S2_A (J8.1/J9.1, R7, U6C),
                          R5 1M                                    S2_B (J8.2/J9.2, R8, U6D)
                           │  S1A_IN
                (D2 BAV99, DNP: to VA / GND)
                           │
                       U6A MCP6004 follower (IN+ 3, IN- 2 = OUT 1), supply VA
                           │  S1A_BUF
                          R9 0R (divider top) ── S1A_DIV ── R13 DNP (divider bottom) ── GND
                           │
                          R17 1k ── S1A_ADC ── C9 100n ── GND
                           │
                       U7 ADS1115 AIN0   (S1B → AIN1, S2A → AIN2, S2B → AIN3)
 U7: VDD 3V3 (C13 100n), ADDR = GND → 0x48, SDA/SCL on I²C, ALERT/RDY → R21 10k ── 3V3, → GPIO10
 JP1 (3-pad, bridged 1-2 by default): 1 = +3V3, 2 = VA, 3 = +5V
```

- **Both NTC wires are buffered,** because which pin is the control board's GND is unknown (M3). The
  ADS1115 can then read each node single-ended, or differentially, in firmware. No pin is assumed to
  be GND.
- **Series R is 1 MΩ, not the plan's 10–100 kΩ** (see [Plan notes](#notes-on-the-plan)). With
  MCP6004 input bias ±1 pA typ, 1 MΩ costs ~1 µV of error. It also limits what flows into the
  op-amp's input diodes if the board is unpowered while the machine runs, or if M3 shows the node
  above VA. A 24 V fault pushes ~24 µA, against the MCP6004's ±2 mA input-pin rating.
- **D2–D5 are DNP.** BAV99 leakage is up to 25 nA at 20 V (Diodes Inc DS). Through a 200 kΩ source
  that is up to ~5 mV of error, which defeats the "no load" goal. The op-amp's own input diodes plus
  1 MΩ are the clamp. Fit them only if T4 shows a need.
- **VA and the divider are M3 placeholders.** Default VA = 3V3, R9–R12 = 0 Ω, R13–R16 not fitted. If
  M3 shows the node above ~3.3 V, set JP1 to 5 V **and** fit R13–R16 so every ADS input stays ≤
  VDD + 0.3 V (SBAS444E abs max). The ADS runs on 3V3 because its SDA/SCL VIH is 0.7 × VDD, which a
  3V3 bus can't reach at VDD = 5 V.
- **R17/C9 (1 kΩ / 100 nF):** RC into the ADS. The 1 kΩ is also the isolation R the MCP6004 needs to
  drive a capacitive load (DS20001733L §4.3).

### F3 / F4 `SB` / `SL` level taps (pass-through + DNP AC front-end)

```text
 J10.1 (SB probe) ═════ SB_PROBE ═════ J11.1          J10.2 ═════ SB_AUX ═════ J11.2 (pass-through only)
                           │
                        C14 (DNP, series coupling C; value + voltage TBD at M4)
                           │  SB_AC
                        R22 100k (DNP)
                           │  SB_FE ── R24 1M ── 3V3, R26 1M ── GND (DNP mid-rail bias)
                           │         D6 BAV99 (DNP) to 3V3 / GND
                         GPIO1 (ADC1_CH0)          SL: J12/J13, C15, R23, R25, R27, D7 → GPIO2 (ADC1_CH1)
```

- The probe line touches **only** the connectors and C14 (checker C7). The bias sits on our side of
  the capacitor, so no DC ever reaches the probe (plan §3.3).
- Firmware samples the AC amplitude on ADC1. ADC1 is used because ADC2 can't run alongside Wi-Fi
  (ESP32-S3 Series DS v2.2).
- Everything after the connectors is DNP until M4/M5. Pin 2 of each placeholder connector is passed
  through and touches nothing else, so a 2-wire sensor still works stock.

### F5 flow: 06-015 verbatim + ESP32 buffer

```text
 J1 GICAR (XH-4)                                   J2 to Vivaldi (XH-4)
   1 key-blank                                       1 key-blank
   2 +14.3V ═══════════ N_PLUS ═══════════════════   2     (J1.2 ↔ J2.2 ONLY; checker C4)
   3 GND    ═══════════ GND ══════════════════════   3
   4 o      ═══════════ N_O ══════════════════════   4
                         ├── U1 74LVC1G17 @ ito 5V (VCC 5 = J3.3 V5_ITO, C1 100n) ── Y 4 ── J3.2 → ito IMPULSE
                         └── U2 74LVC1G17 @ 3V3 (C2 100n) ── Y 4 ── FLOW_3V3 ── GPIO11 (pulse_counter)
 J3 to ito (XH-3): 1 GND, 2 OUT, 3 +5V (ito's)
```

- J1/J2/J3/U1/C1 and the net names are 06-015's, unchanged.
- **The plan's "confirm at layout" is closed:** SN74LVC1G17 input range is 0–5.5 V at any VCC
  (SCES351Y, recommended operating conditions), so U2 takes the 5 V `o` while powered from 3.3 V.
  Ioff keeps both buffers from loading `o` when their supply is off.
- ito's 5 V (`V5_ITO`) and our `+3V3` / `+5V` share only GND (checker C5).

### F6 ito `ENC` interposer

```text
 J14 KK-4 (encoder)   1 GND ═══ GND ═══ 1   J15 KK-4 (to ito ENC)
                      2 SW  ═══ ENC_SW ═ 2 ── Q3 drain │ U10 A
                      3 A   ═══ ENC_A ══ 3 ── Q1 drain │ U8 A
                      4 B   ═══ ENC_B ══ 4 ── Q2 drain │ U9 A
 inject:  GPIO4/5/6 ── R28-30 1k ── gate Q1-3 AO3400A (source GND) ; gate ── R31-33 100k ── GND
 read:    U8/U9/U10 74LVC1G17 @ 3V3 (C16-18 100n), Y → GPIO7 / GPIO15 / GPIO16
```

- **Pull-low only:** the FET can only short a line to GND, like a detent closing, and nothing ever
  drives a line high (checker C9). The 100 kΩ gate pull-downs hold every FET off while the ESP32 is
  unpowered, in reset, or booting, so the knob behaves stock.
- AO3400A: Vgs(th) 0.65–1.45 V, Rds(on) < 48 mΩ at Vgs 2.5 V (AOS DS rev 3.1), so a 3.3 V GPIO turns
  it fully on. Pinout 1 G, 2 S, 3 D. It is a JLC basic part, so no loading fee. The plan's other
  option, a 74LVC1G07, idles low with its input low, which would inject at boot.
- Read-back is a 5 V-tolerant LVC Schmitt input (II ±5 µA max), not a divider, so it adds no DC load
  to ito's pull-ups.

### F7 shared I²C

```text
 GPIO8 SDA / GPIO9 SCL ── R34 / R35 4.7k ── 3V3
   ├── U7 ADS1115 (0x48)
   ├── J16 Qwiic JST-SH 4-pin: 1 GND, 2 3V3, 3 SDA, 4 SCL (sparkfun.com/qwiic)
   └── U11 PCA9306 (DNP): VREF1 = 3V3, SCL1/SDA1 = bus; VREF2 = EN ── R36 200k (DNP) ── ito 5V
         SDA2 ── JP2 (open) ── J17.5 EXP SDA      SCL2 ── JP3 (open) ── J17.4 EXP SCK
         R37 / R38 4.7k (DNP) SDA2/SCL2 ── ito 5V       J17 (DNP): 1 +5V(ito), 2 GND, 3 NC, 4 SCK, 5 SDA
```

- PCA9306 hookup per SCPS113O §8.1.2 (EN tied to VREF2, 200 kΩ to the high-side supply). VREF1 ≤
  VREF2 − 0.6 V is satisfied by 3.3 V / 5 V.
- JP2/JP3 open and U11 unfitted mean the ito `EXPANSION` bus is isolated by default. There is no
  multi-master in rev A (plan §3.6).

### F8 `SER` stub (all DNP)

```text
 J18 (1x6 0.1"): 1 GND, 2 SER_3V3_H ── R39 0R ── 3V3,
   3 SER_TX_H ── R40 ── SER_TX ── GPIO17 (U1TXD)     each MCU-side net also has a DNP divider-bottom
   4 SER_RX_H ── R41 ── SER_RX ── GPIO18 (U1RXD)     R (R44-R47) to GND and a DNP BAV99 clamp
   5 SER_IO1_H ── R42 ── SER_IO1 ── GPIO13            (D8-D11) to 3V3 / GND
   6 SER_IO2_H ── R43 ── SER_IO2 ── GPIO14
```

Values are TBD until the M8 / Saleae capture. Nothing is inserted into the touchpad link (plan
§3.7).

### F9 on/off dry contact (all DNP)

```text
 GPIO12 ── R48 330 (DNP) ── U12 TLP222A pin 1 (LED A), pin 2 (LED K) ── GND
 U12 pins 4 / 3 (contact) ── J19 pins 1 / 2 (to the panel ON/OFF pair, if M8 finds one)
```

The TLP222A datasheet could not be retrieved, so the pinout and the LED resistor are **unverified**.
Check both against the datasheet before fitting.

## GPIO allocation

ESP32-S3-WROOM-1 module pins from datasheet v1.8 Table 3-1. Checker C6 enforces every row.

| GPIO | Module pin | Net          | Use                                  |
| ---- | ---------- | ------------ | ------------------------------------ |
| 0    | 27         | `BOOT`       | strapping (boot mode): SW2 + R4 only |
| 1    | 39         | `SB_FE`      | ADC1_CH0, SB level (DNP until M4)    |
| 2    | 38         | `SL_FE`      | ADC1_CH1, SL level (DNP until M5)    |
| 4    | 4          | `ENC_INJ_A`  | Q1 gate (pull `ENC_A` low)           |
| 5    | 5          | `ENC_INJ_B`  | Q2 gate                              |
| 6    | 6          | `ENC_INJ_SW` | Q3 gate                              |
| 7    | 7          | `ENC_RD_A`   | U8 read-back                         |
| 8    | 12         | `I2C_SDA`    | ADS1115, Qwiic, (PCA9306)            |
| 9    | 17         | `I2C_SCL`    |                                      |
| 10   | 18         | `ADS_ALERT`  | ADS1115 ALERT/RDY                    |
| 11   | 19         | `FLOW_3V3`   | flow `pulse_counter` (U2)            |
| 12   | 20         | `ONOFF_DRV`  | F9 photorelay LED (DNP)              |
| 13   | 21         | `SER_IO1`    | F8 spare (DNP)                       |
| 14   | 22         | `SER_IO2`    | F8 spare (DNP)                       |
| 15   | 8          | `ENC_RD_B`   | U9 read-back                         |
| 16   | 9          | `ENC_RD_SW`  | U10 read-back                        |
| 17   | 10         | `SER_TX`     | U1TXD, F8 (DNP)                      |
| 18   | 11         | `SER_RX`     | U1RXD, F8 (DNP)                      |
| 19   | 13         | `USB_DN`     | USB D- (fixed)                       |
| 20   | 14         | `USB_DP`     | USB D+ (fixed)                       |

Deliberately unused: GPIO3, 45, 46 (strapping, left at their datasheet defaults, Table 4-1);
GPIO35–37 (octal PSRAM on R8 modules, Table 3-1 note b, kept free so a module swap is safe);
GPIO43/44 (UART0 ROM console; add test pads at layout); GPIO39–42 (JTAG, spare); GPIO21, 38, 47, 48
(spare). GPIO26–34 are not module pins.

## Power budget

| Load                       | Rail   | Current                         | Source                   |
| -------------------------- | ------ | ------------------------------- | ------------------------ |
| ESP32-S3-WROOM-1 Wi-Fi TX  | 3V3    | 355 mA peak (802.11b, 20.5 dBm) | module DS v1.8 Table 6-4 |
| ESP32 supply requirement   | 3V3    | **≥ 0.5 A** must be available   | module DS v1.8 Table 6-2 |
| ADS1115                    | 3V3    | 0.2 mA max (25 °C), 0.3 mA max  | SBAS444E §5.5            |
| MCP6004 (4 amps)           | VA     | 4 × 170 µA max = 0.68 mA        | DS20001733L              |
| 74LVC1G17 × 4 (U2, U8–U10) | 3V3    | 4 × 10 µA max                   | SCES351Y ICC             |
| I²C pull-ups (both low)    | 3V3    | 2 × 0.7 mA                      | Ohm's law, 4.7 kΩ        |
| AMS1117 quiescent          | 5V     | 11 mA max                       | AMS1117 DS               |
| U1 74LVC1G17 (ito domain)  | ito 5V | 10 µA max (from ito, as 06-015) | SCES351Y                 |

- **Design point:** 3V3 at 0.5 A (the module's own requirement dominates; everything else is < 5
  mA). 5 V input ≥ 0.52 A (about 2.6 W). Spec the off-board PSU for ≥ 1 A at 5 V. ito's own HLK-PM01
  is only documented as "5 V ≥ 600 mA" (ito manual p.70), which leaves thin margin. A dedicated
  module or a 1 A+ USB brick is the safer choice.
- **LDO heat:** (5.0 − 3.3) V × 0.355 A = 0.60 W at the TX peak. SOT-223 θJA is 90 °C/W (AMS DS), so
  a sustained peak would be a 54 °C rise. TX is bursty, so the average is far lower. Give the tab a
  copper pour at layout anyway, and measure the rail during T2.

## BoM

From `circuit.py` (it is the source; regenerate rather than hand-edit). Library class is as read on
each **jlcpcb.com/partdetail** page on 2026-10-28. **Stock is unchecked for every part**: the page
text we could read shows no stock figure. Check all of it on order day (plan §6). "unstated" means
the page showed no clear Basic/Extended label.

| Refs                               | Value                | MPN                       | LCSC     | JLC class   | Fit |
| ---------------------------------- | -------------------- | ------------------------- | -------- | ----------- | --- |
| U5                                 | ESP32-S3-WROOM-1-N8  | Espressif                 | C2913198 | extended    | fit |
| U4                                 | AMS1117-3.3, 1 A     | AMS1117-3.3               | C6186    | basic       | fit |
| U6                                 | MCP6004 quad op-amp  | MCP6004T-I/SL (Microchip) | C7378    | extended    | fit |
| U7                                 | ADS1115              | ADS1115IDGSR (TI)         | C37593   | extended    | fit |
| U1 U2 U8 U9 U10                    | 74LVC1G17            | SN74LVC1G17DBVR (TI)      | C7836    | extended    | fit |
| Q1 Q2 Q3                           | AO3400A N-FET        | AO3400A (AOS)             | C20917   | basic       | fit |
| U3                                 | USB ESD              | USBLC6-2SC6 (ST)          | C7519    | extended    | fit |
| J5                                 | USB-C 16P            | TYPE-C-31-M-12 (HRO)      | C165948  | extended    | fit |
| D1                                 | Schottky 3 A 40 V    | SS34 (MDD)                | C8678    | unstated    | fit |
| J16                                | JST-SH 4-pin (Qwiic) | SM04B-SRSS-TB(LF)(SN)     | C160404  | extended    | fit |
| SW1 SW2                            | tactile 5.1 mm       | TS-1187A-B-A-B (XKB)      | C318884  | unstated    | fit |
| C1 C2 C6 C8–C13 C16–C18            | 100 nF 50 V X7R 0603 | CC0603KRX7R9BB104         | C14663   | basic       | fit |
| C7                                 | 1 µF 0603            | CL10A105KB8NNNC           | C15849   | basic       | fit |
| C3                                 | 10 µF 0805           | CL21A106KAYNNNE           | C15850   | basic       | fit |
| C4 C5                              | 22 µF 0805           | CL21A226MAQNNNE           | C45783   | unstated    | fit |
| R9–R12                             | 0 Ω                  | 0603WAF0000T5E            | C21189   | basic       | fit |
| R17–R20 R28–R30                    | 1 kΩ                 | 0603WAF1001T5E            | C21190   | basic       | fit |
| R34 R35                            | 4.7 kΩ               | 0603WAF4701T5E            | C23162   | basic       | fit |
| R1 R2                              | 5.1 kΩ               | 0603WAF5101T5E            | C23186   | basic       | fit |
| R3 R4 R21                          | 10 kΩ                | 0603WAF1002T5E            | C25804   | basic       | fit |
| R31–R33                            | 100 kΩ               | 0603WAF1003T5E            | C25803   | basic       | fit |
| R5–R8                              | 1 MΩ                 | 0603WAF1004T5E            | C22935   | basic       | fit |
| D2–D11                             | BAV99                | BAV99,215 (Nexperia)      | C2500    | unstated    | DNP |
| U11                                | PCA9306              | PCA9306DCUR (TI)          | C33196   | extended    | DNP |
| U12                                | TLP222A photorelay   | TLP222A(TP1,F) (Toshiba)  | C2152279 | extended    | DNP |
| C14 C15                            | 100 nF (TBD at M4/5) | CC0603KRX7R9BB104         | C14663   | basic       | DNP |
| R22 R23                            | 100 kΩ               | 0603WAF1003T5E            | C25803   | basic       | DNP |
| R24–R27                            | 1 MΩ                 | 0603WAF1004T5E            | C22935   | basic       | DNP |
| R36                                | 200 kΩ               | 0603WAF2003T5E            | C25811   | basic       | DNP |
| R37 R38                            | 4.7 kΩ               | 0603WAF4701T5E            | C23162   | basic       | DNP |
| R39                                | 0 Ω                  | 0603WAF0000T5E            | C21189   | basic       | DNP |
| R48                                | 330 Ω (TBD)          | 0603WAF3300T5E            | C23138   | basic       | DNP |
| R13–R16 R40–R47                    | TBD                  | —                         | —        | —           | DNP |
| J1 J2 / J3 / J4                    | JST XH 4 / 3 / 2-pin | B4B / B3B / B2B-XH-A      | —        | hand-solder | fit |
| J14 J15                            | Molex KK 254 4-pin   | 22-27-2041                | —        | hand-solder | fit |
| J6–J13                             | **placeholder** 1x2  | 2.54 mm header            | —        | hand-solder | fit |
| J17 J18 J19                        | 1x5 / 1x6 / 1x2      | 2.54 mm header            | —        | hand-solder | DNP |
| JP1 (bridged 1-2), JP2, JP3 (open) | solder jumpers       | copper                    | —        | —           | —   |

Fitted extended parts (one JLC loading fee each): U5, U6, U7, 74LVC1G17, U3, J5, J16, plus D1, SW
and C4/C5 if their "unstated" class turns out to be extended.

## Placeholders: what closes each one

| Closes  | Refs                                | Placeholder today                                                                                       |
| ------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **M1**  | whole board                         | One GND ties ESP32, ito and control-board LV GND. Safe only if the control board's LV side is isolated. |
| **M2**  | J6–J9                               | `S1`/`S2` connector family + pin count. Drawn as 2-pin 2.54 mm headers.                                 |
| **M3**  | JP1, R9–R16, ADS PGA                | Node voltage range: VA 3V3 vs 5 V, whether the divider is fitted, the ADS1115 FSR. Default VA = 3V3.    |
| **M3**  | R5–R8                               | 1 MΩ assumes the node sits within 0..VA. If not, re-run T4 with the board powered **and** unpowered.    |
| **M4**  | J10, J11, C14, R22, R24, R26, D6    | `SB` method + excitation. 2-pin header (pin 2 pass-through only). Front-end DNP; C14 value/rating TBD.  |
| **M5**  | J12, J13, C15, R23, R25, R27, D7    | `SL` method + connector. Same as M4.                                                                    |
| **M6**  | J14, J15                            | KK 254 4-pin and pin order on George's cable. Drawn per ito manual p.63 (1 GND, 2 SW, 3 A, 4 B).        |
| **M7**  | firmware                            | Detent rest state: whether injection is masked at rest. No part change expected.                        |
| **M8**  | J18, R39–R47, D8–D11, U12, R48, J19 | `SER` vs ribbon vs discrete. All DNP; series/divider values TBD.                                        |
| **M9**  | J1, J2, U1, U2                      | GICAR `+` ≈ 14.3 V, `o` pulled to 5 V: re-check only.                                                   |
| **M10** | outline                             | Board size, mount point, cable lengths. No outline drawn.                                               |
| DS      | U12, R48                            | TLP222A datasheet not retrieved: pinout and LED current unverified.                                     |
| DS      | J17                                 | ito `EXPANSION` pad pitch/form not measured: drawn as a 2.54 mm 1x5 header.                             |
| DS      | U3                                  | USBLC6-2SC6 pinout taken from the KiCad library symbol; the ST datasheet would not download.            |
| DS      | U11                                 | KiCad `VSSOP-8_2.3x2mm` land vs TI DCU land pattern: compare at layout (DNP part).                      |

## Layout notes (for the generator, not done here)

- ESP32-S3-WROOM-1 PCB antenna keep-out: module DS v1.8 §3 points to the ESP32-S3 Hardware Design
  Guidelines ("General Principles of PCB Layout for Modules"); read that before placing U5.
- Grep the generated `.kicad_pcb` for a bare `(remove_unused_layers)` before fab (06-015 kiutils
  bug, lab PR #73).
- `D1` pad 1 = cathode (KiCad diode convention). `U4` tab = VOUT (`SOT-223-3_TabPin2`).
- Keep the `S1`/`S2` input nodes (`S*_IN`) short and guarded: they are 1 MΩ, pA-level nodes.

## Notes on the plan

No factual errors found. Four places where this schematic goes beyond, or departs from, the plan's
wording:

1. **§3.2 series R "~10–100 kΩ" → 1 MΩ here.** The plan's range is not wrong for a powered follower.
   But the board runs on its own PSU, and if that PSU is off while the machine is on, the NTC node
   feeds the unpowered op-amp's input diodes. A 1.5 V node through 100 kΩ is ~9 µA of load on a ~200
   kΩ NTC. At 1 MΩ it is ~1 µA, and pA bias makes the extra R free. T4 should run with the board
   both powered and unpowered.
2. **§3.4 "LVC inputs are 5 V-tolerant (confirm at layout)": confirmed** (SCES351Y: VI 0–5.5 V at
   any VCC; Ioff for partial power-down).
3. **§3.5 open-drain driver:** an AO3400A N-FET with a gate pull-down was picked over a 74LVC1G07,
   because the '07 pulls low whenever its input is low, which includes boot. Both options are in the
   plan.
4. **§3.2 one follower per NTC (implied) → one per wire,** because the NTC's GND pin is unknown
   until M3.

## Sources (read 2026-10-28)

- ESP32-S3-WROOM-1/1U datasheet v1.8 (Espressif): Table 1-1 variants, Table 3-1 pins, §4 strapping,
  Table 6-4 current, §9 peripheral schematic. ESP32-S3 Series datasheet v2.2: ADC2 vs Wi-Fi note.
- TI ADS1115 SBAS444E (Dec 2024); TI SN74LVC1G17 SCES351Y (Oct 2025); TI PCA9306 SCPS113O (Sep
  2023); Microchip MCP6001/2/4 DS20001733L; AOS AO3400A rev 3.1; AMS AMS1117 datasheet; Diodes Inc
  BAV99 ds12007 (pinout and leakage; the fitted part is the Nexperia BAV99,215).
- JLCPCB part pages for every LCSC number above; SparkFun Qwiic pinout (sparkfun.com/qwiic).
- ito Hardware Reference Manual pp.59, 63, 64, 70 (via `reference_ito_connector_pinout`); 06-015 for
  J1/J2/J3/U1/C1.
