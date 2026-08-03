# ito + leva! pre-infusion skip — bug record + Home Barista draft

Draft forum post reporting that leva! skips the pre-infusion segment on a manual (switch-triggered)
pull on the Mini Vivaldi II. Kept here alongside the espresso-project reference docs so the writeup
and the ruled-out list don't live only in chat.

**Status: READY TO POST.** Both blocking checks are cleared (2026-08-03):

1. **`Execute PI` is checked** — verified on the machine, and pre-infusion is _still_ skipped. This
   is the global Profiles-menu toggle (manual p.126), the one the firmware manual says gates PI at
   p.133: _"The preinfusion part is only executed if 'Execute PI' is checked in the profiles menu."_
   With it confirmed on, the documented gate is not the cause.
2. **No scale on this build**, so `Drop ends PI` (p.127) — which auto-skips PI→shot on the first
   recorded drop — has no input it could fire from.

A full sweep of the firmware manual turns up no other documented mechanism that suppresses or
short-circuits the pre-infusion segment. The remaining hypothesis is the dose-program one below.

Home Barista runs phpBB, so paste the **BBCode** rendering rather than this markdown.

**Still untested:** the "PI only runs under a dose-program execution" hypothesis — the dose-program
(`MCcDOSE`) path can't be exercised until Relay 2 (group solenoid) is wired (see
`mini-v2-e2-group-solenoid-relay2.md`), so every pull to date has been switch-triggered free-pour.

Related: `project_leva_controller` / `project_espresso_profiling` (memory), where the full debugging
trail lives.

---

**Subject:** ito + leva! skips the pre-infusion segment on a manual (switch-triggered) pull —
expected?

Sanity-checking whether this is a bug or just how the firmware is meant to work.

**Setup**

- Machine: La Spaziale S1 Mini Vivaldi II (LUCCA A53 Mini), vibratory pump.
- Install followed **blondica's build thread** here on HB.
- Factory Progressive Preinfusion chamber removed; pressure sensor (Honeywell MIPAN2XX250PSAAX, 250
  psi) threaded into the group-head port the chamber used to occupy → into the ito ADC.
- Pump driven off the ito relay; sense on the pump line for zero-cross.
- **No flowmeter and no scale** in this build — pressure-only profiling, so there are no flow
  targets or drop-detection inputs anywhere.
- Firmware: **ito 1.1 (2019-06-30)**, running leva! pressure profiling.

**The profile** (dark decline, "Profile 1"):

- Pre-infusion: **8 s @ 2.0 bar**
- Shot: **2 s @ 8.0 bar → 23 s @ 4.0 bar**
- Pump points entered in **bar** (closed-loop pressure, not phase-angle degrees).

**Expected:** the pre-infusion segment runs first — ~8 s of gentle 2 bar bloom — then the shot curve
declines from 8 to 4 bar.

**Observed:** on a manual, switch-triggered pull, **the pump jumps straight to the shot profile and
skips pre-infusion entirely** — shot targets from t=0, no 2-bar bloom.

One detail worth stating precisely, because it rules out the obvious "your pump just can't hold 2
bar" reading: I'm not inferring this from measured pressure. I log the **firmware's own reported
setpoint** — the target and tolerance-band fields in the rich telemetry frame on TCP 23 — and at t=0
that setpoint is already **8.0 bar**, the shot segment's opening target, with the band tracking it.
The machine isn't trying and failing to hold 2 bar; it never adopts the 2 bar setpoint at all. Same
picture on leva!'s own Status Monitor plot and on the OLED.

**What I've ruled out:**

- **`Execute PI` is checked** in the Profiles menu (p.126) — I've verified the global toggle is on,
  not just that the segment is programmed. PI is still skipped with it checked.
- **`Drop ends PI` can't be the cause** (p.127) — there's no scale on this build, so there's no drop
  detection to end preinfusion early.
- **Config is correct and saved** — the PI segment reads back correctly on the machine and in my
  telemetry; genuinely stored, not a lost edit.
- **Not a "NEXT" skip** — no long encoder/button click during the shot, so the segment isn't being
  advanced past by a stray input.
- **Not a units problem** — pump values are in bar, not degrees.
- **Not the boiler-fill / flood confound** — leva! gates boiler-fill with its own ~0.7 bar flood
  pressure, and the observed setpoint goes straight to 8 bar rather than sitting at the flood gate.
- **Isolated with `Execute shot` off** — same result.

The one pattern I can't rule out: pre-infusion may only run when the shot is launched as a
**dose-program execution**, rather than a manual pump-switch pull. I haven't been able to test the
dose-program path yet — the group solenoid isn't on the ito's second relay, so I'm still
switch-triggering every pull — so that's a hypothesis, not something I've confirmed. Which is really
what I'm asking:

> **Does anyone get pre-infusion to run on a manual, switch-triggered pull — or does PI require
> running the shot as a dose program?**

If it's by design, that's worth documenting. If it's a bug, I'm happy to grab whatever
logs/plots/settings dumps are useful — I can pull the full `MCu` setup dump and per-shot setpoint
traces over TCP 23.

**Workaround I'm testing** in the meantime — folding the bloom into the shot segment itself, e.g.
`1 s @ 2 bar → 8 s @ 2 bar → 11 s @ 8 bar → 32 s @ 3 bar`, so pre-infusion happens inside the shot
curve rather than as a separate PI phase. Early days on whether it's as good as a true PI segment.

Thanks — great firmware overall, this is the one thing that's had me stumped.

— George

---

## Corroborating check worth running before posting

The manual (p.152) states the PI and shot **time scales are independent**, with the worked example
that an event defined for the 23rd second of the shot occurs at 29 s in the actual brew when
preinfusion is 6 s. So for this profile a correct run should end at **8 s (PI) + 23 s (shot) = 31
s**, and a PI-skipped run should end at **23 s**.

If the observed brew duration lands at the shot segment's own length, that's clean arithmetic
confirmation independent of the setpoint trace, and worth one line in the post. Don't state it until
it's been measured **on this profile** — the traces captured so far are from a different profile.

## Posting mechanics

home-barista.com sits behind Cloudflare and returns **403 to a headless browser**, so this can't be
posted by automation. Post it by hand, or drive a headed browser with the Cloudflare challenge
solved manually.
