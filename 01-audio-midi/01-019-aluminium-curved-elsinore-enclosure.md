---
title: 'Curved Aluminium Elsinore Enclosure (Offshore-Manufactured)'
number: '01-019'
category: 'audio-midi'
difficulty: 'Hard'
time_commitment: 'Months'
target_skills:
  'Enclosure acoustics, CAD, design-for-manufacture (extrusion/CNC), overseas supplier management,
  anodising/finishing'
status: 'Not Started'
depends_on:
  - hardware/loudspeaker
  - project/01-017
---

# Curved Aluminium Elsinore Enclosure (Offshore-Manufactured)

## Description

Design a **new enclosure for the Elsinore EL-6 in aluminium with curved surfaces**, manufactured in
China or Taiwan, replacing the veneered MDF cabinets. The motivation is **material and form** — an
object built to a specification the owner chose, rather than a plywood box with a nice veneer on it.
A side benefit: it frees the **unused mappa burl** for another project.

This is the third of three Elsinore projects and the only one that is not about electronics.
[`01-017`](01-017-elsinore-passive-crossover-refinement.md) refines the passive network;
[`01-010`](01-010-active-crossover-network-for-speakers.md) goes active. **This one changes the
box.**

## ⚠️ What this does not solve

**It is not a space project.** The temptation is to treat "new enclosure" as a way to reclaim floor
area. It is not, unless the **internal volume shrinks** — and volume is set by the alignment for 4×
6.5″ woofers per side, not by the material. Aluminium walls are thinner than MDF for the same
stiffness, so external dimensions drop _slightly_ for the same internal volume, but that is
centimetres, not a different footprint.

**Shrinking the volume meaningfully means changing the alignment** (vented → sealed, or a different
tuning), which changes the acoustic target, which **invalidates the ULD crossover** and pulls the
work back into a full redesign — i.e. [`01-010`](01-010-active-crossover-network-for-speakers.md)
territory. That may be a fine project. It is a **much larger** one, and it should be entered
deliberately rather than discovered halfway through a cabinet build.

**Scope this project as: same internal volume, same alignment, different material and shape.**

## The engineering problem: aluminium rings

This is the main technical risk and it is the reason most aluminium speakers are either very
expensive or bad.

MDF is acoustically mediocre but **well-damped** — its resonances are low-Q and lossy. Aluminium is
the opposite: stiff, light, and **high-Q**. An undamped aluminium panel does not absorb the energy
put into it, it stores it and re-radiates it later as a narrow, audible ring. A thin rolled-sheet
aluminium box will measurably and audibly underperform the MDF cabinet it replaced.

The three ways this is solved in practice, in ascending order of cost:

1. **Constrained-layer damping** — a viscoelastic layer bonded between the shell and an inner skin
   (or bitumen/CLD tiles applied internally). Cheap, effective, and the pragmatic answer here.
2. **Mass and bracing** — thick walls plus internal ribs that move the panel modes above the
   passband and reduce their amplitude. Adds a lot of weight.
3. **Billet machining** — the Magico/YG route: cut the cabinet from solid. Astronomically expensive
   at floorstander size, and not a realistic target.

**Design assumption for this project: extruded shell + internal CLD + machined end caps.** Verify by
measurement (accelerometer or a nearfield panel measurement) rather than by assertion.

## Manufacturing route — extrusion is almost certainly the answer

Curved aluminium can be produced several ways, and they are not close in cost at this size:

| Route                 | Curvature possible                                  | Tooling                               | Verdict                                          |
| --------------------- | --------------------------------------------------- | ------------------------------------- | ------------------------------------------------ |
| **Extrusion**         | Curved **cross-section**, constant along the length | **Die** — one-time, low thousands USD | ✅ **The route.** Standard for high-end cabinets |
| Rolled / welded sheet | One axis                                            | Minimal                               | Cheap, but thin walls ring; needs heavy damping  |
| CNC from billet       | Anything                                            | None                                  | Cost scales with removed material — prohibitive  |
| Casting               | Complex 3D curves                                   | Heavy pattern/mould cost              | Porosity risk, wrong volume for 2 units          |
| Hydroforming          | Compound curves                                     | Heavy die cost                        | Wrong volume for 2 units                         |

**Extrusion gives the curved side walls for free in the die profile** — the cabinet becomes a cut
length of profile with machined aluminium end caps and a separate baffle. This is exactly how a lot
of high-end monitors are built, and it maps cleanly onto Chinese and Taiwanese suppliers.

**The constraint to check first:** extrusion presses have a **circumscribing-circle limit**. A
cabinet housing 4× 6.5″ drivers needs a wide profile, and large sections need a bigger press and
cost more per kilo. **Ask a supplier for the maximum circle diameter before drawing anything.** That
single number determines whether the whole approach is viable.

## ⚠️ The cost problem is tooling amortised over two units

This is the honest reason to be sceptical, and it should be confronted before any CAD is drawn.

A die is a one-time cost regardless of whether you make 2 cabinets or 200. Spread over **two**, the
per-cabinet tooling cost dominates everything else — the aluminium itself is nearly incidental. The
project is therefore **structurally expensive per unit** in a way that a wooden cabinet is not.

Three ways out, and they should be chosen deliberately:

1. **Accept it.** Treat the die as the price of the object. Legitimate if the point is to own the
   thing.
2. **Design for a no-tooling route.** Flat panels bolted to machined curved corner extrusions using
   _stock_ profiles, or rolled sheet with heavy internal damping. Loses some of the aesthetic intent
   but removes the die entirely.
3. **Make a small batch.** Amortise the die over 6–10 cabinets and sell the rest. This turns a
   personal project into a **product**, with all that implies. Almost certainly not wanted — but it
   is the only route where the economics are actually good, so it should be rejected explicitly
   rather than by default.

**Option 2 is the sensible default until the die quote is in hand.**

## Sequencing — this should come after `01-017`

[`01-017`](01-017-elsinore-passive-crossover-refinement.md) has an exit criterion reading _"ULD kit
built in the boxes."_ **Which boxes is currently undecided, and that ambiguity blocks it.**

**Resolve it in favour of the existing cabinets.** Building the ULD kit into the MDF boxes first
means the drivers get playing, the measurement set gets captured, and the crossover work completes
against a known enclosure. **Only then** does it make sense to change one variable — the box — and
re-measure.

Doing the enclosure first would mean debugging a new crossover and a new enclosure simultaneously,
with no baseline to attribute a problem to either.

## Exit Criteria

- [ ] Supplier confirms **maximum extrusion circumscribing circle**, and it accommodates the
      required profile width
- [ ] Die + per-unit quote obtained from at least **two** suppliers; tooling-amortisation decision
      made explicitly (accept / no-tooling redesign / batch)
- [ ] CAD model with the **same internal volume and alignment** as the MDF cabinet, verified against
      the EL-6 spec
- [ ] Damping strategy specified and **measured**, not assumed — panel resonance at or below the MDF
      cabinet's
- [ ] Baffle cutouts verified against the **ULD** driver drawings before any metal is cut
- [ ] Finish decided (anodised / bead-blasted) and sample approved
- [ ] Pair built, drivers transferred, and A/B measured against the MDF cabinets
- [ ] Mappa burl reallocated to a named project

## Progress

- [ ] Ask suppliers the circumscribing-circle question — **cheapest possible first step, do this
      before anything else**
- [ ] Decide the tooling-amortisation route
- [ ] CAD

## References

- Elsinore EL-6 — <https://www.customanalogue.com/elsinore/elsinore_index.htm>
- Crossover refinement (blocks on "which boxes"):
  [`01-017`](01-017-elsinore-passive-crossover-refinement.md)
- Active redesign, where a volume change would push this:
  [`01-010`](01-010-active-crossover-network-for-speakers.md)
- Prior cabinet-building project:
  [`02-001`](../02-woodworking/02-001-custom-studio-monitor-speaker-cabinets.md)
