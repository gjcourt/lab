---
title: 'Lagom P64 Catch Cup for 53mm Workflow'
number: '06-019'
category: 'coffee-espresso'
difficulty: 'Easy'
time_commitment: '1-2 days'
target_skills: 'Parametric CAD (Onshape), 3D printing or machining, dimensional fit'
status: 'Not Started'
depends_on:
  - hardware/lagom-p64
---

# Lagom P64 Catch Cup for 53mm Workflow

## Description

Design a replacement catch cup for the **Option-O Lagom P64** grinder sized to the **53 mm**
portafilter workflow rather than the stock cup.

The 53 mm figure is not arbitrary: the **La Spaziale Mini Vivaldi II / Lucca A53 Mini** takes a **53
mm** portafilter, while the **Cafelat Robot** is **58 mm**. Two basket standards in one kitchen
means the stock catch cup matches neither dosing workflow cleanly.

## CAD

**Onshape:**
<https://cad.onshape.com/documents/934825dc483925d28bc9729c/w/172d3ef7f3a4919f6b20b8d6/e/42581aab5c654eaf2b1c7f47>

## Open questions

- **Fit reference** — is the cup sized to the 53 mm _basket_, to a 53 mm dosing cup, or to the P64's
  own chute/magnet interface? All three are different constraining dimensions.
- **Retention** — the P64's stock cup locates magnetically. Does the replacement reuse that, or
  friction-fit?
- **Material and process** — 3D printed (PLA/PETG food-contact caveats) or turned from
  aluminium/stainless? Printed is faster to iterate; metal is what the rest of the setup is.
- **Static** — grounds cling. Does the geometry need an RDT workflow assumption or an anti-static
  treatment?

## Exit Criteria

- [ ] Constraining dimension identified and measured (basket / dosing cup / chute)
- [ ] Parametric Onshape model with the fit dimension as a driving parameter
- [ ] One physical iteration produced and test-fitted
- [ ] Retention method proven (magnet or friction)
- [ ] Grounds transfer cleanly with no measurable retention penalty vs stock

## Progress

- [x] Onshape document created (empty — no geometry yet)
- [ ] Fit reference confirmed
- [ ] First iteration produced

## References

- Espresso profiling context: [`06-001`](06-001-lucca-a53-mini-leva-firmware-integration.md)
