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

## Research, 2026-08-20 — the design changed substantially

### Extrusion is dead

Three independent reasons, any one sufficient:

1. **It cannot taper.** The stated inspiration is the **Magico M6**, whose form narrows front to
   back. An extrusion is a constant cross-section pushed through a die and physically cannot do
   this.
2. **Circumscribing circle.** A ~250 × 350 mm section has a **~430 mm (16.9″)** diagonal, above the
   common 7″/9″/12″ press classes. Needs a 16″+ high-tonnage press — exists, but not at the first
   mill you email.
3. **MOQ, not the die.** Dies run $300–800 simple / $2,000–5,000+ large hollow. But **minimum orders
   are 200–1,000 kg** and this build needs **~43 kg**. You would buy 5–23× the material required.

### Rolled sheet is the aluminium route — and curvature is why

**Curvature is structural, not cosmetic.** A flat panel resists bending through `E·t³`; a curved
shell converts bending into membrane stress and is far stiffer. That single fact rewrites the
material budget.

Matching **1″ Baltic birch** on _flat-panel_ bending stiffness needs **~12 mm** aluminium (E ratio
~9, equal `E·t³`) — about **48 kg of metal per cabinet**, i.e. the weight of an entire finished MDF
Elsinore in walls alone. Not viable.

**Curved, 3–8 mm is plausible instead**, and it removes both blockers: no die, no MOQ. You buy
sheet.

_(Note: this also corrects a claim relayed from diyAudio that "1/4″ aluminium ≈ 3/4″ plywood". Equal
bending stiffness for 3/4″ ply is ~9 mm of aluminium, not 6.35 mm. Their figure was optimistic —
consistent with that poster concluding it did not pencil out and abandoning the plan.)_

|                        | Finding                                                                                                                                                                           |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Alloy**              | **5052-H32.** Min bend radius ~1t to 3 mm, ~1.5t to 6 mm, ~2t above                                                                                                               |
| **Why not 6061-T6**    | Cracks cold; needs forming in T4 then ageing. Worse, it is heat-treatable so **everything within ~15 mm of a weld loses T6**. 5052 is non-heat-treatable and does not suffer this |
| **Roll crack floor**   | 6–10 × thickness → **18–80 mm** at 3–8 mm stock. Target radius 100–200 mm is comfortably clear                                                                                    |
| **Real constraint**    | **The shop's top-roll diameter** (≈1.5× for a one-pass roll), not the material                                                                                                    |
| **Springback**         | 5052 ~1.5–4°. For two units expect trial-and-fit, not a computed number                                                                                                           |
| **Welding**            | TIG/laser on a rolled seam is standard. 5052 avoids the HAZ softening problem                                                                                                     |
| ⚠️ **JLCPCB / PCBWay** | **Neither offers roll bending.** JLC lists press-brake bends and R3–R20 arc dies; PCBWay lists laser cutting and bending only. This goes to a dedicated plate-rolling shop        |

### ⚠️ Correction — curved walls do NOT fix standing waves

An earlier version of this reasoning claimed curved walls reduce internal standing waves. **That is
largely a marketing claim.** At low frequencies the wavelengths are far longer than the cabinet; you
get a _change_ versus parallel walls, not a meaningful reduction. **Diffraction** benefit at the
baffle edge has some support; the standing-wave benefit does not.

Curve it for stiffness and for form. Leave the standing waves to Joe's wool/Dacron, which is
specified at 40–50% of internal volume for exactly this.

**Damping remains unsolved either way.** Curvature raises panel resonance in frequency; it does not
lower its Q. Aluminium still rings. Constrained-layer damping on the inner face is non-negotiable
and is the single thing that decides whether this beats 1″ Baltic birch or embarrasses it.

## The second reference — GamuT **Zodiac**, and it points at a different project

The other stated inspiration is the **GamuT Zodiac** (Denmark) — their flagship, not the RS series.
Identified from an unusually specific detail the owner remembered: a grille of metal rods with cord
strung on them.

**The grille** (The Absolute Sound, ⚠️ _via search index only — the page 403s, so unverified against
the live source_): _"two 3/8″ diameter by 56″ long metal rods running vertically along the outside
edge of each side of the front baffle, supported by five matching 3/8″ round, 5/8″ tall standoffs...
Between those two rails are **42 narrow elastic bands**, each wrapped with a proprietary woven
fabric, with a 3/16″ total diameter... spaced... about an inch and a quarter [~32 mm] apart."_

**The cabinet** — built by **Kvist of Denmark**, a furniture manufacturer: _"nearly **30 layers** of
fine wood, glued together and **formed under over a ton of pressure**"_ (Tone Publications, 2024).
Ash is named as the outer veneer.

⚠️ **Do not reuse the RS-series figures here.** An earlier draft of this note attributed _"21 layers
of ash and birch, 1–2 mm"_ to the Zodiac. That is the **RS-series** recipe. Sources for the Zodiac
give **27, ~30, or "21–28 varying by section"** — no consistent number, no published ply thickness,
and **birch is not confirmed** for the Zodiac at all. Treat the Zodiac's layer recipe as _"high
twenties to thirty, form-pressed"_ and nothing more precise.

### Scale check — the Zodiac is not an Elsinore

|         | Zodiac                                                      | Elsinore           |
| ------- | ----------------------------------------------------------- | ------------------ |
| Height  | **165 cm**                                                  | ~120 cm internal   |
| Weight  | **196 kg per cabinet**                                      | 40–50 kg           |
| Drivers | 3-way: 38 mm ring radiator, 178 mm mid, **3 × 250 mm bass** | 4 × 6.5″ + tweeter |
| Retail  | **$159,000–179,000** (2024); £100,000 (2018)                | DIY                |

**So the ~$10–20k US Audio Mart listing was a different GamuT** — an RS3 or similar sibling. The
Zodiac is the _form_ inspiration; it is not the thing seen for sale. Used ex-demo Zodiacs have
appeared around **$56,000**.

At nearly **4× an Elsinore's mass**, a literal translation of Zodiac construction to this cabinet is
not the project. What transfers is the **method**: form-pressed thin plies over a curved former,
done by a furniture shop.

### ⚠️ The two designs disagree about damping, and it matters

GamuT braces the Zodiac with _"complex, fan-shaped internal bracing"_ and **deliberately minimises
conventional absorptive damping material** — structure instead of stuffing.

Joe Rasmussen specifies the **opposite**: wool/Dacron filling **40–50% of the internal volume**
(`01-017`).

A GamuT-inspired cabinet housing an Elsinore therefore inherits a genuine design conflict. Following
the form without the damping philosophy is fine; following both is incoherent. **Joe's alignment was
voiced with his stuffing in place** — a stiffer, emptier box is a different acoustic system, not a
better-built version of the same one.

### Why this route is still the strong one

|                  | Magico M6                          | GamuT Zodiac                |
| ---------------- | ---------------------------------- | --------------------------- |
| Structure        | rolled/tapered aluminium monocoque | ~30-ply form-pressed wood   |
| Made by          | metal fabricator                   | **furniture maker** (Kvist) |
| Curve from       | plate roller + welded seam         | bending form + press        |
| Owner capability | none — needs a vendor              | **already owns the shop**   |

The first Elsinore pair was **built by hand in 1″ Baltic birch**, and the mappa burl is still
unused. Bent lamination needs a form, thin plies and pressure — no die, no MOQ, no supplier, no
springback trial-and-fit with a plate roller.

⚠️ **This note is titled for the aluminium project. On the evidence the wood route may be the better
one** — cheaper, executable solo, and closer to why these speakers were built in the first place.
The aluminium path stays documented because the form ambition is real.

## Open, and blocking

- **External cabinet dimensions are still unrecorded.** Joe publishes them only inside GIF
  construction drawings. **Measure the existing pair** — H × W × D and baffle width. Every
  fabrication number above rests on an assumed 250 × 350 section.
- **Internal volume** — see `01-017`. Needed before any enclosure is sized, and before a ULD port is
  cut.
- Which reference is actually being chased: **bare metal, or layered wood.**
- **Zodiac cross-section — constant or varying?** NOT STATED in any source reached. This decides
  whether a constant-profile method could ever produce the form, and no review gives geometric
  detail. Only photographs will answer it.
- **Damping philosophy** — Joe's 40–50% fill vs GamuT's near-empty braced shell. Pick one
  deliberately.

> **Damping conflict RESOLVED 2026-08-20** — see `01-020` § Damping decision. Outcome: bare curved
> walls (the curve earns that), absorbent on the flat parallel caps (161.5 Hz height mode survives
> the curve), fill set by impedance sweep rather than by either philosophy.
