# ito + `leva!` Integration Walkthrough — Lucca A53 Mini (Mini Vivaldi II)

**From current bench state → fully integrated pressure/flow-profiling espresso machine.**

Roadmap doc. Grounded in `~/src/lab/06-coffee-espresso/`. Cites project IDs (`06-NNN`) and file
paths. Nothing in the lab repo was modified to produce this.

> **Editor's note (2026-07-13):** this was drafted against a working checkout parked on a
> non-default branch, so it describes the flasher, `06-015`, the flow-tap KiCad, the brackets, and
> the STLs as living on an "unmerged branch `feat/ito-flash-tool`." That is **stale** — all of those
> assets are on `main` (the flasher landed via lab PR #51; `06-015` and the reference assets were
> already merged). **Phase A1 ("merge the tooling PR") is therefore already complete** — treat
> everything below as canonical and start the plan at Phase B (finish/fabricate the interposer).

Machine: **La Spaziale S1 Mini Vivaldi II** (Clive's LUCCA A53 Mini rebadge) — **vibratory** pump,
so `leva!`-compatible. Board: **ito V2.0** (Software & Circuits) running `leva!`, replacing nothing
in the stock temperature path — it _interposes_ on the pump for pressure/flow profiling only.

---

## 0. Scope note — the "final product"

The end goal (per `06-001` scope table + Exit Criteria) is **pressure/flow profiling only**:

- ito board flashed with `leva!` and mounted, powered from the machine.
- Pump driven by ito via phase-angle control (lever-style declining-pressure profiles,
  pre-infusion).
- Real-time **flow** read from the machine's own **stock GICAR meter** via the `06-015` interposer
  (the preferred path — no inline Digmesa, which restricts flow ~10%).
- Brew **pressure** read from a sensor tee'd into the brew line.
- Live monitoring/plots via **Status Monitor** over WiFi; **HASS/MQTT** for homelab monitoring +
  control.
- Stock **temperature** control **left factory** — PID takeover is explicitly split out to `06-012`
  and is _out of scope_ for the core product (it conflicts with the A53 stock board).

`06-011` (float-fill plumb-in) is a **parallel, compatible** project that shares the same
machine-open teardown; it is not strictly part of the profiling product but is sequenced alongside
because it taps the same M5 board.

---

## 1. Current state (what is actually done today)

### Hardware in hand

- **Full ito + `leva!` kit** (shipped directly to a US address, Jan 2025): ito V2.0 module, pressure
  sensor, Digmesa FHKSC flow meter, OLED + **rotary encoder**, plus the _fully-loaded_ extras —
  **SSR kit + TSic sensor** (the PID hardware for `06-012`, already on hand), fluid-install kit (OKS
  grease, PTFE, 3× G1/8" fittings), TouchCell bracket, BLE, and a **USB-serial (FTDI) adapter**. Kit
  config card values recorded in `06-001` ("As-received kit configuration"): PCB 2.x, OLED SSD1309
  (jumper J1), Digmesa 932-xxxx, WiFi AP `ito Module` 2.4 GHz.
- **Spare Mini Vivaldi V2 control board on the bench** (ING3/Laurma Elettronica v05.02) alongside
  the ito V2.0 — enables bench work without opening the machine.
- `06-011` plumb-in parts (float valve, regulator, solenoid, Claryum filter) in hand.

### Firmware / flasher — DONE, but note the merge state

- **`ito-flash` CLI flasher built and validated.** `flash_ito.py` + `README.md` + `requirements.txt`
  at `06-coffee-espresso/_reference/ito-flash/`. It flashes `leva!`/`caffè!` over WiFi (XMODEM-CRC
  to the ATMega1284 bootloader on TCP port **2323**) with a verification-first workflow: `loopback`
  (offline byte-for-byte round-trip) → `check` (live, non-destructive bootloader probe) → `backup`
  (settings dump) → `flash --yes`.
- **`leva!` 3.1 (rotary-encoder build) was flashed and validated onto the bench ito at `10.42.7.11`
  on 2026-07-13** (recorded in the flasher README).
- ⚠️ **Merge status:** the flasher, the `06-015` project file, the control-board wiring reference,
  the flow-tap KiCad stub, and the bracket STLs all live on the **unmerged branch
  `feat/ito-flash-tool`** — they are **not on `main`** and not in the current working checkout
  (which is on `audio/elsinore-drivers-confirmed`). Landing that PR is the first housekeeping step
  below.

### Interposer PCB (`06-015`) — designed, not fabricated

- Topology chosen: **in-line, reversible, Schmitt-buffered** interposer. Passes all three GICAR pins
  `J1→J2` straight through to the Vivaldi; breaks out only a buffered pulse to ito on `J3`. The
  **+14.3 V rail is physically confined to `J1↔J2`** (no `+` pin on `J3`) so it can never reach
  ito's 5 V input. Buffer = **74LVC1G17** (SOT-23-5) + 0.1 µF cap.
- Schematic/netlist/BoM drafted, KiCad project **scaffolded as a stub** (`flow-tap.kicad_pro`) — not
  yet drawn in KiCad (no KiCad on the authoring machine).
- **ito-side connector confirmed: JST-XH 2.5 mm, 3-pin** (George metered the pin gap). IMPULSE
  pinout confirmed by multimeter: **pin1 GND / pin2 signal / pin3 +5 V** (silkscreen `# / ⊤ / +`).
- **Still pending: the GICAR meter connector** type/pitch — the meter wasn't on either bench board,
  so `J1/J2` footprints are TBD. JST-XH 2.54 mm + adapter pigtails is the universal fallback.

### Machine electrical reverse-engineering — DONE on the bench board

- `_reference/mini-v2-control-board-wiring.md`: **M5 terminal strip metered and confirmed on a US
  120 V unit (2026-07)**. PUMP identified (3rd-from-top, fires in both brew and autofill), PHASE `F`
  always-live, **no switched mains rail** (the soft-touch pad is logic-only). GICAR flow-meter
  pinout confirmed: `+` ≈14.3 V (Vivaldi-only), `−` GND, `o` 5 V open-collector pulse (~2
  pulses/mL). Two tap topologies documented (blondica buffered / sandc direct); buffered is the
  proven one and is what `06-015` implements.

### Not yet done

- No physical install on the machine. Nothing tee'd, cut, or wired into the running Lucca.
- Pre-flight (`06-001`) not executed: grouphead-path inspection, pump/3-way seal check, bypass-valve
  cracking-pressure measurement (vibe-pump confirmation is the one pre-flight item already known).
- Not-in-kit extras not sourced: flow-meter inline fittings (may be covered by kit G1/8" — verify),
  SNS/mains hookup wire + spades, PETG display housing, monitoring tablet.
- Status Monitor XML not installed; HASS/MQTT bridge not stood up.
- Tuning not started.

---

## 2. End-state definition + acceptance criteria

The final integrated product is the union of the `06-001` and `06-015` Exit Criteria, with the
monitoring layer added. **Acceptance = all of the following true simultaneously:**

**Firmware + control (from `06-001`):**

1. ito installed and powered from the machine; `leva!` `1 - ito with rotary encoder` running.
2. Pump driven by ito via phase-angle control (Relay 1), `SNS` fed from the pump-switch L phase.
3. A `Gen Lever` (or custom) profile tracks setpoint to within a fraction of a bar at the plateau.
4. Pre-infusion (e.g. 10 s @ 1.5 bar) holds without overshoot → clean declining-pressure shot.
5. Over-pressure bypass set **>9 bar**; `PRESS OPV` configured; no flow-meter bias artifacts.
6. **Stock temperature control still works** (PID takeover deferred to `06-012`).
7. Display/encoder mounted **without cutting irreplaceable parts**.
8. No leaks at the sensor tee / flow path after a session of shots.

**Flow sensing via interposer (from `06-015`):** 9. Interposer fabricated + assembled;
bench-verified pulse pass-through `J1→J2` and buffered `J3.OUT` (0↔5 V), with **no continuity**
between the 14.3 V net and any `J3` pin. 10. Installed in-line: machine **still doses + autofills
normally**, ito reads live flow, and pulling the board restores stock behaviour (fully reversible).

**Monitoring (product requirement, beyond the raw Exit Criteria):** 11. Status Monitor plotting live
pressure + flow + temp over WiFi. 12. HASS/MQTT bridge publishing shot/pressure/flow telemetry (and
any control surface) into the homelab — with the documented rule that this poll must be **closed
during any future re-flash**.

---

## 3. Sequenced plan (current → final)

Legend: **[BENCH]** reversible bench work · **[GATE]** physical/irreversible or hard-to-undo action
requiring a go/no-go · **[SOFT]** config/software, reversible.

### Phase A — Land the tooling + lock the bench baseline [BENCH / SOFT]

| Step | Do                                                                                                                                                                                    | Maps to                          | Prereq                                                                                  | Done when                                 |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- | --------------------------------------------------------------------------------------- | ----------------------------------------- |
| A1   | **Merge `feat/ito-flash-tool`** to `main` via PR (flasher, `06-015`, wiring ref, KiCad stub, brackets). Follow branch/PR workflow — no direct main commit, no `--admin`.              | `06-015`, `_reference/ito-flash` | PR green                                                                                | PR merged; files on `main`                |
| A2   | Re-confirm the bench flash is reproducible: `loopback` → `check` → `backup` → (optionally) re-`flash` leva! 3.1 on the ito at `10.42.7.11`.                                           | `06-001` step 6, ito-flash       | ito on bench 5 V (power via IMPULSE pin3/pin1) or FTDI; AP or STA mode (**not STA+AP**) | `backup`/port-23 shows `$id: leva! (3.1)` |
| A3   | Put ito on the LAN: switch AP→**STA** mode, join 2.4 GHz, set a **static DHCP lease** so `10.42.7.11` stays stable/bookmarkable. Set a custom AP password first.                      | `06-001` step 5                  | A2                                                                                      | ito reachable at a fixed IP               |
| A4   | Bench-bring-up **Status Monitor** + its bundled XML against the bench ito; confirm live (empty) plots.                                                                                | `06-001` step 7                  | A3, a tablet                                                                            | Status Monitor connects                   |
| A5   | Stand up the **HASS/MQTT** bridge against the bench board; confirm telemetry flows; document that this poll must be **closed before any re-flash** (ito's WiFi scans corrupt XMODEM). | Product req 11–12                | A3                                                                                      | MQTT topics visible in HASS               |

_Gate before leaving Phase A:_ firmware is proven re-flashable at will, so all later machine work is
de-risked — a bad flash is never fatal (bootloader is protected; "if it fails, repeat").

### Phase B — Finish + fabricate the flow interposer [BENCH]

Do this **before** opening the machine, so the flow path is a 3-plug reversible drop-in on install
day rather than soldering-in-place.

| Step | Do                                                                                                                                                                                          | Maps to                              | Prereq              | Done when                                 |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ | ------------------- | ----------------------------------------- |
| B1   | **Photograph/identify the GICAR meter connector** (type + pitch, 2.0 vs 2.54 mm) — the one open blocker on `06-015`. Requires eyes on the meter (a quick machine peek or the meter itself). | `06-015`                             | machine access      | connector type known (or fallback chosen) |
| B2   | Finalize `J1/J2` footprints (or commit to **JST-XH 2.54 mm + pigtails** fallback). `J3` = JST-XH 2.5 mm (confirmed).                                                                        | `06-015`                             | B1                  | connector BoM closed                      |
| B3   | Draw the schematic in KiCad from the netlist, assign footprints, lay out **~20 × 20 mm, 2-layer**, export Gerbers/BoM/CPL.                                                                  | `06-015`, `_reference/flow-tap-pcb/` | KiCad (Windows), B2 | Gerbers exported                          |
| B4   | Order JLC/PCBWay — **SMT-assemble U1 + C1 only**, hand-solder TH connectors. Piggyback on the plumb-in bracket order (one cart).                                                            | `06-015`                             | B3                  | boards ordered                            |
| B5   | Assemble; **bench-verify**: `J1→J2` passes all 3 pins unchanged; injected pulse on `o` appears clean at `J3.OUT` (0↔5 V); **no continuity `+`↔any `J3` pin**.                             | `06-015` Exit                        | B4                  | bench checks pass                         |

_Note:_ if B1 stalls (meter connector can't be sourced/matched), the interposer can still be built
on the JST-XH fallback, OR the machine can fall back to the **kit Digmesa inline** meter (accepts
the ~10% flow restriction). The interposer is the preferred path; it is not a hard blocker on the
whole product.

### Phase C — Pre-flight the machine [GATE — first machine open]

First time the machine is opened. Unplug at the wall (no switched rail — `F`/`N` live whenever
plugged in), let boilers cool/depressurize. Reversible (nothing cut yet).

| Step | Do                                                                                                                                                                                                                                                                                                                                   | Maps to               | Done when                                     |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------- | --------------------------------------------- |
| C1   | Confirm **vibe pump** (known: Mini Vivaldi II = vibratory → OK; full-size A53 rotary would be incompatible).                                                                                                                                                                                                                         | `06-001` pre-flight 1 | confirmed                                     |
| C2   | **Inspect grouphead**: no spring-loaded valve / gicleur / S11-B restrictor between the intended sensor tap and the portafilter. **Also check for a factory Progressive Preinfusion chamber** (spring accumulator on the left group-head port) — remove it (incompatible with leva! pre-infusion; its port becomes the sensor mount). | pre-flight 2          | clean path verified; pre-infusion chamber out |
| C3   | Check **pump + 3-way seal** condition (worn seals fine at normal pressure leak under profiling).                                                                                                                                                                                                                                     | pre-flight 3          | seals sound (or rebuild kit ordered)          |
| C4   | Measure the **over-pressure bypass** cracking pressure; plan to set it **>9 bar**.                                                                                                                                                                                                                                                   | pre-flight 4          | value recorded                                |
| C5   | Pull **one no-profile, full-power shot** to characterize the pump's bar/s ceiling (Mini Vivaldi pump is "lazy" — leva! can't out-ramp full power).                                                                                                                                                                                   | pre-flight 5          | ceiling known                                 |
| C6   | Meter/confirm M5 loads on the _actual_ machine (PUMP, EV.GR, F, N) — cross-check against the reference (already metered on the bench board). Identify the GICAR connector (closes B1 if not done).                                                                                                                                   | wiring ref            | tabs confirmed                                |

_Gate decision:_ if C2/C3 reveal a restrictor or weeping seals, **stop** and remediate (grouphead
mod out of documented scope; seal-rebuild kit is the `06-001` contingency BoM row 11) before any
irreversible wiring.

### Phase D — Bench-flash-then-install the ito [BENCH → GATE]

`06-001`'s explicit "flash on the bench first" tip: keep the fiddly firmware separate from mains.

| Step | Do                                                                                                                                                                                        | Maps to         | Reversible?       | Done when            |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ----------------- | -------------------- |
| D1   | Firmware is already flashed (Phase A) — ito goes into the machine already running leva! 3.1.                                                                                              | `06-001` step 6 | —                 | ito ready            |
| D2   | **Solder the HLK-PM01 PSU** onto ito (mind L/N→+5V/GND orientation), fit adhesive feet + acrylic insulation shield. _(Or run ito from an external 5 V ≥600 mA supply and skip HLK-PM01.)_ | `06-001` step 2 | **[GATE]** solder | PSU on, 5 V verified |
| D3   | Mount ito in a **non-metal/grounded enclosure**, away from boiler heat, mains leads separated from low-voltage. Wire N/L to the machine's PHASE/NEUTRAL.                                  | step 2          | reversible-ish    | mounted, powers up   |

### Phase E — Mains + sensor install [GATE — single teardown, but REVERSIBLE]

**Do this in one machine-open session, combined with `06-011`'s switched-mains solenoid interlock**
(identical wiring area). **Correction (2026-07): this is NOT the point of no return — nothing is
cut.** M5 is push-on plugs, the pump has faston tabs, and the sensor threads into the factory
pre-infusion port. One teardown for tidiness, not because it is irreversible.

| Step | Do                                                                                                                                                                                                                                                                                                                                                                                           | Maps to                     | Irreversible?                                      | Done when                                            |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- | -------------------------------------------------- | ---------------------------------------------------- |
| E1   | **Relocate the PUMP wire (no cut).** Unplug it at the pump; control-board side → ito **`SNS`** (zero-cross + "pump on") via a pigtail; drive the pump from ito **`SSR 1`** via a second pigtail onto the pump's freed faston tab. ito `L` → mains `F`, `N` → a Neutral tab. Both ends are 6.3 × 0.8 mm fastons / push-on plugs.                                                              | `06-001` step 3, wiring ref | **No — pigtails, reverses by re-seating the plug** | pump runs through ito                                |
| E2   | _(Optional, later)_ move the **group solenoid feed onto `SSR 2`** to unlock dosing/backflush/shot-control — hands the valve to ito. Deferred until profiling is stable.                                                                                                                                                                                                                      | `06-001` step 3 note        | yes                                                | (optional)                                           |
| E3   | **Thread the pressure sensor into the factory pre-infusion port** on the group head (remove the Progressive Preinfusion chamber first — it is incompatible with leva!'s electronic pre-infusion). No tee, no cut. Mount **vibration-free** (the group head is the calmest spot); 125 °C rated. Sensor → ito **ADC**. _Fallback:_ tee the brew line only if the port thread can't be adapted. | `06-001` step 4             | **No — refit the plug/chamber to reverse**         | sensor reads brew-chamber pressure                   |
| E4   | **Flow: plug the `06-015` interposer in-line** (meter→`J1`, `J2`→Vivaldi socket, ito flow cable→`J3` → ito **IMPULSE**). Reversible. _Fallback:_ kit Digmesa on the **tank→pump line, before the pump** (accepts ~10% restriction) — that path is plumbing-irreversible.                                                                                                                     | `06-001` step 4, `06-015`   | interposer **NO** / Digmesa **YES**                | ito reads live pulses; machine still doses/autofills |
| E5   | _(Parallel `06-011`)_ derive the fill-solenoid 12 VDC PSU from the PUMP tab; same teardown.                                                                                                                                                                                                                                                                                                  | `06-011`, wiring ref        | plumbing                                           | solenoid gated on pump                               |

_Gate:_ E1/E3 are still where mains + water get touched, so treat them as a careful go/no-go — but
they are **reversible** (unplug the pigtails / refit the port plug). The one genuinely gated action
left is soldering the HLK-PM01 (Phase D2), which the external-5 V option (order-list item E) removes
entirely. the machine is a profiling machine until re-wired.

### Phase F — Configure + first-light [SOFT]

| Step | Do                                                                                                                                                                                                                                                                                                               | Maps to           | Done when          |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- | ------------------ |
| F1   | Set pressure-sensor scaling, flow-meter type/impulses, and **`PRESS OPV`** in leva!; set the machine's **bypass valve to crack just above 9 bar**.                                                                                                                                                               | `06-001` step 7   | values set         |
| F2   | Run the **pressure pre-test** (blind filter). ⚠️ **A53 gotcha:** the stock board drops `SNS` on "inactivity" and aborts the test — either **press the shot button then start the pre-test**, or temporarily **jumper `SNS`↔`L`** (set SNS action to "do nothing" first). Survives firmware upgrades → one-time. | `06-001` Tuning   | pre-test completes |
| F3   | Confirm Status Monitor + HASS/MQTT now show **live pressure + flow + temp** from the installed machine.                                                                                                                                                                                                          | Product req 11–12 | live plots         |

### Phase G — Tuning (the real, ongoing work) [SOFT, iterative]

Maps entirely to `06-001` "Tuning". Iterate against Status Monitor plots (turn on the pump-power /
phase-angle trace):

- **`Kc` (proportional):** start ~3.5 (plot-relative, firmware-scale dependent); halve on
  oscillation, raise if sluggish. Keep `Kc<SP` and `Kc>SP` **close** (lopsided pair → wild swings).
- **Two parameter sets split at 2.5 bar by _setpoint_** — tune the below-2.5 set to avoid overshoot;
  raise its `Kc` if you undershoot pre-infusion.
- **`PHASE OFF`** (pump-stop angle), **`PRESS MAX`/`PRESS OPV`** (ceiling + bypass), **`Flow Corr`**
  (feed-forward bias — if bias rides ~5° above pump-power, cut `Flow Corr` ~5°).
- Expect a **flooding flow-drop** at hand-off (~0.7 bar) — not a bug; start the profile higher (~1.2
  bar) to kill the stutter.
- Good starting recipe: **`Gen Lever` preset + ~10 s pre-infusion @ 1.5 bar**.

**Done = the `06-001` Exit Criteria** (§2 above): profile tracks setpoint within a fraction of a
bar, clean pre-infusion, no leaks, stock temp intact. Document as-built (sensor location, profile,
tuned params).

### Phase H — Deferred / optional (post-product)

- **Display/encoder PETG housing** — external, no-cut mount (or a printed La Spaziale Dream S1 bezel
  with a display slot). Needed for `06-001` Exit criterion 7; can trail the electrical work.
- **`06-012` leva! PID temperature takeover** — _Not Started, deliberately deferred._ Conflicts with
  the A53 stock board; SSR + TSic hardware already in hand. Bench-test on the spare control board
  first. Out of the core product's scope.
- **`06-014` ESP32 button-automation sidecar** — its temperature role is superseded if `06-012`
  succeeds; otherwise an alternative automation path.

---

## 4. Risks / open questions / blockers

**Needs George's decision or a photo:**

1. **GICAR meter connector (blocks `06-015` layout).** Type + pitch unknown — the meter wasn't on
   either bench board. Decide: match it (needs a photo/the meter in hand) or commit to the **JST-XH
   2.54 mm + pigtail fallback**. This is the single gating unknown for the interposer.
2. **Interposer vs inline Digmesa.** Preferred = interposer (no flow restriction, reversible).
   Fallback = kit Digmesa inline (~10% free-flow loss, plumbing-irreversible). If B1 drags, which
   path for first light?
3. **`ito-flash` PR not merged.** The tool, `06-015`, and the wiring reference are stranded on
   `feat/ito-flash-tool`. Land it (Phase A1) before treating any of this as canonical on `main`.

**Hardware not yet acquired / to verify:**

4. **Not-in-kit extras:** flow-meter inline fittings (may be covered by the kit's 3× G1/8" — verify
   against the Mini V2's brew/tank line sizes before assuming closed), SNS/mains hookup wire +
   spades + heat-shrink, PETG filament, monitoring tablet (do **not** power it from ito).
5. **Sensor tee + adapter fit** — owner reports the adapter needs light filing; no factory
   pre-tapped port to count on. Measure inside; don't pre-order blind.
6. **Pressure-sensor rating** — kit card lists 200/215/300 PSI options; confirm the checked one (9
   bar ≈ 130 psi is within all three, so low risk).

**Physical / process risks:**

7. **Grouphead restrictor or worn seals (Phase C gate).** If C2/C3 fail, remediation is needed
   before the irreversible E1/E3 — grouphead surgery is outside the documented scope; seal rebuild
   is the `06-001` contingency.
8. **"Lazy" pump ceiling.** leva! can't recreate a ramp steeper than full power delivers; extreme
   profiles may want a ULKA EX5 pump swap (one owner did). Characterize in C5 before promising a
   profile.
9. **Mains work.** No switched rail — `F`/`N` are live whenever plugged in. Qualified-electrician
   territory; unplug at the wall, meter don't assume.
10. **`06-011` refill-rate caveat.** If pump-gated fill can't match peak draw (~600 mL/min at boiler
    autofill), the tank ratchets down — size fill ≥ pump draw or add a 30–60 s solenoid off-delay.
    Relevant only because Phase E bundles the two projects.
11. **HASS/MQTT during re-flash.** The ito's WiFi scan corrupts XMODEM; any future re-flash must
    first **close** Status Monitor / Virtual LCD / the MQTT poll (documented in the flasher README).

---

## Appendix — file map

- `06-coffee-espresso/06-001-lucca-a53-mini-leva-firmware-integration.md` — core profiling project
  (scope, BOM, build sequence, tuning, Exit Criteria).
- `06-coffee-espresso/06-015-gicar-flow-tap-interposer.md` — interposer PCB project _(branch
  `feat/ito-flash-tool`)_.
- `06-coffee-espresso/06-011-mini-v2-direct-plumb-in.md` — parallel plumb-in (shares the teardown).
- `06-coffee-espresso/06-012-leva-pid-temperature-takeover.md` — deferred PID takeover.
- `06-coffee-espresso/_reference/ito-flash/{flash_ito.py,README.md,requirements.txt}` — CLI flasher
  _(branch)_.
- `06-coffee-espresso/_reference/mini-v2-control-board-wiring.md` — M5 map, no-switched-rail, GICAR
  pinout, buffer options _(branch)_.
- `06-coffee-espresso/_reference/flow-tap-pcb/` — KiCad stub + netlist/BoM _(branch)_.
- `06-coffee-espresso/_reference/leva/LEVA-DOCS-SUMMARY.md` — manual digest.
- Memory: `reference_ito_impulse_pinout.md` (IMPULSE pinout + JST-XH 2.5 mm), `project_lab_repo.md`
  (6-project Mini V2 build framing).
- Off-repo (NAS): `/Volumes/family/projects/electronics/espresso/` — leva! PDFs, ito DVD manual,
  home-barista thread indexes (t56816, t61709).
