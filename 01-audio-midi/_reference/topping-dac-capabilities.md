# Topping DAC capabilities — house reference

**Purpose: stop re-deriving what these DACs can do.** Capabilities have been guessed wrong more than
once, and a wrong guess about volume support has already propagated into project notes and shaped a
design. Check here first. If a device is not listed as verified, **go read its manual rather than
inferring from a sibling model** — Topping's range is not internally consistent.

Manuals for house audio hardware are archived under the family documents share
(`documents/manuals/audio/`).

---

## Verification status

**All measured 2026-08-27 by plugging each DAC into a Pi and reading ALSA/USB directly.** No claim
below is inferred from a manual's silence.

| Device               | Host-controllable volume? | Steps                       | Evidence           |
| -------------------- | ------------------------- | --------------------------- | ------------------ |
| **D30 Pro**          | ✅ **YES**                | 128, 1 dB (−127…0 dB)       | measured on-device |
| **D90 III Discrete** | ✅ **YES**                | **2032, ~1/16 dB** (−127…0) | measured on-device |
| **DX5 II**           | ✅ **YES**                | **2032, ~1/16 dB** (−127…0) | measured on-device |
| **D50s**             | ✅ **YES**                | 128, 1 dB (−127…0 dB)       | measured on-device |

## ⚠️ The UAC2 volume and the device's own volume are SEPARATE, and they compound

Measured on a DX5 II (office, 2026-08-27). Two ALSA writes, one of them with the DAC awake:

```text
panel:  -30 dB       # device's own volume — did not move
ALSA:   -95.25 dB    # UAC2 stream volume — set twice by the host
```

The front panel never tracked the host control. These are **two attenuators in series**, so total
attenuation is their sum — about −125 dB in the state above, which presents as a DAC that appears
completely dead.

**Both attenuators are real — confirmed audibly** (DX5 II, office, headphones, music playing):

| host (UAC2) | device (panel) | total    | result        |
| ----------- | -------------- | -------- | ------------- |
| −63.50 dB   | −30 dB         | −93.5 dB | **inaudible** |
| 0.00 dB     | −30 dB         | −30 dB   | **audible**   |

So this is not the E30 failure mode: the UAC2 control genuinely attenuates. And the panel held −30
dB across every write, with the DAC awake and a stream running — so the two are independent, and
their attenuation sums.

**Design rule that follows: a controller must own exactly one of them and pin the other at unity.**
Otherwise Snapcast drives the UAC2 control while a HID client drives the device volume, the two
compound, and the same knob position sounds different depending on hidden state.

Resting state for a host-controlled node should therefore be **UAC2 at 0 dB (max)**, with the
device's own attenuator carrying the volume — or the exact inverse, chosen deliberately and
documented per room. Never both.

⚠️ **Unknown for the D50s and D30 Pro.** Neither exposes HID, so the UAC2 control is the only
host-reachable one and the question does not bite today. But whether their UAC2 control drives the
same attenuator as their front panel is **untested** — do not assume it matches the DX5 II's
behaviour either way.

### Auto-standby confounds these measurements

The DX5 II drops to standby after ~1 minute with no valid input signal. The first attempt at this
test silently wrote to a powered-off device. **Confirm the unit is awake before and after any
measurement**, or hold a stream open while testing.

⚠️ **The DX5 II row is not apples-to-apples.** The other three were read from ALSA on a Pi, where
`amixer contents` reports `min`/`max` and `dBminmax` straight from the UAC2 descriptor. The DX5 II
was read over **USB HID from a Mac**, which returns a value and no range. Its step count is
genuinely unknown. To make it comparable, plug it into a Pi and run `amixer -c <n> contents`.

⚠️ **And its dB figure is computed, not reported.** `toppingctl`'s `readsettings.py` renders volume
as `-raw/2`, hardcoding 0.5 dB per step. But `volumeStep` is a _device setting_
(`{0: 'half_db', 1: 'one_db'}`) that nothing in the code reads before dividing. Set the device to
`one_db` from the panel, remote or vendor app and every dB number the tool prints is wrong by 2x,
silently.

## USB descriptor facts (measured 2026-08-27)

| Device           | `bcdDevice` | Serial reported |
| ---------------- | ----------- | --------------- |
| D30 Pro          | `0x0244`    | **none**        |
| D50s             | `0x0103`    | **none**        |
| D90 III Discrete | `0x0052`    | **none**        |
| DX5 II           | —           | `YYMM-017XG-…`  |

### ⚠️ Serial numbers are NOT a usable identity key

**Three of four DACs report no USB serial at all.** Only the DX5 II does, and its value begins
`YYMM-`, which reads like an unsubstituted template rather than a per-unit serial — so it may not be
unique across DX5 II units either.

Any design keyed on `(host, serial)` fails on this hardware. What rescues it is the deployment
shape: **one Pi per DAC**, so the agent's own identity names the device, with the product string as
display name. See [`01-022`](../01-022-multi-dac-control-plane.md).

### `bcdDevice` is not confirmed to be the firmware version

`bcdDevice` is the USB _device release number_. Vendors commonly set it to the firmware revision,
and the D30 Pro's `2.44` is plausible against Topping's 2.x scheme (the DX5 II gates features on
"firmware ≥ 2.40"). **But the fleet reads 2.44 / 1.03 / 0.52**, which looks more like per-model
device revisions than one firmware scheme. **Unconfirmed** — check the unit's own setup menu and
compare before treating `bcdDevice` as the firmware version.

**All four are measured. Nothing in this table is inferred.**

`--mixer hardware:` is not theoretical: `kitchen` has run `snapclient --mixer "hardware:D50s "`
continuously since 2026-07-26, sitting at 118/127. The "exposed but non-functional" failure mode
seen on the sibling E30 does **not** apply to that unit — it is load-bearing in daily use.

⚠️ **The D50s control name carries a trailing space** — `'D50s '`. The working config is
`--mixer "hardware:D50s "`. Retyping it without the space silently mismatches.

### HID presence tracks Topping's _Tune_ support list

| Device           | On Tune list | `/dev/hidraw` |
| ---------------- | ------------ | ------------- |
| D90 III Discrete | ✅           | ✅ present    |
| DX5 II           | ✅           | ✅ present    |
| D50s             | ❌           | ❌ absent     |
| D30 Pro          | ❌           | ❌ absent     |

The list reliably predicts whether a unit exposes a host control channel — while saying nothing
about register-map compatibility between the units that have one.

### ⚠️ Every Topping here shares USB product ID `152a:8750`

Measured: the **D30 Pro**, the **D90 III Discrete** and the **D50s** all enumerate as `152a:8750` —
the same ID as the DX5 II, which `toppingctl` already documents as shared with the DX1 II and E50
II. That is **six known models on one PID**, whose register maps _collide with different meanings_.

**PID is therefore useless for identification.** The USB product string is the only discriminator,
which is what the vendor's own app relies on and what `toppingctl._check_model()` implements. Never
select a register map by PID.

---

## The "no host-side volume" claim was wrong

An earlier version of this file asserted the D30 Pro had no host-controllable volume, reasoning from
its manual not mentioning one. **Measured, it does** — and so does the D90 III:

```text
# D30 Pro, living-room Pi
numid=3  'D30 Pro Playback Volume'
  type=INTEGER, access=rw---R--, min=0, max=127
  dBminmax-min=-127.00dB, max=0.00dB
FEATURE_UNIT  bmaControls(0) 0x0000000f     # mute + volume, master, R/W

# D90 III Discrete, office Pi
numid=4  'D90 III Discrete Playback Volume'
  type=INTEGER, access=rw---R--, values=2, min=0, max=2032
  dBminmax-min=-127.00dB, max=0.00dB
```

Both are genuine UAC2 feature units, read/write, dB-scaled. `--mixer "hardware:<name>"` should work
on either, exactly as the kitchen already does with its D50s.

**Still untested:** whether _setting_ the control audibly changes output level. The sibling E30
reportedly exposes a control that does nothing in pre-amp mode, and a Roon developer notes "exposed
but non functional… happens quite often". Enumeration is necessary, not sufficient — confirm audibly
before designing on it.

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

### Volume control paths

- **Front knob** and **IR remote** — verified from the manual; house IR codes are deployed.
- **USB (host-controllable)** — ✅ **verified on-device**, see above.

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
- **D90 III Discrete** — **volume: measured, host-controllable** (2032 steps). It also presents
  **two USB HID interfaces** (`/dev/hidraw0`, `HID_NAME=Topping D90 III Discrete`), the same shape
  as the DX5 II, and it appears on Topping's official _Tune_ supported-models list. So `toppingctl`
  control is plausible. ⚠️ **Its register map is still unverified and must not be assumed to match
  the DX5 II's.** The E50 II and DX1 II are on that same Tune list _and_ share this PID with
  colliding register meanings. Speaking the protocol and sharing a register map are different
  claims. It is _not_ a confirmed model in `toppingctl`'s device table; follow that repo's
  verification sequence before any write.

---

## The rule this file encodes

**Topping model names do not imply shared capabilities.** D30 Pro, D50s, D90 III and DX5 II differ
in volume support, host controllability and register layout. Before asserting what any of them can
do: read the manual, or read the device. Then record it here.
