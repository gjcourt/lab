# Mini Vivaldi II: bench measurement guide

**Purpose.** This is one checklist for every measurement still open across the Mini Vivaldi II
projects (06-001, 06-012, 06-014, 06-015, 06-016, 06-017). It is sorted by risk: unplugged work
first, mains-hot work last. Every pin, value and claim below comes from the lab docs, with a
citation. Where the docs don't say, this guide says so instead of guessing. `06-014`'s ten
measurements, which gate the interposer PCB, are folded in as Tier 0 (Tests 28-37).

**Published copy.** The [published page](https://claude.ai/artifact/DiZmUDMpqG3V54nRDwrrH4) is an
earlier snapshot of this guide. If the two differ, this file is current.

**Machine.** LUCCA A53 Mini, which is Clive Coffee's rebadge of the **La Spaziale S1 Mini Vivaldi
II**. It has a vibratory pump and dual boilers, with an ito V2.0 running `leva!` interposed on the
pump (`AGENTS:18-20`, `e2:13-14`).

**Control board.**

- **In the machine:** the stock control board, called "Main Computer / CPU" (`06-012:113-115`). Its
  terminal strip is M5 (`wiring:23-36`). The heater triacs are on a separate triac sub-board
  (`06-012:116-117`, `wiring:178-179`).
- **No spare board.** George, 2026-11-07: he considered buying one but never did. `walk:52` said a
  spare was on the bench; that was wrong. Tests that need one are marked on hold.
- **Clive replacement part:** "La Spaziale S1 Main Computer", about $400. Clive describes it as "the
  updated control board that powers all S1 espresso machine models, including the A53 and Vivaldi
  variants" and "a universal main computer board". It says the board "requires configuration to
  match your specific machine's model and parameters" and "features La Spaziale Timer App
  functionality". Clive's support article says post-2022 A53 / Vivaldi II machines have an updated
  Universal S1 Main Computer "equipped with Bluetooth functionality". The same article also says
  "post-2021" elsewhere.
  - **No part number was obtainable.** The product page returns a Cloudflare 403 to every fetch
    method. These quotes come from search-result text and Clive's support article
    (support.clivecoffee.com/en/lucca-a53-mini-/-dp-/-vivaldi-cpu). See Open questions Q13.
  - 06-012 also names a "Universal Control Board SP-14139" at Espresso World (`06-012:115`). The
    docs don't say whether it is the same part.

**How to use this guide.**

1. Work down the tiers.
2. Fill in each **Result:** line as you go.
3. Send the filled-in file back. Results get folded into the project docs.

AGENTS.md is the source of truth for as-built state. When it disagrees with a 06-NNN doc, it wins
(`AGENTS:8-10`).

**Citation key.**

Citations read `name:line` or `name:line-line`. Line numbers match the commit that added this guide,
so check `git log` if one has drifted.

| Short name | File                                                                                                                                 |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `06-NNN`   | project file `06-NNN-*.md` in [`06-coffee-espresso/`](../projects.md)                                                                |
| `AGENTS`   | [`06-coffee-espresso/AGENTS.md`](../AGENTS.md)                                                                                       |
| `wiring`   | [`_reference/mini-v2-control-board-wiring.md`](mini-v2-control-board-wiring.md)                                                      |
| `e2`       | [`_reference/mini-v2-e2-group-solenoid-relay2.md`](mini-v2-e2-group-solenoid-relay2.md)                                              |
| `walk`     | [`_reference/ito-integration-walkthrough.md`](ito-integration-walkthrough.md)                                                        |
| `ito-sum`  | [`_reference/ito-manual-summary.md`](ito-manual-summary.md)                                                                          |
| `t56816`   | [`_reference/mini-vivaldi-thread-t56816.md`](mini-vivaldi-thread-t56816.md)                                                          |
| `fpcb`     | [`_reference/flow-tap-pcb/README.md`](flow-tap-pcb/README.md)                                                                        |
| `mods`     | [`_reference/mini-v2-modifications.md`](mini-v2-modifications.md)                                                                    |
| `plan`     | [`docs/plans/2026-10-27-unified-esp32-interposer-rev-a-plan.md`](../../docs/plans/2026-10-27-unified-esp32-interposer-rev-a-plan.md) |

**Test numbers.** Tests 1-37 are this guide's own. They are not the board's `M1`, `M5` and so on,
which are connector names. Tests 28-37 are `06-014`'s M1-M10 (`06-014:94-104`, `plan:300-309`).

---

## 1. Safety first

> **READ BEFORE OPENING THE MACHINE**
>
> - **`F`/PHASE is 120 VAC to ground whenever the machine is plugged in, even in Standby.** The
>   power pad is a soft-touch logic input, not a mains switch. There is no switched rail.
>   (`wiring:43-48`, `e2:29-31`)
> - **Unplug at the wall** before opening, wiring, or any UNPLUGGED step (`wiring:15-16`,
>   `06-017:23-24`).
> - **Let both boilers cool and depressurise** before opening (`wiring:16`, `e2:189`,
>   `walk:174-175`).
> - **Capacitor discharge: the docs give no discharge time or procedure** (`wiring:19-21`). Before
>   touching anything, check with the DMM that the point you'll touch reads 0 V. The docs don't
>   specify a wait.
> - **Mains-hot steps (Tier 4)** need all of these:
>   - an isolation transformer (fused) or a variac with isolated probes (`06-016:62-64`,
>     `06-012:99`);
>   - boilers disconnected, or dummy resistive loads in their place (`06-016:63`);
>   - for bench heater tests, a lamp or resistor as the load (`06-012:137`).
> - **Never bridge mains, heater or relay-board terminals.** The only thing you bridge is the two
>   ON/OFF pins on the low-voltage panel connector (`06-017:24-25`).
> - **Never wire an ito relay output to N.** Relays 1/2 output the L phase, and wiring one to N is a
>   destructive short. Relay 1/2 load limit is ≤240 W / 1 A. (`e2:191-192`, `ito-sum:648-649`)
> - **Keep GICAR `+` (about 14.3 V) away from every ito input.** ito inputs are rated 5 V + 0.5 V
>   absolute max. (`wiring:81`, `06-015:35-36`)
> - **Name clash: two different things are called `F`.**
>   - On M5, `F` is PHASE at 120 V (`wiring:34`).
>   - 06-016's connector list also labels the GICAR flow input "`F`" (`06-016:105-106`), and so does
>     `plan:215`.
>   - Never drive "the `F` pin" with a pulse generator unless you are sure it is the flow connector.
> - **Phantom voltage.** An unconnected tab near live wiring reads tens of volts (about 40 VAC
>   observed) on a high-impedance meter. Use the meter's LoZ mode or a load to confirm.
>   (`wiring:71-73`, `e2:195-197`)
> - **Keep the safety thermostat / thermal fuse in series.** Never bypass it (`06-012:72-73`).
> - **Leave steam on its original thermostat.** It is the overheat backstop (`06-012:42-43`).
> - **The klixons (TSB/TSC) are backstops, not interlocks.** Remote-ON heats the boilers with nobody
>   there. Confirm the water supply first, and have an auto-off automation and a leak sensor in
>   HASS. (`06-017:25-28`)
> - **Mains crimps need a ratcheting crimper, never pliers** (`06-001:389`).
> - **Pull FASTON plugs by the plug, not the lead** (`ito-sum:75`).
> - **Bench board DIP switches must match the target model.** All-off is a deliberate fault code
>   (`06-016:66-68`).
> - **Mains work is qualified-electrician territory per the docs** (`wiring:16-17`, `ito-sum:67`).

---

## 2. Equipment

| Item                                                                                                                      | Used in                  |
| ------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| DMM with continuity, diode test and ideally **LoZ** (`wiring:71-73`)                                                      | Tests 1-5, 11, 14-16, 22 |
| 4-ch scope, silent (`06-016:75`)                                                                                          | Tests 7, 9, 17-19, 24-26 |
| Logic analyzer, ≥16 ch, deep buffer (`06-016:77`, `06-016:192-195`)                                                       | Tests 7, 8, 20, 22       |
| Tigard (FT2232H), **UART sniff on SD/JP3 only, never on timer bus B** (`06-016:88-98`)                                    | Test 21                  |
| Clamp / current meter (`06-012:67-69`, `06-012:98`)                                                                       | Test 24                  |
| Isolation transformer (fused) or variac + isolated probes (`06-016:62`, `06-012:99`)                                      | Tests 23-27              |
| 2-ch current-limited linear bench PSU (`06-016:76`)                                                                       | Tests 10, 17-22          |
| Divider **15 kΩ (top) : 3.3 kΩ (bottom)**, about ×0.18, for 3.3 V logic; or 10 k : 3.3 k for 5 V logic (`06-016:150-152`) | Test 22                  |
| About 500 kΩ multi-turn pots ×2 (NTC emulation) (`06-016:79`, `06-016:120`)                                               | Test 18                  |
| Resistance decade box (alternative NTC emulation) (`06-012:98`, `06-012:134`)                                             | Test 26                  |
| Pulse source: pulse generator or ESP32 (`06-016:79`, `06-016:129-130`)                                                    | Tests 10, 19             |
| 16-pin IDC ribbon breakout (`06-016:79`)                                                                                  | Tests 8, 20              |
| JST XH pigtails: `XHP-4` / `XHP-3` + `SXH-001T-P0.6` (`06-015:58-61`)                                                     | Tests 10, 11             |
| Measuring jug + kitchen scale                                                                                             | Test 12                  |
| ESP32 + opto (PC817 / TLP222A) or Shelly Plus 1 (`06-017:52-58`)                                                          | Tests 2, 3               |
| Lamp / resistor dummy load (`06-012:137`)                                                                                 | Tests 25-27              |
| Thermocouple (`06-012:98`)                                                                                                | Test 24 (optional)       |
| Factory OEM timer or shot-counter module (two-sided capture) (`06-016:153-155`)                                           | Test 22 (optional)       |

---

## 3. Already measured (don't repeat)

| What                                                              | Value                                                                                                                                                    | Cite                                        |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| `F`/PHASE → GND                                                   | **120 VAC in Standby**; no switched rail                                                                                                                 | `wiring:43-48`, `e2:30`                     |
| M5 strip, top → bottom                                            | `A` EV.AL · `2` EV.H · PUMP (unmarked) · `1` EV.GR · `F` PHASE · N · N. Individual push-on plugs with ID markers.                                        | `wiring:28-36`, `06-001:281-286`            |
| PUMP identity                                                     | Unmarked plug, hot in both brew and autofill. **E1 done:** pump on ito Relay 1, pump-on lead on SNS, profiled shots pulled.                              | `wiring:66`, `AGENTS:32`, `e2:8-9`          |
| Earth                                                             | Separate ground stud, not on M5                                                                                                                          | `wiring:38`                                 |
| Phantom voltage                                                   | About 40 VAC on an unconnected tab, high-Z meter                                                                                                         | `wiring:71-73`                              |
| GICAR VCC                                                         | **+14.3 V** (see Q4: the docs disagree on who measured it and also cite 14.8 V)                                                                          | `06-001:310-312`, `wiring:81`               |
| GICAR signal                                                      | Open collector, **0↔5 V** (pulled up to 5 V inside the Vivaldi)                                                                                          | `06-001:311-312`, `wiring:83`               |
| GICAR connector                                                   | **JST XH 2.5 mm, 4-pin**: 1 key/blank, 2 +14.3 V (red), 3 GND (black), 4 signal (white). Pins are 2.0 mm apart, which gives 2.5 mm pitch with the posts. | `06-015:42-56`, `fpcb:18-25`                |
| ito IMPULSE connector                                             | **JST XH 3-pin**: 1 GND, 2 signal, 3 +5 V (silk `# / ⊤ / +`)                                                                                             | `06-015:51-56`, `walk:82-83`                |
| GICAR resolution (coarse, not calibrated)                         | About 2 pulses/mL; 2 magnets → 2 pulses/rev                                                                                                              | `wiring:92`, `06-016:129-132`               |
| Stock NTC (forum figure, **not this machine**, see Test 5 and Q6) | About **200 kΩ** NTC, **165k–228k at room temp** ("PT1000" label is folklore)                                                                            | `06-016:121-122`                            |
| Faston size                                                       | **6.3 × 0.8 mm** (board blades and pump tabs)                                                                                                            | `06-001:287-288`, `06-001:388`              |
| Pressure-sensor port                                              | **1/8" BSP** (former pre-infusion chamber port); kit G1/8 fitting threads in; sensor installed                                                           | `06-001:178`, `06-001:302-303`, `AGENTS:31` |
| Machine fuse                                                      | 5 A (behind the PUMP output)                                                                                                                             | `06-011:371`, `wiring:174`                  |
| Current board revision                                            | Clive's product photo shows ING3 v.05.02. Whether your installed board is this revision is open (Q25)                                                    | George's photo                              |

---

## 4. Session plan

IDs are stable labels, not run order; follow the tier order.

State tags:

- **UNPLUGGED**: at the wall, boilers cool.
- **POWERED**: plugged in, panels off; probe low-voltage only, never mains.
- **BENCH**: parts on the desk, no mains. Tests that need a spare board are on hold: George doesn't
  own one.
- **MAINS-HOT**: mains present at the probe point. Defer this tier.

> **Gate:** 06-016 says not to start bench RE until 06-001 has shipped (`06-016:17-22`), and 06-001
> is still In Progress. Tier 3 items marked 06-016 are formally gated. Do them only if George lifts
> the gate.

### Tier 0: Interposer gate (from 06-014; do these first)

These are `06-014`'s M1-M10, from the plan's "Open facts" table (`plan:292-313`). Tests 28, 29, 30,
33, 34 and 37 are **required before ordering the PCB**. Tests 31, 32 and 35 are optional for rev A:
without them, those functions ship as pass-through connectors and unpopulated footprints.

Live checks, per the plan: case closed except the probe point, one hand, a CAT-rated meter.

**Test 28 · 06-014 M1 · Is the control board's low-voltage GND isolated from mains? (gates
everything)**

- **Where:** control-board GND at GICAR pin 3 (black), to chassis (PE), to N and to `F`
  (`plan:300`).
- **Instrument / state:** DMM. UNPLUGGED, then POWERED. On the live step one probe touches N, a
  mains conductor.
- **Steps:**
  1. Unplugged: check continuity GND to N, and GND to M5 `F`. Expect open. The plan lists this
     second; do it first, and stop if either reads closed.
  2. Live: DMM AC-V and DC-V from GND to PE, and from GND to N. Expect about 0 V if isolated.
  3. Look for the mains supply on the board. Clive's v.05.02 photo shows a sealed module, `PS1`
     (input 100-240 V, output 5 V 1000 mA, 5 W). Its isolation rating isn't on the visible label.
- **Unblocks:** everything: the board's shared GND (`plan:94`).
- **Result:**

**Test 29 · 06-014 M2 · `S1` / `S2` connector type and pin count**

- **Where:** the plugs at the control board (`plan:301`).
- **Instrument / state:** camera and calipers. UNPLUGGED.
- **Steps:** photograph both plugs head-on and from the side; measure the pitch with calipers, as
  for the GICAR XH (gap + post width); note housing markings and latch style. Record which header
  each plug is on (Q22).
- **Unblocks:** the F1/F2 connectors.
- **Result:**

**Test 30 · 06-014 M3 · `S1` / `S2` node voltage range and bias**

- **Where:** across each NTC at the board connector (`plan:302`).
- **Instrument / state:** DMM DC-V, POWERED; then DMM Ω, UNPLUGGED.
- **Steps:**
  1. Live: measure cold (machine just on), at temperature, and steam boiler at temperature.
  2. Unplugged: NTC resistance cold at ambient; record the °C. Note which pin is GND.
- **Also closes:** Test 5 (cold resistance).
- **Unblocks:** ADS1115 range, buffer rails, T3/T4.
- **Result:**

**Test 31 · 06-014 M4 (optional) · `SB` boiler-level sensing method and excitation**

- **Where:** find `SB` at the board and trace it to the boiler (`plan:303`).
- **Instrument / state:** scope preferred, or DMM AC-V and DC-V probe to GND. POWERED.
- **Steps:** measure with the boiler full and low. Record the waveform, frequency, amplitude and DC
  offset. Photograph the probe and connector.
- **Unblocks:** the F3 front end, or the decision to leave it unpopulated.
- **Result:**

**Test 32 · 06-014 M5 (optional) · `SL` tank-level method and connector**

- **Where:** the tank sensor (`plan:304`).
- **Instrument / state:** DMM continuity. UNPLUGGED.
- **Steps:** identify it (reed/float or probe). Check continuity tank full and empty. If it's a
  probe, measure it as in Test 31. Photograph the connector.
- **Unblocks:** the F4 front end, or the decision to leave it unpopulated.
- **Result:**

**Test 33 · 06-014 M6 · ito `ENC` plug: Molex KK 254 4-pin and pin order**

- **Where:** your encoder cable and the ito header (`plan:305`).
- **Instrument / state:** camera, calipers, DMM continuity. UNPLUGGED.
- **Steps:** photograph the plug and header; measure the pitch (expect 2.54 mm); buzz the encoder
  pin through to the ito silkscreen pin 1.
- **Unblocks:** the F6 connectors.
- **Result:**

**Test 34 · 06-014 M7 · Encoder rest state at a detent, and ito pull-up level**

- **Where:** A, B and SW on the encoder (`plan:306`).
- **Instrument / state:** DMM. BENCH, with the ito powered through `IMPULSE` (+5 V pin 3, GND pin
  1).
- **Steps:** measure each of A/B/SW to GND with the knob resting at a detent (try 3 detents), and
  while held pressed. Expect about 5 V released.
- **Unblocks:** the F6 injection design.
- **Result:**

**Test 35 · 06-014 M8 (optional) · Panel to board link: serial, 16-pin ribbon or discrete**

- **Where:** the panel-to-board connector (`plan:307`).
- **Instrument / state:** eyes and DMM continuity. UNPLUGGED.
- **Steps:** open the panel side; count the wires; photograph the connector and both ends; read the
  IC markings near it. Then do Test 1. Test 7 gives the full answer if you want it.
- **Unblocks:** F8 stub levels, and whether F9 (on/off) gets populated.
- **Result:**

**Test 36 · 06-014 M9 · GICAR `+` about 14.3 V, and `o` pulled to 5 V (re-check)**

- **Where:** the GICAR plug (`plan:308`).
- **Instrument / state:** DMM. POWERED.
- **Steps:** measure `+` to `-`, and `o` to `-` with no flow. A one-minute check, since F5 now feeds
  the ESP32 too. Also settles which rail figure is yours (Q4).
- **Result:**

**Test 37 · 06-014 M10 · Physical envelope**

- **Where:** inside the machine (`plan:309`).
- **Instrument / state:** tape measure. UNPLUGGED.
- **Steps:** decide where the board mounts; measure the distance to each connector (cable lengths)
  and the largest board size that fits; note any heat-shield needs near the boilers.
- **Unblocks:** the board outline and cable list.
- **Result:**

### Tier 1: Unplugged, DMM

**Test 1 · 06-017 · Find the two ON/OFF button pins by continuity**

> Forum map t2629 gives On/Off as **ribbon pins 1 (GND) and 11 (5V)**, the same line as the forum's
> "panel pin 6". This test confirms it on your machine, and also closes the on/off part of Test 35.

- **Where:** the low-voltage front-panel connector. The forum calls them "pin 1 (GND)" and "pin 6
  (ON/OFF)", but its "pin 6" is numbered off the panel picture and may be **connector pin 11**
  (`06-017:32-41`).
- **Instrument / state:** DMM continuity, UNPLUGGED.
- **Steps:**
  1. Unplug the machine and open it.
  2. Put the DMM on continuity across candidate pin pairs on the panel connector.
  3. Find the pair that beeps **only while the physical ON/OFF button is held**.
  4. Release the button and confirm the beep stops.
  5. Photograph the connector and record the physical pin positions, counted from a marked end.
- **Expected:** exactly one pair that closes only on the press (`06-017:39-41`, `06-017:163-165`).
- **Unblocks:** 06-017 wiring and exit criterion 2 (`06-017:175`).
- **Not in the docs:** if you plan to use a polarity-sensitive PC817, you also need to know which
  pin is GND. 06-017 assumes forum pin 1 = GND (`06-017:65-66`). With an opto-MOSFET (TLP222A), a
  reed relay or a Shelly, polarity doesn't matter (`06-017:72-75`).
- **Result:**

**Test 4 · 06-012 Phase A · Locate the safety thermostat / thermal fuse and trace the element
leads**

> The owner's manual schematic (§6.1) shows each element with one side on NEUTRAL and the other
> through its safety thermostat to the triac outlet: RB → TSB → boiler triac, RC → TSC → group
> triac. This test confirms that on your machine.

- **Where:** brew-boiler element circuit. The docs say one lead goes to L, often through a safety
  stat, and the other goes to the triac output (`06-012:67-68`).
- **Instrument / state:** eyes + DMM continuity, UNPLUGGED.
- **Steps:**
  1. With the machine unplugged, follow both element leads.
  2. Note which lead goes to the safety stat or klixon (TSB/TSC per `06-017:27`) and which goes to
     the triac sub-board.
  3. Photograph both.
- **Why:** this tells you which leg is "the leg you cut" and which stat must stay in series
  (`06-012:68-73`).
- **Result:**

**Test 5 · 06-012 Phase A · Confirm the sensor type on this machine (cold resistance)**

- **Where:** boiler probe leads S1/S2 (`06-016:105-107`).
- **Instrument / state:** DMM Ω, UNPLUGGED, cold.
- **Steps:**
  1. Disconnect one probe from the board.
  2. Measure its resistance cold.
  3. Repeat for the other probe.
- **Expected:** NTC about 200 kΩ (165k–228k) per `06-016:121-122`. 06-012's generic rule of thumb is
  "NTC ≈ tens of kΩ, Pt100 ≈ 100 Ω, thermostat = continuity" (`06-012:64-65`).
- **Why:** the 165k–228k figure isn't from this machine, as far as the docs say (Q6). Test 30 also
  wants this reading (`plan:302`).
- **Result:**

**Test 6 · 06-001 · Read the pressure-sensor PSI rating**

- **Where:** the kit "keep this document" card (offline) and the sensor body.
- **Instrument / state:** eyes, any state.
- **Steps:** read which of 200 / 215 / 300 PSI is checked on the card (`06-001:210`), and any rating
  printed on the sensor.
- **Why:** sets pressure scaling in leva!. All three options cover 9 bar ≈ 130 psi (`06-001:210`,
  `walk:279-280`). The ito manual lists only 0–200 psi and 0–300 psi (`ito-sum:92-93`).
- **Result:**

### Tier 2: Powered, low-voltage (scope/LA, no mains probing)

> The board makes its low-voltage rails from an onboard transformer (`06-016:54`), and 06-017 calls
> the button lines low-voltage logic that is safe to interpose (`06-017:22-23`).
>
> - Whether the logic ground is isolated from mains is still open. It is Test 28, which that project
>   marks as gating everything (`06-014:94`, `plan:300`).
> - Before clipping a scope ground lead to the board, confirm with the DMM (AC and DC) that the
>   board GND reads about 0 V to earth. Otherwise use a differential or isolated probe.
> - Stay off M5 and the triac board.

**Test 7 · 06-014 · Panel link: discrete inputs, scanned matrix, or serial?**

- **Where:** the connector between the button panel and the CPU, which 06-016 and 06-017 describe as
  a 16-pin keypad ribbon (`06-016:138`, `06-017:194-197`).
- **Instrument / state:** DMM first, then LA on all lines (or the scope on a few), POWERED,
  Standby/ON.
- **Steps:**
  1. Count the wires and photograph the connector and both ends (`plan:307`).
  2. Check line levels with the DMM before clipping anything on. Don't assume a serial link is
     logic-level (`plan:196-198`).
  3. Clip the LA through a breakout.
  4. Capture idle.
  5. Capture while pressing each button in turn.
  6. Look for lines strobing periodically (rows/columns), static levels that change only when
     pressed, or a serial stream.
- **Expected:** unconfirmed, and the docs conflict.
  - Forum record t2629 says it is a scanned matrix with PWM / ground-multiplexed LEDs
    (`06-016:138-140`, `06-017:59`).
  - The architecture reference behind 06-014 says the panel is an intelligent serial peripheral on
    `SER2`→`SER1`, not a matrix (`06-014:73-75`, `plan:190-194`). The plan notes that the forum
    corpus may be the S1 Vivaldi II, not the Mini (`plan:193`).
- **Unblocks:** which description applies to this machine. This is the same question as `06-014`'s
  Test 8 (`plan:307`), and it decides 06-017's per-button upgrade (`06-017:194-197`).
- **Result:**

**Test 8 · 06-017 v1.1 (optional) · On/STBY LED waveform and duty cycle**

- **Where:** the On/STBY LED, or its ribbon line (`06-017:59`, `06-017:187-192`). Confirm which LED
  it is against the panel and manual. The "D"/"Econ" labels are not in the verified map
  (`06-017:59`).
- **Instrument / state:** scope or LA, POWERED. Capture once in Standby and once in ON.
- **Steps:**
  1. Probe the LED line.
  2. Record the PWM frequency and duty cycle when ON.
  3. Record the blink rate in Standby.
- **Expected:** solid when ON, flashing in Standby, with PWM/multiplexing on top, so a static level
  won't work (`06-017:137-138`, `06-017:189-192`).
- **Unblocks:** sizing the `pulse_counter` / duty-cycle sensor for a true HASS switch
  (`06-017:190-192`).
- **Result:**

**Test 9 · 06-012 Phase A · Scope the boiler sensor input while heating**

- **Where:** S1/S2 sensor input at the board (`06-012:65-66`).
- **Instrument / state:** scope, POWERED, heating from cold.
- **Steps:**
  1. Do the ground check above first.
  2. Probe the sensor node.
  3. Log voltage against time from cold to ready.
- **Expected:** not documented.
- **Result:**

**Test 11 · 06-015 · Install check (after Test 10 passes)**

- **Where:**
  - meter → `J1`;
  - `J2` → the Vivaldi flow socket;
  - `J3` → ito IMPULSE (`06-015:93-98`).
- **Instrument / state:** functional checks, POWERED. Plug the board in UNPLUGGED, then power up.
- **Steps:**
  1. Pull a volumetric shot and confirm it stops normally.
  2. Trigger a boiler autofill and confirm it refills.
  3. Confirm leva!/Vibrato shows live flow.
  4. Pull the board, re-plug the meter, and confirm stock behaviour returns.
- **Expected:** all four pass (`06-015:108-111`).
- **Note:** the kit Digmesa may be the interim meter (`AGENTS:33`). The flow K-factor must be re-set
  after the swap (`06-001:364-367`, `AGENTS:94-95`).
- **Result:**

**Test 12 · 06-001 · GICAR K-factor (pulses per litre)**

- **Where:** buffered pulse at `J3` pin 2 (OUT), or ito IMPULSE pin 2.
- **Instrument / state:** LA/scope pulse counter (or leva!'s count, if it reports one; the docs
  don't say it does), jug + scale. POWERED.
- **Steps:**
  1. Start counting.
  2. Dispense a known volume through the group into a jug on the scale.
  3. Stop counting.
  4. Compute pulses ÷ litres.
  5. Repeat 3 times.
- **Expected:** about 2 pulses/mL, roughly 2000/L, is the coarse figure (`wiring:92`). The real
  value "isn't published like the Digmesa's" (`06-001:209`).
- **Unblocks:** the leva! flow K-factor after the GICAR swap (`06-001:364-367`, `AGENTS:94-95`).
- **Not in the docs:** whether the hot-water / autofill path biases the count, and where along the
  water path the meter sits. Brew only, with the OPV not cracking (`06-001:127-130`).
- **Result:**

**Test 13 · 06-001 E2 · Bench checks after moving EV.GR to Relay 2**

- **Where:**
  - the solenoid hot lead moves from M5 EV.GR (`1`) to ito clamp `2`;
  - the neutral stays on an M5 N tab;
  - the freed `1` tab gets capped (`e2:87-101`).
- **Instrument / state:** functional checks, POWERED. The rewiring itself is done UNPLUGGED.
- **Steps (run all six):**
  1. App-brew (`MCcDOSE`) pulls a real shot.
  2. The Vibrato Start/Stop toggle works, and the group vents on Stop.
  3. The physical button still fires pump **and** valve. This is the load-bearing unknown: does the
     valve follow the pump?
  4. A physical shot still stops at the programmed volume.
  5. The unloaded stock EV.GR output causes no stock-board fault.
  6. The 3-way seals and vents cleanly with no leaks (`e2:205-219`).
- **Also watch:** Relay 2 chatter or SSR heat. Add an RC snubber or MOV if so (`e2:111-113`).
  Confirm step 3 **before** capping the stock tab (`e2:131-137`).
- **Unblocks:** app-brew, and possibly the pre-infusion skip bug (`AGENTS:72-75`).
- **Result:**

**Test 14 · 06-017 · Installed hold-length tuning**

- **Where:** opto across the Test 1 pins, ESP32 on its own USB supply (`06-017:166`).
- **Instrument / state:** functional, POWERED.
- **Steps:**
  1. Fire the HASS button and confirm the machine boots (On/STBY goes solid).
  2. If nothing happens, try up to 3.5 s.
  3. Test a ~1 s OFF press.
  4. Confirm neither press drifts into config mode (a hold of ≥3 s can trigger it). If it does, add
     the double 1 s state-reset pulse. (`06-017:43-48`, `06-017:167-169`, `06-017:178-179`)
- **Result:**

### Tier 3: Bench, parts only (no mains)

> **On hold without a spare board: Tests 15-22 and 26.** George doesn't own one (Clive sells it,
> about $400). 06-016 says not to do this work on the machine you drink from. Tests 2, 3 and 10 only
> need parts on the desk, so they can still go ahead.

**Test 2 · 06-017 · Prove the opto/relay pulse off-machine**

- **Where:** the opto output, with the ESP32 flashed with `a53-power.yaml` (`06-017:82-156`).
- **Instrument / state:** DMM continuity (or an LED) across the output, BENCH.
- **Steps:**
  1. Press the HASS button.
  2. Time how long the contact stays closed.
  3. Confirm it is open the rest of the time.
- **Expected:** closed for the script delay, 3.2 s by default (`06-017:116`), and open otherwise
  (`06-017:160-162`, `06-017:173-174`).
- **Result:**

**Test 3 · 06-017 · (if PC817) confirm output polarity matches Test 1**

- **Not in the docs.** Skip with a TLP222A, reed relay or Shelly (`06-017:72-75`).
- **Result:**

**Test 10 · 06-015 · Interposer bench checks**

- **Where:** `J1` / `J2` (4-pin) and `J3` (3-pin).
- **Instrument / state:** DMM, 5 V supply on `J3.3`/`J3.1`, pulse source, scope. BENCH.
- **Steps:**
  1. Continuity `J1.n` ↔ `J2.n` for pins 2, 3 and 4. Pin 1 is the blank.
  2. **No continuity** between the +14.3 V net (`J1.2`/`J2.2`) and any `J3` pin.
  3. Power `J3.3` = +5 V and `J3.1` = GND.
  4. Inject a 0↔5 V pulse on `J1.4` (signal) referenced to `J1.3`.
  5. Scope `J3.2`.
- **Expected:** a clean 0↔5 V copy at `J3.2`, **non-inverted**. U1 is a 74LVC1G17 (`06-015:81`,
  `fpcb:34`). (`06-015:105-107`, `walk:165`)
- **Result:**

**Test 15 · 06-016 Stage 1 · Static map of the spare board (unpowered)**

- **Where:** a spare board, if you buy one (on hold).
- **Instrument / state:** camera, DMM continuity/diode. BENCH, unpowered.
- **Steps:**
  1. Take high-res photos of both sides.
  2. Label these connectors: 16-pin keypad ribbon, S1/S2 NTC, GICAR flow ("`F`" in 06-016, see the
     safety note), EV solenoids, T1/T2 heat, OEM timer connector **(B)**, external-display header
     **(SD/JP3)**.
  3. **Read the MCU part number off the chip.**
  4. Find: GND plane; regulator → 5 V rail; PIC VDD/VSS; any secondary control rail.
  5. Buzz the keypad ribbon to MCU GPIOs and compare against the t2629 map.
  6. Locate the ICSP pins (typically MCLR/VPP · VDD · VSS · PGD · PGC) and any 8-pin EEPROM near the
     MCU.
  7. Record the DIP switch positions. (`06-016:104-114`, `06-016:91-92`, `06-016:66-68`)
- **Unblocks:** PICkit vs Tigard for firmware, rail injection points, and the keypad map
  (`06-016:108-109`).
- **Result:**

**Test 16 · 06-016 · Regulator and rail voltages**

- **Where:** regulator output (the "PIC's ~5 V VDD rail") and the secondary DC control rail
  (`06-016:56-59`).
- **Instrument / state:** first read the regulator part number and its datasheet output. Measuring
  live voltages needs the board powered from mains, which makes it **Tier 4** (or measure on the
  installed machine POWERED, on the low-voltage side only).
- **Expected:**
  - About 5 V for VDD.
  - The secondary rail value is **unverified**: "low-tens-of-volts is plausible … treat any specific
    figure as unverified" (`06-016:58-60`). The board does feed GICAR `+` at about 14.3 V
    (`wiring:81`). Whether that is the same rail is undocumented.
  - The timer bus runs on ">12 V" rails (`06-016:94-95`).
- **Unblocks:** the PSU settings for Test 17.
- **Result:**

**Test 17 · 06-016 Stage 2 · Injection power-up**

- **Where:** inject 5 V (and the secondary rail, once known from Test 16) from the current-limited
  PSU (`06-016:56-61`).
- **Instrument / state:** PSU, scope. BENCH.
- **Steps:**
  1. Set DIP switches for the Mini V2.
  2. Start with a low current limit.
  3. Inject the rails.
  4. Scope the MCU oscillator.
  5. Watch the power-up LED blink.
- **Expected:** the oscillator runs, and the LED blink shows V1 vs V2 mode (`06-016:118-119`, t963).
  DIP all-off gives a fault code, which is a useful liveness check (`06-016:66-67`).
- **Result:**

**Test 18 · 06-016 Stage 2 · NTC sweep (R → T curve)**

- **Where:** a ~500 kΩ multi-turn pot on each of S1/S2 in place of the probes (`06-016:120`).
- **Instrument / state:** pots, DMM, scope on the heater-control output. BENCH.
- **Steps:**
  1. Sweep resistance.
  2. Log resistance against the displayed temperature step.
  3. Note where the heater-control output toggles.
- **Expected:** toggling at about a 1 °C deadband (bang-bang) (`06-016:122-124`).
- **Result:**

**Test 19 · 06-016 Stage 2 · Flow-pulse ↔ dose mapping**

- **Where:** the GICAR flow input (**not** M5 `F`). Drive it from the pulse source at the GICAR rate
  (`06-016:129-134`).
- **Instrument / state:** pulse source, LA/counter. BENCH.
- **Steps:**
  1. Press a dose button.
  2. Count pulses delivered until the cut-off.
  3. Repeat for each dose button.
- **Expected:** nobody has counted these externally yet (`06-016:133-134`).
- **Result:**

**Test 20 · 06-016 Stage 3 · Keypad ribbon logic-analyzer capture**

- **Where:** all 16 ribbon lines (`06-016:138-141`).
- **Instrument / state:** ≥16-ch LA. BENCH.
- **Steps:**
  1. Capture idle.
  2. Capture each button press.
  3. Capture the LED-multiplex/PWM pattern.
- **Output:** timing to simulate presses and read LED state. Feeds 06-014 and Test 7.
- **Result:**

**Test 21 · 06-016 Stage 3 · External-display header SD/JP3 via Tigard UART**

> On hold without a spare board. The owner's manual (§6.5) calls `DISPLAY` the "cable connector for
> optional timer module", `JP3` the "optional timer switch connector" and `SD` the "optional timer
> on/off switch". So the data header may be `DISPLAY`, not SD/JP3 (Q21).

- **Where:** SD/JP3 (`06-016:88-90`, `06-016:146-148`).
- **Instrument / state:** scope first, then Tigard RX + GND only (leave TX open). BENCH.
- **Steps:**
  1. Measure Vtarget.
  2. Scope one bit width to get the baud rate.
  3. Set the Tigard to that level and baud.
  4. Capture during power-up and operation.
- **Expected:** possibly temperature and state in the clear. Unconfirmed.
- **Result:**

**Test 22 · 06-016 Stage 3 · OEM timer bus (B) waveform**

- **Where:** timer connector (B).
- **Instrument / state:** scope or LA **through the 15 k : 3.3 k divider**. Check it against the
  LA's max input. **Not the Tigard:** the bus is not UART and the Tigard's inputs are at risk.
  BENCH. (`06-016:94-98`, `06-016:149-155`)
- **Steps:**
  1. Capture at power-up.
  2. Capture during operation.
  3. Optional: plug in a factory timer for a two-sided capture.
- **Expected:** a custom line code. The ~4-bits-per-symbol guess is **unverified and conflicting**
  (`06-016:94-97`).
- **Result:**

**Test 23 · 06-001 · Pump output: relay or semiconductor?**

> Likely answered. The manual schematic (§6.1) draws a mechanical relay contact on the PUMP output,
> and Clive's photo of the v.05.02 board shows five NT10-A-S-5 relays beside M5. Which relay drives
> PUMP isn't marked. Check your own board by eye; no spare is needed.

- **Where:** the component that drives M5 PUMP on your board (`06-001:248-256`).
- **Instrument / state:** visual. BENCH. The method is not in the docs.
- **Steps:** identify a mechanical relay versus a triac/SSR on the PUMP output path.
- **Why:** ito SNS is an opto input. A semiconductor switch might not sink enough current. SNS draws
  typically 0.5–2.5 mA (`ito-sum:562`).
- **Note:** in practice E1 works with SNS live (`AGENTS:32`), so this is a record-keeping check.
- **Result:**

### Tier 4: Mains-hot (defer; needs isolation transformer or variac + isolated probes)

**Test 24 · 06-012 Phase A · Heater-switch leg + safety stat in circuit**

- **Instrument / state:** clamp meter, live machine heating. MAINS-HOT.
- **Steps:** clamp each element lead (from Test 4) while the boiler heats, and record which one
  carries the switched current (`06-012:67-69`).
- **Result:**

**Test 25 · 06-012 Phase A · Triac gate drive ("heat command")**

- **Where:** CPU → triac gate.
- **Instrument / state:** scope with isolated / differential probes. MAINS-HOT.
- **Steps:** capture the drive and classify it as on/off, zero-cross burst or phase-angle; record
  the logic level (`06-012:70-71`).
- **Bench alternative:** isolation transformer, boilers disconnected or dummy loads
  (`06-016:62-64`).
- **Result:**

**Test 26 · 06-012 Phase B · Spare-board fault behaviour**

- **Where:** a spare board on a bench rig, if you buy one (on hold): decade box for the probe, a
  jumper for "water present", momentary switches for buttons, a lamp/resistor as the heater load
  (`06-012:131-137`).
- **Instrument / state:** scope/DMM. BENCH with mains through the isolation transformer. MAINS-HOT.
- **Steps:**
  1. **Current-sense check:** open the triac output while heating and watch for an instant error.
  2. **Watchdog:** element disconnected and probe cold, then time any fault; repeat with the probe
     spoofed at temperature.
  3. **Plausibility:** probe open, shorted and out of range, then record the fault thresholds.
     (`06-012:77-85`)
- **Go/no-go:** see `06-012:101-104`.
- **Result:**

**Test 27 · 06-001 (likely superseded) · PUMP hot in brew AND autofill**

- **Where:** M5 PUMP tab → N tab (`wiring:57-67`).
- **Instrument / state:** DMM (LoZ). MAINS-HOT.
- **Note:** E1 is done and working (`AGENTS:32`). Re-run this only if the PUMP identity is ever in
  doubt.
- **Result:**

**Out of scope here:** 06-016 Stage 4 firmware dump/reflash. It carries brick risk, needs a PICkit,
and is spare-board only (`06-016:157-167`).

---

## 5. Open questions / unverified

- **Q1. Stale 06-001 checkboxes: fixed; some stale text remains.**
  - The "verify" box and the T-tap plan are now split and corrected (`06-001:487-495`).
  - Still stale, not changed: `06-001:176` (T-tap), `mods:71` (pressure tee), `walk:84-85` and
    `walk:263-265` (GICAR connector "pending"), `walk:277-278` (no pre-tapped port).
- **Q2. Buffer part: resolved.** 06-015 uses the **74LVC1G17** (non-inverting) (`06-015:81`), and
  `AGENTS:33`, 06-001 (`06-001:60`, `06-001:109`, `06-001:181`) and `mods:65` now match. CD4011B
  stays only as the record of blondica's build (`wiring:103`).
- **Q3. Connector family: left open.** ito-sum says all ito headers are **Molex KK 2.54 mm**
  (`ito-sum:531`, `ito-sum:623`). 06-015 says IMPULSE is metered as **JST XH 2.5 mm**
  (`06-015:42-45`). A note now says so (`ito-sum:536-540`). No doc records an XH plug mated with
  IMPULSE, and Test 11 is the first time it happens, so check that it actually mates before trusting
  `J3`.
- **Q4. GICAR rail, 14.3 V vs 14.8 V: left open.** Both figures appear (`06-001:319`,
  `t56816:26-37`). The t56816 digest attributes the 14.3 V figure to blondica's thread (#26), and
  `walk:84` says the meter wasn't on George's bench boards. Notes now say so (`wiring:85-90`,
  `06-001:320-323`). No M here measures it; Test 36 does (`plan:308`).
- **Q5. Pressure sensor thread.** ito-sum lists the sensor as 1/8" NPT (`ito-sum:93`). The port is
  1/8" BSP, and the docs describe the "kit G1/8 fitting" threading in (`06-001:178`). It is
  installed and working, so this is documentation only.
- **Q6. NTC source: left open.** 06-016 doesn't say which unit gave "measured 165k–228k". The rev A
  plan treats it as forum t2330, not measured on this machine (`plan:100-101`). A note now says so
  (`06-016:125-128`). Test 5 settles it.
- **Q7. ON/OFF pin numbering: left open.** Forum "pin 6" may be connector pin 11 (`06-017:37-41`).
  The text still says "pins 1 & 6", with a note (`06-017:77-80`, `06-017:164-165`). Test 1 settles
  it. The plan also asks whether this panel has the pair at all (`plan:203-206`).
- **Q8. Matrix vs discrete vs serial: left open.** The matrix comes from forum t2629 and is marked
  unconfirmed (`06-016:141-145`, `06-017:195`). 06-014 and the plan say serial (`06-014:73-75`,
  `plan:190-194`). Test 7 and Test 35 settle it.
- **Q9. "`F`" naming collision: fixed in 06-016.** M5 `F` is PHASE at 120 V. 06-016 now spells out
  the flow input (`06-016:105-106`, `06-016:129-130`). `plan:215` still says "Flow `F`".
- **Q10. Interposer status: resolved.** `AGENTS:33` and `AGENTS:94` already say boards in hand, not
  fitted, and e2 says "PCBs shipped 2026-07-22" (`e2:237`). 06-015's order box and the walkthrough
  now match (`06-015:121-122`, `walk:73-74`). The docs don't record whether the KiCad GUI review
  happened.
- **Q11. "Cut the PUMP wire": fixed.** The wiring ref now says unplug (`wiring:165`), matching
  `06-001:284-290`. `06-011:361` still says "pump-wire cut".
- **Q12. 06-016 gate vs reality: George's call.** It is gated on 06-001 shipping (`06-016:17`), and
  needs a spare board, which George doesn't own. The gate is unchanged, and nothing in 06-016 can
  start without one (`06-016:24-26`).
- **Q13. Clive board vs the docs.**
  - Clive calls it "universal" across all S1 models, with model configuration required. That fits
    06-016's DIP switches (`06-016:66`).
  - Clive mentions a Bluetooth / "Timer App" generation from post-2022 (it also says post-2021). The
    docs record neither the machine's board generation nor whether v05.02 is pre- or post-Bluetooth.
  - No Clive part number could be retrieved, and the SP-14139 link is unconfirmed.
  - Price (about $400) matches `06-012:114`. "In stock" (`06-012:114`) is unverified; one search
    listing showed it sold out.
  - 06-016's warning about fake "WiFi control board" listings (`06-016:49-50`) is not contradicted:
    Clive's part is Bluetooth, not WiFi.
- **Q14. SNS voltage range.** ito-sum gives 32–240 VAC (`ito-sum:133`) and 48–240 VAC
  (`ito-sum:562`).
- **Q15. Secondary DC rail value** is unverified by the docs' own statement (`06-016:58-60`).
- **Q16. E2 open questions** (`e2:129-152`): does the valve follow the pump on a physical brew, is
  an unloaded EV.GR tolerated, and does volumetric dosing survive? All are untested.
- **Q17. Relay vs triac on the PUMP output** has never been recorded, though it works in practice
  (`06-001:248-256`, `AGENTS:32`). A note now points at Test 23.
- **Q18. Capacitor discharge.** No discharge procedure or time is documented anywhere.
  `wiring:19-21` now says so.
- **Q19. `06-014`'s list: resolved.** Folded in as Tier 0, Tests 28-37. Tests 35 and 36 overlap
  Tests 1, 7 and Q4.

- **Q20. Serial or parallel ribbon?** The hestia ARCHITECTURE.md and 06-014 call `SER1`-`SER2` a
  serial link to an "M1 MCU". The forum map (t2629) says parallel contacts. In the manual's figures
  and on the v.05.02 silkscreen, `M1` is the header's own name, not a chip, and it is a 16-pin 2x8
  box header. Tests 7 and 35 settle it; correct ARCHITECTURE.md after.
- **Q21. Which header is the timer's data line?** 06-016 says SD/JP3; the manual's definitions point
  to `DISPLAY` (see Test 21). The forum calls the timer plug 3-wire; the schematic numbers it 1
  to 4.
- **Q22. Which header carries which sensor?** Figure §6.2 shows S1 on its own 2-pin header and S2 +
  SB on another. Schematic §6.1 shows S2 on a 2-pin header and S1 + earth + SB on a 4-pin header.
  The v.05.02 silkscreen labels these headers `M2`, `M3`, `M10` and `M9`, with no function names.
  Trace the leads before unplugging anything.
- **Q23. Does the t2629 ribbon map apply to this model?** It was posted on an S1 thread. Test 1 and
  Test 7 confirm it on the Mini Vivaldi II.
- **Q24. Fuse rating.** The docs and manual say 5 A. Clive's v.05.02 photo has silkscreen "220Vac
  T5A / 110Vac T10A" beside `F3`. Read the fuse in your machine. Don't change it based on this.
- **Q25. Which board revision is in your machine?** Clive's photo is v.05.02: five relays, `M5` +
  `M4` tabs. The manual shows four relays and seven tabs on `M5`, which is what `wiring:24-32`
  records. A photo of your installed board settles it.

---

## 6. Results template

Copy one block per measurement:

```text
ID:            M__
Date / who:
Unit:          machine | interposer
State:         UNPLUGGED | POWERED | BENCH | MAINS-HOT
Instrument:    (model, range, probe/ground used)
Points:        (connector + pin, how you counted pins)
Reading(s):
Photo/capture: (filename)
Matches docs?  yes | no | n/a  (cite line if no)
Notes / next:
```
