# Mini Vivaldi II — Modifications at a Glance

Combined before/after of the **fluid** and **electrical** paths across the two machine projects:
[06-001 pressure/flow profiling](../06-001-lucca-a53-mini-leva-firmware-integration.md) and
[06-011 direct plumb-in](../06-011-mini-v2-direct-plumb-in.md). Both are done in **one teardown**
(panels off → pump/boiler/wiring exposed).

Every `★` is something you add; everything unmarked stays stock. The water side gains **two taps**
(no added flow meter — the machine's own stock GICAR meter is reused electrically); the electrical
side is pure **interposition** — the ito slips into the pump's mains circuit, and both ito's
pump-sense and the plumb-in solenoid tap the control-board **PUMP output** (there is **no** switched
mains rail on this machine — see the wiring reference). The stock control board, the low-water float
switch, the boilers, and the pump itself are **untouched**.

```text
════════════════════════ FLUID PATH ════════════════════════

BEFORE  (stock — tank-fed)

   ┌───────────┐
   │ RESERVOIR │   hand-filled · low-water float switch = dry-run cutoff
   └─────┬─────┘
         │ gravity
         ▼
    [VIBE PUMP] ───────────► [brew boiler] ──► [group] ──► portafilter
         ▲
         └── [over-pressure bypass]  → back to pump inlet


AFTER   (★ = added / changed)

  Claryum → [ball valve] → ★[NC solenoid] → ★[regulator ~25psi] ┐
                                                                ▼
                                                     ★[FLOAT VALVE]   (hole in tank wall)
   ┌───────────┐ ◄──────────────────────────────────────────────┘   tops the tank up
   │ RESERVOIR │   low-water float switch  ← UNCHANGED
   └─────┬─────┘
         │ gravity  (still stock)
         ▼
   [VIBE PUMP] → ★[PRESSURE TEE] → [brew boiler] → [group] → PF
        ▲
        └── [bypass] ★ set >9 bar
   (no added in-line meter — flow is read off the machine's own stock GICAR meter; see Electrical)


═════════════════════ ELECTRICAL PATH ═════════════════════

BEFORE  (stock)

  MAINS → [power switch] → [stock control board] → [pump switch] → [VIBE PUMP]


AFTER   (★ = added;  stock control board left alone)

  MAINS (always live — no hard switch) ─► [stock control board]   (unchanged)
     F/PHASE + N ─► ★ ito power (N/L)                  (always-live mains)
     PUMP output ─┬─► ★ ito SNS                        (zero-cross + "pump on")
                  └─► ★ solenoid 12 V PSU              (fill interlock — open only while pump draws)

  pump run:   ★[ito Relay 1] → [VIBE PUMP]                      ← leva! phase-angle control (solid-state relay, phase-fired)
  sense:      controller pump-on lead → ★[ito SNS]             ← zero-cross + "pump on"; ito SNS is an opto input,
                                                                  so the stock board must switch the pump via a
                                                                  mechanical relay to trigger it reliably
  data in:    pressure sensor → ★[ito ADC]
              stock GICAR meter → ★[CD4011 NAND buffer @5V] → ★[ito IMPULSE]   (reuse machine's meter; opto optional)
```

## Reading it

- **Water — two taps + one setting.** Solenoid/regulator/float valve upstream of the tank (06-011)
  and a single pressure tee on the brew line (06-001); the existing over-pressure bypass dialed to
  crack just above 9 bar. **Flow is read off the machine's own stock GICAR meter — no added in-line
  meter** (a second meter in series restricted free flow ~10 %, t56816 #31).
- **Electrical — interposition, not a rebuild.** The ito **`Relay 1`** (a solid-state relay) slips
  into the pump's mains circuit for phase-angle control; `SNS` reads the controller's pump-on lead
  for zero-cross timing + "pump on"; the stock GICAR meter is shared to `IMPULSE` through a **CD4011
  NAND buffer on ito's 5 V rail** (opto optional — galvanic isolation only; blondica's proven build
  is the bare NAND); and both ito's `SNS` and the plumb-in solenoid's PSU tap the control-board
  **PUMP output** — there is **no switched mains rail** on this machine (`F`/PHASE is always live;
  full M5 terminal map in [control-board wiring](mini-v2-control-board-wiring.md)).
- **Untouched:** stock control board (profiling only — PID takeover is the deferred
  [06-012](../06-012-leva-pid-temperature-takeover.md)), low-water float switch (dry-run
  protection), boilers, group, and pump.
- **Reversibility:** the ito interposes (unplug → stock); the plumb-in disconnects at the regulator.
  The only semi-permanent bits are the pressure-sensor tee (reversible with a plug, or use a
  pre-tapped group port) and the ~$65 reservoir tub.
- ⚠️ **The electrical work is mains-voltage** — qualified-electrician territory per the ito manual.
  Water taps and mounting are DIY-friendly; treat the mains splices accordingly.

## Shared teardown

Because the float valve (06-011) and the pressure tee + stock-meter tap (06-001) are all reachable
once the panels are off, and the control-board **PUMP output** serves both ito's `SNS` sense and the
solenoid PSU, **do both projects' in-machine work in one session.** Panel removal:
[Clive — LUCCA A53 / Mini / Vivaldi: Panel Removal](https://support.clivecoffee.com/en/la-spaziale-lucca-a53-panel-removal).
