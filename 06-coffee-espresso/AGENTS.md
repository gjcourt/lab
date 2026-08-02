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

| Component                              | Status          | Detail                                                                                                                                                                                                                                                                                                                                               |
| -------------------------------------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ito V2.0 module**                    | ✅ installed    | HLK-PM01 PSU soldered (2026-07-16) → runs on its own clean 5 V off mains. On the IoT VLAN at **`10.42.7.11`**, `leva!` flashed (`1 - ito with rotary encoder`).                                                                                                                                                                                      |
| **Progressive Preinfusion chamber**    | ✅ **removed**  | Was factory-fitted. It's a mechanical hydraulic accumulator that La Spaziale document as incompatible with electronic pre-infusion (saturates → dumps ~6 s of uncontrolled PI mid-profile). Removing it was a prerequisite for clean profiling — done.                                                                                               |
| **Pressure sensor**                    | ✅ installed    | Mounted **in the vacated factory pre-infusion port** on the left of the group head (**1/8" BSP**, kit G1/8 fitting threads straight in, PTFE-sealed) — reads brew-chamber pressure directly, no tee, no cut plumbing. Wired to the **ADC** header. This replaces the old "T-tap into the brew line" plan in `06-001` — the port is the better mount. |
| **Pump phase-angle control**           | ✅ in place     | Pump driven from ito **Relay 1 / SSR 1**; controller's pump-on lead moved to **SNS** (zero-cross + "pump on"). Profiled shots have been pulled and traced on Vibrato, so the closed loop is live.                                                                                                                                                    |
| **Flow meter**                         | ⏳ pending      | Permanent path = stock **GICAR** meter → CD4011 buffer → `IMPULSE`, via the **`06-015` interposer PCB (in fab)**. Interim option = kit **Digmesa** straight into `IMPULSE` (5 V, no buffer). **Pressure profiling does not need flow** (leva! profiles on pressure; flow only feeds readout + `Flow Corr`), so this doesn't block the PI work.       |
| **Over-pressure bypass / `PRESS OPV`** | ⚠️ verify       | Set the machine bypass to crack just above 9 bar and configure `PRESS OPV`, or it fights the profile and biases flow. Confirm current setting before trusting a plateau.                                                                                                                                                                             |
| **Display / encoder + housing**        | ➖ optional     | `leva!` runs headless over WiFi, so a mounted OLED isn't required. PETG external housing is a `06-001` nicety, not a blocker.                                                                                                                                                                                                                        |
| **Temperature / PID**                  | 🚫 out of scope | Stock board retains all temperature control. leva! PID conflicts with the A53 board → deferred to `06-012`.                                                                                                                                                                                                                                          |

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

The hardware is ready and Vibrato is live. The device is believed to have a PI step programmed; the
open problem is that PI **does not execute** on a pull.

**⚠️ Tooling gotcha — `/api/profiles` is NOT the machine.** It reads Vibrato's **local profile
store** (`data/profiles/<slot>.json`). Vibrato pushes profiles one way (editor → machine via
`write-to-machine`, "edits existing points in place only") and does **not** import PI/shot step
definitions back from the device. So an empty `pi: []` there means "Vibrato's store has no steps,"
**not** "the ito has none." To see what's actually programmed on the machine, read it directly — a
raw **`MCu` setup dump** over port 23 — never infer the device's profile from `/api/profiles`.

**What DID run is answered by the shot trace, not the store.** The trace's `pressureTargetBar` /
`pressureMinBar` / `pressureMaxBar` are decoded from **fixed-width columns of the machine's rich
telemetry frame** (the firmware's own reported setpoint + tolerance band, live during the shot). On
the 2026-08-02 shot (`id 1785699032614`, "Dark", peak 7.8 bar) that setpoint **began at 8 bar with
the pump full-power (0°) straight to peak — no sub-2.5 bar plateau → PI did not execute**, even
though the device likely has a PI step defined.

So the gap is PI **execution**, not definition. Suspects, to check next time it's online:

1. **Global `Profiles → Execute PI` toggle** — machine-global, _not_ in any Vibrato read; the #74
   root cause. Eyeball it on the machine.
2. **PI/shot phase overlap** — the other #74 cause.
3. **Flood masking PI** — `floodEnabled` was true and the pump flooded straight to 8 bar. If the
   flood target sits **≥ the PI pressure**, the fill phase swallows the low PI plateau and it never
   shows. Compare flood pressure vs PI pressure.

**Next online session:** (a) `MCu`-dump the device's real profile and confirm the PI step + step
values; (b) confirm the global Execute PI toggle is ON; (c) check flood-vs-PI pressures; (d) pull a
shot and re-check the **trace setpoint** for a sub-2.5 bar opening plateau (the un-clipped chart
will show it). A sane PI to aim for: **~10 s @ 1.5 bar** (`Gen Lever` recipe; phase-angle PI is
capped ~1 bar).

**PI-skip history:** the earlier "PI never executes" saga is recorded in
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
