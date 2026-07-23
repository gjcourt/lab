# Interposition Step E2 — Group Solenoid → `leva!` Relay 2

**Plan for a future bench session.** Hands the **group / brew solenoid (EV.GR)** to the ito board's
**on-board Relay 2**, so `leva!` controls **both** halves of a shot — pump _and_ valve — and a shot
can be **started and stopped by `leva!`** (app-brew / `MCcDOSE`, a Vibrato Start/Stop toggle), not
just by the physical button.

This is the follow-on to **E1 (pump interposition)**, which is **DONE** — the machine is
commissioned and pulling profiled shots, but brew is **physical-button-only** because the group
solenoid is still driven by the stock board. Nothing here has been executed. Do not touch the
machine off this doc alone — it is a sequenced plan, not a build log.

**Machine:** La Spaziale S1 Mini Vivaldi II (Clive's LUCCA A53 Mini) — vibratory pump, dual boiler,
**volumetric** dosing off the stock GICAR flow meter. **Board:** ito V2.0 running `leva!` 3.1.

**Ground-truth references (cite, don't re-derive):**

- [`ito-integration-walkthrough.md`](ito-integration-walkthrough.md) — the sequenced install plan;
  **step E2** is exactly this task ("move the group solenoid feed onto `SSR 2` to unlock
  dosing/backflush/shot-control — hands the valve to ito. Deferred until profiling is stable").
- [`mini-v2-control-board-wiring.md`](mini-v2-control-board-wiring.md) — the **M5 terminal map** and
  the **no-switched-rail** gotcha.
- [`ito-manual-summary.md`](ito-manual-summary.md) — the ito board: on-board **Relays 1 & 2** both
  output the **L phase**, 1 A / 240 W, FASTON leads.
- [`../06-001-lucca-a53-mini-leva-firmware-integration.md`](../06-001-lucca-a53-mini-leva-firmware-integration.md)
  — core project; the step-3 E2 note ("move the group solenoid (`1`/EV.GR) onto `Relay 2` … this
  hands the valve to ito; dosing stays off until you do it").

> ⚠️ **Mains voltage — no switched rail.** The soft-touch pad only toggles ON ⇄ Standby; it is
> **not** a mains switch. `F`/PHASE and `N` are **live the entire time the machine is plugged in**
> (metered 120 VAC to GND even in standby). **Unplug at the wall** before opening; let both boilers
> cool and depressurize. Qualified-electrician territory — measure, don't assume.

---

## 1. Why E2 — the "two things must happen together" model

Pulling a shot on this machine is **two** simultaneous actions:

1. **Run the pump** — push water toward the group.
2. **Open the 3-way group valve (EV.GR)** — give that water a path through the puck; when it closes
   it also vents the group to the drip tray so the puck depressurises.

Run the pump with the valve shut and nothing brews — the pump just dead-heads into a closed 3-way
until the over-pressure bypass cracks. Open the valve with no pump and nothing brews either. **Both
have to be true at once**, and they have to _stop_ together too.

**Where E1 left us.** E1 handed `leva!` only the **pump** (`Relay 1`). The **valve is still on the
stock board** (M5 EV.GR). So today:

| Trigger             | Pump                                                                | Valve (EV.GR)                                                          | Result                                        |
| ------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------- | --------------------------------------------- |
| **Physical button** | stock board asserts pump command → `SNS` → `leva!` drives `Relay 1` | **stock board opens EV.GR directly**                                   | ✅ real shot (pump + valve both fire)         |
| **App / `MCcDOSE`** | `leva!` drives `Relay 1`                                            | **stays shut** — no button press, so the stock board never opens EV.GR | ❌ pump spins against a closed valve, no shot |

That asymmetry is the whole reason app-brew doesn't work yet. `leva!` can _start_ the pump but can't
_open the valve_, so `MCcDOSE` (Vibrato Control → Dose) would just churn the pump into a shut group.

**What E2 changes.** Relocate the EV.GR feed onto **Relay 2**. Now `leva!` owns both outputs and
fires them together as one brew:

- `MCcDOSE` / a Vibrato **Start/Stop** toggle → `leva!` closes **Relay 1 (pump) + Relay 2 (valve)**
  together → a real, app-initiated shot; **Stop** → opens both → pump off, valve vents.
- The physical button still works (§4) — it just reaches the valve _through_ `leva!` now instead of
  directly.

---

## 2. The wiring — one 1:1 faston relocation

E2 is **simpler than E1**: the valve needs no zero-cross / phase-angle sense, so there is **no
SNS-side wire** — just move the solenoid's hot lead from the stock output to `leva!`'s relay output.
It mirrors the pump relocation E1 already did (the "one 1:1 relocation" pattern), and it is **fully
reversible** — both ends are 6.3 mm push-on fastons; re-seat the original plug to undo.

### The terminals involved

| Where              | Terminal                 | Board mark | Function                                            | Notes                                                                                         |
| ------------------ | ------------------------ | ---------- | --------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Stock board M5** | pos 4 · **EV.GR**        | `1`        | Group / brew solenoid — **switched-L output**       | Today this drives the solenoid coil's hot lead. E2 frees it.                                  |
| **Stock board M5** | pos 6 / 7 · **NEUTRAL**  | _(white)_  | Neutral                                             | The solenoid coil's **other** lead stays here — do not move it.                               |
| **ito clamp**      | **`2`** · Relay 2 output | —          | Switched **L phase** (on when `leva!` energises it) | New home for the solenoid's hot lead. OMRON 1 A / 240 W SSR, instant-on.                      |
| **ito clamp**      | **`L`**                  | —          | ito power-in / relay-source phase = machine **`F`** | Already landed in E1 (via the Fase splitter). Relay 2 sources L from here — no new mains tap. |

Earth stays on the separate ground stud (yellow ⏚), untouched.

### The move

The 3-way solenoid coil has **two leads**: a **hot** lead (today on M5 EV.GR, mark `1`) and a
**neutral** lead (on an M5 Neutral tab).

1. **Unplug the solenoid's hot lead** at the M5 **EV.GR (`1`)** tab — or at the solenoid, whichever
   faston is cleaner to reach. This is the same push-on-plug bank as the pump (plastic ID markers
   `A` / `2` / `1` / `F`; EV.GR = **`1`**). No cut.
2. **Land that hot lead on ito `Relay 2` output (clamp `2`)** via a **6.3 mm pigtail** (male into
   the solenoid lead / female onto clamp `2`, matching whatever E1 used for the pump). Relay 2
   outputs the switched **L** phase; ito already sources that L from machine `F` (the E1 Fase
   splitter) — **no new F/N tap is needed for E2.**
3. **Leave the solenoid's neutral lead on its M5 Neutral tab.** Unchanged.
4. **Cap / insulate the freed stock EV.GR (`1`) tab** — the stock board will still _try_ to assert
   it on a physical brew (see §3); it now drives nothing, so isolate it so it can't touch anything.

> **Do not disturb the E1 pump wiring** (PUMP_M → `SNS`, `Relay 1` → PUMP_F) or the **Fase / Neutral
> splitters**. E2 touches only the EV.GR lead and clamp `2`.

**Polarity is already correct.** ito's on-board relays 1 & 2 _both_ output the **L** phase and `SNS`
senses **L**; E1 already set the N/L order so that clamp `1` (pump) outputs L cleanly. Relay 2 draws
the same L — no re-polarising, no short risk introduced, as long as the solenoid's _other_ lead is
on **N** (it already is).

**Inductive-load note (verify at bench).** The solenoid coil is an inductive load on an SSR, same as
the pump on Relay 1 (which works fine). If Relay 2 chatters or the SSR runs hot, fit an **RC snubber
or a MOV across the coil**. Treat as a watch-item, not a required part.

---

## 3. How the stock board reacts — decision + the open question

**Decision: E2 fully hands the valve to `leva!`.** After E2 the solenoid coil is driven **only** by
Relay 2. The stock board's EV.GR output becomes a **dead tab** — it still gets asserted during a
physical brew, but it drives an open circuit (capped in §2 step 4).

**What still needs to reach `leva!` on a physical brew.** The physical button asserts the **pump
command**, which E1 routes to `SNS` ("pump on / brew requested"). `leva!` runs the brew off that
sense — pump on `Relay 1`. **The design intent of E2 is that `leva!` opens the valve (`Relay 2`) as
part of that same brew**, tied to the pump/brew state, so a physical shot still gets its valve. That
depends on `leva!` being configured to drive the 3-way valve together with the pump (§4).

### Open questions — verify at the bench (do **not** skip)

1. **Does `leva!` auto-open `Relay 2` with the pump on a physical-button brew?** This is the load-
   bearing unknown. If `leva!`'s brew logic drives the assigned valve output whenever it brews (SNS
   "pump on"), the physical button keeps working end-to-end. If it does **not** — if the valve only
   opens on `MCcDOSE` / an app command — then physical-button brews would run the pump with the
   valve shut (regression). **Confirm the valve-follows-pump behaviour before capping the stock
   tab.** Fallback if it doesn't: leave EV.GR on the stock board (revert E2) and drive brew only
   from the app, or feed the stock EV.GR command into a second `leva!` sense contact.
2. **Does an unloaded stock EV.GR output fault the stock board?** The board will still assert EV.GR
   on a physical brew, now into an open circuit. Confirm the stock controller **tolerates the
   unloaded output** — no error, no dosing lockout. (SSR/triac outputs usually don't care about an
   open load, but verify.)
3. **Does relocating EV.GR confuse stock volumetric dosing?** The stock board doses by counting its
   own **GICAR** pulses and dropping the **pump command** at target volume — it does _not_ need to
   see the valve to count. On a physical shot, the volumetric stop still fires: pump command drops →
   `SNS` drops → `leva!` stops pump **and** closes `Relay 2`. So volumetric behaviour _should_
   survive for physical-button shots. **Confirm the shot still stops at the programmed volume**
   after E2.
4. **`MCcDOSE` stop condition.** App-brew fires `leva!` directly, **not** through the stock button,
   so the stock volumetric counter never runs. Flow is **not** wired to `leva!` yet (pressure-only
   phase; flow deferred to the `06-015` GICAR interposer). So `MCcDOSE` will run on `leva!`'s own
   Dose logic (timer) or open-ended until **Stop** — it will **not** volumetrically auto-stop until
   flow is integrated. Expect to stop app-brews by the Vibrato toggle / scale for now.

---

## 4. `leva!` configuration

E1's precedent: the pump only triggered once **Setup → Contacts → SNS signal = PUMP** was set (input
assignment). E2 is the **output** side — assign the **group / 3-way valve function to Relay 2**.

**Where to look (bench-verify the exact path — the MCu config dump has these sections):**

- **`Setup → Pump`** — `leva!` models the 3-way/group valve alongside the pump; the valve-open
  output is most likely assigned here (valve follows the pump/brew state).
- **`Setup → Contacts`** — output/relay function assignment (this is where E1's `SNS = PUMP` lives;
  the relay-output side may map here too).
- Look for a **"Valve" / "3-way" / "Group" / "Relay 2"** function to point at **on-board Relay 2**.

**This assignment is not yet confirmed on-device — treat it as a bench-verify step:**

1. Dump the live config first (`MCh` primer → `MCu`, or Vibrato's read-only **Settings** tab) and
   locate the valve/relay-output assignment.
2. Assign the **group / 3-way valve output → Relay 2**.
3. Confirm **valve-follows-pump** on a physical brew (open question §3-1).
4. Ensure **Auto save** is ON (`/`) so the assignment persists (per the E1 config gotchas — settings
   can be lost if Auto save is off).

If no explicit valve→relay assignment exists (i.e. `leva!` hard-wires the 3-way to Relay 2 by
convention), that itself is the finding — record it. Either way, **do not blind-navigate the menu**:
`Factory reset` / `Restart Wifi` / `Update FW` are top-level scroll items; drive the pad by sight or
via a confirmed path.

---

## 5. Safety

- **Unplug at the wall.** No switched rail — `F`/PHASE is live (120 VAC) whenever the machine is
  plugged in, ON or Standby. The pad is logic-only.
- Let **both boilers cool and depressurise** before opening.
- **Qualified-electrician framing** (consistent with the other docs): the solenoid coil is a mains
  load; ito relays output the **L** phase at ≤ 1 A / 240 W. The coil is small and well inside that
  rating. Never wire a relay output to **N** (destructive short).
- **Do not disturb the E1 pump wiring or the F/N splitters.** E2 touches only the EV.GR lead and
  clamp `2`.
- **Phantom voltage:** the freed, capped EV.GR tab (and any unconnected tab next to live wiring)
  will read tens of volts on a high-impedance meter — capacitive coupling, not a real source.
  Confirm with a LoZ meter / under load. Insulate it regardless.
- **Reversible:** pull the pigtail off clamp `2`, re-seat the solenoid's hot lead on M5 EV.GR (`1`),
  un-cap — back to the E1 (pump-only) state.

---

## 6. Verification (after E2)

Bench-verify all of the following:

1. **App-brew works.** `MCcDOSE` (Vibrato **Control → Dose**) pulls a **real shot** — pump runs
   **and** the group valve opens together; water reaches the cup.
2. **A Vibrato Start/Stop toggle works.** Start fires the brew (Relay 1 + Relay 2 via `MCcDOSE`);
   **Stop** closes Relay 2 / stops the pump; the group **vents** (puck depressurises, no dribble).
3. **The physical button still works** — pump **and** valve fire on a button press (confirms
   valve-follows-pump, open question §3-1).
4. **Stock volumetric behaviour is unaffected** on physical-button shots — the shot still stops at
   the programmed volume (open question §3-3). _Caveat:_ app-brews (`MCcDOSE`) do **not**
   volumetrically auto-stop yet (no flow to `leva!` — §3-4); stop by toggle/scale until the `06-015`
   flow interposer lands.
5. **No stock-board fault** from the unloaded EV.GR output (open question §3-2).
6. **Valve seals / vents cleanly** — no weeping at the 3-way, full depressurisation on stop, no
   leaks after a session of shots.

---

## 7. Follow-on software (Vibrato)

Once E2 lands, **re-introduce a Brew-tab Start/Stop toggle** in Vibrato:

- **Start** = fire the brew via `MCcDOSE` (Relay 1 + Relay 2 together).
- **Stop** = stop / close Relay 2.

This was **deliberately deferred** in the Brew/Control polish PR — **Vibrato PR #37** _removed the
misleading "Start Shot" control precisely because you "can't brew w/o E2 valve."_ E2 is the hardware
gate that unblocks it. Cross-reference that PR when re-adding the toggle. See
[[project_leva_controller]] (the Vibrato app) and [[project_espresso_profiling]] (the machine) for
current state.

Sequencing note: `MCcDOSE` app-brews stop on `leva!`'s own logic / the toggle until **flow is wired
to `leva!`** (the `06-015` GICAR flow-tap interposer, PCBs shipped 2026-07-22). Volumetric app-brew
auto-stop is a _later_ pass, not part of E2.

---

## Sources

- `ito-integration-walkthrough.md` §3 Phase E, step **E2** (this task).
- `mini-v2-control-board-wiring.md` — M5 map (**EV.GR = pos 4, mark `1`**), no-switched-rail gotcha,
  load-identification-by-meter table.
- `ito-manual-summary.md` §4 (mains clamps `SNS N L 1 2`; on-board relays 1 & 2 output L phase, 1 A
  / 240 W, instant-on) and §11 specs.
- `06-001-lucca-a53-mini-leva-firmware-integration.md` step 3 (E1 pump relocation + the E2 note).
- Memory: `project_espresso_profiling.md` (E1 DONE — PUMP_M→SNS, Relay1→PUMP_F, F/N splitters;
  commissioned, brew physical-button-only), `project_leva_controller.md` (control surface `MCcDOSE`;
  Vibrato PR #37 dropped "Start Shot").
