# Shot Feedback Loop (+ Machine Control) — Scope → Gravimetric → Temperature → On/off

> **Cross-repo roadmap.** Strategic plan for the A53 shot-feedback program. **Phases 1–2** (and
> Phase 3's Vibrato data-model work) are **Vibrato software** — implemented in the `vibrato`
> monorepo; the paths in the [Files](#files) section are vibrato, not this repo. **Phase 3 hardware
> taps** and **Phase 4 machine control** are lab hardware projects:
> [06-010](../06-010-grouphead-temperature-sensor.md) (grouphead temp),
> [06-016](../06-016-a53-control-board-reverse-engineering.md) (bench-board RE),
> [06-017](../06-017-a53-hass-onoff-interposer.md) (HASS on/off interposer). Kept here to
> consolidate the A53 espresso program in one taxonomy; the ito+leva! app itself is
> [06-001](../06-001-lucca-a53-mini-leva-firmware-integration.md).

## Context

Vibrato can monitor machine state, walk menus, and fire direct commands, but it shows **no live
numbers** — the Brew tab's oscilloscope renders a target curve over empty traces. The reason is
narrow: `parseRichFrame` (`packages/core/src/protocol/frames.ts`) decodes only `state` (and the
event marker); the byte offsets for pressure/flow/temp/weight/volume were never pinned because the
**bench ito has no sensors** (every field read `?`). Until that's fixed, Vibrato isn't actually
useful for pulling shots.

Two facts make this the moment to close the gap:

1. The **pressure sensor arrives Wednesday** and profiling gets wired into the machine — so a real
   sensored capture becomes possible for the first time.
2. **MV2 is volumetric** — it stops a shot at one of two flowmeter-counted preset _volumes_
   (programmed by pulling a shot). Its shot-to-shot **water-output variance is low but
   significant**, and because it stops at volume (not mass), the _yield weight_ varies more than the
   volume does (puck resistance, grind, and channelling all move the volume→weight relationship).
   That variance is precisely what a feedback loop targets: the **live scope quantifies it**, and
   **gravimetric (stop-at-weight) fixes it**.

**George's current workaround (the thing to automate):** set the **second volumetric preset "long"
(1 min+)** so it never self-terminates, then **cut the shot by hand on a scale** at target weight.
That is manual gravimetric — the machine is already running in "pour until told to stop" mode. **The
real fix is native:** leva! itself has a weight-stop (Phase 2) that cuts the shot at mass with zero
network latency — better than any app-side or hand cut. Automating the cut _from Vibrato_ (read the
scale → send the stop, beating a ~300–500 ms human reaction) is the **fallback** for if native can't
drive MV2's termination — still an improvement, but second choice.

Outcome: a working shot feedback loop — **target profile → live actual (pressure/flow/temp/weight) →
shot record with taste rating → the data to tune**, and a concrete fix for MV2's volumetric
variance.

Good news from the code: the model and the UI are already built for this. The `Telemetry` interface
(`model.ts:24`) already carries every field, and `brew.js` + `chart.js` already push
`t.pressureBar`/`t.flowGs`/… into series and draw them. **Pinning the offsets lights up the existing
scope.** So Phase 1 is mostly a protocol/capture task, not a UI build.

---

## Phase 1 — Live Scope (pin the numeric offsets)

### 1a. On-machine sensored capture (George-gated)

Capture real rich frames while the sensors are live and correlate byte columns to known values. Add
a capture mode that timestamps and dumps raw `{…~NN}` frames alongside a reference signal:

- Run the CLI/server against the **installed machine** (`LEVA_TRANSPORT=tcp`,
  `LEVA_HOST=<machine ito>`), `MCr` rich mode.
- **Isolate fields ONE AT A TIME with static inputs** — during a real pull, pressure, flow, weight
  and volume all rise together, so you can't tell their columns apart. Instead move each field
  _alone_ against everything else static: put **known masses on the scale** with no shot running
  (pins `weightG`); change **setpoint** alone (pins `setpointC`); let the boiler drift to read temp;
  trickle water to a **known volume** with the group cool (flow/volume). Reserve full pulls for
  _cross-checking_ the finished map, not for pinning it.
- **Log a synchronized reference, not eyeballed timestamps** — have the harness stamp each raw frame
  and, where possible, fold the reference value (scale reading, entered setpoint) into the same log,
  so column↔value alignment isn't a manual guess that one mis-aligned reading can corrupt.
- Harness: extend `@leva/cli` (or a small `scripts/capture-shot.mjs`) to log `ts,rawframe` (+ any
  reference readings) to a file; keep the existing lossless raw-sink pattern from
  `ConnectionService.dumpSetup`.

### 1b. Pin offsets + decode (core)

Fill the offset map in `parseRichFrame` (`frames.ts`, the `TODO(protocol)` at ~:227):

- Replace the best-effort state regex with fixed-offset slices for
  `pressureBar / flowGs / flowMlS / volumeMl / weightG / tempC / setpointC / timerS` (only the
  fields the frame actually carries — some may stay absent on MV2). Keep the existing `event`-marker
  decode.
- **Key the offset map by firmware id.** `frames.ts:11-12` warns offsets are
  firmware-version-specific; the bench is `leva!-65D751CF`, the installed machine will report a
  different id, and the frame layout may differ. Store offsets per-firmware; on an **unrecognised
  id, or a frame whose length/checksum/shape doesn't match the pinned layout, decode NOTHING**
  (surface a "needs recapture" state) rather than emit numbers from an unverified layout.
- Keep `parseKeyValue` as the sim/test path (unchanged). Decode `?` → field absent.
- **Tests** (`frames.test.ts`): add real captured frames as fixtures and assert each numeric field
  decodes; a deliberately-wrong offset must fail a test. A wrong offset silently shows
  plausible-but-wrong numbers on the scope/history.
- **Accuracy gate for the _displayed_ telemetry.** Before the scope/history are trusted, validate
  the decoded columns against a reference (weight within, say, ±0.2 g on known masses; setpoint vs
  the value you entered). Note this is **display hygiene, not an actuation guard**: the decoded
  frame never actuates — Path A/C stop _inside_ leva! (it reads the scale over its own BLE), and
  Path B's `ShotController` triggers off the **MQTT `ScaleSource`** weight, not `parseRichFrame`.
  The actuating signal is validated where it's produced (§Path B), separately from this.

### 1c. Repoint to the real machine (deploy)

`LEVA_HOST` currently points at the sensorless bench `10.42.7.11`
(`homelab apps/base/vibrato/deployment.yaml`, "repoint later" TODO). Point prod at the installed
machine's ito once it's on the network; keep staging on `sim`.

### 1d. Scope polish + per-shot capture (UI, mostly wiring)

The traces render as soon as 1b lands. Then:

- **Shot detection** — bound a shot (state → pulling/brewing, or flow > 0) to auto-start a trace and
  auto-save the actual curve + peak pressure + final volume/weight/ratio to History on stop
  (`history.js` / the existing `/history` POST from `brew.js`).
- **Variance view** — overlay the last N shots' actual curves (History already stores them) so the
  volumetric weight spread is _visible_ — this is the MV2-variance readout that justifies
  gravimetric.

**Phase 1 exit:** live pressure/flow/temp (and weight if a supported scale is paired) plot against
the target in real time; shots auto-log with their real curve; the shot-to-shot variance is
measurable on screen.

---

## Phase 2 — Gravimetric (native stop-at-weight — the scale + whether it drives MV2 are the open questions)

**The config dump shows the ito is _configured_ for native gravimetric** (this is the config
surface, not proof it actually cuts MV2's shot — see the open question at the end of this phase).
Pending that, the scale is the main open choice:

- **BLE card present + on** (`Bluetooth /`).
- **Scale menu SCANS** (`Scan` / `Unpair` / `Disconnect`) with per-model config for **Skale 2 /
  Felicita Arc / Eureka** (no `DiFluid` on this unit — DiFluid is a leva! 3.2+ addition and the
  bench runs ~3.1). **How pairing _binds_ — by advertised name/type or by a bonded MAC — is NOT
  shown in the dump**; that's an open question that gates the shim (Path C), not an established
  fact.
- **Native weight-stop**: a **fixed `Stop early 0.5g`** mass offset (a constant, _not_
  flow-compensated), `Tare 1/2`, weight `Filter`, and a dose **`Method: WEIGHT`**. The firmware cuts
  the shot at mass itself with zero network hop — tighter than any app-side cut.

This **demotes the app-side auto-stop** (my earlier "centerpiece") to a fallback: native is strictly
better. The interesting work moves to the scale link.

### Path A (primary) — a natively-supported scale

Pair a supported scale via **Scale → Scan**, set the dose **Method: WEIGHT** (+ `Stop early`). leva!
stops at mass natively; `weightG` also rides in the rich frame (Phase 1's offset), so Vibrato just
**surfaces** live weight / flow-rate / ratio on the scope and exposes the config. Minimal Vibrato
code.

**Which scale (this firmware):** the dump lists **Skale 2 / Felicita Arc / Eureka** only. Of those,
**Felicita Arc** (~$110) is the best in-stock native pick — Skale 2 is discontinued, Eureka is
micro-USB and dated. **DiFluid Microbalance** (~$89, USB-C, modern) is native only on **leva!
3.2+**, so it's the better buy _if_ you upgrade the firmware first.

### Path C (the interesting problem) — an unsupported scale via a BLE translation shim

Make an _unsupported_ scale look like a supported one to leva!, so it gets the **same native
weight-stop**. **Plausible, but the load-bearing assumption is UNVERIFIED:** leva! clearly _scans_
(the `Scan` menu + per-model submenus), but the dump says nothing about how it _binds_ a scale — by
advertised name/type, or by a bonded MAC after first pair. If it's name/type, a spoofed peripheral
pairs like a real one and this whole path works; if it bonds a MAC, the shim is harder (clone the
MAC, or pair once from the target). **Verify this first** (§Risks) — it gates everything below.

- **Architecture** — an **ESP32 running dual-role BLE**: _central_ to the real scale (read its
  weight; relay any tare/timer command leva! issues back down to it) and _peripheral_
  **impersonating a supported scale** (advertise that scale's name plus GATT service/chars, push
  weight notifications in its byte format at ~100 ms) to the leva! BLE card. A protocol translator,
  ~one device.
- **Emit target — impersonate Skale 2.** Its protocol is **fully published** (Atomax/Decent released
  it: weight on `0000EF81-…`, commands on `0000EF80-…`, tare `0x10`) and it's near one-way
  (weight-notify + `Auto-tare FW`) — the cleanest thing to emulate. Felicita Arc is richer (leva!
  also drives `Auto-tare FW/S`, `Mode idle/shots`, `Sync timer`, `Buzzer`) AND its protocol is only
  reverse-engineered ("try-and-error"), so it's a _worse_ emit target than my earlier note implied.
- **Source scale — read a Bookoo Themis Mini** (~$111). It has a **published open protocol** and is
  already implemented in **`kstam/esp-arduino-ble-scales`** (the ESP32 lib GaggiMate builds on) — so
  you _read_ it with proven code rather than sniffing. That library is effectively the shim's
  reference implementation.
- **So the RE burden is small** — compose two _documented_ protocols (Bookoo in, Skale 2 out) on top
  of an existing ESP32 scale lib, not a from-scratch sniff. Still confirm the leva! side by
  **sniffing a real Skale 2 ↔ leva! session** (nRF Sniffer) to catch any commands leva! writes the
  scale that the published spec omits.
- **Risks / unknowns** — **(1) the binding question above** (name/type vs bonded MAC) is the
  make-or-break; verify before building. Then: **Acaia-style auth** on the real-scale side is the
  hardest read (avoid Acaia as the source — Bookoo sidesteps this); BLE dual-role stability on the
  ESP32; one extra ~BLE-interval of latency (the fixed `Stop early` absorbs a little); and whether
  leva! drops a peripheral that doesn't answer every command it sends the model.
- **Payoff** — native leva! weight-stop with **any** scale you run, and a reusable, publishable
  "any-scale → leva!" shim. Effort medium-high but mostly _integration_ (two documented protocols +
  a reference lib), little Vibrato code.
- **Scale shopping for this path:** the daily/**source** scale = **Bookoo Themis Mini** (open
  protocol, in the reference lib). The **native baseline** — so you're unblocked while building and
  can capture a real supported-scale↔leva! session — = a **Felicita Arc** on this firmware (or
  **DiFluid** if you upgrade to leva! 3.2). Emit target = **Skale 2** (you emulate its published
  spec; no need to own one).

### Path B (last resort) — bridge into Vibrato, app-side stop

Only if native can't drive MV2's stop **or** the shim isn't worth it: an ESP32 reads the scale →
MQTT → a Vibrato **`ScaleSource`** port (`packages/core/src/ports.ts`) → a tested
**`ShotController`** that fires the stop at `weightG ≥ target − flowGs·t_stop`, with a hard
max-time/max-weight ceiling that always cuts and a fail-safe on a stuck reading.

- **Calibrate `t_stop` empirically** — it's command latency + valve-close + in-flight coast, not a
  guess. Pull a few shots logging commanded-vs-final weight and fit `t_stop` from the measured
  overshoot; without it, over/undershoot is unbounded.
- **Tare + drift** — zero the scale before each shot (or subtract a cup/portafilter tare), and treat
  baseline drift as a fault (re-tare or abort), not just a "stuck reading".

Beats a hand-cut, but app-side latency + no native `Stop early` make it strictly worse than A/C.
Keep it specced as the escape hatch, not the plan of record.

**Open question to resolve on-machine (1a):** does leva!'s native weight-stop actually **drive MV2's
shot termination**, or does MV2's own volumetric controller own the stop (making leva!'s
`Method: WEIGHT` cosmetic)? If native drives it → Path A/C win outright; if not → Path B's app-cut
(re-press dose / `MCcSKIP`) is the only lever.

**Phase 2 exit:** a shot stops at target **mass** (native via A/C, or app-side via B) within a
tolerance **tighter than the manual hand-cut**, live weight + ratio on the scope, and final weight
saved to each History record — the loop is closed: target → actual+weight → rated shot → data to
tune.

---

## Phase 3 — Temperature observability

The ito has **no temperature feedback** today — its PID sensor input is empty (which is why PID
`Control` had to be `OFF`, and why `ERR:TSTAT` appeared). So the scope's temp trace stays dead and
shot records carry no brew temperature — a real gap, since temp is a top extraction variable
(intra-shot decline, cold-group / first-of-morning shots, drift). This phase feeds temperature into
the ito → the rich frame's `tempC` (Phase 1's offset) → the scope + History. **Measurement only** —
MV2 keeps controlling its own temp; the ito just watches. Hard rule: never wire the ito's heater
output to MV2's element (no two-controller fight); keep the ito's loop read-only.

Correction from the A53 schematic (Phase 4 research): the machine **already senses temperature** —
two NTC probes, **S1 (boiler)** and **S2 (delivery group)** — and newer units expose temp on a
**4-pin external-display header (SD / JP3)**. So "MV2 doesn't measure the group" was wrong; the
first move is to **read what's already there**, not add a probe.

### v1 — Read MV2's own temperature (cleanest)

- **Tap the external-display header** (SD/JP3) if it carries the temp value — no probe, no
  electrical loading. Natural home: the **Phase 4 ESP32 interposer** (already in the machine) →
  HASS, and/or bridged into Vibrato.
- **Else buffer-read the S1/S2 NTC lines** — do **not** parallel-load them (a second reader skews
  _MV2's own_ control); use an isolated high-impedance buffer, or co-locate an independent probe in
  the same well.

### v2 — A true brew-water probe (additive — the reading MV2 lacks)

S2 reads the group _body_, not the water at the puck. For closer-to-brew-water temp, add a probe at
the grouphead / portafilter (or a Scace-style in-path probe) into an **ito PID sensor input** →
`tempC` in the rich frame → Vibrato scope/history. Bonus: giving the ito its own sensor **cures
ERR:TSTAT for good**. Type-match the probe to the ito input (NTC / PT100 / thermocouple per the
leva! spec).

- **Channel-count limit**: the ito exposes ~2 temp inputs (PID 1 / PID 2 — check the `Sensors`
  menu). Routing MV2's temps through the ito competes for those; reading MV2's temps via the Phase-4
  ESP32 instead sidesteps the limit.
- **Vibrato data model**: `Telemetry` carries a single `tempC` today — surfacing group + boiler
  needs multiple named channels; the rich frame likely carries PID 1 + PID 2 temps, so pin those
  offsets too (Phase 1 method).

### Verify on-machine

Ito-probe path: does the ito populate `tempC` with PID `Control = OFF`, or only when a loop is
active (→ find a measure-only posture)? Header-tap path: confirm the external-display connector
actually carries a readable temp value (it's optional — not all units are fitted).

**Phase 3 exit (v1):** MV2's own group/boiler temp on the scope + in each shot record (via the
external-display header or a buffered read). v2 adds a true brew-water probe (and clears ERR:TSTAT
by giving the ito its own sensor).

---

## Phase 4 — Machine control (HASS on/off → full control → understand the board)

A **different animal** from Phases 1–3: this is the A53 Mini's **own** control system, NOT the added
ito+leva!. The vehicle is a separate **ESP32 (ESPHome)** interposer that talks straight to Home
Assistant, complementing the ito→Vibrato→MQTT→HASS path. **Start with on/off**, grow to full button
control, and — the ambition — sniff the control board.

**The machine is a rebadged La Spaziale S1 Mini Vivaldi II** (Clive / LUCCA house brand), which
changes everything: the **full wiring diagram + power/keyboard diagrams + a labelled component key
are IN the A53 Mini manual (§12–13)** (and the S1 Vivaldi II manual) — so the topology is
**documented, not blind RE**. Two earlier guesses corrected: it is **not** a Vibiemme, and there is
**no separate Gicar dosing box** — a single **proprietary La Spaziale main board** does dosing +
per-boiler temp + pump + solenoids + heating itself (the only Gicar part is the flowmeter). And
**`S1 Cafe` = s1cafe.com**, the La Spaziale forum — source of the on/off recipe below.

> ⚠️ **Safety.** This machine is mains voltage + ~kW heating elements + water. Interposing on
> **low-voltage button/signal lines is relatively safe**; anything touching **mains, heaters, or
> main power is high-voltage** — properly-rated + isolated parts only, and **never bypass the
> machine's own safeties** (klixons TSB/TSC, level probes). Remote-ON means the boilers heat
> **unattended** → confirm tank water, and pair with an auto-off timer + a leak sensor.

### 4a. Recon (mostly a docs read now)

From the official wiring diagram, the main board's labelled connectors: **SER1 / M1** front-keypad
ribbon, **M2** logo lights, **F** flowmeter, **S1** boiler NTC, **S2** delivery-group NTC, **P**
vibratory pump, **EV GR / EV H / EV AL** the three solenoids, **T1/T2 + P1/P2** boiler/group heating
static relays, **SB / SL** boiler-level / tank-lever probes, klixons **TSB/TSC**, and an optional
**external-display header (SD / JP3)**. So the map is known; the **one genuine unknown** is the
digital behaviour of the **SER1/M1 keypad↔main-board ribbon** — switch-matrix vs a small serial
link — a logic-analyzer job (4d). **Bench-unit option:** to probe without opening the working
machine, buy a spare front keypad + main board and reverse it on the bench with the scope/analyzer
(the same bench-unit pattern that de-risked the ito).

### 4b. On/off via HASS (v1 — near-solved)

It's **soft power** — a membrane ON/OFF button; mains-apply → **Stand-by**, and a **~3 s press**
boots it heating. Two documented paths:

- **Button intercept (matches the control goal):** an ESP32/ESPHome **opto/MOSFET across the front
  connector pins 1 (GND) & 6 (ON/OFF), pulsed ~3 s** — the s1cafe recipe (t=261) → an ESPHome switch
  in HASS. Low-voltage, mirrors the factory press, and extends to the other buttons.
- **Mains-side (no logic wiring):** fit the La Spaziale **power-retain** module (board
  auto-powers-on when mains returns) + a **≥15–20 A-rated** smart plug/contactor (Shelly).
  **Gotcha:** without power-retain, a mains cut drops it to _Stand-by_, so a bare smart plug won't
  start a heat-up on its own.
- (A factory Bluetooth "S1 Timer" iOS scheduler already exists — proves soft-power scheduling, but
  it's not HASS-native.)

**Safety:** dual-boiler **~15 A** resistive load — size the switch for it; confirm tank water before
any unattended remote heat-up (klixons are backstops, not interlocks).

### 4c. Full button control

Same principle across the panel — the buttons are **low-voltage membrane contacts** on the front
board, so drive each with a cheap **opto/MOSFET** (silent, no relay) from the ESP32. Only ON/OFF
(pins 1 & 6) is documented; **map the rest by continuity**. Exposes Single / Double / Hot-water /
Boiler to HASS. (Dose is _also_ reachable via the ito+leva! `MCcDOSE`, but the **La Spaziale board
owns dosing here**, not leva!, so the interposer is the general path.)

### 4d. Deep sniff (the ambition — learn how it operates)

- **Directly sniffable now (no protocol):** tap the **flowmeter signal** (Gicar magnetic-turbine,
  ~24 V Hall, part #2498/#3418 — count pulses → dose volume) and the **S1/S2 NTC lines** (analog).
  Solenoid/heater drives are switched mains — observe with care, not a logic analyzer.
- **Logic-analyzer the SER1/M1 ribbon** (the real unknown): capture during a power press, a
  dose-programming cycle, and a temp-set — reveals matrix-vs-serial and whether dose/temp **state is
  queryable** (so you could inject events digitally instead of bridging contacts).
- Output: a documented model of the machine + a HASS-integrated sniffer.

**Sequencing:** independent of Phases 1–3. **4a docs read** → **4b on/off** (near-solved: pins 1 &
6, or power-retain) → 4c full buttons → 4d the deep sniff. Prior art: the s1cafe power-on HOWTO
(t=261), Home-Barista timer / remote-start threads, and the commercial S1TIMER power-retain module.
Note **no drop-in GaggiMate/Gaggiuino** exists for La Spaziale (those replace a Gaggia single-boiler
board) — flowmeter-tap + interpose is DIY here.

---

## Files

- `packages/core/src/protocol/frames.ts` — pin `parseRichFrame` offsets (core change).
- `packages/core/src/protocol/CAPTURE.md` — update the ruler with the confirmed offsets.
- `packages/core/src/protocol/frames.test.ts` — real-frame fixtures for the numeric path.
- `packages/cli/src/index.ts` or `scripts/capture-shot.mjs` — the capture harness (new).
- `packages/ui/public/tabs/{brew,history}.js` + `packages/ui/public/chart.js` (not under `tabs/`) —
  shot detection + variance overlay (wiring; traces already render).
- `homelab apps/base/vibrato/deployment.yaml` — repoint `LEVA_HOST`.
- **Path C (shim)** — an **external ESP32 firmware** (its own repo, not this monorepo): dual-role
  BLE translator (real scale → impersonated supported scale). Little/no Vibrato change; Vibrato just
  reads `weightG` from the rich frame like any native scale.
- **Path B (fallback) only** — `packages/core/src/ports.ts` `ScaleSource` port + a
  `@leva/scale-mqtt` source + `packages/core/src/shot-controller.ts` (arm/fire/abort,
  flow-compensated coast, hard safety ceiling; pure + unit-tested) + `server/src/index.ts` to
  arm/disarm and route the dose-cancel stop.

## Verification

- **Unit**: `frames.test.ts` decodes each numeric field from captured fixtures; a deliberately-wrong
  offset fails a test (guards against plausible-but-wrong values).
- **Bench/sim**: `LEVA_TRANSPORT=sim` still drives the scope via `parseKeyValue` (no regression).
- **Path C shim** (Phase 2): first prove leva! **pairs with and reads the impersonator** (a bench
  ESP32 advertising as e.g. a Skale 2, streaming synthetic weight) before wiring the real scale —
  sniff a genuine supported-scale↔leva! session to fix the target format.
- **`ShotController` unit tests** (Path B only): fires at `target − flowGs·t_stop`; the hard ceiling
  always cuts; a dropped/`undefined` reading fails **safe** (stops), never open; abort works. (Low
  physical risk — a bad early stop wastes a shot / spills water, not a burn — but a shot costs
  dose + time, so test it thoroughly.)
- **Weight-accuracy gate** (Phase 2 precondition, from 1b): decoded `weightG` agrees with a
  reference scale across the range before auto-stop is allowed to arm.
- **On-machine integration**: pull a shot → the live trace tracks the machine's own pressure/flow
  readout and the logged curve matches; and the **stop command actually terminates a live shot** —
  measure the final-weight error across several pulls and confirm it lands **tighter than the
  hand-cut** consistently, not once.

## Sequencing / decisions

1. **Phase 1 is the unlock** — without pinned offsets Vibrato shows nothing; do it first, ship
   incrementally (1b core + tests → 1c deploy → 1d UI).
2. **Scale strategy (Phase 2's real fork):** native weight-stop is confirmed in firmware
   (`Method: WEIGHT` + `Stop early` + `Scan`), so the choice is _which scale link_:
   - **A** — buy a supported scale (Skale 2 / Felicita Arc / Eureka; DiFluid needs leva! 3.2+):
     near-zero build, works today.
   - **C** — the BLE translation shim (use any scale you own): the interesting project; medium-high
     effort, mostly reverse-engineering, and it _also_ lands on native weight-stop. Do A first to
     de-risk (a known-good native baseline), then C as the hack.
   - **B** — app-side bridge + `ShotController`: last resort only.
3. **Resolve the native-stop question BEFORE buying a scale (on-machine, 1a):** does leva!'s native
   weight-stop actually drive **MV2's** shot termination, or does MV2's volumetric controller own
   the stop (making `Method: WEIGHT` cosmetic)? Native driving it → A/C win and the scale purchase
   makes sense; if it's cosmetic → only B's app-cut (re-press dose / `MCcSKIP`) works, which changes
   what scale is even worth buying. Also confirm `10.42.7.11` is MV2's controller vs a separate dev
   ito, and check the leva! firmware version (it gates DiFluid support and the offset map).
