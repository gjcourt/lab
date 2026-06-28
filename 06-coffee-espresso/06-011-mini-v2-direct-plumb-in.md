---
title: 'Mini Vivaldi II Direct Plumb-In via Reservoir Float-Fill'
number: '06-011'
category: 'coffee-espresso'
difficulty: 'Easy'
time_commitment: '1-2 days'
target_skills: 'Water Plumbing, Pressure Regulation, BSP Fittings'
status: 'Not Started'
depends_on:
  - hardware/lucca-a53
---

# Mini Vivaldi II Direct Plumb-In via Reservoir Float-Fill

## Description

Convert the **La Spaziale Mini Vivaldi II** (Clive's **LUCCA A53 Mini** rebadge — vibratory pump,
currently tank-fed) to a plumbed setup that's **robust** — meaning low-maintenance, reversible, and
respectful of the vibe pump's design constraints.

The s1cafe.com / home-barista.com community converged answer for vibe-pump Mini V2 plumb-in is
**reservoir float-fill, not inlet-side direct plumb**: the line keeps the existing tank topped up
via a mechanical float valve; the pump still gravity-feeds from the tank exactly as
factory-designed. Community reports suggest this preserves pump life substantially (multi-year vs.
~1-2 years on inlet plumb where the vibe pump fights inlet pressure on every stroke), keeps the
existing low-water float **switch** as dry-run protection, and is fully reversible without internal
modification.

**Out of scope (deliberately):**

- Drain plumbing for the drip tray — keep removable for now.
- Pump replacement / rotary conversion — explicitly not desired.

## Approach: reservoir float-fill

```text
[Aquasana Claryum output, 1/4" braided]
        │
        ├─ 1/4" inline shut-off (ball valve) ── for service isolation
        │
        ├─ 1/4" NC brass solenoid valve       ── energized only when machine is on; fail-closed
        │
        ├─ 1/4" pressure regulator @ ~20–25 PSI
        │
        └─ 1/4" line ─→ float valve in Mini V2 reservoir
                          │
                          └─ closes when tank reaches set level
                             → vibe pump still gravity-feeds as stock
                             → existing low-water switch unchanged
```

The Mini V2's existing **low-water float switch** (the magnetic switch that disables the pump when
the tank is dry) is **untouched** by this work and continues to provide dry-run protection. The new
mechanical **float valve** controls fill, not pump enable.

## Why this is "robust"

1. Vibe pump operates at atmospheric inlet pressure as factory-designed. No backpressure → no
   accelerated diaphragm / check-valve wear.
2. Original dry-run protection (low-water switch) remains in place.
3. Failure modes are bounded:
   - Stuck-open float valve → tank overfills → drip tray catches the overflow.
   - Stuck-closed float valve → tank slowly drains → original low-water switch trips → exact same
     failure mode as today.
   - Hose burst / fitting failure → only possible while machine is on (NC solenoid closes the line
     whenever machine is off); unattended flood risk is eliminated.
4. Reversible: disconnect at the regulator, refill manually, machine is back to stock.
5. Pressure-tolerant: even if the regulator fails high, the tank can't be over-pressurized (it's
   vented). Worst case is float-valve hammering / chatter and accelerated float-seat wear, which is
   loud and obvious — not a silent flood.
6. Fail-safe on power loss: NC solenoid de-energizes closed, so a house power outage shuts off the
   water supply automatically.

## Pre-flight: verify source-water hardness

The **Aquasana Claryum is a contaminant/taste filter (chlorine, chloramine, PFAS, lead, etc.) — it
does not soften water.** It does not remove calcium / magnesium hardness or significantly reduce
alkalinity. La Spaziale boilers don't auto-flush, so scale matters here.

**Do this before installing anything:**

1. Hardness test strip ($5 hardware store) or TDS meter.
2. Test from the **Claryum output**, not the upstream tap.
3. Three numbers to check:

| Metric                    | Espresso-safe target | Action if exceeded                                                                                                             |
| ------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Total hardness (as CaCO₃) | ≤ 60 ppm             | If 60–120: proceed, plan annual descale. If >120: add a softening cartridge (Pentair Claris, BWT Bestmax) **before** plumb-in. |
| Total alkalinity (KH)     | 40–80 ppm            | High alkalinity = fast scale. Same softening cartridge addresses this.                                                         |
| Chloride                  | < 30 ppm             | Claryum reduces chlorine but not chloride salts. High chloride pits boilers. RO is the only reliable answer here.              |

If targets met → Claryum is sufficient and plan proceeds as written. If not → add softening stage to
BoM before going further.

## Bill of materials

Thread-standard note: this plan does **not** plumb into the boiler — all joints live on the supply
line between the Aquasana output and the reservoir float valve. Most espresso-aftermarket regulators
and RO-style float valves use **G-thread BSP-parallel** ports (sealed with a fiber/nylon washer
against a flat face), not tapered NPT. **Don't mix:** an NPT male into a BSPP female will start
threading and then leak under pressure. Verify each part's thread standard from its spec sheet
before buying, and replace fiber washers on every disassembly.

| #   | Item                                       | Spec                                                                                                               | Notes                                                                                                                                                                                                                    |
| --- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | 1/4" inline shut-off ball valve            | Full-port, push-to-connect or compression                                                                          | Local cutoff for service. Don't rely on the house valve.                                                                                                                                                                 |
| 2   | NC brass solenoid valve                    | 1/4", normally-closed, lead-free / DZR brass body, food-grade EPDM seals, 110 V AC or 24 V DC coil                 | Candidates: U.S. Solid 1/4" NPT brass NC, 110 V AC, EPDM (~$30); Cleyon 1/4" brass NC, 24 V DC (~$25). Avoid plastic-body solenoids on potable water. Energized only when machine is on; NC = fail-closed on power loss. |
| 2a  | Smart plug (machine-side)                  | 15A indoor smart plug (Kasa / TP-Link / equivalent)                                                                | Single switched outlet feeds both the machine and the solenoid's coil-supply wall-wart. Machine "on" ⇒ solenoid open; machine "off" ⇒ solenoid closed.                                                                   |
| 2b  | Solenoid coil supply                       | If 24 V DC solenoid: 24 V DC wall-wart, ≥1 A; if 110 V AC solenoid: none needed (coil runs direct from smart plug) | Mount the wall-wart and any coil wiring in a small junction box near the under-counter outlet. Don't free-air splice AC mains.                                                                                           |
| 3   | Pressure regulator                         | 1/4" inlet/outlet, gauge'd, set to ~25 PSI                                                                         | Watts U5B-LF (3/8" NPT) needs a 1/4" NPT→BSPP transition before the float valve, since the float valve is BSPP. A 1/4" BSPP-native in-line regulator avoids this. Don't mix tapered/parallel threads at the same joint.  |
| 4   | Reservoir float valve                      | 1/4" male thread inlet (RO-style brass), with quarter-turn shut-off                                                | Mounts through a hole drilled in the **tank lid**. Set to close ~1/2" below max-fill mark.                                                                                                                               |
| 5   | 1/4" LLDPE polyethylene tubing             | Length: filter output → machine + ~12" service loop                                                                | Espresso aftermarket standard. Routes easier than braided; takes John Guest fittings cleanly.                                                                                                                            |
| 6   | Push-to-connect fittings (John Guest 1/4") | Tees, elbows, straight unions as needed                                                                            | Push-to-connect at any joint that may need disassembly for service.                                                                                                                                                      |
| 7   | Fiber washers                              | 1/4" BSPP sized (parallel-thread, flat-face seal)                                                                  | One per joint; replace on every disassembly.                                                                                                                                                                             |
| 8   | Hardness test strip / TDS meter            | One-time use                                                                                                       | Pre-flight check. ~$5–25.                                                                                                                                                                                                |

### Orderable picks (concrete products)

Specific products for the spec'd lines above (the **solenoid** already has candidates on line 2).
Verify thread standard (BSPP vs NPT) per part before buying — see the thread note at the top of this BoM.

| Line | Pick | ~Price | Where |
|---|---|---|---|
| 1 — shut-off ball valve | John Guest 1/4" push-fit ball valve (**PPSV040808W**) | ~$8 | Amazon |
| 3 — regulator (recommended) | Chris' Coffee Pressure Regulator w/ gauge — 0–100 psi, ships with 1/4" John Guest fittings, dial to ~25 psi (JG-native → avoids the BSPP/NPT transition) | ~$80 | chriscoffee.com |
| 3 — regulator (budget alt) | Espresso Parts 30 PSI fixed inline regulator (not adjustable; 30 vs ~25 target is fine for float-fill) | ~$30 | espressoparts.com |
| 4 — float valve | 1/4" brass RO float valve, male-thread + quarter-turn (e.g. LiquaGen / PureSec) | ~$10 | Amazon |
| 5 — tubing | 1/4" LLDPE RO tubing, 25 ft (e.g. Malida) | ~$10 | Amazon |
| 6 — JG fittings | 1/4" John Guest push-fit assortment (tees / elbows / unions) | ~$15 | Amazon |
| 7 — washers | 1/4" BSPP fiber/nylon washer pack | ~$6 | Amazon |
| 8 — water test | TDS meter (~$15) + GH/KH test strips or an API GH/KH titration kit (~$8) | ~$23 | Amazon |

Links: [Chris' Coffee regulator](https://www.chriscoffee.com/products/pressure-regulator-valve) ·
[Espresso Parts 30 PSI](https://www.espressoparts.com/products/30-psi-inline-water-pressure-regulator) ·
[JG ball valve PPSV040808W](https://www.amazon.com/Speedfit-Connect-Plastic-Plumbing-PPSV040808W/dp/B003YKF2E2) ·
[LiquaGen RO float valve](https://www.amazon.com/LiquaGen-Reverse-Osmosis-Filtration-Systems/dp/B07DGX3NGB)

Spec'd lines total ≈ **$70–130** depending on regulator choice (excludes the deferred solenoid +
the reused Claryum filter / cold-water branch). Note: most espresso regulators (Chris'/Watts) ship
NPT or with JG; the **float valve is typically BSPP/male-thread** — keep a 1/4" NPT↔BSPP adapter +
fiber washers on hand for that joint.

**Existing infrastructure being reused (no purchase):** dedicated cold-water branch to kitchen,
Aquasana Claryum Direct Connect filter, 1/4" braided output line from filter.

## Installation steps

### 1. Pre-flight (do not skip)

- Run hardness/alkalinity test on Claryum output. Record numbers.
- If outside targets → stop, add softening cartridge to BoM, then resume.

### 2. Plan the route

- Measure from existing 1/4" braided output to where the Mini V2 will sit.
- Service loop (~12" slack) near the machine so it can be pulled forward without disconnecting.
- Avoid 90° kinks in LLDPE — use elbow fittings or wide sweeps.

### 3. Build the regulation stack

In order, downstream of the existing Aquasana output:

1. **Inline shut-off** (close it now while building the rest).
2. **NC solenoid valve** — installed upstream of the regulator and the long run to the reservoir, so
   a downstream hose burst still triggers shut-off when the machine cycles off. Flow arrow on the
   valve body points downstream. Verify thread standard (NPT vs. BSPP) matches the adjacent
   fittings; transition with a brass adapter + PTFE tape (NPT) or fiber washer (BSPP) as needed.
3. **Pressure regulator** — bench-set to ~25 PSI **before** mounting.
4. **1/4" line** continuing to the machine.

Mount the regulator stack against the cabinet wall — don't let it hang from the line. Mount the
solenoid coil-up so any seal weep drips clear of the coil and electrical connection.

**Solenoid wiring** (recommended: smart-plug path):

- Single switched outlet (smart plug) feeds both the machine's power cord and the solenoid coil
  supply.
- If the solenoid is **110 V AC**: wire the coil leads into a small junction box fed from the
  switched outlet. No transformer. Use a proper strain relief and grounded box — this is mains.
- If the solenoid is **24 V DC**: plug a 24 V DC wall-wart into the switched outlet, then run the
  low-voltage leads to the coil. Easier and lower-risk; preferred unless there's a reason not to.
- Result: machine "on" ⇒ solenoid energized ⇒ valve open. Machine "off" or power loss ⇒ solenoid
  de-energized ⇒ valve closed.

### 4. Modify the reservoir for the float valve

- Pull Mini V2 reservoir out.
- Drill a hole in the **lid** (not the wall) for the float-valve thread. Step bit + lubricant; lid
  is plastic, easy.
- Mount the float valve through the lid; tighten with supplied gasket/washer.
- Verify the float arm swings freely without contacting walls or the bottom magnet of the existing
  low-water switch.
- Set float position to close ~1/2" below the existing max-fill line.

### 5. Connect line to float valve

- Route 1/4" LLDPE from regulator output to reservoir.
- Push-to-connect (John Guest) at the float-valve end so the tank can be lifted out for cleaning
  without breaking the joint.
- Re-seat the reservoir.

### 6. Pressurize and verify

- Smart plug **on** (solenoid energized, valve open). Open inline shut-off slowly, watch every
  joint.
- Float valve fills to set level and **closes cleanly** (no oscillation / hammering).
- If hammering: drop regulator setpoint in 5 PSI increments until quiet.
- Drain the tank manually to confirm the existing low-water switch still trips.
- **Solenoid functional check**: with the inline shut-off open, smart plug **off** — confirm no flow
  downstream of the solenoid (watch the float valve; tank should not refill as you draw it down).
  Then smart plug **on** — confirm flow resumes within ~1 second.

### 7. Wet test

- Boilers to temperature. Pull a single shot. Tank refills as level drops; no hammer.
- 30s blank flush. Tank refills concurrently without overfilling.
- 5–10 consecutive shots over 15 minutes. Steady operation.

### 8. Burn-in (24h)

- Leave on the line under static pressure for 24h (machine off OK — line still pressurized).
- Inspect every joint for weep / drip.
- Re-tighten any wet joint; re-test.

## Reserved future enhancements

- **Drain plumb**: drill the drip tray for a hose barb, run silicone hose to a drain on continuous
  downhill slope. Independent workstream.
- **Softening upgrade**: if hardness creeps up (annual re-test), add Pentair Claris or BWT Bestmax
  cartridge upstream of regulator stack, downstream of Claryum.
- **Home Assistant integration of the smart plug**: schedule, away-mode auto-off, leak-sensor
  triggered shutoff. The plug from Phase 1 is already HA-compatible; this is a software-only
  follow-up.

## Exit Criteria

- [ ] Pre-install: hardness ≤60 ppm, alkalinity 40–80 ppm, chloride <30 ppm at Claryum output.
      Numbers recorded.
- [ ] Inline shut-off closes cleanly with full water-flow stop downstream.
- [ ] Regulator gauge reads 20–25 PSI under static line pressure.
- [ ] Float valve fills to set level and closes without hammering.
- [ ] Solenoid: smart-plug off ⇒ no downstream flow; smart-plug on ⇒ flow within ~1 s. Pulling the
      wall outlet (simulated power loss) also closes the valve.
- [ ] Existing low-water switch trips when tank is manually drained.
- [ ] No leaks at any joint after 24 hours of static line pressure.
- [ ] 5+ consecutive shots pulled with steady tank refill.

## Progress

- [x] Researched s1cafe.com / home-barista.com community approaches
- [x] Decided: reservoir float-fill (not inlet plumb) for vibe-pump robustness
- [x] BoM scoped against existing Aquasana Claryum infrastructure
- [ ] Buy parts (incl. NC brass solenoid + smart plug + coil supply)
- [ ] Test water hardness at Claryum output
- [ ] Build regulation stack (shut-off → solenoid → regulator)
- [ ] Wire solenoid via smart plug; bench-test open/close before plumbing
- [ ] Modify reservoir lid; mount float valve
- [ ] Wet test
- [ ] Solenoid power-cycle + power-loss shutoff verified
- [ ] 24h burn-in observation
- [ ] Document as-built (regulator setpoint, line route, water test numbers, solenoid model/coil V)

## Sources

- [LUCCA A53 Mini / Mini Vivaldi — Clive Coffee Help Center](https://support.clivecoffee.com/en/lucca-a53-mini-mini-vivaldi)
- [LUCCA A53 Mini Vibratory Pump Replacement (pump access reference)](https://support.clivecoffee.com/en/la-spaziale-lucca-a53-mini-mini-vivaldi-vibratory-pump-replacement)
- [LUCCA A53 manual (PDF)](https://ep-shopify.s3.amazonaws.com/related-documents/lucca/lucca-a53-manual.pdf)
- [Vivaldi II / Lucca A53 plumb thread — s1cafe.com](https://www.s1cafe.com/viewtopic.php?t=2231)
- [Tank-version Vivaldi plumb conversion — s1cafe.com](https://www.s1cafe.com/viewtopic.php?t=2376)
- [How to plumb the La Spaziale S1 Vivaldi II — home-barista.com](https://www.home-barista.com/espresso-machines/how-to-plumb-la-spaziale-s1-vivaldi-ii-t5386.html)
- [Aquasana Claryum Direct Connect — contaminant reduction spec](https://www.aquasana.com/water-filtration-systems/under-counter-water-filters/claryum-direct-connect-water-filter-system)
