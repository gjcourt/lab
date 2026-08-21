# Crossover magnetic layout — rules for large air-core inductors

Written 2026-08-21, from what the Elsinore build turned out to look like inside. Applies to any
passive crossover with large air-cored inductors, and specifically to the redesign in
[`01-017`](../01-017-elsinore-passive-crossover-refinement.md).

## The problem, as actually found

The Elsinore crossover is **three boards on brass standoffs**, every inductor **flat-mounted with
its axis perpendicular to its board**.

Parallel boards therefore put **every coil axially aligned with every other coil**. There is no 90°
anywhere in the assembly — and there cannot be, because flat-mounting on parallel boards makes
orthogonality geometrically impossible. The orientation rule was not broken; the topology made it
unreachable.

## The numbers

Mutual inductance `M = k√(L₁L₂)`, so two identical coils in series give `L = L₁ + L₂ ± 2M`. For two
10 mH coils with `C = 300 µF`:

| k | Geometry | Aiding | f₀ | Opposing | f₀ |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0.00 | 90°, separated — ideal | 20 mH | **65.0 Hz** | 20 mH | **65.0 Hz** |
| 0.05 | side by side, ~1 dia apart | 21 mH | 63.4 Hz | 19 mH | 66.7 Hz |
| 0.15 | side by side, touching | 23 mH | 60.6 Hz | 17 mH | 70.5 Hz |
| 0.30 | coaxial, ~1 dia apart | 26 mH | 57.0 Hz | 14 mH | 77.7 Hz |
| 0.50 | coaxial, close | 30 mH | 53.1 Hz | 10 mH | 91.9 Hz |
| 0.70 | coaxial, stacked touching | 34 mH | 49.8 Hz | 6 mH | **118.6 Hz** |

**Coplanar side-by-side is mild. Coaxial-and-close is not.** Stacking boards produces the second
case for any pair of coils that overlap in XY.

## ⚠️ The constraint that causes it

**The crossover is serviced through the driver cutouts** — the assembly must pass through a
~150–160 mm hole. One large board does not fit. **Stacking is a correct answer to an aperture
constraint**, which is why this is a design trap rather than an error: the obvious fix (one big
board, coils spaced) is unbuildable.

So the real problem is: **maximise magnetic separation subject to fitting through the driver
cutout.**

## The rules

### 1. Mount to perpendicular cabinet surfaces, not to standoffs

**This is the one that actually solves it.** A board on the cabinet floor has vertical coil axes; a
board on a side wall has horizontal coil axes. That is a true 90°, `k ≈ 0` — and **each board still
passes through the cutout individually**, because they are separate boards entering one at a time.

Standoff stacking forces parallel axes by construction. Perpendicular *surfaces* is the only way to
get orthogonality in an assembly that must go through a hole.

### 2. Where coils must share a plane, space them

Coplanar coils have parallel axes no matter how they are rotated — **in-plane rotation does nothing
for coplanar coupling.** Separation is the only lever. **One coil diameter edge-to-edge** puts you
near `k ≈ 0.05`.

### 3. Where boards must stack, break the XY overlap

If perpendicular mounting is impossible, **offset the coils laterally so none is coaxial with
another.** Counter-intuitively, in-plane rotation of one board *does* help here — not by changing
any axis, but by moving coils out of vertical alignment. **Coaxial-and-close is the failure mode;
laterally offset by one diameter is nearly harmless even with parallel axes.**

### 4. Keep the conjugate branch out, and the space it frees is the point

Removing a large shunt conjugate is not only an electrical decision. **Two 10 mH air cores, a 20 W
resistor and a 300 µF cap are the largest components on the assembly** — deleting them is what makes
rules 1–3 satisfiable at all. **The conjugate removal and the layout fix are the same project.**

### 5. Log every inductor's DCR before installation

Designers net inductor DCR into the series resistor values — Joe's `R2 7R` explicitly "already nets
out the big inductor's DCR". **A 10 mH air core can carry 4–5 Ω at 18 AWG**, so two in series may
meet the target resistance on their own. **You cannot verify a network whose DCR you did not
record.**

### 6. Terminal blocks, not soldered leads

Anything that will be swapped through a driver cutout should be swappable through a driver cutout.

## Diagnosing coupling in an existing build, for free

**The impedance sweep measures it.** A shunt conjugate leaves a signature at `f₀`; read where it
sits and look it up in the table above to recover the real total inductance, and therefore `k`.

- **f₀ at 65 Hz** → coils are barely coupling.
- **f₀ meaningfully off** → they are, and the sign tells you aiding or opposing.

No extra instrumentation, and it rides along with the Fb and Ql measurements already planned.

## ⚠️ The prediction this changes

The standard prediction for removing an inert shunt conjugate is **"SPL unmoved"** — the branch is
parallel, and a voltage-source amp holds the node voltage regardless.

**Magnetic coupling breaks that.** If a conjugate coil sits coaxially above an acoustic-path
inductor, removing it **restores that inductor to its designed value**, and SPL may genuinely
improve.

**Same observable, opposite conclusion** — an SPL shift after removal reads either as "the removal
thesis was wrong" or as "the coupling lifted". **Record both hypotheses before measuring**; they
cannot be separated afterwards.

## Sources

- Build photography, 2026-08-21 — three stacked boards, all coils flat-mounted.
- Owner confirmation, 2026-08-21 — the bass conjugate is **2 × 10 mH air-cored** in series, not a
  single cored 18 mH part as previously recorded.
