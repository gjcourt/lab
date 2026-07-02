---
title: 'Espresso Water Remineralization (Soft SF Water → Balanced Cup)'
number: '06-013'
category: 'coffee-espresso'
difficulty: 'Easy'
time_commitment: '1-2 days (tasting experiment)'
target_skills: 'Water Chemistry, Espresso Dial-In'
status: 'Not Started'
depends_on:
  - hardware/lucca-a53
---

# Espresso Water Remineralization (Soft SF Water → Balanced Cup)

## Description

San Francisco tap (Hetch Hetchy) is **very soft** — for 3545 Washington / Presidio Heights the
current SFPUC numbers are **hardness 18, alkalinity 22, chloride 8 mg/L** (see
[06-011](06-011-mini-v2-direct-plumb-in.md) pre-flight). That's ideal for the **machine** (low
scale) but under-mineralized for **taste**: low hardness means thin extraction, and low alkalinity
leaves the cup bright to the point of sharp. This project is the controlled experiment to decide
whether adding minerals back is worth it — build a balanced water, taste it head-to-head against the
plumbed soft water, and keep it only if the cup clearly wins.

**This is a taste experiment, not a permanent build.** See the conflict with the plumb-in below.

## The two axes

| Axis                        | What it does                                                            | SF now | Target |
| --------------------------- | ----------------------------------------------------------------------- | ------ | ------ |
| **Hardness (GH = Ca/Mg)**   | Extraction minerals — body + flavor intensity. Mg = bright; Ca = round. | 18     | ~50    |
| **Alkalinity (KH = HCO₃⁻)** | Buffer — tames brightness, adds balance/sweetness. Too much = flat.     | 22     | ~40    |

Target ≈ **GH 50 / KH 40 mg/L (as CaCO₃)** — a balanced, SCA-ish espresso water.

## The catch (why this stays an experiment)

The [06-011](06-011-mini-v2-direct-plumb-in.md) plumb-in feeds the machine **soft water straight
from the wall** — great for the boiler. Remineralizing fights that two ways:

1. **You can't dose a plumbed line.** Remineralization is per-batch (mix into a jug); a plumbed feed
   has no mixing stage.
2. **Adding hardness adds scale** — the exact thing the soft-water plumb-in avoids.

The float-fill plumb-in is reversible, so the experiment is easy: **pop the push-fit at the tank,
hand-fill recipe water, pull shots, compare.** Only if the remineralized cup is clearly better do
you weigh giving up the plumb-in convenience (hand-filling ongoing, or a dosing setup).

## Recipe (DIY — precise, cheap)

Build from **distilled water** (a zero-mineral blank) so the recipe is exact. Mix two concentrates
once, then dose by volume. Only needs a **0.1 g kitchen scale** (for the concentrates) and a **10 mL
syringe** — no milligram scale, because dosing is volumetric.

| Concentrate            | Recipe                                                  | Dose → effect                |
| ---------------------- | ------------------------------------------------------- | ---------------------------- |
| **Stock A — hardness** | 12.3 g Epsom salt (magnesium sulfate) in 1 L distilled  | 10 mL / L final = **+50 GH** |
| **Stock B — buffer**   | 6.7 g baking soda (sodium bicarbonate) in 1 L distilled | 10 mL / L final = **+40 KH** |

**Recipe water:** into ~980 mL distilled, add **10 mL Stock A + 10 mL Stock B**, top to 1 L, stir. →
~GH 50 / KH 40.

## Three rules — because it's a boiler machine

1. **Sulfates, not chlorides.** Epsom salt (MgSO₄) and gypsum (CaSO₄) are the sulfate forms.
   **Never** use calcium/magnesium _chloride_ — chloride pits stainless boilers. (SF chloride is
   already a low 8; keep it there.)
2. **Go magnesium-forward.** All-Epsom is the default for machines: **magnesium scale is softer and
   less tenacious than calcium-carbonate scale.** For more body, add a little calcium as **gypsum**
   — but Ca scales harder.
3. **Cap KH at ~40.** Higher alkalinity both flattens taste and accelerates scale.

At GH 50 / KH 40 you're still inside the plumb-in's ≤60 / 40-80 safe band, so scale risk is modest —
just descale a bit more often than on the bare soft water.

## No-chemistry shortcut

**Third Wave Water — Espresso Machine profile:** pre-measured mineral packets, one per gallon of
distilled, formulated lower-scale for machines. Zero weighing. (Lotus / Aquacode drops are a
liquid-dose equivalent.) Costs more per gallon but is foolproof for the tasting test.

## Tasting-test protocol

1. Mix 1 L recipe water (DIY or Third Wave).
2. Disconnect the float-fill line (push-fit); hand-fill the Mini V2 tank with recipe water.
3. Pull 2-3 shots — **same beans, grind, dose, ratio** — against reference shots on the plumbed soft
   water.
4. Score body, sweetness, acidity balance. Be honest: espresso is fairly water-forgiving (short
   contact, high pressure), so the delta may be small.
5. **Decide:** clear win → keep (accept hand-filling, or plan a dosing setup); marginal → stay on
   the convenient soft plumbed water and chase taste via beans + dial-in.

## Related projects

- **[06-011 Mini V2 Direct Plumb-In](06-011-mini-v2-direct-plumb-in.md)** — source of the soft-water
  baseline and the plumb-in this trades against.
- **[06-005 Water Quality and TDS Monitor](06-005-water-quality-and-tds-monitor.md)** — could log
  the GH/KH/TDS of recipe batches for repeatability.

## Exit Criteria

- [ ] Recipe water mixed to ~GH 50 / KH 40 (verified by test kit or by-recipe).
- [ ] Head-to-head taste test vs plumbed soft water, same dial-in, documented scores.
- [ ] Decision recorded: adopt (with how) or stay on soft water.

## Progress

- [x] Established SF soft-water baseline (06-011: H18 / Alk22 / Cl8, Presidio Heights)
- [x] Scoped targets (GH ~50 / KH ~40) + DIY concentrate recipe
- [ ] Buy distilled + Epsom salt + baking soda (or Third Wave Espresso packets)
- [ ] Mix recipe water; hand-fill tank via disconnected float line
- [ ] Head-to-head tasting vs soft plumbed water
- [ ] Decide + document

## Sources

- SCA / Hendon & Colonna-Dashwood, _Water for Coffee_ — GH/KH targets and the extraction vs buffer
  framing.
- Barista Hustle recipe-water method — two-concentrate (Epsom + bicarbonate) dosing.
