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

## Exit Criteria

- [ ] Define done: e.g. "leva! holds brew-boiler temp within ±0.3 °C at the sensor, stock board
      undisturbed for dosing/valve, steam still on original thermostat, no fault state."

## Progress

- [ ] Reverse-engineer A53 control-board heater switching
- [ ] Decide co-exist vs. replace
- [ ] Bench-test SSR interception on the brew boiler
- [ ] Install TSic sensor(s); configure PID1/PID2
- [ ] Tune; verify stock functions intact

## Sources

- Local: leva! hardware-installation PDF (PID/SSR wiring),
  `/Volumes/family/projects/electronics/espresso/leva! (for ito)/`
- Local: thread index,
  `/Volumes/family/projects/electronics/espresso/home-barista-thread-index/INDEX.md`
- [ITO/Leva! Controller thread (t61709)](https://www.home-barista.com/espresso-machines/ito-leva-controller-q-experience-t61709.html)
