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
