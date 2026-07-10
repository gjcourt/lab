---
title: 'Active Crossover — Elsinore EL-6 (DSP, Multi-Amp, 3-Way)'
number: '01-010'
category: 'audio-midi'
difficulty: 'Hard'
time_commitment: 'Months'
target_skills:
  'DSP crossovers (CamillaDSP/DSPi), loudspeaker measurement (VituixCAD), multichannel
  amplification, filter design'
status: 'Not Started'
depends_on:
  - hardware/loudspeaker
  - repo/dspi
---

# Active Crossover — Elsinore EL-6 (DSP, Multi-Amp, 3-Way)

## Description

Re-implement the **Elsinore EL-6 (ULD drivers)** as an **active** loudspeaker: move the crossover
upstream of amplification (DSP), give **each driver band its own amplifier channel**, and use the
freedom that unlocks to fix the design's one open weakness — **vertical directivity** — ideally by
going a **true 3-way**. This is the redesign path; the "keep one amp, refine the passive" path is a
separate project ([`01-017`](01-017-elsinore-passive-crossover-refinement.md)).

**Target drivers:** the unbuilt **ULD kit** — Purifi PTT6.5W08-NFA-01 ×4 + tweeter (the built pair
uses discontinued paper woofers = baseline only). **Amps today:** one Purifi Eigentakt stereo pair —
enough for _one passive speaker pair_ and no more, so this project's gating cost is **more amplifier
channels**.

## Why this can't be "one amp + active"

An active crossover splits the signal at line level, before amplification, so **every driver band
needs its own amp channel** — true whether the crossover is analog op-amps or DSP. And the designer
explicitly marks the EL-6 **"DO NOT BI-AMP"**: its passive network is a single-amp design, so this
is a **ground-up re-derivation**, not a bi-amp of the existing crossover.

| Topology              | Amp channels / speaker | Stereo total | vs. current 1 pair |
| --------------------- | ---------------------- | ------------ | ------------------ |
| Passive (`01-017`)    | 1                      | 2            | have it            |
| Active 2-way          | 2                      | 4            | +1 stereo amp      |
| Active 3-way (target) | 3                      | 6            | +2 stereo amps     |

## The engineering payoff

- **Directivity / vertical lobing** — a four-6.5″ array crossing at ~2.7 kHz is prone to vertical
  combing; the designer's data (a single modeled 15° curve) never tests it. Active lets one driver
  own **400 Hz – 2.7 kHz** (true 3-way) or steepen/graduate the array rolloff — the honest fix.
- **Per-driver time alignment + phase** — arbitrary delay per band, exact acoustic-offset
  correction.
- **Room correction / target curve** — done in the digital domain, per driver, per room.
- **No dissipative passive parts** — the impedance-flattening conjugates (see `01-017`) and big
  inductors simply don't exist; the amp sees each driver directly.

## Approach

- **DSP crossover engine** — options, cheapest→most-integrated: **DSPi** (RP2040/RP2350
  USB→multi-S/PDIF appliance from [`01-016`](01-016-diy-digital-domain-streamer.md) — active
  multiway + PDM sub in a ~$5 board), **CamillaDSP** (software on a Pi — convolution, arbitrary
  FIR/IIR), or a miniDSP Flex/8. Design the acoustic Linkwitz-Riley (or FIR linear-phase) targets in
  VituixCAD against measured drivers, then realize them as DSP filters.
- **Amplification** — add 1–2 stereo amp channels (match Eigentakt-class Zout so the driver EQ
  holds).
- **DACs** — one channel per driver band (DSPi's S/PDIF outs → DACs, or a multichannel DAC).
- **Shared foundation with `01-017`** — the gated quasi-anechoic measurement set (on/off-axis fans,
  especially the **vertical fan**, + nearfield bass) is **Phase 0 for both projects**. Take it once.

## Exit Criteria

- [ ] Gated quasi-anechoic driver measurements (incl. vertical fan) imported to VituixCAD; the
      vertical directivity of the current array quantified (confirm/deny the lobing hypothesis).
- [ ] Active crossover target designed in VituixCAD (2-way minimum; 3-way if the array data
      justifies) and realized in the chosen DSP engine (DSPi / CamillaDSP / miniDSP).
- [ ] Per-driver amplification + DACs in place; each band driven independently.
- [ ] Measured active system meets the target (flat gated on-axis + improved vertical polar vs the
      passive baseline from `01-017`).

## Progress

- [x] Scoped: active = multi-amp ground-up redesign (not a bi-amp); target = ULD drivers
- [x] Directivity identified as the payoff; DSP-engine options mapped (DSPi/CamillaDSP/miniDSP)
- [ ] Phase 0 measurement set (shared with 01-017) — vertical fan is the open question
- [ ] Active target design + DSP realization
- [ ] Amplification + DACs

## References

- Elsinore EL-6 — <https://www.customanalogue.com/elsinore/elsinore_index.htm>
- Schematics + Mark-6 measurements: Immich asset `f9f18b24-79e0-40a0-96d1-07eaa91f34f1` (george,
  2026-07-10)
- Passive counterpart: [`01-017`](01-017-elsinore-passive-crossover-refinement.md)
- DSP crossover via DSPi / CamillaDSP: [`01-016`](01-016-diy-digital-domain-streamer.md)
