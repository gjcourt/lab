---
title: 'Laminated Curved Elsinore Cabinet (Bent Lamination, GamuT-style)'
number: '01-020'
category: 'audio-midi'
difficulty: 'Hard'
time_commitment: 'Months'
target_skills: 'Bent lamination, form/buck making, vacuum pressing, veneer work, CAD (Onshape)'
status: 'Not Started'
depends_on:
  - hardware/table-saw
  - project/01-017
---

# Laminated Curved Elsinore Cabinet (Bent Lamination, GamuT-style)

## Description

Build a **curved Elsinore cabinet from bent-laminated Baltic birch**, in the manner of the **GamuT
Zodiac** — thin plies form-pressed over a curved former. The Zodiac uses _"nearly 30 layers of fine
wood, glued together and formed under over a ton of pressure"_, built by **Kvist of Denmark, a
furniture manufacturer**.

**This is the route that matches existing capability.** The first Elsinore pair was built by hand in
1" Baltic birch. Bent lamination needs a former, thin plies and pressure — no die, no minimum order,
no offshore supplier, no springback trial-and-fit with a plate roller. The **mappa burl** is still
unused and is the obvious outer veneer.

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

## Why this route

- **No tooling cost.** A former is shop-made from MDF or ply offcuts.
- **Any curve is free.** Unlike rolling, a varying radius costs nothing — the former defines it. A
  Magico-style taper is available if wanted.
- **Damping is inherent.** Wood is lossy where aluminium is high-Q. The panel resonance problem that
  dominates `01-021` largely does not exist here.
- **It is the same craft as the existing pair**, so the skill is proven.

## Sourcing and cost

Researched 2026-08-20. **Shell panel is 805.5 × 1099.8 mm = 9.54 sq ft each, 19.07 sq ft for the
pair** — but lamination multiplies that by the layer count.

### Plies — Aircraft Spruce, NOT a veneer house

**1/16″ (1.5 mm) 3-ply birch plywood, 4×8 sheets, ~$139.75** ($4.37/sq ft).
<https://aircraftspruce.com/catalog/wppages/domplywood2.php> They also list **0.8 mm Finnish
birch**, 24×48, $19.90.

Why aircraft ply rather than veneer:

- **Already cross-grain 3-ply** — dimensionally stable, far less prone to splitting over the bend
  than single-grain leaves.
- **Full 4×8 sheets** — panels cut without edge-joining. Veneer houses sell 6–15″ leaves that would
  need matching across the width.
- **Military-spec thickness consistency**, which matters when stacking 8–17 of them to a target
  wall.

⚠️ **VeneerSupplies (Joe Woodworker) cannot supply the core plies.** Their own site states they do
not sell thicker veneer, lumber or plywood. Raw stock is **0.55–0.6 mm**; paper-backed is a **0.015″
face on paper**, non-structural. "Bulk" is same-flitch _lots_ capped by flitch size, with no
wholesale tier and no grain match across lots. They remain the right vendor for glue and vacuum.

⚠️ **Bending ply / "wiggle wood" is not a structural core.** Reduced cross-banding for single-axis
flex, voidier than cabinet grade. Fine for a non-structural liner, not for the shell.

### Cost by wall thickness — this is the decision

| Wall      | Layers | Ply +15%  | Sheets | **Ply cost** | Glue         |
| --------- | ------ | --------- | ------ | ------------ | ------------ |
| 10 mm     | 7      | 154 sq ft | 5      | **$699**     | 5 lb $42.50  |
| **12 mm** | **8**  | **175**   | **6**  | **$838**     | 5 lb $42.50  |
| 15 mm     | 10     | 219       | 7      | $978         | 5 lb $42.50  |
| 18 mm     | 12     | 263       | 9      | $1,258       | 5 lb $42.50  |
| 25.4 mm   | 17     | 373       | 12     | $1,677       | 2 × 5 lb $85 |

**Do not default to 25.4 mm** just because the existing flat cabinet is 1″. A curved cross-grain
shell is far stiffer than a flat panel of equal thickness — the same argument that took the
aluminium route from 12 mm flat to 4 mm curved. **The wall thickness is an ~$840 decision and a test
lamination settles it.**

### Glue — Ultra-CAT PPR (urea-formaldehyde)

**5 lb $42.50 · 25 lb $151** — <https://veneersupplies.com/products/Ultra-CAT-PPR-Veneer-Glue.html>

⚠️ **Not PVA.** PVA creeps under sustained bending load; a laminated curve opens up over months and
years. This is the one adhesive choice with a documented failure mode specific to this application.
UF is a zero-creep thermoset.

Glue covers _panel_ area, not stacked area: 7 glue lines × 19.07 sq ft ≈ 134 sq ft, and 5 lb makes
~1 gallon covering 200–250 sq ft. **One pail does a 12 mm pair.**

**Buy the lightener** (+$8.60). UF glue lines cure dark and will read as brown stripes on pale birch
wherever the shell is cut — and on a curved cabinet the laminations are visible at every trimmed
edge.

### Vacuum press

|                                  |                                       |
| -------------------------------- | ------------------------------------- |
| Project V4 venturi kit           | **$344.50** — needs a compressor      |
| Excel 5 electric kit             | **$489.50**                           |
| DIY bag (poly + breather + tape) | ~$20 in materials vs ~$200 commercial |

Not strictly required — a two-part clamped caul is traditional — but at 805 × 1100 mm and 8+ layers,
vacuum gives far more even pressure, and UF's long open time suits it.

### Former

A **ribbed former** (profile stations + a bending-ply skin) uses ~2 sheets of ¾″ MDF plus skin. A
solid stacked buck would need ~58 layers of ¾″ MDF to reach 1099.8 mm — **4–6 sheets, $260–390, and
a great deal of cutting.** Rib it.

### Rough total, 12 mm wall

|                            |              |
| -------------------------- | ------------ |
| Plies, 6 sheets            | $838         |
| Ultra-CAT 5 lb + lightener | $51          |
| Vacuum, venturi + DIY bag  | ~$365        |
| Former, MDF + skin         | ~$150        |
| **Total**                  | **≈ $1,400** |

Mappa burl already owned. Baffle uses the existing 19.05 + 25.4 mm birch stack.

## Open questions

- **Ply thickness and count.** Thinner plies bend tighter and laminate stronger but multiply the
  glue-ups. At 114.3 mm radius, what is the thickest birch ply that will take the bend without
  springback or cracking?
- **Pressing method.** Vacuum bag vs clamped caul over the former. Vacuum is more even; a two-part
  caul is cheaper.
- **Glue.** PVA creeps under sustained load and can spring back over years; urea-formaldehyde or
  epoxy hold the curve. This matters more here than in flat work.
- **Baffle integration.** Does the flat baffle join the shell with a rebate, a spline, or a glued
  butt into a machined recess?
- **Damping philosophy** — Joe's 40–50% wool/Dacron fill vs the Zodiac's near-empty braced shell.
  See `01-019`; the two are incompatible and this is where it gets decided.

## Method

### 0. Test lamination FIRST — ~$280, and it decides everything

Two sheets of 1/16″ ply and a short former section. **Do not order the full quantity before this.**

It answers, in one afternoon:

- **Springback.** Laminate a test strip over a known radius, release it, measure what it opens to.
  That number is subtracted from the former radius for the real shell. It cannot be predicted — it
  depends on ply, glue, layer count and cure.
- **Does 1.5 mm take the R=80 stern?** That is the tightest radius on profile D — ~53× ply
  thickness, which should be comfortable, but confirm rather than assume.
- **Layer count for target stiffness.** Flex the test panel. This is the $840 question: 8 layers
  or 17.
- **Grain orientation.** Aircraft ply is stiffer along its face grain, so it bends more readily
  about one axis than the other. **Cut test strips both ways** and use whichever bends without
  complaint. This determines how panels are cut from the 4×8 sheets and therefore how many sheets
  you need.
- **Glue-line colour** with and without lightener, on the trimmed edge.

### 1. Former

Build **ribbed**, not solid: profile stations cut from ¾″ MDF on the CNC-less route (bandsaw +
template), spaced ~150 mm up the height, skinned with bending ply to give a continuous surface.

- Cut the stations to the **profile-D internal curve minus the measured springback**.
- The former is the **inside** of the shell, so it carries the internal 342.4 × 248 mm section.
- Wax or tape the skin — UF glue will bond to anything it touches.

### 2. Cut plies

Panels are **805.5 × 1099.8 mm** plus trim allowance — call it 850 × 1150. From a 4×8 sheet (1220 ×
2440), that yields **2 panels per sheet** with the long dimension along the 8-ft axis. Grain
direction per the test.

Cut all plies for one shell at once so they are identical.

### 3. Glue-up

⚠️ **This is the step with a hard time limit and no way to pause.**

- Mix Ultra-CAT to the sheet's ratio; note the pot life at your shop temperature.
- Roll glue on **both faces of each interface** — a laminate this thick is unforgiving of a dry
  line.
- Stack, align to a registration edge, and get it onto the former and under vacuum before pot life
  expires.
- **Consider two stages** — laminate half the layers, cure, then laminate the second half onto the
  first. Halves the time pressure, at the cost of one extra cure cycle and a mid-wall glue line. For
  12+ layers this is worth it.

### 4. Cure and release

Full cure per the glue spec — UF wants warmth; a cold shop extends it considerably. Release, and
**measure the actual radius against the target.** This is where the springback allowance is proved
or corrected before the second shell.

### 5. Trim and fit

- Trim to final height on the table saw with a sled, or by router against a straightedge.
- The **baffle joins the shell at the flat land** where the curve leaves tangent to the axis — that
  short parallel run exists precisely to give a mating surface rather than a knife edge.
- Fit top and bottom caps to the section profile.

### 6. Internals

Bracing and damping per `01-017` — but ⚠️ **the damping philosophy is undecided** (Joe's 40–50%
wool/Dacron fill vs the Zodiac's near-empty braced shell). Settle it before closing the box; it is
not reversible afterwards.

Crossover mounts on the cabinet floor, reachable through the driver cutouts, as in the existing
pair.

### 7. Mappa burl

**Last, and separately.** Burl is brittle and splits over a tight radius — it is ~0.5 mm decorative
veneer with no structural role. Apply to the cured shell, not in the main stack, and expect to
soften it first. The stern at R=80 is where it will fight you.

### Order of operations across both shells

Do the **test**, then **shell 1 completely** — including release and measurement — before starting
shell 2. If springback is off, only one shell is wrong.

## Exit Criteria

- [ ] Onshape model (import `_reference/curved-cabinet/former.dxf`) of the shell section at the
      shared geometry above
- [ ] Former design, with springback allowance, cut and trued
- [ ] Test lamination on scrap — confirm ply thickness, glue and press method
- [ ] Measured springback of the test piece, former corrected
- [ ] One shell laminated and trimmed to height
- [ ] Baffle joined, cabinet closed, internal volume verified against 78.1 L
- [ ] Fb measured and compared to the existing pair

## Progress

- [x] Shared section geometry solved
- [x] Parametric tool + DXF emitted — `_reference/curved-cabinet/`
- [ ] Onshape model
- [ ] Test lamination

## Geometry tool

**`_reference/curved-cabinet/`** — parametric solver emitting DXF for Onshape sketch import:
internal section, shell at thickness, lamination former (with springback allowance) and the rolling
flat pattern. Run `python3 section.py`.

## References

- Crossover + as-built cabinet: [`01-017`](01-017-elsinore-passive-crossover-refinement.md)
- Design study and fabrication comparison: [`01-019`](01-019-aluminium-curved-elsinore-enclosure.md)
- Aluminium counterpart: [`01-021`](01-021-rolled-aluminium-elsinore-cabinet.md)
