---
title: 'Rolled Aluminium Elsinore Cabinet (5052 Shell)'
number: '01-021'
category: 'audio-midi'
difficulty: 'Hard'
time_commitment: 'Months'
target_skills:
  'Sheet-metal DfM, plate rolling, TIG welding, constrained-layer damping, CAD (Onshape)'
status: 'Not Started'
depends_on:
  - project/01-017
---

# Rolled Aluminium Elsinore Cabinet (5052 Shell)

## Description

Build a **curved Elsinore cabinet as a rolled 5052 aluminium shell** — the **Magico M6** direction,
executed at a scale and cost that is actually reachable. A rolled shell with machined end caps and a
separate flat baffle.

**Curvature is what makes this viable.** Matching 1" Baltic birch on _flat-panel_ stiffness needs
~12 mm aluminium — ~48 kg of metal per cabinet. A curved shell converts bending into membrane
stress, so **3–8 mm** plausibly suffices. See `01-019` for the full analysis.

## Shared geometry — profile D (DECIDED)

Both curved-cabinet projects target the **same section**, derived from the as-built cabinet in
`01-017` (Onshape "Elsinore v6.1"). Only fabrication differs.

| Constraint             | Value                                   | Why fixed                                                 |
| ---------------------- | --------------------------------------- | --------------------------------------------------------- |
| Baffle width           | **228.6 mm**                            | Joe's driver-array spacing is part of the acoustic design |
| Internal height        | **1099.8 mm**                           | as-built                                                  |
| Internal volume        | **78.1 L gross**                        | matches the existing cabinet — no re-tuning               |
| Rear radius            | **114.3 mm** (full bullnose)            | most volume-efficient curve; one constant radius          |
| Internal depth         | **335.2 mm**                            | solved                                                    |
| Straight run each side | **220.9 mm**                            | before the rear semicircle                                |
| Developed length       | **1029.4 mm** (wrap 800.8 excl. baffle) |                                                           |

### The curve is dimensionally free

|                | Existing | Curved       |
| -------------- | -------- | ------------ |
| External depth | 380.9 mm | **379.6 mm** |

**1.3 mm shallower.** The bullnose shell replaces the flat rear panel and recovers exactly the depth
the curve costs. Same footprint, same volume, same baffle — curved.

### Sheet yield

Shell blank **1100 × 801 mm** → **3 per 1220 × 2440 sheet**, and two are needed. **One standard
sheet does both cabinets** with a spare for a test roll.

## Fabrication notes (from `01-019` research)

- **Alloy: 5052-H32.** Min bend radius ~1.5t at 3–6 mm; the 114.3 mm target is far inside the 6–10 ×
  t crack floor. Non-heat-treatable, so it avoids the HAZ softening that costs 6061-T6 its temper
  within ~15 mm of a weld.
- **The binding constraint is the shop's top-roll diameter** (≈1.5× for a one-pass roll), not the
  material.
- **Springback 1.5–4°** — for two units expect trial-and-fit, which is what the spare blank is for.
- ⚠️ **Neither JLCPCB nor PCBWay offers roll bending.** This goes to a dedicated plate-rolling shop.

## Rolling schedule — profile D is piecewise, not one radius

⚠️ **Profile D is a Bézier: curvature varies continuously.** A plate roller cannot do that in one
pass — it holds one radius per setting. The earlier stadium section was a single constant radius;
**that property was given up when the bulge was adopted, and the cost is a multi-pass rolling
schedule.**

**This constrains only this project.** For bent lamination (`01-020`) a varying radius is free — the
former defines whatever curve is cut into it. It is one of the clearest practical differences
between the two routes.

### Measured curvature along the top outline (396 mm of arc, baffle → centreline)

| Along      | Position                   | Radius                      |
| ---------- | -------------------------- | --------------------------- |
| 0–13 mm    | leaving the baffle         | ~281–305 mm                 |
| 33–66 mm   |                            | 343–406 mm                  |
| 134 mm     | widest point               | **496 mm** (flattest)       |
| 201 mm     |                            | 480 mm                      |
| 263 mm     |                            | 343 mm                      |
| **315 mm** | **Bézier → stern tangent** | **discontinuity: 343 → 80** |
| 315–396 mm | stern                      | **80 mm exactly**           |

**Real range is 80–496 mm.** Well inside 5052's crack floor (6–10 × t = 24–40 mm at 4 mm), so
nothing here is a tight bend.

_(An earlier reading of "7 mm minimum radius" was a numerical artifact — a three-point circle fit
straddling the curvature discontinuity. Exactly one sample out of 1199. Not a real feature of the
geometry.)_

### Practical decomposition — 3 rolled sections per side + flat baffle

Break at curvature changes, not at equal lengths (equal-length segmentation gives poor fits —
spreads of ±150 mm were measured).

| Section                  | Arc     | Roller setting      | Notes             |
| ------------------------ | ------- | ------------------- | ----------------- |
| 1 — baffle to mid-bulge  | ~135 mm | **R ≈ 320 mm**      | leaves the baffle |
| 2 — mid-bulge to tangent | ~180 mm | **R ≈ 460 mm**      | flattest part     |
| 3 — stern                | ~81 mm  | **R = 80 mm exact** | already constant  |

**The section-1/2 and 2/3 boundaries are where seams belong anyway** — the 2/3 boundary is a genuine
curvature discontinuity, so a weld or joint there is invisible in a way it would not be mid-curve.

⚠️ **The curvature discontinuity may show in a gloss finish.** Tangent-continuous (G1) but not
curvature-continuous (G2), so a reflection sweeping across it will kink. If that matters, the fix is
a G2 blend at the tangent point — which changes the section slightly and must be re-solved for
volume.

## ⚠️ The unsolved problem is damping, not stiffness

Curvature raises panel resonance **in frequency**; it does not lower its **Q**. Aluminium still
rings. **Constrained-layer damping on the inner face is non-negotiable** and is the single thing
that decides whether this beats 1" Baltic birch or embarrasses it. Verify by measurement —
accelerometer or nearfield panel measurement — not by assertion.

## Damping

**Decided in `01-020` — bare curved walls, damped top and bottom caps, fill set by impedance
measurement.** It is a section decision, not a material one: profile D's flat parallel caps leave a
161.5 Hz height mode the curve cannot touch, and removing fill raises both Fb and Ql. Port length is
cut last, to the measured Fb.

## Open questions

- Wall thickness: 3, 4, 5 or 6 mm — trades mass, cost and how much CLD is needed
- CLD spec: viscoelastic layer plus constraining skin, or bitumen tiles
- Baffle: aluminium (matching) or wood (damped, and reuses the existing method)
- End caps: CNC plate, and do they carry the internal bracing
- Finish: bead-blast and anodise, or raw
- Whether a **taper** is wanted — rolling can cone, but it complicates every step

## Exit Criteria

- [ ] Onshape model (import `_reference/curved-cabinet/section-shell-4mm.dxf`) of the shell at the
      shared geometry
- [ ] Flat pattern (developed blank) generated and checked against sheet size
- [ ] Plate-rolling shop identified; top-roll diameter confirmed against 114.3 mm
- [ ] Test roll on the spare blank; springback measured and compensated
- [ ] Damping strategy specified **and measured** against the birch cabinet
- [ ] One shell rolled, seam welded, caps fitted
- [ ] Internal volume verified against 78.1 L; Fb measured

## Progress

- [x] Shared section geometry solved
- [x] Parametric tool + DXF emitted — `_reference/curved-cabinet/`
- [x] Alloy, radii, sheet yield researched (`01-019`)
- [ ] Onshape model
- [ ] Shop identified

## Geometry tool

**`_reference/curved-cabinet/`** — parametric solver emitting DXF for Onshape sketch import:
internal section, shell at thickness, lamination former (with springback allowance) and the rolling
flat pattern. Run `python3 section.py`.

## References

- Crossover + as-built cabinet: [`01-017`](01-017-elsinore-passive-crossover-refinement.md)
- Design study and fabrication comparison: [`01-019`](01-019-aluminium-curved-elsinore-enclosure.md)
- Wood counterpart: [`01-020`](01-020-laminated-curved-elsinore-cabinet.md)
