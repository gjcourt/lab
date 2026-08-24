---
title: 'Headphone PEQ Generation (Topping DX5 II)'
number: '01-018'
category: 'audio-midi'
difficulty: 'Easy'
time_commitment: '1-4 hours'
target_skills:
  'AutoEQ, parametric EQ (peaking/shelf filters), headphone FR measurement & target curves, Topping
  Tune / DX5 II on-device PEQ'
status: 'In Progress'
depends_on:
  - hardware/topping-dx5-ii
---

# Headphone PEQ Generation — Agent Handoff Brief

**Objective:** Generate parametric EQ (PEQ) presets for each headphone below, correcting measured
frequency response toward a defined target. Output presets sized for the playback hardware's PEQ
limits and formatted for direct loading.

**Owner priority:** Objectivist — accuracy first. Correct toward target FR; minimize audible
distortion. Do **not** apply "house sound" voicing unless explicitly flagged as an optional variant.

---

## 1. Playback chain & hard constraints

- **DAC/amp:** Topping DX5 II (dual ES9039Q2M). Drives all units with huge headroom — amplification
  is **not** a limiting factor.
- **PEQ engine:** DX5 II on-device PEQ = parametric peaking + shelf filters, plus a global
  preamp/gain. **Loaded with [`toppingctl`](https://github.com/gjcourt/toppingctl)** — an
  AutoEQ/oratory1990 `ParametricEQ.txt` is applied directly over USB HID, preamp included, with no
  vendor software involved. Topping Tune remains a fallback and a cross-check.
- **Band count is 10 for planning purposes, and the reason is unresolved.** Eleven registers
  (`0x91`–`0x9b`) accept band writes and the vendor app writes all eleven, but its UI reports
  capacity as "BANDS n / 10". Nobody has confirmed the 11th band is audible, so presets stay at 10.
  See `_reference/topping-dx5ii-hid-protocol.md`.
- **HARD LIMIT: max 10 filter bands per preset.** Every generated preset must fit in ≤10 bands. If
  AutoEQ's optimal solution exceeds 10, constrain the band count.
- **Preamp/negative gain is mandatory.** Any preset that boosts must include a negative global
  preamp equal to (or more negative than) the highest cumulative positive gain, to prevent
  inter-sample/DAC clipping. Report the preamp value with every preset.
- **Filter format required per band:** `Type` (PK / LSC / HSC), `Fc` (Hz), `Gain` (dB), `Q`. Plus
  one global `Preamp` (dB) per preset. This matches AutoEQ's `ParametricEQ.txt` output and Topping
  Tune's import fields.

---

## 2. Targets (set per type; default = Harman)

- **IEMs — default `Harman IE 2019 v2`.** Alternative to evaluate: **Crinacle IEF Neutral** — two of
  the three IEMs are Crinacle-tuned collaborations, so against the IEF target they may need
  _minimal_ correction. Generate against Harman IE 2019 as primary; optionally produce an IEF-target
  variant for comparison.
- **Over-ears — default `Harman OE 2018`.** Consider the `harman_over-ear_2018_wo_bass` target + a
  **+3 to +6 dB bass-boost parameter** if full Harman bass is judged excessive (owner to confirm
  preference). Generate the full-Harman version as primary.
- Targets are a **parameter**, not a fixed choice — expose the target used in each preset's metadata
  so the owner can regenerate against a preference-shifted target later.

---

## 3. The collection + measured correction regions

The "regions" below are the **known measurement-consensus deviations** to sanity-check the
auto-generated filters against. **Do not treat these as final filter values** — pull exact
`Fc/Gain/Q` from the numeric sources in §4. Use these only to verify the output is targeting the
right areas and hasn't mis-fit.

### IEMs

| #   | Model                                    | Driver           | Known deviation regions to correct (vs. Harman IE)                                                                       | Notes                                                                                    |
| --- | ---------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| 1   | **Truthear × Crinacle Zero:RED**         | 2× DD            | Deliberate **sub-bass shelf** (elevated ~20–100 Hz) — reduce only if targeting strict Harman; minor **lower-treble** adj | Target-tuned; low distortion; smooth. Minimal correction expected vs. Harman/IEF.        |
| 2   | **Moondrop × Crinacle Blessing 2: Dusk** | 1DD + 4BA hybrid | **Treble peak(s) ~5–8 kHz** (BA timbre) — primary target; check **upper-treble ~10 kHz**; bass near-neutral              | Very target-adherent except the treble peak. This is the main fix.                       |
| 3   | **Moondrop Quark**                       | 1× DD (budget)   | **Upper-mid / lower-treble unevenness**; fit-dependent treble; coarser overall                                           | Lowest priority; correction is approximate and **highly fit/insertion-depth dependent**. |

### Over-ears

| #   | Model               | Driver | Known deviation regions to correct (vs. Harman OE)                                                                | Notes                                                                                       |
| --- | ------------------- | ------ | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 4   | **HiFiMan Sundara** | Planar | **Treble peaks ~5–6 kHz and ~9–10 kHz** (primary); small **low-shelf bass lift** to meet Harman; watch mid-treble | oratory1990 preset exists — prefer it as the source of truth. Higher unit-to-unit variance. |
| 5   | **HiFiMan Ananda**  | Planar | **Bright treble peaks ~5–8 kHz** (primary); small **bass shelf** to target; wide-band treble tilt down            | Owner is selling this unit — generate the preset but flag as **low priority / optional**.   |

> **Note on distortion:** PEQ corrects FR, not distortion. The over-ears (Sundara/Ananda) show
> rising **bass THD at high SPL** that EQ cannot fix — do **not** apply large low-shelf boosts that
> push them into higher excursion/distortion. Keep bass boosts conservative and note this tradeoff
> in the preset comments.

---

## 4. Authoritative numeric data sources (pull exact values here)

Use these in priority order. Prefer **oratory1990** measurements/presets for over-ears (same rig
used to derive the Harman target), **Crinacle** for the IEMs (his collabs, measured on his rig).

- **AutoEQ** — <https://github.com/jaakkopasanen/AutoEq> and web app <https://autoeq.app>

  - Repo contains numeric FR CSVs (oratory1990, Crinacle, Rtings, Innerfidelity) + a target
    library + a CLI that outputs parametric presets directly.
  - Example CLI (adapt input path/target/band-count per unit):

    ```bash
    python -m autoeq \
      --input-file="measurements/oratory1990/data/over-ear/HiFiMan Sundara.csv" \
      --target="targets/harman_over-ear_2018.csv" \
      --output-dir="results" \
      --parametric-eq \
      --parametric-eq-config=8_PEAKING_WITH_SHELVES \
      --max-gain=6 --bass-boost=0 \
      --fs=48000
    ```

    - `8_PEAKING_WITH_SHELVES` = 8 peaking + low shelf + high shelf = **10 bands total** (matches
      the DX5 II limit). Confirm the config resolves to ≤10 filters.
    - Tune `--max-gain` and `--bass-boost` conservatively (see distortion note above).

- **oratory1990 preset list** (Reddit wiki) —
  <https://www.reddit.com/r/oratory1990/wiki/index/list_of_presets/> — ready-made Harman-target PEQ
  for Sundara/Ananda; use as cross-check against AutoEQ output.
- **Crinacle measurements / graphing** — <https://crinacle.com> and the squig.link databases — for
  Zero:RED, Blessing 2: Dusk, Quark FR curves vs. IEF/Harman IE targets.
- **AutoEQ web app** — <https://autoeq.app> — fastest path; select model + target + "Parametric
  EQ" + set band count to 10, copy the filter table + preamp.

---

## 5. Deliverable per headphone

For each of the 5 units, produce:

1. A **≤10-band parametric preset** (Harman target, primary).
2. The **global preamp (dB)** for that preset.
3. The **target + source measurement** used (metadata line).
4. _(IEMs only, optional)_ an **IEF-target variant** for comparison.
5. _(Over-ears, optional)_ a **wo_bass + bass-boost variant** if the owner prefers less bass.

**Output format** (one block per preset — this is `toppingctl apply <file>` input verbatim, and
Topping-Tune-importable):

```text
# <Model> — target: <target> — source: <source> — preamp: <-X.X dB>
Preamp: -X.X dB
Filter 1: ON PK Fc <Hz> Gain <dB> Q <Q>
Filter 2: ON PK Fc <Hz> Gain <dB> Q <Q>
...
Filter 10: ON HSC Fc <Hz> Gain <dB> Q <Q>
```

---

## 6. Caveats to carry into the work

- **Unit variation:** HiFiMan planars have notable sample-to-sample variance, especially in the
  treble. Presets are a database-average starting point, not a calibrated fit to the owner's
  specific units. Note this.
- **IEM fit dependence:** IEM treble/upper-mid response shifts with tip and insertion depth. The
  Quark especially is fit-sensitive. Flag that presets assume the measurement rig's coupling.
- **Don't over-EQ the peaks:** narrow, high-Q treble cuts can sound worse than a gentler correction
  if the peak's exact center differs on the owner's unit. Prefer moderate Q unless the source data
  justifies otherwise.
- **Verify ≤10 bands and clipping-safe preamp on every preset before finalizing.**
- **Preamp handling is conditional — check it per preset.** `toppingctl apply` writes the preset's
  preamp to the confirmed `0x9c` register **only when the preset declares one** (a `Preamp:` line in
  AutoEQ `.txt`, or `preamp_db` in JSON). For those, do not lower the volume by hand as well, or you
  attenuate twice. A preset that boosts and declares no preamp writes nothing, and the device keeps
  whatever preamp was last set — which cannot be read back. Every preset produced here must carry an
  explicit preamp for that reason.

---

## Exit Criteria

- [ ] ≤10-band **Harman-target** preset generated for all 5 units, each with a clipping-safe
      **negative preamp** reported (preamp ≥ cumulative positive gain).
- [ ] Every preset verified **≤10 filter bands** (DX5 II limit) and in the required per-band format
      (Type/Fc/Gain/Q + global Preamp), Topping-Tune-importable.
- [ ] Each preset's **metadata** records the target + source measurement used.
- [ ] Output **sanity-checked against the §3 correction regions** (right areas targeted, no mis-fit;
      moderate Q on treble cuts).
- [ ] _(Optional)_ IEF-target IEM variants + `wo_bass` + bass-boost over-ear variants produced for
      comparison.

## Progress

- [ ] Pull numeric FR/measurement data (AutoEQ CSVs / Crinacle / oratory1990)
- [ ] Generate Harman-target presets (5 units, ≤10 bands, safe preamp)
- [ ] Verify band count + preamp + §3 region sanity-check
- [ ] (optional) alternate-target variants
