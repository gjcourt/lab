# ito + leva! pre-infusion skip — bug record + Home Barista draft

Draft forum post reporting that leva! skips the pre-infusion segment on a manual
(switch-triggered) pull on the Mini Vivaldi II. Kept here alongside the espresso-project
reference docs so the writeup and the ruled-out list don't live only in chat.

**Status:** not yet posted. The "PI only runs under a dose-program execution" line is an
**untested hypothesis** — the dose-program (`MCcDOSE`) path can't be exercised until Relay 2
(group solenoid) is wired (see `mini-v2-e2-group-solenoid-relay2.md`), so every pull to date
has been switch-triggered free-pour. Related: `project_leva_controller` /
`project_espresso_profiling` (memory), where the full debugging trail lives.

---

**Subject:** ito + leva! skips the pre-infusion segment on a manual (switch-triggered) pull — expected?

Sanity-checking whether this is a bug or just how the firmware is meant to work.

**Setup**
- Machine: La Spaziale S1 Mini Vivaldi II (LUCCA A53 Mini), vibratory pump.
- Install followed **blondica's build thread** here on HB.
- Factory Progressive Preinfusion chamber removed; pressure sensor (Honeywell MIPAN2XX250PSAAX,
  250 psi) threaded into the group-head port the chamber used to occupy → into the ito ADC.
- Pump driven off the ito relay; sense on the pump line for zero-cross.
- **No flowmeter** in this build — pressure-only profiling, so there are no flow targets anywhere.
- Firmware: **ito 1.1 (2019-06-30)**, running leva! pressure profiling.

**The profile** (dark decline, "Profile 1"):
- Pre-infusion: **8 s @ 2.0 bar**
- Shot: **2 s @ 8.0 bar → 23 s @ 4.0 bar**
- Pump points entered in **bar** (closed-loop pressure, not phase-angle degrees).

**Expected:** the pre-infusion segment runs first — ~8 s of gentle 2 bar bloom — then the shot
curve declines from 8 to 4 bar.

**Observed:** on a manual, switch-triggered pull, **the pump jumps straight to the shot profile
and skips pre-infusion entirely** — shot targets from t=0, no 2-bar bloom. Triple-confirmed:
leva!'s own Status Monitor plot, my telemetry capture off the port-23 MC stream, and the machine's
OLED all show the same thing.

**What I've ruled out:**
- **Config is correct and saved** — the PI segment reads back correctly on the machine and in my
  telemetry; genuinely stored, not a lost edit.
- **Not a "NEXT" skip** — the segment isn't being advanced past by a stray input.
- **PI isn't disabled** — it's an active segment in the profile.
- **Not a units problem** — pump values are in bar, not degrees.
- **Not the boiler-fill / flood confound** — leva! distinguishes boiler-fill from a shot via its
  ~0.7 bar flood-pressure gate, and this isn't that.
- **Isolated with Execute-shot off** — same result.

The one pattern I can't rule out: pre-infusion may only run when the shot is launched as a
**dose-program execution**, rather than a manual pump-switch pull. I haven't been able to test the
dose-program path myself yet — I'm still switch-triggering every pull — so that's a hypothesis, not
something I've confirmed. Which is really what I'm asking:

> **Does anyone get pre-infusion to run on a manual, switch-triggered pull — or does PI require
> running the shot as a dose program?**

If it's by design, that's worth documenting. If it's a bug, I'm happy to grab whatever
logs/plots/settings-dumps are useful (I can pull full MC state over TCP 23).

**Workaround I'm testing** in the meantime — folding the bloom into the shot segment itself, e.g.
`1 s @ 2 bar → 8 s @ 2 bar → 11 s @ 8 bar → 32 s @ 3 bar`, so pre-infusion happens inside the shot
curve rather than as a separate PI phase. Early days on whether it's as good as a true PI segment.

Thanks — great firmware overall, this is the one thing that's had me stumped.

— George
