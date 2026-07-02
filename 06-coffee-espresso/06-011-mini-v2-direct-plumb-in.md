---
title: 'Mini Vivaldi II Direct Plumb-In via Reservoir Float-Fill'
number: '06-011'
category: 'coffee-espresso'
difficulty: 'Easy'
time_commitment: '1-2 days'
target_skills: 'Water Plumbing, Pressure Regulation, NPT/Push-Fit Fittings'
status: 'In Progress'
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
                        ⟵ upstream shutoff (your Claryum-feed valve) = SERVICE isolation
[Aquasana Claryum output] ── 3/8" NPT
        │   [JG PP010823W · 1/4" push × 3/8" NPT]
        │
        ├─ ( 1/4" ball valve )     ─ OPTIONAL local cutoff (upstream valve already isolates)
        │
        ├─ 1/4" NC brass solenoid  ─ 24 V, fail-closed; coil on the machine's SWITCHED-MAINS
        │   [2× JG PP010822WP]        rail → open only when the machine is ON
        │
        ├─ 1/4" pressure regulator ─ gauged, ~20–25 PSI (mount to the wall, not the line)
        │
        └─ 1/4" LLDPE tube ─ ~12" service loop, routed OVER the drawer rim
                │
                ▼
           ══╡ FLOAT VALVE ╞══  stem + gasket + locknut through a ~5/8" hole in the REAR
                │               WALL; closes ~½" below the rim
                ▼
           RESERVOIR (five-sided open drawer)
           · low-water float switch UNTOUCHED (dry-run protection)
           · floor outlet → pump  (keep the float-arm arc clear)
                │
                ▼  gravity feed — exactly as stock
           [ vibe pump ] → brew boiler → group → cup
```

The Mini V2's existing **low-water float switch** (the magnetic switch that disables the pump when
the tank is dry) is **untouched** by this work and continues to provide dry-run protection. The new
mechanical **float valve** controls fill, not pump enable.

> **See also:** [Mini V2 modifications at a glance](_reference/mini-v2-modifications.md) —
> before/after of the fluid + electrical paths across this project and
> [06-001](06-001-lucca-a53-mini-leva-firmware-integration.md) (one shared teardown).

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
6. Fail-safe on power loss **and machine-off**: the coil is fed from the machine's switched-mains
   rail (BoM 2a), so the NC valve closes whenever the machine is switched off or loses power — no
   dependence on a smart plug or the wall outlet being cut.

## Pre-flight: verify source-water hardness

The **Aquasana Claryum is a contaminant/taste filter (chlorine, chloramine, PFAS, lead, etc.) — it
does not soften water.** It does not remove calcium / magnesium hardness or significantly reduce
alkalinity. La Spaziale boilers don't auto-flush, so scale matters here.

> **Resolved 2026-07-01 — current SFPUC data confirms soft water.** SFPUC weekly monitoring for the
> week of 6/28/2026 (from Colleen Taggart, `CTaggart@sfwater.org`, the current SFPUC water-quality
> contact; Table 9) puts **Presidio Heights (Lombard zone)** on the northern Hetch Hetchy blend zone
> (Lombard reservoir; Sutro nearly identical): **hardness 18, alkalinity 22, chloride 8 mg/L** —
> essentially unchanged from 2017 (22 / 27 / 7) and comfortably inside the espresso-safe targets
> below. Hetch Hetchy is very soft and stable year-to-year; the Claryum doesn't alter these three,
> so the distribution figures proxy the Claryum output. **Verdict: soft water → Claryum sufficient,
> no softening cartridge, low scale risk.** (Only College Hill / HTWTP-fed neighborhoods — Bernal,
> Glen Park, parts of Mission/Noe — run harder ~56; not this address.) Alkalinity ~22 sits below the
> 40–80 taste band — a remineralization / dial-in nicety, not a plumb-in blocker.

**To verify independently (optional):**

1. API GH/KH titration kit (~$8) — reads hardness + alkalinity directly. (A TDS meter is only a
   rough proxy; the Claryum doesn't reduce TDS, so its reading ≈ tap.)
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
line between the Aquasana output and the reservoir float valve. In this build (a US
plumber-installed Claryum line) every threaded joint is **NPT**, sealed with PTFE tape — **no BSP,
no compression, no fiber washers**. Three transitions need an NPT↔push adapter; everything else is
1/4" John Guest push-fit:

| Joint                                         | Thread             | Adapter                                          |
| --------------------------------------------- | ------------------ | ------------------------------------------------ |
| Braided Claryum output                        | 3/8" NPT female    | JG **PP010823W** (1/4" push × 3/8" NPT male)     |
| Solenoid inlet + outlet                       | 1/4" NPT female ×2 | 2× JG **PP010822WP** (1/4" push × 1/4" NPT male) |
| Ball valve · regulator · float valve · tubing | 1/4" push-fit      | none — native                                    |

⚠️ Verify your own line before buying: confirm the Claryum output is 3/8" NPT (read the hose label /
the male port it threads onto). European machines often use **BSP** instead — if so, swap the
braided adapter for the BSP equivalent.

| #   | Item                                                                  | Spec                                                                                                                                            | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| --- | --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | 1/4" inline shut-off ball valve **(optional)**                        | Full-port, push-to-connect or compression                                                                                                       | **Optional.** An **upstream shutoff (e.g. your Claryum-feed valve)** already covers service isolation, and the NC solenoid handles automatic shutoff — so a local valve is redundant-but-convenient. [John Guest PPSV040808W](https://www.amazon.com/Speedfit-Connect-Plastic-Plumbing-PPSV040808W/dp/B003YKF2E2) (~$8) if you want a cutoff right at the stack.                                                                                                                                                                                                                                                                                                                                                                                                             |
| 2   | NC brass solenoid valve                                               | 1/4" NPT, normally-closed, brass, Viton (FKM), direct-acting (0 psi min), 24 V DC; **continuous-duty coil** if the machine is ever left on >8 h | **Continuous-duty (recommended):** [WIC 2BCK-1/4-D](https://wicvalve.com/1-4-Inch-Fast-Response-Direct-Acting-Electric-Solenoid-Valve-2BCK-1-4-D.htm) (1/4" NPT, 24 V DC, 100% ED coil, ~$30–45). Short-session only: [U.S. Solid 1/4" 24 V DC brass NC](https://ussolid.com/products/u-s-solid-electric-solenoid-valve-1-4-24v-dc-solenoid-valve-brass-body-normally-closed-viton-seal-html) (~$16) — coil is **not** continuous-duty (>8 h energized risks burnout). Both are 1/4" NPT female → need 2× PP010822WP adapters + PTFE tape. Install **flow-arrow toward the reservoir**, observe DC polarity. Not NSF-61 (fine for a cold feed). NC = fail-closed on power loss.                                                                                              |
| 2a  | **Machine-on interlock** — switched-mains tap (⚠️ _not_ a smart plug) | Splice off the machine's **switched-mains rail** (live only when its own power switch is on)                                                    | ⚠️ **Correction:** a smart plug does **not** gate this safely — outlet power ≠ machine-on (the Mini V2 has its own power switch), so the solenoid would sit open with the machine off. Feed the coil supply (row 2b) from the machine's switched-mains rail — the same rail the **ito** module powers from (its **N/L** input, "only live when machine on"; see [06-001](06-001-lucca-a53-mini-leva-firmware-integration.md) connector map). Machine on ⇒ coil live ⇒ valve open; off / power loss ⇒ NC closed. Tap L/N **downstream of the machine's power switch** (full mains — not a logic rail, not ito's supply). Cleanest done during the ito install. A smart plug or ESP32 is **optional**, only for a Home Assistant layer (leak-sensor auto-shutoff, scheduling). |
| 2b  | Solenoid coil supply                                                  | 24 V DC wall-wart, **≥2 A** (covers ~1.8 A inrush — a 1 A supply can brown out at pull-in)                                                      | Solenoid has bare lead wires → splice to the wall-wart (cut the barrel or use a barrel-to-screw-terminal adapter); observe polarity. **Power the wall-wart from the machine's switched-mains rail (row 2a), not a wall outlet**, so the coil is live only when the machine is on. Mount wiring in a small junction box near the machine's mains entry.                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 3   | Pressure regulator                                                    | 1/4" JG push-fit, **gauge'd**, set to ~20–25 PSI                                                                                                | **Recommended: [Chris' Coffee regulator w/ gauge](https://www.chriscoffee.com/products/pressure-regulator-valve)** (~$100, JG 1/4") — ships preset ~50 psi, **dial down to ~25 before trusting it**; the gauge is what lets you verify, which is why it beats the value pick for error-proofing. Value alt: [JG Micro regulator](https://www.wb.coffee/shop/john-guest-micro-pressure-regulator-valve-1-8-1-4-43588) (~$29; 0–4 bar adjustable, **no gauge → set blind**, ships from the EU). Skip the [Flojet → JG kit](https://www.espressoparts.com/products/flojet-water-pressure-regulator-to-john-guest-kit) — non-adjustable 1750-series pump regulator, vendor-rated "temporary use."                                                                                |
| 4   | Reservoir float valve                                                 | Plastic RO float valve with a threaded mounting shank + 1/4" inlet                                                                              | [Example: LiquaGen RO float valve](https://www.amazon.com/LiquaGen-Reverse-Osmosis-Filtration-Systems/dp/B07DGX3NGB) (~$10). Brass/quarter-turn unnecessary — service shut-off is line 1. The reservoir is a **five-sided open-top drawer (no lid to drill)**, so mount the valve to a bracket on a wall/rim and drape the supply line over the open rim — no vessel penetration. Close ~1/2" below the rim. **Test-fit before committing** (see install §4).                                                                                                                                                                                                                                                                                                                |
| 5   | 1/4" LLDPE polyethylene tubing                                        | **1/4" OD (0.25") imperial — NOT 6 mm**                                                                                                         | ⚠️ JG sells imperial _and_ metric; 6 mm tube leaks in a 1/4" collet. Buy 1/4" OD. Routes easier than braided; takes JG fittings cleanly.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 6   | Push-to-connect fittings (John Guest **1/4" imperial**)               | A couple of elbows for corners + spare collets                                                                                                  | Run is linear (no tee needed). **1/4" imperial, not 6 mm.** Push-to-connect at any joint that may need service.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 7   | NPT thread adapters + PTFE tape                                       | 1× PP010823W (3/8" NPT) + 2× PP010822WP (1/4" NPT), all × 1/4" push                                                                             | Bridge the braided line + solenoid into the push-fit chain (see the adapter table above). **Plastic — hand-tighten with PTFE tape, don't wrench** (cracks). No BSPP fiber washers needed in this build.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 8   | Water test: GH/KH kit (+ optional TDS meter)                          | One-time use                                                                                                                                    | [API GH & KH titration kit](https://www.amazon.com/API-TEST-Freshwater-Aquarium-Water/dp/B003SNCHMA) (~$8) measures hardness + alkalinity — the numbers that matter. Claryum doesn't reduce TDS, so a TDS meter (~$15) is only a rough proxy. Pre-flight check.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |

### Orderable picks (concrete products)

Every line item in the BoM table above links to a concrete product. Order-ready list, grouped by
vendor (robust path: continuous-duty solenoid + gauge'd regulator):

**Amazon (one cart):**

| Part                  | Pick                                                  | ~Price |
| --------------------- | ----------------------------------------------------- | ------ |
| Braided→chain adapter | JG PP010823W (1/4" push × 3/8" NPT male)              | $6     |
| Solenoid adapters ×2  | JG PP010822WP (1/4" push × 1/4" NPT male), 5-pk       | $8     |
| PTFE tape             | any                                                   | $2     |
| Ball valve (optional) | JG PPSV040808W — skip if you have an upstream shutoff | $8     |
| Float valve           | LiquaGen, threaded stem + nut, 1/4" push (B07DGX3NGB) | $10    |
| 1/4" LLDPE tubing     | 25 ft roll — **1/4" OD, not 6 mm**                    | $10    |
| JG fittings           | elbows + spare collets (1/4" imperial)                | $10    |
| Smart plug (optional) | Kasa EP25 — only for the optional ESP32/HA layer      | $13    |
| 24 V DC wall-wart     | **≥2 A** DC supply for the coil                       | $12    |
| Water test            | API GH/KH titration kit (B003SNCHMA)                  | $8     |

**WIC Valve:** continuous-duty solenoid WIC 2BCK-1/4-D (1/4" NPT, 24 V DC) — ~$30–45. **Chris'
Coffee:** gauge'd JG regulator — ~$100.

**Robust-path total ≈ $230** (continuous-duty solenoid + gauge'd regulator). Dropping to the EU
JG-micro regulator saves ~$70. All threaded joints are NPT (PTFE tape) — no BSP, no compression, no
fiber washers. Excludes the reused Claryum filter / cold-water branch.

**Existing infrastructure being reused (no purchase):** dedicated cold-water branch to kitchen,
Aquasana Claryum Direct Connect filter, braided output line from filter terminating in a **3/8" NPT
female** fitting (this build's measured value — verify yours).

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

**Solenoid wiring** (switched-mains-rail interlock — _not_ a smart plug):

- ⚠️ A smart plug on the wall outlet does **not** work: the Mini V2 has its own power switch, so
  outlet power ≠ machine-on. The solenoid would open whenever the plug is on, even with the machine
  switched off — defeating the fail-safe.
- Instead, power the coil from the machine's **switched-mains rail** — the L/N that goes live only
  when the machine's own power switch is on (the same rail the ito module powers from; see
  [06-001](06-001-lucca-a53-mini-leva-firmware-integration.md) connector map). Tap L/N **downstream
  of the machine power switch**, at the mains entry — full mains, not a logic rail, and not ito's
  supply (which has no spare current).
- If the solenoid is **110 V AC**: wire the coil leads (via a small strain-relieved, grounded
  junction box) directly across the switched-mains rail. This is mains — treat it as such.
- If the solenoid is **24 V DC**: feed a 24 V DC wall-wart from the switched-mains rail, then run
  the low-voltage leads to the coil. Lower-risk; preferred.
- Result: machine on ⇒ coil live ⇒ valve open. Machine off **or** power loss ⇒ NC valve closed.
- ito can't drive the valve itself (both its on-board relays are committed to the pump and the 3-way
  brew valve), so the valve keeps its own coil supply off the rail. Optional: an ESP32 tapping the
  same rail adds Home Assistant control (leak-sensor auto-shutoff, scheduling) — not required for
  the fail-safe.

**Two separate supplies — don't confuse them.** The 24 V solenoid coil runs off its **own 24 V DC
supply**, _not_ the ito's 5 V PSU (the ito's HLK-PM01 is **5 V / 0.6 A** — wrong voltage and far too
little current for a solenoid). Both simply hang off the **same switched-mains rail**:

```text
power switch → SWITCHED-MAINS RAIL   (120 VAC, live only when machine ON)
      ├─► ito HLK-PM01 → 5 VDC 0.6 A → ito module         (ito's own supply)
      └─► your 24 VDC PSU → 24 V solenoid coil            (the interlock)
machine OFF → rail dead → 24 VDC PSU off → NC coil de-energized → VALVE CLOSED
```

Wire the 24 V supply's **AC input downstream of the power switch** (onto the switched-mains rail) so
the coil is energized only when the machine is on — that's what makes it fail-closed. Cleanest
method: **hardwire the wall-wart** — crack its case, wire its AC input (rated 100–240 V, so 120 V is
fine) to the switched-mains at the control board, and its 24 V DC output to the coil (**observe
polarity**). ⚠️ A cracked-open wall-wart is a bare mains PCB — **enclose it in a junction box**;
don't leave it floating.

### 4. Mount the float valve (through-wall)

The reservoir is a plain rectangular **open-top tub**
([Clive part](https://clivecoffee.com/products/la-spaziale-water-tank-plastic-housing), ~$65) with
one outlet hole in the floor and the existing low-water float inside; the "retaining cross" is
**non-structural**. So mount the
[LiquaGen float valve](https://liquagen.com/products/liquagen-float-valve-for-reverse-osmosis-water-filtration-systems)
the way it's designed — its **threaded stem + locking nut through a hole in an upper wall**, float
arm swinging inside, 1/4" push inlet outside. Fixing the valve directly to the vessel is the most
rigid mount; the tub being a cheap replaceable part makes the one hole low-stakes and revertible
(keep the stock tub).

- **Confirm the stem size** with calipers. 1/4" RO float valves standardize on a **5/8" mounting
  hole** (some 1/2") — verify the LiquaGen before drilling.
- **Dry-fit and clock first — before the bit touches plastic.** Hold the valve against the **rear
  wall** (most cabinet clearance, natural tube entry), high enough to close ~1/2" below the rim, and
  swing the float through its **full arc**: confirm it clears the existing low-water float and the
  walls, and that neither valve nor boss sits over the **floor outlet**. Mark center.
- **Drill with a step bit, slow.** A titanium step bit reaching 5/8"+ in 1/16" steps (e.g. LaserBest
  90588, 1/4"–3/4") lets you sneak up to a snug hole; the single-flute Irwin Unibit #2 is cleaner in
  plastic but stops at 1/2". Low RPM — too fast melts, too aggressive cracks the thin wall. Back the
  wall with a scrap block; sneak up to a **snug** hole (the gasket seals against the edge — don't
  oversize); deburr both faces.
- **Mount:** stem through the hole, **rubber gasket between the valve base and the wall**, locking
  nut on the outside — snug by hand (plastic; don't wrench). Position to close ~1/2" below the rim.
- **Check outside clearance:** the 1/4" inlet + tube must clear the cabinet and still let the drawer
  slide home. Leave a service loop and a **push-fit at the valve** so the drawer pulls forward /
  lifts out for cleaning.
- Re-verify the float arm swings free through full travel, clear of the low-water float and walls.

_No-drill alternative (not chosen): a PETG bridge spanning the tub's short dimension takes its
rigidity from the beam rather than the tub — use only if you won't modify the tub._

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

## Compatibility with pressure profiling (06-001)

This plumb-in is **profiling-friendly** — and that's an argument _for_ the float-fill approach, not
just a coincidence:

- [06-001](06-001-lucca-a53-mini-leva-firmware-integration.md) (ito + `leva!` pressure profiling)
  controls the **vibratory pump** via phase-angle, and its pressure loop assumes the pump draws from
  an **atmospheric inlet** — exactly what float-fill preserves. An **inlet-side direct plumb**
  (pressurized pump inlet) would change pump behavior and complicate profile calibration. So the
  robustness choice here is also the right choice for a future profiler.
- leva!'s **flow meter installs on the tank→pump line** (before the pump). Float-fill leaves that
  line intact — the meter goes downstream of where the float valve tops up the tank, unaffected.
- Heads-up for later: the Mini V2 has a **brew over-pressure bypass valve** returning water to the
  pump inlet. It's irrelevant to this plumb-in but matters for profiling (set it >9 bar; see
  06-001).
- **The fill-solenoid interlock reuses ito's wiring:** power the coil from the machine's
  switched-mains rail — the same L/N that feeds ito's **N/L** input. ito can't drive the valve (both
  its relays are taken by the pump + 3-way valve), so the valve gets its own coil supply off that
  rail. Tap it during the ito install to avoid opening the machine twice.

Net: do this project freely now; it does not foreclose — and arguably enables — 06-001 later.

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
- [ ] Solenoid: machine off ⇒ no downstream flow; machine on ⇒ flow within ~1 s. Pulling mains
      (simulated power loss) also closes the valve.
- [ ] Existing low-water switch trips when tank is manually drained.
- [ ] No leaks at any joint after 24 hours of static line pressure.
- [ ] 5+ consecutive shots pulled with steady tank refill.

## Progress

- [x] Researched s1cafe.com / home-barista.com community approaches
- [x] Decided: reservoir float-fill (not inlet plumb) for vibe-pump robustness
- [x] BoM scoped against existing Aquasana Claryum infrastructure
- [x] Buy parts (incl. NC brass solenoid + coil supply; smart-plug/ESP32 optional, HA layer only)
- [x] Water quality confirmed soft (SFPUC current 6/2026, Presidio Heights: H18/Alk22/Cl8) — no
      softener; optional re-verify at Claryum output
- [ ] Build regulation stack (shut-off → solenoid → regulator)
- [ ] Wire solenoid coil to machine's switched-mains rail; bench-test open/close before plumbing
- [ ] Drill rear-wall hole (~5/8", step bit); mount float valve with gasket + locknut
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
- [Aquasana Claryum Direct Connect — contaminant reduction spec](https://www.aquasana.com/under-sink-water-filters/claryum-direct-connect-100329886.html)
