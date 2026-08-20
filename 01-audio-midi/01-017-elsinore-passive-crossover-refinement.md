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
reference only — not worth further investment), plus an **unbuilt ULD kit purchased 2021** (still
boxed): **8× Purifi PTT6.5W08-NFA-01** ULD woofers (4/speaker, ~15,300 kr) + **2× Scan-Speak
Discovery D2608/9130** textile-dome tweeters (the schematic's Peerless alternate is _not_ used) +
the ULD crossover parts. The Purifi driver is still current, so no obsolescence risk on this path.
Amps: Purifi Eigentakt. Measurement: UMIK-1 + REW. A crossover is already modeled in **KiCad on the
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

## Designer's published specification (customanalogue.com, read 2026-08-20)

Joe Rasmussen's own documentation, which had not previously been read into this note. Chapter pages
`elsinore_1` … `elsinore_25` plus `elsinore_mk2.htm` and `elsinore_kit.htm`.

|                    |                                                                                                     |
| ------------------ | --------------------------------------------------------------------------------------------------- |
| Internal volume    | **75 litres** (`elsinore_3.htm`)                                                                    |
| Alignment          | **Vented**, **Fb = 40 Hz**, F3 ≈ 53 Hz (F3/Fb = 1.325)                                              |
| Port               | 90 mm cut-out, **86–87 mm ID**; length adjusts for smaller tube                                     |
| Finished weight    | **40–50 kg each** (`elsinore_4.htm`)                                                                |
| Front panel        | **18 mm**; plus a 230 × 200 × 25 mm sub-front panel at the tweeter                                  |
| Current revision   | **Mk6** (author's note, September 2024)                                                             |
| External H × W × D | ⚠️ **NOT PUBLISHED AS TEXT** — exists only inside the construction-drawing GIFs on `elsinore_4.htm` |

**Damping** (`elsinore_5.htm`) — wool 60% / Dacron 40%, low density, covering "forty to fifty
percent of the volume", cut as **2 × 1200 × 160 × 25 mm** front, **1 × 850 × 110 × 75 mm** centre
rear, **2 × 1100 × 50 × 75 mm** corner rear. All fit through the 6.5″ driver holes after assembly.

**Bracing philosophy** (`elsinore_11.htm`) — _"Longitudinal bracing where the brace is off centre
(asymmetrical) is better than lateral bracing. **Bracing the edges of a panel is totally
ineffective.**"_ Main brace sits 170–178 mm behind the sub-front panels.

**Internal wiring** (`elsinore_5.htm`) — 22 AWG PTFE, 19 strands silver-clad copper, Farnell
**1184037**. _"INCORRECT WIRING OR WRONG PHASE WILL SERIOUSLY DEGRADE PERFORMANCE."_

### ✅ The variant question is settled — and it unblocks this project

> **"All variants share identical box designs with modified port lengths."**

| Variant | Midbass                      | Status                                            |
| ------- | ---------------------------- | ------------------------------------------------- |
| **MFC** | SB Acoustics **SB17MFC35-8** | current standard kit — **this is the built pair** |
| **ULD** | Purifi **PT6.5W08-NFA-01**   | premium — **this is the boxed kit**               |
| NBAC    | aluminium cone               | needs ~2× amplification                           |
| NRX     | SB17NRXC35-8                 | legacy, discontinued                              |

Tweeter from Mk2 onward is the **Scan-Speak Discovery D2608/913000**; Mk1/Mk2 used **Peerless HDS**
— which is where the owner's "I thought they were Peerless" recollection comes from. He was
remembering an earlier revision, not misremembering.

**So the ULD kit drops into the existing cabinets.** Driver and crossover change only, no cabinet
change. This is the fact this project was implicitly betting on and it is now confirmed from the
designer.

### ⚠️ OPEN — measure the internal volume before cutting a ULD port

The variants differ by **port length**, and Joe's lengths are computed for **75 litres**.

The built pair uses **Joe's outer dimensions** but **1″ Baltic birch** on the back, sides, top and
bottom, with a **3/4″ front** (≈ his 18 mm spec). Thicker walls at unchanged outer dimensions means
**less internal volume** — plausibly around 67 L, i.e. ~10% down, though the true figure is unknown
because Joe never publishes a wall thickness for the non-front panels.

**Using the published ULD port length in a box that is not 75 L will mistune the alignment.**
Measure the real internal volume first. This is a prerequisite for the build step below, not a
nicety.

### Correction — the conjugate frequencies in this note are DERIVED, not published

The 65 Hz bass conjugate and 2.8 kHz tweeter conjugate quoted above were computed from the schematic
component values (`L4 18mH · R2 8R · C3 300µF`). **Neither figure appears in Joe's prose.** He
describes the network as flattening impedance between **300 Hz and 1500 Hz**, and quotes a phase
result of **−18° at 2200 Hz** (`elsinore_mk2.htm`). He also confirms the conjugate filter is
**optional** (`elsinore_22.htm`) — though omitting it breaks his documented static test procedure.

The removal thesis is unaffected: it rests on amp output impedance, not on the exact centre
frequency. But the numbers should be labelled as derived.

## Build photography — Immich, 2021

Construction photos are in Immich and searchable via the smart-search API. Two clear build sessions,
**2021-05-04** and **2021-06-12**, with outliers from 2020-12 through 2022-06 — consistent with the
recorded 20-month build.

| Asset                                  | Date       | Shows                                             |
| -------------------------------------- | ---------- | ------------------------------------------------- |
| `61657eb1-5c4a-49b2-a20f-d937be070e48` | 2021-05-04 | Baffle with all five drivers dry-fitted           |
| `69120e42-743a-4ee6-ab8d-5bdc8ef38efc` | 2021-05-04 | Open driver holes — **crossover visible in situ** |
| `d1032f3c-2039-4e28-a130-641c05fbb374` | 2021-05-04 | Baffle / carcass                                  |
| `ce3e62ce-2aaf-4800-a273-9ff9d3dce6f3` | 2021-06-12 | Later session                                     |

### What the photos establish

- **Four 6.5″ midbass + one tweeter, tweeter fourth from top** — the graduated EL-6 array, as
  designed.
- **Baltic birch throughout**, laminations countable on the baffle edge, with a chamfer worked into
  the front edge.
- **Rebated, flush-mounted driver cutouts** — routed to the drawings.
- Panels pencil-marked to Joe's cut list (_"TOP/BOTTOM PANEL #3"_) — built panel-by-panel from the
  published drawings.

### ⚠️ The crossover is mounted INSIDE the cabinet

Asset `69120e42` shows it plainly through the open driver holes: green resistors, a copper air-core
inductor and terminal blocks, sitting on the cabinet floor.

**So the ULD crossover swap happens through the driver cutouts** — the same access route Joe
specifies for fitting damping after assembly. No cabinet disassembly, no veneer at risk. Fiddly but
feasible, and it makes the build step materially less invasive than a rear-panel-mounted network
would be.

_(Access: the Immich API key lives at `~/.config/immich/api-key`. An older key sat in plaintext in
the memory store flagged "recommend revoke" in July — it has since been revoked and now 401s. The
dead string should still be scrubbed.)_

## Cabinet dimensions — ESTIMATED, pending measurement

⚠️ **Every number in this section is inferred, not measured.** Joe publishes external dimensions
only inside GIF construction drawings. These are derived from the figures he _does_ publish plus
constraints visible in the build photos.

**Anchors:** internal volume **75 L**; front damping panels **1200 mm tall** (so internal height ≈
1200); 6.5″ drivers (~165 mm frame) must fit the baffle with margins; front panel **18 mm**.

### Joe's cabinet (estimated)

|        | Internal | External @ 18 mm walls |
| ------ | -------- | ---------------------- |
| Height | ~1200    | **~1236 mm**           |
| Width  | ~190     | **~226 mm**            |
| Depth  | ~329     | **~365 mm**            |

1200 × 190 × 329 = 75.0 L, and ~48.7″ × 8.9″ × 14.4″ matches the proportions in the build photos.

### This build (estimated)

Joe's **outer** dimensions held, **25.4 mm** walls, **19 mm** front:

```
internal ≈ 1185 × 175 × 321  →  ~66.6 L   (vs 75 L, −11%)
```

**Confidence:** height ±30 mm; **width and depth no better than ±25 mm**, i.e. **±8 L on volume**.
Directionally solid, numerically soft.

### The volume loss probably lands inside Joe's own sanctioned window

Smaller box → higher tuning. Holding the published port length:

```
Fb ≈ 40 × √(75 / 66.6) ≈ 42.4 Hz
```

Joe explicitly allows this: _"increasing Fb up to 42-44 Hertz (just shorten the vent)"_ for a static
alignment. **So the deviation may be self-correcting.**

⚠️ Note the counterintuitive part: to hold **40 Hz** in a _smaller_ box the port must get **~18 mm
LONGER**, not shorter. Do not shorten a port reasoning that a smaller box needs less port.

_(Port arithmetic uses an approximate end correction — treat as indicative.)_

## ✅ Don't calculate the volume. Measure the tuning.

**A vented box's impedance curve has two peaks with a saddle between them, and that saddle is Fb.**
Measuring it reads the box's real tuning directly — including bracing, damping and driver
displacement that no external measurement captures. It makes the whole estimate above irrelevant.

Spare **Parts Express ports** are on hand, which makes iterative trimming practical.

**Sequence:**

1. **Measure the current MFC cabinet's impedance.** The saddle gives real Fb, and back-solves
   effective volume better than a tape measure. Needs a series-resistor jig rather than the UMIK —
   same session as the gated acoustic measurements in the Method above.
2. **Fit the ULD drivers, then re-measure.** Different Vas/Qts move the alignment at identical
   volume.
3. **Trim a port toward target, re-measure, repeat.** Cutting is one-way — start long and bracket
   down. A too-long port tunes low and can be shortened; a too-short one is scrap.

⚠️ **Fit the ULD drivers BEFORE finalising port length.** Joe's per-variant port lengths exist
because the drivers differ. Trimming to a target derived from the MFC drivers and then swapping to
Purifi mistunes it a second time.

**This supersedes the "measure the internal volume before cutting a ULD port" blocker above** — the
measurement to take is Fb, not volume, and it is not blocking so much as scheduling.

### Placeholder — replace with measured values

| Quantity                           | Measured | Date |
| ---------------------------------- | -------- | ---- |
| External H × W × D                 | ⬜       |      |
| Baffle width                       | ⬜       |      |
| Port length (as built)             | ⬜       |      |
| **Fb from impedance saddle (MFC)** | ⬜       |      |
| Fb after ULD fit                   | ⬜       |      |
