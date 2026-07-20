---
title: 'A53 / Mini V2 Control-Board Reverse Engineering (bench board)'
number: '06-016'
category: 'coffee-espresso'
difficulty: 'Hard'
time_commitment: 'Weeks–months (staged)'
target_skills:
  'Logic Analysis, Protocol RE, ICSP / Firmware, Bench Bring-up, Tigard (UART/I2C/SPI/JTAG)'
status: 'Not Started'
depends_on:
  - 06-001-lucca-a53-mini-leva-firmware-integration
  - hardware/lucca-a53
---

# A53 / Mini V2 Control-Board Reverse Engineering (bench board)

> ⛔ **GATED on [06-001](06-001-lucca-a53-mini-leva-firmware-integration.md).** Do not start this
> project until the ito + `leva!` pressure/flow profiling on the daily machine is **proven and
> shipped**. This work needs a **spare control board on the bench** (never the machine you drink
> from), and several stages risk bricking that board. Finish the thing that makes coffee first; this
> is the "learn how the machine works fundamentally" follow-on, not a prerequisite for any shipping
> capability.

Reverse-engineer a **spare** La Spaziale S1 Mini Vivaldi II controller board on the bench to
document, at signal level: the front-panel button/LED matrix, the sensor front-ends, the boiler
control lines, the proprietary OEM-timer serial bus, and — if reachable — the MCU firmware. The
output is a wiring/protocol reference that feeds the sibling hardware projects
([06-010](06-010-grouphead-temperature-sensor.md),
[06-012](06-012-leva-pid-temperature-takeover.md),
[06-014](06-014-esp32-button-automation-sidecar.md), [06-015](06-015-gicar-flow-tap-interposer.md)).

Grounded in the [control-board wiring reference](_reference/mini-v2-control-board-wiring.md) (M5
strip, GICAR meter, "no switched mains rail"). This project extends it into the **digital** side the
reference doesn't yet cover: keypad matrix, PIC, timer bus, external-display header.

## Why a bench board (not the machine)

The community RE record (s1cafe) is deep on button/power/temperature and stalled at exactly two
walls: the OEM **serial bus** was scoped but never decoded (only one side ever captured — nobody had
a factory timer to see the handshake), and the controller **PIC** was never dumped ("my old PIC
debugger won't talk to the board"). Both walls are downstream of _not wanting to experiment
destructively on a daily-driver machine_. A spare board removes that constraint: free desoldering,
pin-lifting, reset-holding, and reflashing, permanently instrumented on the desk — no mains, no
boilers, no water, no teardown per iteration. **Source a used/broken board** (a dead power stage is
fine as long as the digital section is intact); do **not** buy the fake "WiFi control board"
listings — no such OEM part exists, and the too-good pricing is the bait.

## Power strategy (the safety fork — decide first)

The board makes its own low-voltage rails from an onboard transformer fed by mains. Two ways up:

- **Preferred — low-voltage injection, no mains on the desk.** Find the regulator output (the PIC's
  ~5 V VDD rail) and any **secondary DC control rail** the board uses to drive its heater-switching
  stage, and feed them from the **current-limited bench PSU**. (A rail in the low-tens-of-volts is
  plausible — **probe and confirm it on the bench; treat any specific figure as unverified**, not a
  documented value.) This powers the entire digital side — PIC, keypad, serial bus, flowmeter input
  — which is everything the RE needs. No mains, no boilers.
- **Only for triac-gate timing** — feed real mains through an **isolation transformer**, fused,
  boilers disconnected (or dummy resistive loads). The triac drive needs mains zero-cross sync;
  nothing else does. Skip unless heater switching is the specific target.

Set the board **DIP switches to match the target machine's model** (t2671; DIP-all-off = a
deliberate fault code, handy as a liveness check), and confirm it comes up in the right **V1/V2
mode** — that's the power-up LED blink (t963), not a DIP setting.

## Tooling

| Tool                                                      | Role here                                                                                                      | Have?              |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------ |
| **Tigard** (FT2232H, level-shifted UART/I2C/SPI/JTAG/SWD) | External-display **UART** sniff, onboard **EEPROM** dump, MCU debug UART, JTAG/SWD **iff** the MCU isn't a PIC | ✅                 |
| **4-ch scope** (silent)                                   | Raw capture of the timer-bus waveform + triac gate timing; bit-width measurement for autobaud                  | ✅                 |
| **2-ch linear PSU**                                       | Low-voltage rail injection (5 V digital + the secondary control rail), current-limited                         | ✅                 |
| **Logic analyzer, ≥16 ch, USB3, deep buffer**             | The 16-pin **keypad matrix** (parallel) + long streaming capture of the **timer bus** for software decode      | ⬜ see rec below   |
| **PICkit 4 / Snap + SOIC clip**                           | PIC **ICSP** dump/reflash — the Tigard does **not** speak Microchip ICSP                                       | ⬜ if MCU is a PIC |
| Bench harness                                             | ~500 kΩ multi-turn pots ×2 (NTC emul), pulse gen or ESP32 (flowmeter emul), 16-pin IDC ribbon breakout         | ⬜ build           |

**Logic-analyzer recommendation** → see the standalone note at the bottom of this doc. Short
version: **Saleae Logic Pro 16** (caliber match, best custom-decoder software) or **DSLogic
U3Pro16** (out-specs it on buffer/clock for ~⅕ the price, sigrok software). Either is 16-ch —
required for the parallel keypad ribbon.

**Tigard fit — where it wins and where it can't help:**

- ✅ **External-display header (SD / JP3):** if it carries standard **UART**, the Tigard reads it
  directly — and that stream likely contains **temperature + machine state**, a clean digital
  back-door that sidesteps the undecoded timer bus. Probe here **first**.
- ✅ **Onboard config EEPROM** (look for an 8-pin 24Cxx / 25-series near the MCU): dump via Tigard
  I2C (pyftdi) or SPI (flashrom). Likely holds offset/model/calibration.
- ✅ **MCU debug UART** on the PIC's TX pin, if firmware emits one at boot (version strings).
- ❌ **OEM timer bus (B):** **not** UART — a custom line code on **>12 V** rails (one forum member's
  _unverified_ guess was ~4 bits per symbol, e.g. `1001` start / `1000`=0 / `1010`=1, but they
  posted a conflicting reading and never confirmed it — treat as undecoded). Wiring the Tigard to it
  won't frame anything and risks the FT2232H inputs. Capture with the **scope or LA + a divider**
  (below), decode in software.
- ❌ **PIC firmware:** the Tigard does JTAG/SWD, not ICSP → **cannot program a PIC.** Only if Stage
  1 shows the MCU is an ARM/JTAG part does the Tigard become the dumper.

## Stage 1 — Static map (unpowered)

- High-res photos both sides. Label every connector against the known set: 16-pin keypad ribbon,
  S1/S2 NTC probes, `F` GICAR flow, EV solenoids, T1/T2 heat, the OEM **timer connector (B)**, the
  **external-display header (SD/JP3)**.
- **Read the MCU part number off the chip** — the linchpin. It fixes the ICSP pinout, memory map,
  and read-protect story, and decides **PICkit vs Tigard** for Stage 4. Pull the datasheet.
- DMM continuity/diode: find the GND plane, the regulator → 5 V rail, the PIC VDD/VSS, any secondary
  control rail, and **buzz the keypad ribbon to the PIC GPIOs** (confirm the t2629 map on _this_
  board).
- Locate the **ICSP pins** (a PIC header is typically
  `MCLR/VPP · VDD · VSS · PGD/ICSPDAT · PGC/ICSPCLK`, ± AUX) for the Stage 4 dump.

## Stage 2 — Power up + emulate the sensors

- Inject the 5 V rail; confirm the PIC boots — scope the oscillator, watch the **V1/V2 power-up LED
  blink** (t963) for liveness + correct mode.
- **NTC emulation:** a **~500 kΩ multi-turn pot** on each of S1/S2 in place of the probes (the stock
  sensor is a **~200 kΩ NTC, negative-coefficient** — measured 165k–228k Ω at room temp; the
  "PT1000" label is folklore, t2330). Sweep "temperature" and watch the heater-control output toggle
  at the ~1 °C deadband → the bang-bang loop, characterized live. **Log resistance vs. the displayed
  temp step** to recover the board's own R→T curve (the corpus has spot points, not a Beta).
- **Flowmeter emulation:** drive `F` with a pulse gen / ESP32 at the GICAR rate — the impeller has
  **2 magnets → 2 pulses/rev** (t704), which the wiring reference and
  [06-015](06-015-gicar-flow-tap-interposer.md) calibrate to **~2 pulses/mL** volumetrically. Press
  a dose button, watch the count + cut-off → dose↔pulse mapping. **Nobody in the corpus counted
  these externally.**

## Stage 3 — Instrument the buses

1. **Keypad ribbon (parallel scanned matrix).** LA all 16 lines; press each button; capture the
   scan + LED-multiplex pattern (incl. the PWM/ground-oscillation on the LED lines). Output: exact
   timing to _simulate_ any press **and** _read_ state (which LED = which temp/ready). Delivers
   [06-014](06-014-esp32-button-automation-sidecar.md). No factory timer needed.
2. **External-display header → Tigard UART.** Passive sniff (RX + GND only; leave TX open); set the
   Tigard level to the sensed Vtarget. Unknown baud → measure one bit's width on the scope first,
   then set the rate. If it's temp/state in the clear, this is the biggest win in the project.
3. **OEM timer bus (B) — the frontier.** Capture on power-up + operation with the **scope or LA +
   divider**. Example divider to bring ~15 V into 3.3 V-logic range: **15 kΩ (top) : 3.3 kΩ
   (bottom)** → ×0.18 → ~2.7 V (verify against the LA's max input; use ×0.25 with 10 k:3.3 k for 5 V
   logic). You will capture the board's outbound frames in the custom 4-bit-per-bit code (t2507).
   **To decode the _protocol_ (not just bits) you need both directions → plug a genuine factory
   timer (or shot-counter module) into B and capture the link between them.** That two-sided capture
   is the specific rig that breaks the wall the forum stalled at. Budget for one OEM timer.

## Stage 4 — Firmware (deepest, brick-risk — hence the spare)

- **If PIC:** clip the **PICkit 4 / Snap** to PGC/PGD/MCLR/VDD/VSS, try to read flash + EEPROM. The
  known blocker ("debugger won't talk to the board") is usually: MCLR fought by an onboard
  pull-up/cap → isolate MCLR; PGC/PGD loaded by other circuitry → lift those pins or socket the PIC;
  or the **code-protect fuse** is set → flash can't be _read_ (dump dead-ends), but you can still
  **erase + flash your own firmware** → onboard PID becomes possible
  ([06-012](06-012-leva-pid-temperature-takeover.md)). Reflash only after a dump attempt, only on
  the spare.
- **If not PIC** (ARM/JTAG/SWD): the **Tigard** is the dumper — OpenOCD over SWD/JTAG.
- If it reads: disassemble (Ghidra/IDA handle PIC) and map the temp/dose/state logic.

## Exit Criteria

- [ ] **Gate cleared:** 06-001 shipped before any bench work starts.
- [ ] Spare board sourced (digital section verified intact) + bench-powered on low-voltage
      injection.
- [ ] Stage 1: full connector/pinout map + MCU part number identified (PICkit-vs-Tigard decided).
- [ ] Stage 2: R→T curve logged from NTC sweep; dose↔flow-pulse mapping captured.
- [ ] Stage 3a: keypad matrix + LED-state map confirmed on this board (feeds 06-014).
- [ ] Stage 3b: external-display header characterized (UART? → what fields?).
- [ ] Stage 3c: timer-bus waveform captured; two-sided capture attempted with a factory timer.
- [ ] Stage 4: MCU dump attempted; result recorded (dumped / read-protected / reflash-only).
- [ ] Findings folded back into
      [`mini-v2-control-board-wiring.md`](_reference/mini-v2-control-board-wiring.md).

## Progress

- [ ] **Blocked on 06-001** — not started by design.
- [x] Methodology + tooling drafted (this doc); Tigard fit + LA recommendation resolved.
- [x] Community RE state-of-the-art surveyed (local s1cafe synthesis) → the two open frontiers
      (external flow-pulse counting, PIC dump/reflash) identified as the novel work.

## Logic-analyzer recommendation (standalone)

Requirements this project imposes: **≥16 channels** (the keypad ribbon is a 16-pin parallel matrix —
8-ch won't cover it), **deep capture / streaming** (long timer-bus and keypad-scan captures), decent
edge resolution (the buses are slow; 100+ MS/s is ample), and **good protocol + custom-decoder
support** (for the non-standard 4-bit-per-bit timer code).

| Analyzer                       | Ch  | Notable                                                                                                                                                                                      | Price (approx)     | Pick when…                                                                                       |
| ------------------------------ | --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------ |
| **Saleae Logic Pro 16**        | 16  | Best-in-class **Logic 2** software; analog+digital together; USB3 streaming = effectively unlimited depth; trivial **custom high-level analyzers** (Python) — ideal for the weird timer code | ~$1,350 (hobbyist) | You want the caliber-match, zero-friction, buy-nice-once tool that matches the rest of the bench |
| **DSLogic U3Pro16**            | 16  | **2 Gbit** onboard buffer, USB3, up to 1 GS/s (3 ch) / 125 MS/s (16 ch), **external clock + trigger in/out**; sigrok/PulseView + DSView                                                      | ~$299              | You want equal-or-better _hardware_ for ~⅕ the cost and don't mind less-polished software        |
| **Digilent Digital Discovery** | 16+ | LA **+ pattern generator + static I/O**, 800 MS/s, FPGA-based                                                                                                                                | ~$300–450          | You want the **flowmeter/keypad stimulus built in** — one box does capture _and_ emulation       |

- **Default: Saleae Logic Pro 16** — matches the "robust, similar-caliber" bar of a silent scope +
  linear PSU, and its custom-decoder path saves real time on the custom timer encoding.
- **Smart-money alternative: DSLogic U3Pro16** — out-specs the Saleae on buffer/clock; the trade is
  software polish. Genuinely robust; many pros prefer it.
- **If you want stimulus in the same box: Digilent Digital Discovery** — its pattern generator
  covers the Stage-2 flowmeter-pulse and keypad-drive emulation the others need a separate
  ESP32/pulse-gen for. (Note: its LA front-end is 3.3 V-centric; use the high-speed adapter /
  level-shift for 5 V lines.)

Prices drift — confirm at purchase.

## Sources

- [Mini V2 control-board wiring reference](_reference/mini-v2-control-board-wiring.md) — the analog
  / power side this project extends into the digital side.
- [06-001](06-001-lucca-a53-mini-leva-firmware-integration.md) — the gate + parent.
- Sibling consumers of the findings: [06-010](06-010-grouphead-temperature-sensor.md),
  [06-012](06-012-leva-pid-temperature-takeover.md),
  [06-014](06-014-esp32-button-automation-sidecar.md),
  [06-015](06-015-gicar-flow-tap-interposer.md).
- Community RE pointers (s1cafe thread numbers): t2629 (16-pin keypad/LED map), t261 (on/off + LED
  state-sense), t2507 (PIC MCU, PicoScope timer-bus capture, stalled decode), t2330 (NTC-vs-PT1000
  sensor type), t704 (GICAR internals). Full local synthesis kept off-repo.
