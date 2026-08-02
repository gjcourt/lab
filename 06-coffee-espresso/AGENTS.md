# Coffee & Espresso — Agent Guidelines + Live As-Built State

**Read this first.** The `06-NNN-*.md` files are design/roadmap docs (the plan, the BOM, the full
tuning theory). This file is the **current physical + software state** of the one real build — what
is actually installed and working _right now_ — so an agent (or George) doesn't have to
reverse-engineer "where are we" from a dozen roadmap docs whose checkboxes lag reality.

> **When the build moves, update this file first**, then check the corresponding box in the relevant
> `06-NNN`. If this file and a `06-NNN` disagree, **this file wins** and the `06-NNN` is stale — fix
> it.

_Last updated: 2026-08-02._

---

## The build in one line

**La Spaziale S1 Mini Vivaldi II** (Clive's LUCCA A53 Mini) — **vibratory** pump — with an **ito
V2.0** module running **`leva!`** firmware, interposed on the pump for **pressure/flow profiling
only** (temperature stays on the stock board; PID takeover is deferred → `06-012`).
Monitored/controlled from **Vibrato**, our own clean-room TS app, deployed in the homelab.

---

## As-built hardware state

| Component                              | Status          | Detail                                                                                                                                                                                                                                                                                                                                                     |
| -------------------------------------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ito V2.0 module**                    | ✅ installed    | HLK-PM01 PSU soldered (2026-07-16) → runs on its own clean 5 V off mains. On the IoT VLAN at **`10.42.7.11`**, `leva!` flashed (`1 - ito with rotary encoder`).                                                                                                                                                                                            |
| **Progressive Preinfusion chamber**    | ✅ **removed**  | Was factory-fitted. It's a mechanical hydraulic accumulator that La Spaziale document as incompatible with electronic pre-infusion (saturates → dumps ~6 s of uncontrolled PI mid-profile). Removing it was a prerequisite for clean profiling — done.                                                                                                     |
| **Pressure sensor**                    | ✅ installed    | Mounted **in the vacated factory pre-infusion port** on the left of the group head (**1/8" BSP**, kit G1/8 fitting threads straight in, PTFE-sealed) — reads brew-chamber pressure directly, no tee, no cut plumbing. Wired to the **ADC** header. This matches `06-001`'s updated primary mount (the port; a brew-line T-tap is the documented fallback). |
| **Pump phase-angle control**           | ✅ in place     | Pump driven from ito **Relay 1** (per the M5 wiring doc); controller's pump-on lead moved to **SNS** (zero-cross + "pump on"). Profiled shots have been pulled and traced on Vibrato, so the closed loop is live.                                                                                                                                          |
| **Flow meter**                         | ⏳ pending      | Permanent path = stock **GICAR** meter → CD4011 buffer → `IMPULSE`, via the **`06-015` interposer PCB (in fab)**. Interim option = kit **Digmesa** straight into `IMPULSE` (5 V, no buffer). **Pressure profiling does not need flow** (leva! profiles on pressure; flow only feeds readout + `Flow Corr`), so this doesn't block the PI work.             |
| **Over-pressure bypass / `PRESS OPV`** | ⚠️ verify       | Set the machine bypass to crack just above 9 bar and configure `PRESS OPV`, or it fights the profile and biases flow. Confirm current setting before trusting a plateau.                                                                                                                                                                                   |
| **Display / encoder + housing**        | ➖ optional     | `leva!` runs headless over WiFi, so a mounted OLED isn't required. PETG external housing is a `06-001` nicety, not a blocker.                                                                                                                                                                                                                              |
| **Temperature / PID**                  | 🚫 out of scope | Stock board retains all temperature control. leva! PID conflicts with the A53 board → deferred to `06-012`.                                                                                                                                                                                                                                                |

---

## Software / homelab state

- **Vibrato** (`github.com/gjcourt/vibrato`) — our clean-room TS re-implementation of the leva!
  client (design:
  [`_reference/leva-controller-clean-room-design.md`](_reference/leva-controller-clean-room-design.md)).
  Speaks the firmware's **port-23 "MC" protocol** (`MCr` → ~10 Hz rich telemetry frames).
  - **Deployed:** `vibrato-prod` (+ `vibrato-stage`) namespaces, Flux-reconciled. Prod runs image
    `ghcr.io/gjcourt/vibrato:5b02c77` (= PR **#66**, two-column Brew layout, un-clipped chart).
  - **Wired to the machine:** `LEVA_HOST=10.42.7.11:23`, `LEVA_NODE_ID=espresso`, MQTT bridge →
    `mosquitto` → Home Assistant. History/profiles on a `/data` PVC.
- **Status Monitor** (vendor Java app) — kept only as the generic-firmware fallback; nothing it does
  is functionally unique on a leva! machine.

---

## Current focus: get pre-infusion to execute, and capture it on the Vibrato chart

The hardware is ready and Vibrato is live. The device **has** a PI step programmed — "Profile 1"
(dark decline) is **PI 8 s @ 2.0 bar → shot 2 s @ 8.0 bar → 23 s @ 4.0 bar**, entered in bar
(closed-loop pressure, not phase-angle degrees). The open problem: **on a manual, switch-triggered
pull the pump jumps straight to the shot curve and skips pre-infusion** (shot targets from t=0, no
2-bar bloom). Triple-confirmed — leva!'s Status Monitor, the port-23 MC telemetry, and the OLED all
agree.

**⚠️ Tooling gotcha — `/api/profiles` is NOT the machine.** It reads Vibrato's **local profile
store** (`data/profiles/<slot>.json`). Vibrato pushes profiles one way (editor → machine via
`write-to-machine`) and does **not** import PI/shot step definitions back from the device, so an
empty `pi: []` there says nothing about the machine. Read the device directly — a raw **`MCu` setup
dump** over port 23 — to see what's actually programmed. (The 2026-08-02 shot trace corroborates the
skip independently: `pressureTargetBar` — decoded from the machine's own rich-telemetry setpoint
column, not the store — **began at 8 bar with no 2-bar PI plateau**.)

**Leading hypothesis (from the #74 bug record):** PI may only run when the shot is launched as a
**dose-program execution (`MCcDOSE`)**, not a manual pump-switch pull — untestable until **Relay 2
(the group solenoid) is wired** (see `_reference/mini-v2-e2-group-solenoid-relay2.md`, landing on
the `docs/e2-group-solenoid-relay2` branch); every pull to date has been switch-triggered free-pour.

**Already ruled out — do NOT re-chase (per the #74 record):** the PI segment is stored and reads
back correctly on the machine; it is **not disabled** (it's an active segment); it's not a stray
"NEXT" segment-skip; not a units error (values are bar, not degrees); **not the ~0.7 bar
boiler-fill/flood confound** (leva! gates fill separately); and Execute-shot-off gives the same
result. So this is **not** a missing definition, a disabled/Execute-PI toggle, or flood masking.

**Interim workaround being tested:** fold the bloom into the shot segment itself (e.g.
`1 s @ 2 bar → 8 s @ 2 bar → 11 s @ 8 bar → 32 s @ 3 bar`) so pre-infusion happens inside the shot
curve rather than as a separate PI phase.

**Full bug record + Home Barista draft:**
[`_reference/ito-preinfusion-forum-draft.md`](_reference/ito-preinfusion-forum-draft.md) (lab #74).

---

## Open items (not yet done)

- Fabricate + fit the **`06-015` GICAR flow-tap interposer**; swap off the interim Digmesa; **re-set
  the flow K-factor** after the swap (Digmesa and GICAR have different pulses/L).
- **Tune** the pressure loop against Vibrato plots: `K`/`I` per band (esp. the sub-2.5 bar PI band),
  `Flow Corr`, `PHASE OFF`. Defaults won't produce good shots "except by luck."
- Verify the **bypass valve** cracking pressure + `PRESS OPV`.
- Design/print the **PETG display housing** (optional).
- Once dialed: **document the as-built profile** (sensor location ✓, tuned params, chosen curve).

---

## Where the detail lives

| Doc                                                                                                  | What it holds                                                                                  |
| ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| [`06-001`](06-001-lucca-a53-mini-leva-firmware-integration.md)                                       | **Master profiling project** — BOM, build sequence, the A53 wrinkles, full tuning theory.      |
| [`06-011`](06-011-mini-v2-direct-plumb-in.md)                                                        | Direct plumb-in (float-fill); shares the machine-open teardown with the pump tap.              |
| [`06-015`](06-015-gicar-flow-tap-interposer.md)                                                      | GICAR flow-tap interposer PCB (the permanent flow path).                                       |
| [`06-012`](06-012-leva-pid-temperature-takeover.md)                                                  | PID temperature takeover — deferred (conflicts with the A53 stock board).                      |
| [`_reference/leva-controller-clean-room-design.md`](_reference/leva-controller-clean-room-design.md) | Vibrato's design record — protocol surface, domain model, ports/adapters, deploy.              |
| [`_reference/leva/LEVA-DOCS-SUMMARY.md`](_reference/leva/LEVA-DOCS-SUMMARY.md)                       | Firmware digest — profile model, the PI-with-bias controller, tuning workflow, param glossary. |
| [`_reference/ito-integration-walkthrough.md`](_reference/ito-integration-walkthrough.md)             | Bench → integrated roadmap.                                                                    |
| [`_reference/ito-preinfusion-forum-draft.md`](_reference/ito-preinfusion-forum-draft.md)             | The PI-skip bug record + Home Barista forum draft.                                             |
| [`_reference/mini-v2-control-board-wiring.md`](_reference/mini-v2-control-board-wiring.md)           | Authoritative M5 terminal map (which tab is pump / phase / neutral).                           |

---

## Repo conventions (this category)

- One project per `06-NNN-slug.md`; index in [`projects.md`](projects.md). Root repo guidance:
  [`../AGENTS.md`](../AGENTS.md).
- Public repo — **no secrets** (WiFi creds, keystores, IPs beyond the already-published `10.42.7.x`
  IoT bench address stay in NAS notes, not here).
- Changes go through a **branch + PR** (never commit to `main`).
