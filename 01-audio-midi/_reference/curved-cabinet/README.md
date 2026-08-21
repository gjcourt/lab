# Curved Elsinore cabinet — shared section geometry

One parametric model serving **both** curved-cabinet projects:

- [`01-020`](../../01-020-laminated-curved-elsinore-cabinet.md) — bent lamination
- [`01-021`](../../01-021-rolled-aluminium-elsinore-cabinet.md) — rolled aluminium

They share the section exactly and differ only in fabrication output. Design once, emit two
manufacturing packages, compare like for like.

## The section is a stadium

Choosing **rear radius = half the baffle width** makes the tangent lines parallel, so the profile
collapses to a **capsule**: flat baffle, two straight parallel sides, one semicircular rear.

That is not an aesthetic choice — it is simultaneously:

- **the most volume-efficient curve** for a given baffle and depth,
- **the cheapest to roll** — one constant radius, one roller setting, one springback figure to dial
  in,
- **the simplest former to cut** for lamination.

## Solved geometry

Anchored to the as-built cabinet from the Onshape model `Elsinore v6.1` (see
[`01-017`](../../01-017-elsinore-passive-crossover-refinement.md)).

|                     |                                                  |
| ------------------- | ------------------------------------------------ |
| Baffle width        | **228.6 mm** — FIXED, Joe's driver-array spacing |
| Internal height     | 1099.8 mm                                        |
| Rear radius         | **114.3 mm**                                     |
| Straight run        | 220.9 mm each side                               |
| Internal depth      | 335.2 mm                                         |
| Section area        | 710.1 cm²                                        |
| **Internal volume** | **78.10 L** — matches the existing cabinet       |
| External depth      | 379.6 mm — **1.3 mm shallower than existing**    |

**The curve is dimensionally free.** The bullnose shell replaces the flat rear panel and recovers
exactly the depth the curve costs.

## Usage

```bash
python3 section.py                              # 78.1 L, stern 80, 4 mm wall
python3 section.py --stern 114.3                # stadium — no taper
python3 section.py --stern 60 --thickness 6     # strong taper, thicker shell
python3 section.py --springback 2.5             # former compensation
```

## Outputs — DXF, importable directly into an Onshape sketch

| File                      | Use                                                                                 |
| ------------------------- | ----------------------------------------------------------------------------------- |
| `section-internal.dxf`    | the 78.1 L cavity profile — the acoustic ground truth                               |
| `section-shell-<t>mm.dxf` | internal + external at wall thickness `t`                                           |
| `former.dxf`              | lamination former, radius reduced by the springback allowance                       |
| `flat-pattern-<t>mm.dxf`  | rolling blank, with `ROLL_START` / `ROLL_END` layers marking where the curve begins |

DXF is written as minimal R12 ASCII (LINE + ARC only) — no library dependency, diffable in git, and
accepted by Onshape's sketch import.

## Notes

- The rolling blank uses the **neutral axis** wrap (`r + t/2`), not the inner or outer surface.
  Using the inner surface undersizes the blank by ~2× the thickness in arc length.
- `--springback` shrinks the _former_ radius so the laminated part relaxes onto the target. 1.5% is
  a starting guess; **measure it on a test piece** and correct the former before committing to a
  full shell.
- Volume is a **gross cavity**. Bracing, drivers, crossover and damping all subtract — see `01-017`.
