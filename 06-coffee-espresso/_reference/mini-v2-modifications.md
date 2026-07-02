# Mini Vivaldi II — Modifications at a Glance

Combined before/after of the **fluid** and **electrical** paths across the two machine projects:
[06-001 pressure/flow profiling](../06-001-lucca-a53-mini-leva-firmware-integration.md) and
[06-011 direct plumb-in](../06-011-mini-v2-direct-plumb-in.md). Both are done in **one teardown**
(panels off → pump/boiler/wiring exposed).

Every `★` is something you add; everything unmarked stays stock. The water side gains **three
taps**; the electrical side is pure **interposition** — the ito slips into the pump's mains circuit
and rides the same switched-mains rail that also powers the plumb-in solenoid. The stock control
board, the low-water float switch, the boilers, and the pump itself are **untouched**.

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
  ★[FLOW METER] → [VIBE PUMP] → ★[PRESSURE TEE] → [brew boiler] → [group] → PF
   (tank→pump)          ▲
                        └── [bypass] ★ set >9 bar


═════════════════════ ELECTRICAL PATH ═════════════════════

BEFORE  (stock)

  MAINS → [power switch] → [stock control board] → [pump switch] → [VIBE PUMP]


AFTER   (★ = added;  stock control board left alone)

  MAINS → [power switch] → SWITCHED-MAINS RAIL ─┬─► [stock control board]   (unchanged)
                                                ├─► ★ ito power (N/L)
                                                └─► ★ solenoid coil supply   (plumb-in interlock)

  pump run:   [pump switch] → ★[ito RELAY 1/2] → [VIBE PUMP]    ← leva! phase-angle control
  sense:      pump-switch L → ★[ito SNS]                        ← zero-cross + "pump on"
  data in:    pressure sensor → ★[ito ADC]      flow meter → ★[ito IMPULSE]
```

## Reading it

- **Water — three taps + one setting.** Solenoid/regulator/float valve upstream of the tank
  (06-011); a flow meter on the tank→pump line and a pressure tee on the brew line (06-001); the
  existing over-pressure bypass dialed to crack just above 9 bar.
- **Electrical — interposition, not a rebuild.** The ito relay slips into the pump's mains circuit
  for phase-angle control, `SNS` reads the pump-switch L phase for zero-cross timing, and the module
  shares **one switched-mains tap** with the plumb-in solenoid, downstream of the machine's power
  switch.
- **Untouched:** stock control board (profiling only — PID takeover is the deferred
  [06-012](../06-012-leva-pid-temperature-takeover.md)), low-water float switch (dry-run
  protection), boilers, group, and pump.
- **Reversibility:** the ito interposes (unplug → stock); the plumb-in disconnects at the regulator.
  The only semi-permanent bits are the pressure-sensor tee (reversible with a plug, or use a
  pre-tapped group port) and the ~$65 reservoir tub.
- ⚠️ **The electrical work is mains-voltage** — qualified-electrician territory per the ito manual.
  Water taps and mounting are DIY-friendly; treat the mains splices accordingly.

## Shared teardown

Because the float valve (06-011) and the flow meter + pressure tee (06-001) are all reachable once
the panels are off, and the single switched-mains tap serves both the ito and the solenoid, **do
both projects' in-machine work in one session.** Panel removal:
[Clive — LUCCA A53 / Mini / Vivaldi: Panel Removal](https://support.clivecoffee.com/en/la-spaziale-lucca-a53-panel-removal).
