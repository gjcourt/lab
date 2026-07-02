---
title: 'leva! PID Temperature Takeover (A53 Stock-Board Conflict)'
number: '06-012'
category: 'coffee-espresso'
difficulty: 'Hard'
time_commitment: 'Months'
target_skills: 'Mains Wiring, SSR Control, Espresso Electronics Reverse-Engineering, PID Tuning'
status: 'Not Started'
depends_on:
  - hardware/lucca-a53
  - hardware/ito-module
  - 06-001-lucca-a53-mini-leva-firmware-integration
---

# leva! PID Temperature Takeover (A53 Stock-Board Conflict)

## Description

Optional second half of the leva! integration: hand **boiler temperature control** to leva!'s PID
channels (two SSRs, two boilers) instead of the La Spaziale stock electronics. leva! provides
TSic-based PID that is meaningfully tighter than a typical Pt100 + PID, and a dual-channel version
suits the A53's **dual-boiler** layout.

**This is split out of [06-001](06-001-lucca-a53-mini-leva-firmware-integration.md) because, on this
machine, it does not work cleanly.** Pressure profiling (06-001) is proven; PID takeover is not.

## Why it's blocked / its own project

The A53 Mini is **electronically controlled** (volumetric push-buttons, a stock control board) — not
the mechanical-switch machine leva!'s PID install assumes. Owner report from the thread:

> _"I bought the entire kit, but I don't use the PID function as it currently interferes with the
> control board."_

So the open problem is **co-existence or clean replacement**: how to drive the heating elements from
leva!'s SSRs without the stock board fighting it (or how to cleanly retire the stock board's
temperature role while keeping its dosing/valve functions). This needs the A53 wiring reverse-
engineered, which is the bulk of the work and the reason this is rated **Hard / Months**.

The hardware manual's general PID requirements still apply: heating element(s) in the 110–240 V
circuit controlled via thermostat/pressurestat, sensor position ≤150 °C, a 20 A SSR per element on a
heatsink. **Steam should stay on the original steam thermostat** for safety (it's the overheat
backstop) — leva! controlling steam is explicitly _not recommended_.

## Open questions to resolve before starting

- [ ] Trace the A53 control board: where does it switch the brew-boiler element, and can that leg be
      intercepted by an SSR without the board faulting / fighting?
- [ ] Can the stock board keep dosing + valve duties while leva! owns temperature, or is it
      all-or-nothing?
- [ ] TSic sensor placement on the brew boiler (and service boiler if doing both).
- [ ] Is the gain (tighter temp control) worth the risk/effort vs. leaving the competent stock PID
      alone? Default answer today: **no — do 06-001 first, revisit only if temp stability proves
      limiting.**

## Test / probe plan (prove feasibility)

Feasibility hinges on one question — **does the stock brain fault when it loses the element, or can
it be pacified?** Answer it in three phases. Phase A is free and safe on the live machine, so do it
before spending anything.

### Phase A — map the control path (non-destructive, live machine)

- [ ] **Identify the temp sensor** — resistance across the boiler-probe leads, cold: NTC ≈ tens of
      kΩ (drops with heat), Pt100 ≈ 100 Ω (rises ~0.385 Ω/°C), thermostat = continuity. Scope the
      sensor input while heating.
- [ ] **Find the heater-switch leg** — trace the element leads (one to L, often via a safety stat;
      the other to the triac output). Clamp-meter which leg carries the switched current. _This is
      the leg you cut._
- [ ] **Capture the "heat command"** — scope the CPU→triac gate drive: on/off vs zero-cross burst vs
      phase-angle, and logic level.
- [ ] **Locate the safety thermostat / thermal fuse** in the element circuit — **keep it in series**
      after interposing (overheat backstop); do not bypass it.

### Phase B — characterize fault behavior (spare board / bench rig)

- [ ] **Current-sense check (the decider):** is there a shunt or CT in the heater circuit feeding
      the board? Open the triac output while heating and watch for an instant error. **Senses
      current → the cut is visible → likely faults. Watches temperature only → the cut is invisible
      as long as temp reads fine.**
- [ ] **Heater-timeout / watchdog:** element disconnected + probe reading **cold** → does it fault
      after N minutes? Note the timeout. Repeat with the probe **spoofed at-temp** → does it stay
      happy?
- [ ] **Sensor-plausibility window:** feed the sensor input open / shorted / out-of-range → find the
      fault thresholds (the stock probe must stay in-range).

### Phase C — prove the co-exist (integration, bench)

- [ ] **Interception dry-run:** cut the leg → element on ito's SSR → leva! holds temp via TSic →
      leave the stock probe reading real temp. Run cold-start → warm-up → hold → brew → recovery;
      watch for any fault.
- [ ] **Cold-start:** compare ito's time-to-temp against the Phase-B timeout. If the watchdog is
      shorter, mitigate (spoof the probe warm during warm-up, or let the brain heat until setpoint
      then hand off to ito).
- [ ] **Dosing/valve integrity:** exercise dosing, 3-way valve, hot water, steam — confirm all still
      work with ito owning the heat.

**Tools:** DMM, clamp/current meter, oscilloscope or logic analyzer, resistance decade box,
thermocouple, mains isolation (isolated probes / variac), plus the SSR + TSic + ito for the dry-run.

**Go / no-go:** **clean** if the brain watches temperature only (Phase B, current-sense) and stays
satisfied on a valid probe reading (watchdog); **workable with mitigation** if there is a survivable
cold-start timeout; **hard no** (→ full replacement, not co-exist) if it monitors element current or
interlocks the moment it loses actuation.

## De-risking: bench-test on a spare control board

The board-fault risk is the crux, so the responsible path is to do the reverse-engineering and the
destructive interception test on a **spare** A53 control board on the bench — never on the
in-service machine first. This turns "experiment on my daily driver" into a bench project and yields
a pristine fallback board.

**Source a spare board — know which board you need.** Three distinct boards exist: the **Main
Computer / CPU** (the brain that runs the temp loop — the fault-relevant one, **~$400 new and often
sold out**; Clive, or the "Universal Control Board SP-14139" listed for the Mini V2 at Espresso
World); the **triac / heater sub-board** (the power stage that actually switches the element —
**~$77**, e.g. Caffe Tech SP7388; confirm Mini V2 fitment first); and the **button / touchpanel
board** (front buttons only, ~$65 — irrelevant here). Used boards are scarce and a gamble (the CPU
is usually the part that fails). Order the board **with its connector harness** (or mating
connectors + pinout) and grab the **wiring diagram** (Mini V2 owner's manual §6 / service manual) as
the map.

**Staged spend (cheapest-first):** (1) map the control path **on the live machine, non-destructively
and free** (Phase A above); (2) buy the **~$77 triac sub-board** as the sacrificial power stage; (3)
only spring for a **spare CPU (~$400, or a used gamble)** if you commit to the destructive
board-fault test — by then Phase A may have taught you enough to work the live board carefully.

**Build a bench rig that emulates the machine around the board** — it won't command heat until its
interlocks are satisfied. What each machine input/output becomes on the bench:

| Machine signal          | Bench emulation                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------ |
| Power                   | Bench supply or the machine's transformer                                                        |
| Boiler temp probe       | Resistance decade box (identify NTC vs Pt100 first); sweep cold→hot to force the heater to cycle |
| Water-level + low-water | Jumper / resistor = "water present"                                                              |
| Volumetric buttons      | Momentary switches                                                                               |
| Heater-element output   | Lamp / resistor + meter/scope on the switching leg (**the leg you intercept**)                   |

Tools: multimeter + scope/logic analyzer + the 20 A SSR + TSic (already in the kit).

**Black-box framing:** you never need the board's internal logic — treat it as sensors → box →
heater output and intercept the _output leg_. A potted/opaque board is fine.

**Bench workflow:**

1. Power into a heating state → find the heater-switch leg.
2. Sweep temp to cycle it.
3. Cut the leg + insert the SSR (ito+leva!).
4. **Check whether the board faults** (key unknown: does it monitor the element or expect its own
   temp loop to close?).
5. Work out co-exist (feed a "temp OK" signal so the board keeps dosing/valve duties).
6. Only then replicate on the machine.

**Swap-in fallback:** do the _entire_ mod on the spare board, validate on the bench, then swap the
modified board into the machine — keeping the original untouched as an instant revert (full
reversibility).

**Caveat / sequencing note:** this _raises_ the cost/effort of 06-012 (spare board + rig) but moves
the risk off the working machine; it does **not** change sequencing — do 06-001 first, pull this
plan off the shelf only if temp stability proves limiting.

## Exit Criteria

- [ ] Define done: e.g. "leva! holds brew-boiler temp within ±0.3 °C at the sensor, stock board
      undisturbed for dosing/valve, steam still on original thermostat, no fault state."

## Progress

- [ ] Reverse-engineer A53 control-board heater switching
- [ ] Decide co-exist vs. replace
- [ ] Source spare control board + harness/pinout
- [ ] Build bench rig (sensor simulators + heater-leg monitor)
- [ ] Run the test/probe plan (Phase A live → Phase B/C on the bench)
- [ ] Bench-test SSR interception + board-fault check
- [ ] Validate co-exist / prep swap-in modified board
- [ ] Install TSic sensor(s); configure PID1/PID2
- [ ] Tune; verify stock functions intact

## Sources

- Local: leva! hardware-installation PDF (PID/SSR wiring),
  `/Volumes/family/projects/electronics/espresso/leva! (for ito)/`
- Local: thread index,
  `/Volumes/family/projects/electronics/espresso/home-barista-thread-index/INDEX.md`
- [ITO/Leva! Controller thread (t61709)](https://www.home-barista.com/espresso-machines/ito-leva-controller-q-experience-t61709.html)
