# Unified ESP32 Interposer Board, rev A: plan

**Status:** plan only (no KiCad yet). **Decided 2026-10-26:** rev A ships **everything except the
`SER` interposer**: ESP32, ADS1115 taps on `S1`/`S2`, `SL`/`SB` level taps, the ito `ENC`
interposer, a shared I²C header, and the 06-015 flow-tap circuit merged in. `SER` is a header +
footprint only, for rev B after the Saleae capture. **Goal:** order this week.

**Project file:** TBD. Either this extends **06-014** or it becomes a new **06-020**; George is
deciding (see [Relationship to existing projects](#8-relationship-to-existing-projects)).

**Machine:** La Spaziale S1 Mini Vivaldi II = LUCCA A53 Mini, US 120 V. Architecture source of
truth: hestia `/mnt/main/family/projects/electronics/espresso/ARCHITECTURE.md` (cited as **ARCH
§n**), plus the lab
[control-board wiring reference](../../06-coffee-espresso/_reference/mini-v2-control-board-wiring.md).

> **Ground rule for this plan.** A fact marked **✅ verified** has a cited source or a measurement
> on record. Everything else is **⚠️ unverified** and is listed in
> [Open facts George must measure before layout](#open-facts-george-must-measure-before-layout).
> Layout must not start on a function whose open facts are not closed. A function that can't be
> closed this week gets **DNP footprints** (or is left off) rather than a guessed circuit.

---

## 1. What the board does

ito keeps the real-time profiling loop (pump phase-angle, zero-cross, brew pressure, flow into
`IMPULSE`). The ESP32 board owns everything else and reports it to Home Assistant over ESPHome (ARCH
§10, hestia AGENTS.md "Unified interposer board").

| #   | Function                          | Rev A                                 | Feeds                                     |
| --- | --------------------------------- | ------------------------------------- | ----------------------------------------- |
| F1  | `S1` steam-boiler NTC tap         | ✅ in (passive, buffered)             | HA temp + **derived steam pressure**      |
| F2  | `S2` group NTC tap                | ✅ in (passive, buffered)             | HA temp                                   |
| F3  | `SB` boiler-level tap             | ⚠️ in **only if** method is confirmed | HA level / refill state                   |
| F4  | `SL` tank-level tap               | ⚠️ in **only if** method is confirmed | HA tank-empty                             |
| F5  | GICAR flow tap (06-015 merged)    | ✅ in                                 | ito `IMPULSE` (5 V) **and** ESP32 (3.3 V) |
| F6  | ito `ENC` interposer              | ✅ in (open-drain inject + read)      | drive leva! menus open-loop from HA       |
| F7  | Shared I²C header                 | ✅ in                                 | future sensors; later ito `EXPANSION`     |
| F8  | `SER` touchpad interposer         | ❌ stub (header + DNP footprints)     | rev B                                     |
| F9  | On/off dry contact (06-017 style) | ⚠️ optional DNP, see §3.8             | HA on/off without `SER`                   |

## 2. Block diagram

```text
                     ┌──────────────────────── UNIFIED INTERPOSER (rev A) ────────────────────────┐
 5 V in (off-board   │  5V ─► 3V3 LDO ─► ESP32-S3 module ◄─ USB-C (bench flashing only)           │
 isolated PSU) ─────►│                     │  │  │  │  │                                           │
                     │          I²C ───────┘  │  │  │  └── SER stub header (DNP, rev B) ─────────────┼─► (touchpad SER, later)
                     │           │            │  │  └───── on/off opto (DNP) ───────────────────────┼─► front-panel ON/OFF pins (if confirmed)
                     │   ADS1115 ◄─ buffers ◄─┼──┼── S1 in ═══════ pass-through ═══════ S1 out ─────┼─► control board S1
  S1 probe ─────────►│                        │  │   S2 in ═══════ pass-through ═══════ S2 out ─────┼─► control board S2
  S2 probe ─────────►│   level front-end(s) ◄─┼──┼── SB/SL in ════ pass-through ═══════ SB/SL out ──┼─► control board SB/SL
  SB/SL probes ─────►│                        │  │                                                  │
  GICAR meter ──────►│ J1 ════ pass-through ══╪══╪═══════════════════════════════ J2 ──────────────┼─► control board F
                     │   └─ o ─► 74LVC1G17 @5V (ito domain) ─► J3 ──────────────────────────────┼─► ito IMPULSE
                     │   └─ o ─► 74LVC1G17 @3V3 ─────────────► ESP32 pulse counter              │
  encoder (KK) ─────►│ ENC in ═══ pass-through ════ ENC out ───────────────────────────────────────┼─► ito ENC
                     │   A/B/SW ◄─ open-drain inject (ESP32) + 5V-safe read                        │
                     │  STEMMA-QT/JST-SH I²C header (3V3) ; ito EXPANSION I²C pads (DNP translator)│
                     └─────────────────────────────────────────────────────────────────────────────┘
 ═══ = copper pass-through: the stock signal path is unbroken whether the ESP32 is powered or not.
```

**Design invariant (the 06-015 rule, applied to every channel):** each machine signal goes in on a
connector and straight out on the matching connector. The ESP32 side only **listens** at high
impedance. The one exception is `ENC`, which can also **pull low**, the same way the real encoder
does. Unplug the board and re-mate the original plugs → bone stock.

## 3. Per-function interface

### 3.1 Power (F0)

- **No mains on this PCB.** Rev A takes **5 V DC from an off-board, isolated, certified supply**:
  either a second HLK-PM01-class module in its own enclosure on always-live `F`/`N` (ito already
  does this: ARCH §11, lab 06-001), or a USB brick on a smart plug. That deletes every creepage
  problem from this board.
  - ito's manual specifies **8 mm creepage 5 V↔mains** for its own on-board HLK footprint (✅
    `reference_ito_connector_pinout`, manual p.70). A future rev that puts the AC-DC module on-board
    must honour ≥8 mm plus a routed slot. Rev A does not.
  - `F`/PHASE + `N` are **always live while plugged in**, even in standby (✅ wiring reference, "NO
    switched mains rail"). So the board is powered whenever the machine is, which is what HA wants.
- **3V3 rail:** an LDO from 5 V, rated ≥ 500 mA continuous for ESP32 Wi-Fi peaks. Pick the MPN at
  layout from JLC basic/preferred stock. Bulk + local decoupling per the module datasheet.
- **Budget (estimate, verify at layout):** ESP32 module (Wi-Fi peaks dominate) + ADS1115 + buffers +
  two LVC gates. Well under 1 A at 5 V.
- **Grounds (the safety question).** One GND net is unavoidable. `ENC` needs ito GND (the encoder
  shorts lines to ito GND, ✅ manual p.63). The flow tap and NTC taps need control-board GND (06-015
  already ties ito GND to control-board GND via GICAR pin 3, ✅ 06-015). So **ESP32 GND = ito GND =
  control-board low-voltage GND.**
  - That is only safe if the control board's low-voltage side is **isolated from mains**. 06-016
    says the board makes its rails from an **onboard transformer** (isolated if so), but this is ⚠️
    **unverified** on the machine. **Measure before layout (M1).**
  - **Never connect USB to the board while the machine is plugged in.** Flash on the bench; OTA
    after install.

### 3.2 `S1` / `S2` NTC taps (F1, F2)

- **Known:** `S1` = steam-boiler NTC, `S2` = group NTC (✅ ARCH §6). Community RE reports a **~200
  kΩ NTC**, 165–228 kΩ at room temperature, not PT1000 (⚠️ s1cafe t2330 via 06-016; not measured on
  this machine). Alarm thresholds: short > 145 °C / open < 60 °C (✅ ARCH §6).
- **Tap method (passive, high impedance).** Pass both NTC wires straight through. Sense the **node
  voltage the control board already develops across the NTC**: tap → series R (~10–100 kΩ, ESD/fault
  limit) → **CMOS rail-to-rail op-amp follower** (pA-class input bias) → RC → ADS1115 input.
  - Why a buffer: with a ~200 kΩ source, the ADS1115's switched-capacitor input impedance (it is
    PGA-dependent; take the figures from the TI datasheet at layout) is not negligible and would
    shift the reading the **control board** sees. The follower's input load is effectively zero. The
    stock board must read the same temperature with the ESP32 board in or out (test **T4**).
  - **No bias current is injected.** We never add a pull-up/down onto the NTC line.
- **Converting voltage → temperature** needs the board's bias network (supply voltage + series
  resistor, or a current source) and the NTC curve (R25/β). Neither is documented (⚠️ ARCH §13 item
  3). **Rev A only has to capture the voltage cleanly**, so the curve can be fitted in firmware
  later from bench data (06-016 Stage 2: log R vs displayed temp). Layout needs only the **node
  voltage range** (M3).
- **Derived steam pressure:** firmware-only, from the saturation curve of the `S1` temperature (ARCH
  §10 decision; no transducer).
- **Input protection:** clamp the follower input to its rails (BAV99-class or the op-amp's own
  diodes, through the series R), so a probe fault can't damage the ESP32 side. The clamp current
  path must not load the line in normal range.

### 3.3 `SB` / `SL` level taps (F3, F4)

- **Known:** `SB` drives auto-refill (`EV AL`); `SL` drives the `EMPTY` lamp (✅ ARCH §6). **Sensing
  method unknown** (⚠️). Boiler level on espresso machines is commonly a conductive probe excited
  with **AC** (to prevent electrolysis and plating); tank level may be a reed/float switch. Neither
  is confirmed for this machine.
- **Hazard if the method is a conductive probe:** any **DC** path or DC bias on that line (a GPIO
  pull-up, an un-coupled ADC input, a leaky clamp) can plate the probe, scale it, or shift the
  board's threshold, so autofill fails or overfills. So:
  - **AC-couple** (series C) into a high-impedance comparator/peak detector. No DC path to the probe
    line, ever.
  - **Bench-prove on a beaker** (T5) before the machine.
- **Rev A rule:** if M4/M5 are not closed this week, **lay out the pass-through connectors and a DNP
  front-end footprint only**. The pass-through still lets a later rework add the circuit, and the
  board can ship without blocking on this.

### 3.4 Flow tap (F5): 06-015 merged

- Reuse 06-015 verbatim for the ito path (✅ lab 06-015 + `_reference/flow-tap-pcb/`):
  - `J1` GICAR in / `J2` to the Vivaldi: **JST XH 4-pin**, pos 1 key-blank, 2 = +14.3 V (red), 3 =
    GND (black), 4 = signal `o` (white). `J3` to ito `IMPULSE`: **JST XH 3-pin**, 1 GND / 2 OUT / 3
    +5 V (✅).
  - `+14.3 V` bridges `J1↔J2` **only**. No path to any other net (✅ 06-015 "safe by
    construction").
  - `U1` 74LVC1G17 on **ito's 5 V** (from `J3.3`), C1 100 nF, LCSC C7836 / C14663 (✅ BoM).
- **Add the ESP32 path:** a second 74LVC1G17 (`U1b`) **powered from 3V3**, input on `o`. LVC inputs
  are 5 V-tolerant per the TI datasheet (confirm at layout). Its output goes to an ESP32 GPIO for
  ESPHome `pulse_counter`.
  - `o` is a **5 V open-collector, pulled up inside the Vivaldi** (✅ wiring reference), so two
    high-impedance Schmitt inputs don't load it.
- Keep the two buffer domains separate: ito's 5 V never meets the ESP32 3V3 (only GND is shared).
- **Layout lesson carried over:** grep the generated `.kicad_pcb` for a bare
  `(remove_unused_layers)` before fab (kiutils bug that made the 06-015 JST pads unsolderable from
  the bottom; ✅ lab PR #73).

### 3.5 ito `ENC` interposer (F6)

- **Known (✅ ito manual p.63, `reference_ito_connector_pinout`):** `ENC` is **passive quadrature,
  no power pin**: `1 = GND, 2 = SW (A3), 3 = phase A (A2), 4 = phase B (A1)`. **The encoder shorts
  each line to GND.** Header = **Molex KK 254 (2.54 mm)** single row. ATMega1284 I/O = **5 V
  logic**.
- **Pass-through:** encoder plug → board KK 4-pin header → board KK 4-pin out → ito `ENC`. Same
  copper both ways.
- **Inject = open-drain only (the tri-state rule).** Each of A, B, SW gets an **open-drain
  pull-down** driven by an ESP32 GPIO: a small N-MOSFET or a 5 V-tolerant open-drain buffer
  (74LVC1G07 class).
  - When idle the output is **high-Z**, so it can't fight the real encoder or the ito pull-ups.
  - Injection only ever pulls low, exactly like a detent closing. That makes it wired-OR safe with
    the physical knob.
  - **Never drive high.** The high level comes from ito's own pull-up.
- **Read (optional, recommended):** sense A/B/SW through a 5 V→3.3 V divider or a 5 V-tolerant
  buffer, so ESPHome can see human turns and verify its own injected edges.
- **Detent state matters (⚠️ M7):** if this encoder rests with a phase **closed (low) at a detent**,
  injection on that phase is masked while the knob sits there. Measure the rest state.
- **Timing:** leva! samples the encoder in its ISR. The safe pulse width / edge rate is ⚠️ unknown;
  tune it in firmware on the bench with a logic analyzer (T7). No hardware dependency.

### 3.6 Shared I²C (F7)

- The ESP32 is the **only master** in rev A. Bring the bus to a **JST-SH 4-pin (Qwiic/STEMMA-QT)
  header at 3V3** for add-on sensors. The ADS1115 sits on the same bus.
- **ito `EXPANSION` (rev 2.0+): HW-I²C on pad 5 SDA / pad 4 SCK, pad 1 +5 V, pad 2 GND, pad 3 +3.3
  V, max 10 mA** (✅ manual p.59). ito masters it **only under future custom firmware**. Provide a
  **DNP PCA9306-class translator + solder jumpers** so it is isolated by default. No multi-master in
  rev A.

### 3.7 `SER` stub (F8)

- ARCH §4 and §10 say the touchpad is an **intelligent serial peripheral** on `SER2`→`SER1`, with an
  MCU at each end and an undocumented protocol. ⚠️ This **conflicts** with two other lab docs:
  - 06-016 / 06-017 (s1cafe corpus) describe a **16-pin parallel keypad/LED ribbon** with a front
    ON/OFF pin pair. The corpus may be the S1 Vivaldi II, not the Mini.
  - **M8 resolves which applies to this machine.**
- **Stub:** an unpopulated 0.1" header carrying one ESP32 UART pair (RX/TX) + 2 spare GPIO + 3V3 +
  GND. Each signal goes through **DNP series-R / divider / clamp footprints**, so rev B can bodge
  whatever levels the capture shows (06-016 notes the separate OEM timer bus runs on **> 12 V**, ⚠️
  unverified; don't assume `SER` is logic-level either).
- No `SER` connector is fitted in rev A. Nothing is inserted into the touchpad link.

### 3.8 On/off without `SER` (F9, optional)

06-017's recipe (short the front-panel ON/OFF pin pair ~3 s on, ~1 s off; s1cafe t261/t2671) gives
HA on/off **now**, if this machine's panel connector really has that pin pair (M8). Put **one DNP
opto-MOSFET (TLP222A class) dry contact** + a 2-pin header on the board, so it costs nothing to
populate later. If M8 shows the panel is pure serial, leave it empty.

## 4. Connectors: a reversible plug-in harness

Every machine-side tap is a **male/female pair** so the board drops in-line and comes out leaving
the machine stock (the 06-015 pattern).

| Channel     | Mates                           | Family                               | Status                                         |
| ----------- | ------------------------------- | ------------------------------------ | ---------------------------------------------- |
| Flow `F`    | GICAR plug ↔ control board `F` | **JST XH 4-pin**, pos 1 key-blank    | ✅ (06-015)                                    |
| ito IMPULSE | board → ito                     | **JST XH 3-pin**                     | ✅ (06-015 / `reference_ito_impulse_pinout`)   |
| ito `ENC`   | encoder plug ↔ ito `ENC`       | **Molex KK 254, 4-pin**              | ✅ family (manual); ⚠️ mate with George's plug |
| `S1` / `S2` | probe plug ↔ control board     | ⚠️ unknown                           | **M2**                                         |
| `SB` / `SL` | probe lead ↔ control board     | ⚠️ unknown (faston? header?)         | **M4 / M5**                                    |
| 5 V in      | off-board PSU → board           | choose (JST XH 2-pin or screw term.) | our choice                                     |
| I²C         | add-ons                         | JST-SH 4-pin (Qwiic)                 | our choice                                     |
| `SER` stub  | rev B                           | 0.1" header, DNP                     | our choice                                     |

**Interposer jumper cables:** where the board can't present the native plug back to the control
board (as `J2` does for flow), use short pigtails with the native housing on one end. Crimp families
on hand: George owns XH and other crimp tools (✅ `project_espresso_profiling`); confirm the tool
for any new family once M2/M4/M5 name it.

## 5. Firmware outline (ESPHome)

- `i2c:` → `ads1115:` → `sensor: platform: ads1115` (S1, S2 node voltage; PGA and rate set from M3).
- **Temperature:** template sensor = f(voltage) from a fitted curve (bench-derived; until then
  publish voltage + an `unverified` attribute). Missing or out-of-range data is published as
  **unavailable**, never 0 (`UI.md` rule).
- **Steam pressure:** template sensor from `S1` °C via a saturation table (water vapour, gauge = abs
  − 1.013 bar). Firmware only.
- **Flow:** `pulse_counter` on the 3V3 buffer output → `total` = volume. Calibrate the pulses/mL
  volumetrically (~2 pulses/mL is the documented starting point, ✅ wiring reference).
- **Levels:** `binary_sensor`s from the level comparator outputs (if populated).
- **ENC:** small external component (C++) that emits **N quadrature steps** at a tuned rate on A/B
  (open-drain) and an SW click/long-click. Exposed to HA as a `number` ("inject detents") +
  `button`s. Optional read-back of A/B/SW to log human turns and verify injected edges.
- **On/off (if F9 populated):** 06-017's `script` + `button` verbatim.
- OTA + native API; no USB in the machine.

## 6. Fab plan (JLC)

- **2-layer**, SMT on top only. JLC assembles the ESP32-S3 module, LDO, ADS1115, op-amp(s), LVC
  gates, MOSFETs/buffers, passives. **Hand-solder the THT connectors** (XH/KK/SH), or use JLC THT
  assembly if offered for those parts at order time.
- **Module choice:** ESP32-S3 (native USB for bench flashing, plenty of GPIO, hardware pulse
  counter). A C3 also works. Pick the **JLC-stocked variant at layout**; check stock the day of
  ordering.
- **Headless toolchain** (✅ `reference_kicad_headless_toolchain`): kiutils generate →
  `pcbnew.LoadBoard` zone fill → `kicad-cli` DRC / gerbers / drill / render in `kicad/kicad:9.0`
  (amd64). **Docker is currently down on this Mac.** Use Podman, or fix Docker, before layout day.
- Pre-fab checks: DRC 0 / unconnected 0; grep for bare `(remove_unused_layers)`; render top/bottom
  and eyeball; BoM/CPL LCSC numbers all in stock; Y-sign convention on CPL (as 06-015).
- **Order 5** (JLC minimum). Keep the 06-015 boards as the fallback flow path.

## 7. Test plan

| #   | Where           | Test                                                                                                                                      | Pass                                                         |
| --- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| T1  | Bare board      | Continuity: every pass-through pin in→out; no short `+14.3 V` to anything but `J2.2`                                                      | All pass                                                     |
| T2  | Bench, 5 V in   | Rails: 3V3 within spec; ESP32 boots, joins Wi-Fi, OTA works                                                                               | Clean                                                        |
| T3  | Bench, NTC emul | 500 kΩ multi-turn pots + a fixed bias standing in for the board; sweep; ADS1115 tracks the node voltage                                   | Monotonic, low noise                                         |
| T4  | Bench, loading  | Node voltage with the board's follower connected vs disconnected                                                                          | Δ below the board's ~1 °C deadband (set the number after M3) |
| T5  | Bench, level    | Probe in a beaker with the board's measured excitation (from M4): detect wet/dry; scope for **zero DC** on the probe line                 | Detects; no DC                                               |
| T6  | Bench, flow     | Pulse gen 0–100 Hz at 5 V OC → `J3.2` clean 0↔5 V **and** ESP32 counts match                                                             | Counts equal                                                 |
| T7  | Bench, ito      | ito bench-powered via `IMPULSE` pin 3 (✅ memory); LA on A/B/SW; inject N detents; leva! menu moves exactly N; knob still works alongside | Exact N, no fights                                           |
| T8  | Machine         | Install in-line; machine doses, autofills, heats, alarms exactly as stock; ito reads flow; HA shows temps / levels / flow                 | Stock behaviour preserved                                    |
| T9  | Machine         | Pull the board and re-mate the plugs                                                                                                      | Bone stock                                                   |

## 8. Relationship to existing projects

- **06-014 ESP32 button sidecar:** shares the goal (ESP32/ESPHome → HA control of the machine's
  native functions) but its **mechanism is superseded**. It assumes discrete buttons or a scanned
  matrix with an opto per button. ARCH §4 says the panel is a serial peripheral (`SER`), so the
  per-button opto plan likely doesn't apply to the Mini V2 (pending M8). Its temp/hot-water/standby
  goals move to **rev B (`SER` MITM)**; its "probe the panel" pre-flight becomes **M8**. If George
  files rev A under 06-014, rewrite its How-it-works/BoM around this plan and keep its HA exit
  criteria. If it becomes 06-020, mark 06-014 as superseded by 06-020 (status note + link) rather
  than deleting it.
- **06-015 flow tap:** absorbed as F5 (same circuit + connectors). The standalone boards stay valid
  as the fallback and for bench work.
- **06-016 board RE:** the supplier of open facts (NTC curve, `SER`/timer bus, panel map). Rev A
  doesn't need its spare-board bench to ship; rev B does.
- **06-017 on/off interposer:** absorbed as optional F9 (DNP), only if M8 confirms the pin pair.
- **06-001 ito + leva!:** unaffected; F5 and F6 tap ito's `IMPULSE` and `ENC` without changing its
  wiring.

## Open facts George must measure before layout

This is the critical path to "order this week". Each item: **what, where, how, and what it
unblocks.** Do them with the machine **unplugged** unless marked **(live)**. Live measurements: case
closed except the probe point, one hand, a CAT-rated meter.

| #   | Fact                                                                             | Where / how                                                                                                                                                                                                                                           | Unblocks                               |
| --- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| M1  | **Is the control board's low-voltage GND isolated from mains?**                  | **(live)** DMM AC-V and DC-V from control-board GND (GICAR pin 3 / black) to **PE** (chassis) and to **N**. Expect ≈ 0 V if isolated. Then, unplugged, check continuity GND↔N and GND↔`F` (expect open). Look for a mains transformer on the board. | **Everything** (shared GND, §3.1)      |
| M2  | `S1` / `S2` connector type + pin count at the control board                      | Photo both plugs head-on + side; calipers on pitch (as for the GICAR XH: gap + post width); note housing markings and latch style.                                                                                                                    | F1/F2 connectors                       |
| M3  | `S1` / `S2` node voltage range + bias                                            | **(live)** DMM DC-V across each NTC at the board connector: cold (machine just on), at temp, and steam boiler at temp. Unplugged: NTC resistance cold at ambient (record the °C). Note which pin is GND.                                              | ADS1115 PGA/range, buffer rails, T3/T4 |
| M4  | `SB` (boiler level) sensing method + excitation                                  | Find `SB` at the board; trace to the boiler. **(live)** scope (preferred) or DMM AC-V **and** DC-V probe-to-GND, boiler full vs low. Record waveform, frequency, amplitude, DC offset. Photo the probe and the connector.                             | F3 front-end, or DNP decision          |
| M5  | `SL` (tank level) method + connector                                             | Find the tank sensor (reed/float vs probe). Unplugged: continuity tank full vs empty. If it's a probe, measure like M4. Photo the connector.                                                                                                          | F4 front-end, or DNP decision          |
| M6  | ito `ENC` plug: confirm Molex KK 254 4-pin + pin order on George's encoder cable | Photo the encoder plug + ito header; calipers on pitch (expect 2.54 mm); continuity encoder pin → the ito silkscreen pin 1.                                                                                                                           | F6 connectors                          |
| M7  | Encoder rest state at a detent + ito pull-up level                               | Bench-power ito via `IMPULSE` (+5 V pin 3, GND pin 1). DMM each of A/B/SW → GND with the knob resting at a detent (try 3 detents), and while held pressed. Expect ~5 V released.                                                                      | F6 injection design (masking, T7)      |
| M8  | Front panel ⇄ board link: **serial `SER` vs 16-pin ribbon vs discrete pins**     | Open the panel side; count wires on the panel→board connector; photo the connector + both ends; read IC markings near it (the panel `M1`). Continuity: is there a pin pair that closes **only** while ON/STBY is held (06-017)?                       | F8 stub levels, F9 populate/omit       |
| M9  | GICAR `+` really ~14.3 V on this machine, and `o` pulled to 5 V                  | **(live)** DMM at the GICAR plug: `+`→`−`, and `o`→`−` with no flow. (Already documented; one-minute re-check, since F5 now feeds the ESP32 too.)                                                                                                     | F5 confirmation                        |
| M10 | Physical envelope                                                                | Where the board mounts; distance to each connector (cable lengths); max board size; any heat-shield needs (near boilers).                                                                                                                             | Board outline, cable BoM               |

**Can't-close-this-week rule:** M1, M2, M3, M6, M7 and M10 are **required** to order. M4, M5 and M8
are **optional for rev A**. Without them, `SB`/`SL`, `SER` and on/off ship as pass-through
connectors plus DNP footprints, and the board is still worth ordering.
