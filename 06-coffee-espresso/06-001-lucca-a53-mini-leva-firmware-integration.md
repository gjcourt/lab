---
title: 'Lucca A53 Mini Pressure & Flow Profiling via ito + `leva!`'
number: '06-001'
category: 'coffee-espresso'
difficulty: 'Hard'
time_commitment: '2-4 weeks (install) + ongoing tuning'
target_skills: 'Mains Wiring, Sensor Plumbing/Fittings, `leva!` Configuration, Pressure-Loop Tuning'
status: 'In Progress'
depends_on:
  - hardware/lucca-a53
  - hardware/ito-module
---

# Lucca A53 Mini Pressure & Flow Profiling via ito + `leva!`

## Description

Add **lever-style pressure and flow profiling** to the **La Spaziale Mini Vivaldi II** (Clive's
**LUCCA A53 Mini**) by installing the **ito microcontroller module** (softwareandcircuits.com, EU)
and running the **`leva!`** firmware. leva! closes a feedback loop on a pressure sensor and drives
the existing **vibratory pump** via phase-angle control — nearly stepless — to follow a programmed
pressure/flow curve (pre-infusion → ramp → decline), exactly like a lever machine.

**This is no longer speculative for this machine.** Multiple Mini Vivaldi II owners in the
[home-barista ito/leva! thread](https://www.home-barista.com/espresso-machines/ito-leva-controller-q-experience-t61709.html)
have this running. A full local index of that thread (365 posts, Nov 2019 → Apr 2026) lives at
`/Volumes/family/projects/electronics/espresso/home-barista-thread-index/INDEX.md`, and the leva!
firmware + hardware-install PDFs are at
`/Volumes/family/projects/electronics/espresso/leva! (for ito)/`.

The **seminal build thread** for this exact machine is the older
[La Spaziale Mini Vivaldi and pressure profiling](https://www.home-barista.com/espresso-machines/la-spaziale-mini-vivaldi-and-pressure-profiling-t56816.html)
(t56816, 46 posts, Feb–Apr 2019) — `blondica73`'s original US install, with `sandc` answering. It is
now indexed (with 20 install/graph photos) on the NAS at
`/Volumes/family/projects/electronics/espresso/home-barista-mini-vivaldi-t56816/INDEX.md`; the
in-repo synthesis is
[`_reference/mini-vivaldi-thread-t56816.md`](_reference/mini-vivaldi-thread-t56816.md).

> Owner `blondica73` (thread post #2): _"I used the ITO board to upgrade my La Spaziale Mini Vivaldi
> II … I have mine set up to read the pressure, flow, and temperature (group head block)."_ Cost was
> ~$200 for the kit, shipped to family in the EU and hand-carried to the US (it isn't sold here).

**See also:** [Mini V2 modifications at a glance](_reference/mini-v2-modifications.md) —
before/after of the fluid + electrical paths across this project and
[06-011](06-011-mini-v2-direct-plumb-in.md) (one shared teardown).

## Scope

This project is **pressure/flow profiling only**. leva! can _also_ take over PID temperature
control, but on the A53 that **conflicts with the stock control board** — owners run profiling and
leave temperature to the factory electronics. That separate, optional, harder workstream is split
out into **[06-012 leva! PID Temperature Takeover](06-012-leva-pid-temperature-takeover.md)**.

| Capability                        | This project | Notes                                                            |
| --------------------------------- | ------------ | ---------------------------------------------------------------- |
| Pressure profiling (vibe pump)    | ✅ in scope  | The proven core. Lever profiles, pre-infusion, declining curves. |
| Flow display + flow-based control | ✅ in scope  | Needs the Digmesa flow meter on the tank→pump line.              |
| Pressure / flow / temp logging    | ✅ in scope  | Via the Status Monitor app (the XML config ships with leva!).    |
| Dosing by time / volume / weight  | ✅ in scope  | Volume needs the flow meter; weight needs a BLE scale.           |
| PID temperature control           | ❌ → 06-012  | Conflicts with the A53 stock board. Leave temp to the factory.   |

## How leva! profiles a vibratory pump

Not obvious that you _can_ pressure-profile a vibe pump — you can, and have been able to since the
`caffè!`/`leva!` lineage added it (~2016; same idea the Decent uses). Per the firmware author
(`sandc`/Dietmar) in-thread:

> "Regular control loop with feedback: pressure sensor measures pressure, controller adjusts pump
> power, nearly stepless via phase-angle control (the pump sounds more or less normal)."

Pump power is expressed as a **phase angle**: 0° = full power, ~105–120° = pump stops (vibe pumps
quit well below 180°). leva! computes that angle from a proportional + integral response to the
pressure error; you tune it like a PID loop. Factory defaults won't produce good shots "except by
luck" — tuning is the real, ongoing work of this project (see Tuning below).

## Before / after: the control loop

Stock, the pump is a brute — full power until the shot ends. With ito + leva!, brew pressure is
measured continuously and the pump's power is dialed via **phase angle** to track a programmed curve
— a real feedback loop, like a lever machine's declining pressure. (Complements the shared
[modifications-at-a-glance](_reference/mini-v2-modifications.md) wiring view; this one tells the
control-loop story.)

```text
06-001 — pressure / flow profiling via ito + leva!    (★ = added)

BEFORE  (stock — fixed-power vibe pump)
  [tank] ─gravity─► [VIBE PUMP] ─► [brew boiler] ─► [group] ─► cup
                        ▲  full power, on/off
  [stock board] ─► [pump switch] ─┘        over-pressure bypass ─► pump inlet
  The brew button just runs the pump flat-out — no pressure control.

AFTER  (ito interposed; leva! closes a feedback loop on the pump)
  Sensing taps into the fluid path:
    [tank] ─►★[FLOW METER]─► [VIBE PUMP] ─►★[PRESSURE TEE]─► [brew boiler] ─► [group] ─► cup
             (pre-pump)                      (brew line)        bypass ★set >9 bar

  The closed loop leva! runs continuously:
       ┌──────────────────── pump produces pressure ◄────────────────────────┐
       ▼                                                                      │
  ★[PRESSURE SENSOR] ─► ito ADC ─► ★[ ito + leva! PID ] ─► phase angle ─► ★[ito RELAY] ─► [VIBE PUMP]
    measures brew P                 vs. a target profile    0°=full …            modulated,
                                    (pre-infuse→ramp→        ~110°=stop          not on/off
                                     decline)
       also feeding leva!:  ★flow meter → ito IMPULSE   ·   pump-switch L → ★ito SNS
                                                            (zero-cross timing + "pump on")

  Control / monitor:  ★ito WiFi ─► Status Monitor app (live pressure / flow / temp plots)

UNTOUCHED:  stock temperature board · boilers · low-water switch · dosing / 3-way valve
```

## The A53-specific fluid-system wrinkle: the over-pressure bypass

The Mini Vivaldi II has a **brew over-pressure bypass valve** that returns water to the pump inlet.
Two consequences for profiling, both from the thread:

1. **Set it above your max brew pressure.** If it opens at/near brew pressure it will fight the
   profile and bias the flow meter. Aim for it to crack only **just above 9 bar** (or whatever your
   profile ceiling is). leva! has a `PRESS OPV` setting to account for it.
2. **Flow-meter placement matters because of it.** Install the flow meter on the **tank→pump line
   (before the pump)**, which is what owners did. A meter downstream of the bypass would read high.

Note the manual's general profiling rule — _no pressure-affecting component between the sensor and
the portafilter_ (no gicleur jet, no spring-loaded shower-screen valve, no S11/B valve). Owners
report tapping a **T-fitting into the brew line** and profiling cleanly, so the A53 grouphead has
**not** required surgery in practice — but **verify your own grouphead** when you're in there
(Pre-flight below). The bypass valve, not a grouphead valve, is the thing to get right.

## Bill of materials

The ito kit bundles most of this. Buy the **full kit with pressure sensor + flow meter**; you can
ignore the PID/SSR parts for now (those belong to 06-012).

| #   | Item                          | Spec / pick                                                                             | Notes                                                                                                                                                                                                                                                                                                                                                              |
| --- | ----------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | **ito module + leva! kit**    | From [softwareandcircuits.com](http://www.softwareandcircuits.com) — EU only, ~€180–220 | Ships from the EU — softwareandcircuits.com shipped directly to a US address in this build, so the community "hand-carry" workaround isn't required (see As-received below). Get the **rotary-encoder display** variant (firmware `1 - ito with rotary encoder`).                                                                                                  |
| 2   | Pressure sensor               | Included in kit; ~24 mm × 54 mm, rated **125 °C**                                       | T-tap into the brew line. **Adapter may need light filing to fit** (owner report). Mount away from the pump — **vibration kills it**, heat is fine.                                                                                                                                                                                                                |
| 3   | Digmesa flow meter            | Included in kit (type FHKSC or nano PP)                                                 | Install on the **tank→pump line, before the pump** (see bypass note). ≤65 °C ambient. **Better still: skip it and share the machine's own (GICAR) flow meter** — a second meter in series adds a restricting nozzle that cut free flow ~10 % in t56816 (#31); see the flow-meter step in Build sequence.                                                           |
| 4   | T-fitting + sensor adapter    | To tee the pressure sensor into the brew line                                           | **Owners tee a T-fitting into the brew line** (t56816 #3 photo) and cap the spare branch for an optional gauge — plan on adding a tee, **not** on finding a factory pre-tapped port. The adapter **needed light filing to fit** (#1).                                                                                                                              |
| 5   | Display + rotary encoder      | Included in kit (OLED + encoder)                                                        | The one real ergonomics problem: mounting it without cutting the machine face. Plan a **3D-printed external housing**; a reversible no-cut option (`sandc`, t56816 #30) is to 3D-print a **La Spaziale Dream S1 bezel** (it has a display slot by design) and swap the passive LED PCB for a custom-shaped one. Otherwise owners Dremel-cut the opening (#28/#31). |
| 6   | Status Monitor 4+ + tablet    | App from softwareandcircuits; any cheap tablet                                          | Reads/plots pressure/flow/temp over WiFi using the bundled XML. Owner uses an Alldocube iPlay50 Mini, woken per-shot. **Do not power the tablet from ito** — its supply has no spare current.                                                                                                                                                                      |
| 7   | Flow-meter inline fittings    | Barb/adapter set matching the Digmesa ports to the OEM tank→pump tube                   | **Not in kit.** Measure the tank→pump line ID + the meter's port type once inside; the Digmesa FHKSC uses small barb ports. Add hose clamps or push-fit as appropriate.                                                                                                                                                                                            |
| 8   | Pump-switch → `SNS` wiring    | Mains-rated hookup wire + faston/spade connectors + heat-shrink                         | **Not in kit.** Taps the pump switch's mains phase to ito `SNS`. Same teardown as the 06-011 switched-mains interlock tap — do both in one session.                                                                                                                                                                                                                |
| 9   | Display/encoder housing       | PETG filament (self-print) or a print service                                           | **Not in kit.** External housing to avoid cutting the case. **PETG, not PLA** — warm/humid environment; PLA creeps and hydrolyses over time.                                                                                                                                                                                                                       |
| 10  | PTFE tape / thread sealant    | Standard                                                                                | For the sensor tee + any threaded adapters.                                                                                                                                                                                                                                                                                                                        |
| 11  | Pump / 3-way seal-rebuild kit | La Spaziale service seal kit — **contingency**                                          | Buy only if the machine is old or seals weep under profiling. Worn non-return / 3-way seals leak under profiling even when fine at normal pressure (pre-flight §3).                                                                                                                                                                                                |

**Existing infrastructure reused:** the machine's vibratory pump, brew solenoid, and (for now) the
entire stock temperature-control board.

> **Measure before ordering rows 4 & 7.** The sensor tee/adapter and the flow-meter fittings depend
> on the machine's internal line sizes — and on whether the La Spaziale group has a **pre-tapped
> sensor port** (row 4 note). Confirm both when you're inside, not before. Rows 1–3, 5 are in the
> kit; rows 4, 6–11 are the not-in-kit extras (6 and 11 are optional/contingency).

## As-received kit configuration

The kit shipped **directly to a US address** (Jan 2025, from Dietmar Eilert /
softwareandcircuits.com), so the "hand-carry from an EU address" note above is optional — the vendor
will ship to the US.

Configuration from the "keep this document" card (these are the values you set in leva! at setup):

| Setting           | This kit                                                                                                                           |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| PCB revision      | 2.x                                                                                                                                |
| OLED module       | SSD1309 (jumper J1)                                                                                                                |
| Flow meter        | Digmesa FHKSC, type 932-xxxx (1925 / 1934 / 2016 / 2012 impulses/L at 0° / 90° / 180° / 270°); no integrated pull-up → R6 on ito   |
| Pressure sensor   | 200 / 215 / 300 PSI option — **confirm the checked rating** (9 bar ≈ 130 psi, within range of all three)                           |
| WiFi              | AP `ito Module`, 2.4 GHz WPA/WPA2-PSK — **set a custom password on first boot** (credentials are on the offline card, not in repo) |
| Manual / software | on the bundled DVD (English)                                                                                                       |

**Fully loaded — reconciles the BOM above:**

- Includes the **SSR kit + TSic sensor** (the PID hardware). This project stays profiling-only, but
  the temperature-takeover hardware for [06-012](06-012-leva-pid-temperature-takeover.md) is already
  on hand — no re-order.
- Also includes a **fluid-installation kit** (OKS grease, PTFE, 3× fittings for G1/8" systems), the
  **TouchCell bracket**, **BLE**, and the **USB-serial (FTDI) adapter** — so BOM row 7 (flow-meter
  fittings) and the programming adapter are largely covered by the kit. **Verify the G1/8" fittings
  match the Mini V2's brew/tank lines** before assuming row 7 is closed.

## Pre-flight (verify before committing)

1. **Confirm it's the Mini (vibe pump).** leva! drives **vibratory** pumps only. The full-size A53
   uses a **rotary** pump and is **not** compatible (its motor's inrush can destroy the SSR). The
   Mini Vivaldi II / A53 Mini is the vibe-pump model → OK.
2. **Inspect the grouphead.** Open it and confirm there's no spring-loaded valve / gicleur / S11/B
   restrictor between the sensor tap point and the portafilter. Owners report a clean path; verify
   yours.
3. **Check pump + 3-way valve seal condition.** Worn non-return / 3-way seals that are fine at
   normal pressure **leak under profiling**. An old machine may want a pump rebuild first.
4. **Confirm the bypass valve cracking pressure** and plan to set it >9 bar.
5. **Characterize the pump's full-power ceiling.** The Mini Vivaldi pump is "lazy" — at full power
   it rises **~half as fast (bar/s) as a Rancilio Silvia** (t56816 #17), likely a mix of pump type,
   flow-meter restriction, and a larger brew-boiler air pocket. **leva! can't recreate a profile
   whose ramp is steeper than the machine hits at full power**, so pull one no-profile, full-power
   shot first to see the ceiling. (One owner eventually swapped in a **ULKA EX5** pump, #21.)

## Build sequence (start here — all parts + machine on hand)

Grounded in the ito **Hardware Reference Manual** (on the kit DVD, archived at
`.../espresso/ito-dvd/Manual/Manual.pdf`). The pressure-loop tuning is the _separate_ leva! firmware
manual — see **Tuning** below and `_reference/leva/`.

1. **Pre-flight** (section above): vibe-pump confirmed, grouphead path clear (no gicleur/S11 between
   the sensor tap and the portafilter), pump/3-way seals sound, bypass valve noted.
2. **Mount & power ito.** Solder the on-board HLK-PM01 PSU (or wire external 5 V / ≥600 mA). Fit the
   4 adhesive feet + acrylic insulation shield; mount in a **non-metal or grounded enclosure — not
   metal screws** (insulation distance), away from boiler heat. Wire **N/L to the machine's
   switched-mains rail**; use a surge-protected outlet. Keep mains leads separated from low-voltage
   leads (EMC).
3. **Wire the pump for phase-angle control.** Route the vibratory pump through an ito on-board
   **relay (clamp 1 or 2)**; feed the **pump-switch L phase into `SNS`** for zero-cross detection +
   "pump on" (phase-angle needs SNS to see the L phase). **As-built on a Mini Vivaldi II** (t56816
   #35): ito `L` → the mains **L phase (the 3rd cable from the bottom** on the MV control board; 1st
   & 2nd are N); the MV board's **switched pump output → `SNS`**; **`SSR 1` → pump**. Optionally, a
   later step moves the **group-head solenoid feed (4th from bottom) onto `SSR 2`** to unlock dosing
   / backflush / shot control — this hands the valve to ito (the "secondary-controller" trade-off;
   dosing stays off until you do it). → **Do steps 2–3 in the same machine-open session as
   [06-011](06-011-mini-v2-direct-plumb-in.md)'s switched-mains solenoid interlock** — identical
   wiring area, one teardown.
4. **Install the sensors.** Pressure sensor → **ADC** header — **tee a T-fitting into the brew
   line** (cap the spare branch for an optional gauge; file the adapter if it's tight); mount
   **vibration-free** and cool-ish (125 °C-rated — heat is fine, vibration kills it; never at the
   pump). Flow meter → **IMPULSE** header. Two options: (a) the **kit Digmesa on the tank→pump line,
   before the pump** (R6 pull-up already fitted for the 932-xxxx), or (b) **share the machine's
   stock GICAR meter** to avoid stacking a second restricting nozzle. For (b): the GICAR connector
   (behind 3× 3 mm Allen screws) is **red = +VCC, white = signal/output, black = GND**; it's an
   **open-collector output already pulled to 5 V** (measured: +14.3 V rail, signal swings 0↔5 V),
   so bridge **signal + ground** to ito through a **CD4011 NAND gate + PC817 optocoupler** for
   isolation — and **never route the 14.8 V meter rail to an ito input** (5 V + 0.5 V absolute max).
   _(TSic → AUX and OLED → SPI/ENC are optional / for
   [06-012](06-012-leva-pid-temperature-takeover.md).)_
5. **WLAN.** ito boots in **AP mode** (SSID `ito Module`; **set a custom password first** at
   `http://192.168.4.1`). Switch it to **STA mode** to join your 2.4 GHz router; set a **static DHCP
   lease** so the IP stays stable/bookmarkable.
6. **Flash leva!** (macOS) — in **ZOC**, connect to ito's IP on **port 2323** (Telnet / Raw socket,
   **Xmodem-CRC**) → press RETURN (drops into the bootloader) → type **`f`** → **Upload** the leva!
   `.hex` (firmware `1 - ito with rotary encoder`, from the `leva! (for ito)` archives) → exit with
   `q`. ⚠️ ito must be in **AP or STA mode, _not_ STA+AP**; close Status Monitor first; back up
   settings via port 23 beforehand if wanted.
7. **Configure + fluid prep.** Install Status Monitor + its XML (plots pressure/flow/temp over
   WiFi). Set the pressure-sensor scaling, flow-meter type, and **`PRESS OPV`**; set the machine's
   over-pressure **bypass valve to crack just above 9 bar**. Then → **Tuning**.

## Tuning (the real, ongoing work)

Run the firmware-manual tutorials, then iterate with the Status Monitor plots (turn on the **pump
power / phase-angle** trace — temperature plots don't help when debugging pressure):

- **Pressure pre-test** (Menu, p.49) to seed pump characterization — needs a blind filter. ⚠️
  **A53-specific gotcha:** the pre-test **won't run** out of the box because the stock control board
  **drops the `SNS` signal on "inactivity"** (it reads the still pump as a too-fine grind) and
  aborts the test. Two fixes (t56816 #12–#14): temporarily **jumper `SNS`↔`L`** (set the SNS
  contact action to "do nothing" first), _or_ simply **press the machine's shot button, then start
  the pre-test** so a live pump keeps SNS energised. The result **survives firmware upgrades**, so
  this is a one-time chore.
- **`K` (proportional)** — start near the values owners cite (~3.5 gave clean graphs on later
  firmware; blondica's early build settled near ~20 — the absolute number is firmware-scale-
  dependent, so tune to the plot, not the digit). Halve it if you see oscillation/roughness; raise
  it if the pressure jump is sluggish. **Keep `Kc<SP` and `Kc>SP` close** — a lopsided pair (his 25
  vs 90) produced wild pump-power swings; balancing them cleaned up the graph (#17–#19).
- **`I`** — integral response.
- **Two parameter sets, split at 2.5 bar by _setpoint_ (not actual pressure)** — one for the 0–2.5
  bar pre-infusion range, one above (#40). The below-2.5 set is tuned to avoid overshoot (little
  coffee flows there, so pressure lingers); if you **undershoot** below 2.5 bar, **raise its `Kc`**
  (Setup→Pump→Control→Below 2.5 bar→Kc). A small "swing" right after the 2.5 bar setpoint crossing
  is the two sets handing off.
- **`PHASE OFF`** — the pump-stop phase angle; tune if a soaking pre-infusion (e.g. 20 s @ 1.1 bar)
  drifts above setpoint.
- **`PRESS MAX` / `PRESS OPV`** — ceiling + bypass accounting.
- **`Flow Corr`** — biases the feed-forward; nudge so the bias line tracks the pump-power line in
  the first seconds of the shot. Concrete rule from the thread: if the **bias plot rides ~5° above
  the yellow pump-power plot, reduce `Flow Corr` by ~5°** (#22). A large negative value (blondica's
  −25°) is a big power kick and can drive pre-infusion swing (#39–#40).
- **Flooding flow-drop is expected, not a bug.** The pump runs full power until ~0.7 bar fills the
  air pockets, then the control loop takes over and flow **drops sharply** (P and I ≈ 0 at zero
  error → only bias remains) (#45–#46). To kill the audible stutter at the hand-off, **start the
  profile at a higher pressure (e.g. 1.2 bar)** and/or adjust the flood-pressure setting.
- **Mid-shot "blips"** trace to coffee behaviour (channeling/fine-grind stall), **mains sag when the
  stock heater switches ~10 A** (leva! can't power-factor-correct it — it doesn't control the stock
  heater), measurement noise (verify with a blind-filter static-pressure test), or over-aggressive
  P/I turning a small disturbance into oscillation (#20).

A good starting recipe from the thread: **`Gen Lever` preset profile + ~10 s pre-infusion @ 1.5
bar** produced well-regarded shots on a Mini Vivaldi II. The firmware author actively tunes owners'
curves in-thread if you post phase plots.

> Note the ito pressure sensor and the machine's own gauge can **read slightly differently** —
> expect a small offset and trust the ito sensor's loop, not the factory gauge (t56816 #18).

## Exit Criteria

- [ ] ito installed; leva! `1 - ito with rotary encoder` flashed; Status Monitor plotting live
      pressure + flow + temp.
- [ ] Pressure sensor reads a credible brew-pressure curve; flow meter reads plausible mL/s.
- [ ] Over-pressure bypass set >9 bar; `PRESS OPV` configured; no flow-meter bias artifacts.
- [ ] A `Gen Lever` (or custom) profile tracks setpoint within a fraction of a bar at the plateau
      (not 7.9 bar when 9 is programmed).
- [ ] Pre-infusion (e.g. 10 s @ 1.5 bar) holds without overshoot; clean declining-pressure shot.
- [ ] No leaks at the sensor tee or flow meter after a session of shots.
- [ ] Display/encoder mounted without cutting irreplaceable parts.
- [ ] Stock temperature control still works (PID takeover deferred to 06-012).

## Progress

- [x] Researched leva! firmware + hardware-install manuals (local PDFs)
- [x] Indexed the full home-barista ito/leva! thread; confirmed Mini Vivaldi II owners profiling
      successfully (index at `.../home-barista-thread-index/INDEX.md`)
- [x] Indexed the seminal Mini Vivaldi build thread (t56816, 46 posts + 20 photos) and folded its
      findings in (index at `.../home-barista-mini-vivaldi-t56816/INDEX.md`; synthesis at
      `_reference/mini-vivaldi-thread-t56816.md`)
- [x] Scoped to profiling-only; split PID takeover into 06-012
- [ ] Pre-flight: confirm vibe pump, inspect grouphead path, check seal condition, bypass pressure
- [x] Source ito kit from the EU (complete kit in hand: module + pressure sensor + flow meter +
      encoder)
- [ ] Source not-in-kit extras (flow-meter fittings, SNS wiring, PETG, tablet) — measure line
      sizes + plan the brew-line T-fitting (no factory pre-tapped port to count on)
- [ ] Install pressure sensor (brew-line T-tap) + flow meter (kit meter pre-pump, or share the stock
      GICAR meter via NAND-gate + optocoupler)
- [ ] Wire pump to ito SNS (combine the machine-open work with 06-011's switched-mains interlock
      tap); design + print PETG display/encoder housing
- [ ] Flash leva!; install Status Monitor XML
- [ ] Set bypass + `PRESS OPV`; run pressure pre-test (mind the SNS-inactivity gotcha — jumper
      `SNS`↔`L` or press the shot button first)
- [ ] Tune K/I, PHASE OFF, Flow Corr against Status Monitor plots
- [ ] Dial in a lever profile; document as-built (sensor location, profile, tuned params)

## Related projects

- **[06-012 leva! PID Temperature Takeover](06-012-leva-pid-temperature-takeover.md)** — the
  optional temperature-control half, split out because it conflicts with the A53 stock board.
- **[06-009 Pump Pressure Transducer Retrofit](06-009-pump-pressure-transducer-retrofit.md)** — the
  DIY/no-ito way to read brew pressure; largely **subsumed** by the leva! kit's sensor.
- **[06-002 ESP32 Shot Profiler & Logger](06-002-esp32-espresso-shot-profiler-and-logger.md)** — DIY
  logging alternative; leva!'s Status Monitor covers most of this.
- **[06-011 Mini V2 Direct Plumb-In](06-011-mini-v2-direct-plumb-in.md)** — the float-fill plumb-in
  keeps an atmospheric pump inlet, which **this** project's profiling assumes; the two are
  compatible (and float-fill is the profiling-friendly choice).

## Sources

- **In-repo digest:** [`_reference/leva/LEVA-DOCS-SUMMARY.md`](_reference/leva/LEVA-DOCS-SUMMARY.md)
  — executive summary + page index of the two manuals (read this before the PDFs).
- **In-repo digest:**
  [`_reference/mini-vivaldi-thread-t56816.md`](_reference/mini-vivaldi-thread-t56816.md) — synthesis
  of the seminal Mini Vivaldi build thread + NAS image catalog.
- Local: leva! firmware manual + hardware-installation PDF,
  `/Volumes/family/projects/electronics/espresso/leva! (for ito)/`
- Local: full thread index,
  `/Volumes/family/projects/electronics/espresso/home-barista-thread-index/INDEX.md`
- Local: Mini Vivaldi build-thread index + photos,
  `/Volumes/family/projects/electronics/espresso/home-barista-mini-vivaldi-t56816/INDEX.md`
- [ITO/Leva! Controller — Q&A + Experience (home-barista, t61709)](https://www.home-barista.com/espresso-machines/ito-leva-controller-q-experience-t61709.html)
- [La Spaziale Mini Vivaldi and pressure profiling (home-barista, t56816)](https://www.home-barista.com/espresso-machines/la-spaziale-mini-vivaldi-and-pressure-profiling-t56816.html)
- [softwareandcircuits.com — ito module + leva!](http://www.softwareandcircuits.com)
- [projectcaffe.bplaced.net — leva! features / beta manual](http://projectcaffe.bplaced.net/features_leva.html)
- kaffee-netz.de — pressure-sensor install on a similar machine (linked from thread)
