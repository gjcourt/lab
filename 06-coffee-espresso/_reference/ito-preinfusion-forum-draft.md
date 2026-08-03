# ito + leva! pre-infusion skip — bug record + Home Barista draft

Draft forum post reporting that leva! skips the pre-infusion segment on a manual (switch-triggered)
pull on the Mini Vivaldi II. Kept here alongside the espresso-project reference docs so the writeup
and the ruled-out list don't live only in chat.

## Status: NOT POSTED — four on-machine values still needed

Two earlier blockers **are** cleared (2026-08-03):

- **`Execute PI` is checked** — verified on the machine, and pre-infusion is _still_ skipped. That's
  the global Profiles-menu toggle (p.126), the one the manual says gates PI at p.133: _"The
  preinfusion part is only executed if 'Execute PI' is checked in the profiles menu."_ The
  documented gate is on, so it isn't the cause.
- **No scale on this build**, so neither `Drop ends PI` (p.127, auto-skips PI→shot on the first
  recorded drop) nor cup detection (p.126 note → p.174, recognises cups by weight and activates
  their assigned profile) has any input it could fire from.

But a closer read of the manual turned up **four more documented mechanisms** that produce this
exact symptom, and the earlier claim that no others existed was wrong. Each is a one-glance check,
and each is something `sandc` would ask on the first reply. In rough order of how well they match
the symptom:

1. **`Flood` → `Pressure` value (p.131).** _"The firmware will automatically discard pressure
   profile setpoints below the flood pressure."_ Also: _"pressure profiling will begin at 0.7 bar —
   even if the pressure profile begins at 0 bar."_ **If flood pressure is set at or above the PI
   target of 2.0 bar, the entire PI segment is discarded and the profile starts at the shot** —
   which is precisely what's observed. The manual's 0.7 bar is only its example value; read the
   actual setting. This is the strongest candidate.
2. **The PI segment's real point table.** p.153: _"The implicit starting point of preinfusion is
   'pump off' (phase = 180°) at 0 s"_, and p.151 says the firmware interpolates only _between
   setpoints of the same type_ (phase→phase, pressure→pressure). A PI segment holding a **single
   pressure point at 8 s** therefore has nothing to ramp from — the implicit start is a _phase_
   point, which won't interpolate to a pressure point. Write down the actual `No./Action/Time/Pump`
   rows for both segments, plus `Repeat`, `Wait`, `Resize PI`/`Resize S` and `End`.
3. **`Use` (p.126)** — _"This item selects a pressure profile for shots or turns pressure profiling
   off (if you select none)."_ Confirm the profile selected under `Use` is the same slot that was
   edited; the selected profile's name shows in the display title line. Editing one slot while `Use`
   points at another is the most mundane possible cause.
4. **No contact assigned `PREINFUSE` (p.88 / p.228).** _"Temporarily enable preinfusion… The
   preinfusion part of active pressure profile will be executed **if the contact is closed**."_ If a
   contact carries this function and sits open, PI never runs.

**Also still untested:** the "PI only runs under a dose-program execution" hypothesis — the
dose-program (`MCcDOSE`) path can't be exercised until Relay 2 (group solenoid) is wired (see
`mini-v2-e2-group-solenoid-relay2.md`, pending on the `docs/e2-group-solenoid-relay2` branch), so
every pull to date has been switch-triggered free-pour.

Note the manual actually argues _against_ that hypothesis: the `End` → STOP description (p.134)
explicitly contemplates a profile _"started by a toggle switch"_, and the flood tip (p.127) assumes
profiling applies to any plain pump-on. That's worth saying in the post — it's why this looks like a
bug rather than by-design.

**Before posting**, resolve 1–4, then reconcile the two internal inconsistencies flagged below.

Home Barista runs phpBB — convert to BBCode before pasting (no BBCode rendering is stored here).

Related: `project_leva_controller` / `project_espresso_profiling` (memory), where the full debugging
trail lives.

## Two things in the post that don't yet add up

- **t=0 reads 8.0 bar, but the shot's first point is at 2 s.** Per p.153 the implicit shot start is
  _full power (phase = 0°) at 0 s_, and phase↔pressure points don't interpolate — so a logged
  _pressure_ setpoint of 8.0 bar at t=0 shouldn't follow from the profile as written. Either the
  profile has a 0 s @ 8 bar point that the description omits, or the decode is off. Resolve before
  publishing; it's the sort of thing that unravels a report.
- **`Execute shot` off — "same result"** doesn't parse. With the shot segment disabled there is no
  shot curve to jump to, so "same result" either means something much bigger (the shot ran anyway)
  or the test predates the `Execute PI` check. Write down what was actually observed, and when.

---

**Subject:** ito + leva! skips the pre-infusion segment on a manual (switch-triggered) pull —
expected?

Sanity-checking whether this is a bug or just how the firmware is meant to work.

**Setup**

- Machine: La Spaziale S1 Mini Vivaldi II (LUCCA A53 Mini), vibratory pump.
- Build loosely based on **blondica73's** thread here on HB (I mount the sensor differently — see
  below).
- Factory Progressive Preinfusion chamber removed; pressure sensor (Honeywell MIPAN2XX250PSAAX, 250
  psi) threaded into the group-head port the chamber used to occupy → into the ito ADC.
- Pump driven off the ito relay; sense on the pump line for zero-cross. Pressure profiling needs
  that SNS signal (p.126) and the shot segment does execute, so zero-cross sensing is demonstrably
  fine.
- **No flowmeter and no scale** in this build — pressure-only profiling, so there are no flow
  targets or drop-detection inputs anywhere.
- **leva! 3.1** on an ito V2.0 module. (The module's own base firmware string reads
  `ito 1.1 – 2019-06-30` in its web UI — that's the WiFi firmware, not leva!.)

**The profile** (dark decline, "Profile 1"):

- Pre-infusion: **8 s @ 2.0 bar**
- Shot: **2 s @ 8.0 bar → 23 s @ 4.0 bar**
- Pump points entered in **bar** (closed-loop pressure, not phase-angle degrees).

<!-- TODO(George): replace the two lines above with the literal No./Action/Time/Pump rows for both
segments, plus Repeat / Wait / Resize PI / Resize S / End. sandc will want the table, and per p.153
the number of PI points changes what the firmware is even able to do. -->

**Expected:** the pre-infusion segment runs first — ~8 s of gentle 2 bar bloom — then the shot curve
declines from 8 to 4 bar.

**Observed:** on a manual, switch-triggered pull, **the pump jumps straight to the shot profile and
skips pre-infusion entirely** — shot targets from t=0, no 2-bar bloom. Triple-confirmed: leva!'s own
Status Monitor plot, my telemetry capture off the port-23 MC stream, and the machine's OLED all show
the same thing.

Worth stating precisely, because it heads off the obvious "your pump just can't hold 2 bar" reading:
I'm not inferring this from measured pressure. I stream `MCr` telemetry (~10 Hz) over TCP 23 and
read the field carrying the profiling setpoint, and at t=0 it already sits at **8.0 bar** with the
tolerance band tracking it. The machine isn't trying and failing to hold 2 bar; it never adopts the
2 bar setpoint at all. (Decode is my own from the MC stream, so I'm happy to be corrected on the
field mapping — raw sample lines available.)

**What I've ruled out:**

- **`Execute PI` is checked** in the Profiles menu (p.126) — I've verified the global toggle is on,
  not just that the segment is programmed. PI is still skipped with it checked.
- **`Drop ends PI` and cup detection can't be the cause** (p.127, p.174) — no scale on this build,
  so there's nothing to detect a first drop or a cup.
- **Config is correct and saved** — the PI segment reads back correctly on the machine and in my
  telemetry; genuinely stored, not a lost edit.
- **Not a "NEXT" skip** (p.129) — no long encoder/button click during the shot, so the segment isn't
  being advanced past by a stray input.
- **Not a units problem** — pump values are in bar, not degrees.
- **Flood isn't discarding the PI setpoint** — flood pressure is set at `<FILL IN>` bar, below the
  2.0 bar PI target, so p.131's "discard setpoints below the flood pressure" doesn't apply.

The one pattern I can't rule out: pre-infusion may only run when the shot is launched as a
**dose-program execution**, rather than a manual pump-switch pull. I can't test that yet — the group
solenoid isn't on the ito's second relay, so I'm still switch-triggering every pull. It's a
hypothesis, not something I've confirmed, and the manual arguably cuts against it: the `End` → STOP
text (p.134) talks about a profile "started by a toggle switch". Which is really what I'm asking:

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

## Corroborating check (optional, post-publication)

The manual (p.153) states the PI and shot **time scales are independent**, with the worked example
that an event defined for the 23rd second of the shot occurs at 29 s in the actual brew when
preinfusion is 6 s. So for this profile a correct run should end at **8 s (PI) + 23 s (shot) = 31
s**, and a PI-skipped run at **23 s**.

⚠️ This only works if the shot timer is counting preinfusion. The Shot Timer menu has
**`Ignore PI`** and **`Ignore flood`** options (p.177); with `Ignore PI` checked, 31 s and 23 s are
indistinguishable. Read those settings first, or time it externally.

## Posting mechanics

home-barista.com sits behind Cloudflare and returns **403 to a headless browser**, so this can't be
posted by automation. Post it by hand, or drive a headed browser with the Cloudflare challenge
solved manually.
