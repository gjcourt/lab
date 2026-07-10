---
title: 'Elsinore Passive Crossover Refinement (Eigentakt-Optimized ULD Build)'
number: '01-017'
category: 'audio-midi'
difficulty: 'Medium'
time_commitment: '1-4 weeks'
target_skills: 'Passive crossover theory, loudspeaker measurement (REW/VituixCAD), soldering'
status: 'In Progress'
depends_on:
  - hardware/loudspeaker
---

# Elsinore Passive Crossover Refinement (Eigentakt-Optimized ULD Build)

## Description

Build the **unbuilt ULD kit** of Joe Rasmussen's **Elsinore EL-6** (customanalogue.com) with a
passive crossover **optimized for a low-output-impedance amp** — i.e. delete the
impedance-flattening apparatus that only benefits high-Zout (tube/SET) amps, which buys nothing on
the owner's **Purifi Eigentakt** and costs sensitivity, heat, and a large cored inductor. Then
verify the change by measurement, and tune tweeter level to a gated curve. This is the "one amp,
keep passive" path — a **refinement of a validated design**, not a redesign. The active/3-way
redesign is a separate project ([`01-010`](01-010-active-crossover-network-for-speakers.md)).

**Hardware on hand:** a built pair using the **old, now-discontinued paper woofers** (baseline /
reference only — not worth further investment), plus an **unbuilt ULD kit** — Purifi
**PTT6.5W08-NFA-01** midbasses ×4 + Peerless/Scan-Speak tweeter + the ULD crossover parts. Amps:
Purifi Eigentakt. Measurement: UMIK-1 + REW. A crossover is already modeled in **KiCad on the
Windows box** (retrieve when powered on — likely this ULD network).

## The design (EL-6 ULD, from the schematic)

Six-driver, graduated MTM-style array: four 6.5″ midbasses (top pair `MidBass 1,2` via `L2 1.5mH`;
bottom pair `MidBass 3,4` via `L1 3.0mH` — the graduated rolloff for vertical directivity) + tweeter
crossing ~2.7 kHz. Two **shunt conjugate networks sit across the amp terminals** (parallel to the
input, ahead of the series inductors — so they shape _impedance_, not the acoustic transfer
function):

| Network               | Parts                                    | Purpose                                            | Eigentakt verdict               |
| --------------------- | ---------------------------------------- | -------------------------------------------------- | ------------------------------- |
| **Bass conjugate**    | `L4 18mH · R2 ≈8R · C3 300µF` (~65 Hz)   | Pulls the vented upper-bass impedance peak to ~8 Ω | **Delete** — audibly invisible  |
| **Tweeter conjugate** | `L5 0.15mH · R3 9R · C4 22µF` (~2.8 kHz) | Flattens the voice-coil-inductance rise at the XO  | Evaluate; small, lower priority |

Tweeter level pad: optional `R5 33R` (designer notes omit for a slightly brighter balance). The `R2`
resistor is spec'd "10 W min, 20 W recommended" and its nominal value already nets out the big
inductor's DCR — the tell that it's a dissipative flattening leg. Designer marks the array **"DO NOT
BI-AMP"** (bi-wire OK) — the passive network is a single-amp design; that constraint is exactly why
going active (`01-010`) is a ground-up redesign, not a bi-amp of this.

## Why the refinement is safe (and why it's free on the Eigentakt)

Frequency response is only modulated by impedance swings to the extent the amp has output impedance
(amp Zout + speaker Z form a voltage divider). The Eigentakt's Zout is single-digit milliohms
(damping factor in the hundreds), so the speaker's impedance curve — flattened or not — is
**acoustically invisible** to it. The Mark-6 measurements confirm the design's premise (impedance
flat ~6–8 Ω above 150 Hz, electrical phase ~0°), which is precisely what makes the flattening
network removable: pulling `L4/R2/C3` leaves the SPL unchanged (a good amp holds the node voltage),
while restoring the classic vented impedance double-hump and a ±30–45° phase wiggle in the upper
bass — graphs the amp ignores. Net win: **lose the 18 mH cored inductor** (distortion + cost + size)
**and the 20 W resistor dissipation** (sensitivity), with no audible penalty. If tube compatibility
is ever wanted, the leg goes back.

## Method (measurement-first, model before soldering)

1. **Gated baseline** — REW + UMIK-1, windowed/gated on-axis before the first reflection; nearfield
   woofer + port splice for the bass. Get a quasi-anechoic SPL+phase, not the room-dominated 1/6-oct
   RTA. (Get the calibration file + acoustic-timing reference right, or phase data is garbage.)
2. **Vertical + horizontal fans** — on-axis, ±7.5°, ±15° vertical (the four-6.5″ array's lobing risk
   at 2.7 kHz is untested by the designer's single 15° curve) and a horizontal fan. This data is
   also Phase 0 of `01-010`.
3. **VituixCAD model** — import measured SPL+phase + impedance; verify the model overlays the real
   system, then _simulate_ removing `L4/R2/C3` (expect SPL unchanged, impedance peak returns).
4. **Execute** — physically pull the bass conjugate, re-measure, confirm SPL unmoved within noise.
5. **Tweeter level** — from the gated on-axis vs a Harman-style downtilt, adjust `R5` / tweeter-leg
   resistors ±1–2 dB. Low-risk, reversible, measurement-guided.

## Exit Criteria

- [ ] ULD kit built (Purifi PTT6.5W08 ×4 + tweeter) in the boxes.
- [ ] Gated quasi-anechoic baseline (on/off-axis fans + nearfield bass) captured and VituixCAD model
      overlays the measured system.
- [ ] Bass conjugate `L4/R2/C3` removed; re-measured SPL unchanged within measurement noise (thesis
      confirmed) — 18 mH inductor + 20 W resistor eliminated.
- [ ] Tweeter level set to the gated target.
- [ ] KiCad crossover model (from the Windows box) reconciled with the as-built network + archived.

## Progress

- [x] Read the ULD schematic + Mark-6 measurements (impedance flat, removal-is-safe thesis
      validated)
- [x] Scoped as the "one amp, keep passive" path; active redesign split to 01-010
- [ ] Retrieve the KiCad model from the Windows box
- [ ] Gated measurement set → VituixCAD
- [ ] Remove bass conjugate + re-measure + tweeter tune

## References

- Elsinore EL-6 (ULD/NBAC/NRX/MFC) — <https://www.customanalogue.com/elsinore/elsinore_index.htm>
- Schematics + Mark-6 measurements: Immich asset `f9f18b24-79e0-40a0-96d1-07eaa91f34f1` (george,
  2026-07-10)
- Active/3-way counterpart: [`01-010`](01-010-active-crossover-network-for-speakers.md)
- DSP-crossover option shared with [`01-016`](01-016-diy-digital-domain-streamer.md) (DSPi /
  CamillaDSP)
