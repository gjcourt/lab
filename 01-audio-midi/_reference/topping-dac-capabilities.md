# Topping DAC capabilities — house reference

**Purpose: stop re-deriving what these DACs can do.** Capabilities have been guessed wrong more than
once, and a wrong guess about volume support has already propagated into project notes and shaped a
design. Check here first. If a device is not listed as verified, **go read its manual rather than
inferring from a sibling model** — Topping's range is not internally consistent.

Manuals for house audio hardware are archived under the family documents share
(`documents/manuals/audio/`).

---

## Verification status

| Device               | Volume?                                   | Source of truth       | Verified        |
| -------------------- | ----------------------------------------- | --------------------- | --------------- |
| **D30 Pro**          | ✅ **yes** — but **host control UNKNOWN** | official manual (PDF) | 2026-08-27      |
| **DX5 II**           | ✅ **yes**                                | live device read      | 2026-08-27      |
| **D50s**             | ✅ likely                                 | inferred — see below  | ❌ NOT verified |
| **D90 III Discrete** | ❓ unknown                                | —                     | ❌ NOT verified |

---

## D30 Pro — verified from the manual

### ⚠️ It has a volume control, and it is adjustable **by default**

The single most-repeated error about this unit is calling it a fixed-output DAC. It is not. Output
mode is a setting with two values:

| Screen display | Mode                                                   |
| -------------- | ------------------------------------------------------ |
| **`m-p`**      | **Pre-Amp mode — volume adjustable — DEFAULT**         |
| `m-d`          | DAC mode — volume **not** adjustable, fixed at maximum |

From the manual, verbatim:

> "In PRE (Pre-amplifier) mode, the D30 pro will display the volume level. When the sampling rate of
> the input signal changes, it will display the sampling rate for 2 seconds and then continue
> displaying the volume level; In DAC mode, the D30 pro will always display the sampling rate, keep
> the maximum volume output and the volume is not adjustable."

So "the D30 Pro has no volume" is only true of a unit someone deliberately switched to `m-d`. Out of
the box it is a pre-amp with an adjustable level.

### Volume control paths

- **Front knob** — rotate to adjust. _Verified: manual._
- **IR remote** — dedicated volume up / volume down keys. _Verified: manual, and the house IR codes
  are deployed._
- **USB (host-controllable) — ❓ UNKNOWN, NOT TESTED.** See below. Do **not** state either way.

### ⚠️ Whether USB volume works is an OPEN QUESTION, not a settled "no"

An earlier version of this file asserted "no host-side volume." **That assertion was not evidence.**
It came from the manual not mentioning USB volume — and a manual describes the front panel and
remote, not USB descriptors. Absence of evidence got written down as evidence of absence, in the
file whose entire purpose is preventing exactly that.

**Why it is genuinely plausible the D30 Pro does expose USB volume:**

- USB Audio Class 2 lets a device advertise a **feature unit** with volume. Whether one appears is a
  property of the USB firmware, not of the product tier — so a D50s having one implies nothing about
  the D30 Pro either way.
- The D30 Pro accepts PCM to 384 kHz/32-bit and native DSD256 over USB, i.e. an XMOS-class interface
  with a vendor driver — the kind that commonly does advertise a volume feature unit.
- It demonstrably **has an attenuator to expose**, since Pre-Amp mode is real.

**⚠️ The test is only valid in `m-p` (Pre-Amp) mode.** In `m-d` (DAC) mode volume is fixed at
maximum, so a host control would plausibly be absent or inert. A test run in DAC mode would produce
a false negative — and may well be how the "no host volume" belief started.

**How to settle it.** The D30 Pro must be connected over **USB** (in the current living-room chain
it is fed S/PDIF from the HAT, so this cannot be tested as-wired):

```bash
# put the unit in m-p Pre-Amp mode FIRST, then:
aplay -l                       # find the card number
amixer -c <card> scontrols     # does a volume control appear?
alsamixer -c <card>            # visual confirmation

# and check for a HID control interface like the DX5 II's:
python3 -c "import hid; print(hid.enumerate(0x152a, 0))"
```

**Why the answer matters:** if a UAC2 control appears, the living room needs **no digital-domain
volume at all** — it becomes `--mixer "hardware:<D30Pro>"`, identical to the kitchen's as-built
pattern. That is a materially different design, so test before building.

**If and only if USB volume turns out to be absent**, the fallback constraint applies: IR is the
sole remote path, and IR volume is **relative up/down with no state readback**, so it cannot back an
absolute "set to 40%" slider — you can nudge, but never know or command a level.

### Inputs / outputs

| Direction   | Connectors                                     | Notes                                                              |
| ----------- | ---------------------------------------------- | ------------------------------------------------------------------ |
| **Inputs**  | USB, **coaxial S/PDIF**, **optical (Toslink)** | One active at a time; switched by remote or front button           |
| **Outputs** | Balanced **XLR** + single-ended **RCA**        | Selectable: `O-1` RCA only · `O-2` XLR only · `O-3` both (default) |

**It has its own optical input.** A TV can feed the D30 Pro directly over Toslink with no capture
device and no computer in the path — at the cost of input _switching_ rather than _mixing_.

### Format ceilings

| Input      | PCM                          | DSD                                   |
| ---------- | ---------------------------- | ------------------------------------- |
| USB        | 44.1 kHz–384 kHz / 16–32 bit | DSD64–DSD256 native, DSD64–DSD128 DoP |
| Coax / Opt | 44.1 kHz–192 kHz / 16–24 bit | DSD64 (DoP)                           |

Output level: 2 Vrms @ 0 dBFS (RCA), 4 Vrms @ 0 dBFS (XLR). Output impedance 20 Ω RCA / 40 Ω XLR.

### Other settings (all remote-settable)

- **PCM filters** `F-1`…`F-5` (linear / minimum phase, fast / slow roll-off, NOS)
- **Screen brightness** `L-1`…`L-4` (`L-4` auto-blanks after 30 s idle)
- **Auto standby** `A-O` on (default) / `A-C` off
- **Factory reset** — in standby, turn the front knob counter-clockwise until the screen fully
  lights

---

## DX5 II — verified by live device read

Read over USB HID with `toppingctl` (see [`01-022`](../01-022-multi-dac-control-plane.md)); these
are observed values, not manual claims:

- **Volume: yes, host-readable and host-writable.** Reports as a raw step plus a dB value (e.g.
  `volume 60 = -30.0 dB`).
- 52 settings records exposed on firmware ≥ 2.40; inputs, output routing, PEQ memory, crossfeed,
  filters, brightness and remote key mapping are all readable.
- **This is the only house DAC with a confirmed host-side control path.**

---

## Not verified — do not assume

- **D50s** — the as-built multi-room deployment drives its volume via
  `snapclient --mixer "hardware:D50s"`, i.e. an **ALSA UAC2 mixer control over USB**, which is
  strong evidence it exposes host-side volume. Recorded as _likely_, not verified, because it is
  inferred from a working configuration rather than read from the manual.
- **D90 III Discrete** — volume support, host-side control, and register map are **all unknown**. It
  is _not_ a confirmed model in `toppingctl`'s device table, and per that project's rules its
  register map must not be assumed to match the DX5 II's. Three models in this vendor's range share
  a USB product ID with _colliding_ register meanings, so sibling inference is actively dangerous
  here.

---

## The rule this file encodes

**Topping model names do not imply shared capabilities.** D30 Pro, D50s, D90 III and DX5 II differ
in volume support, host controllability and register layout. Before asserting what any of them can
do: read the manual, or read the device. Then record it here.
