# Topping DX5 II — USB HID control protocol

Originally reverse-engineered 2026-08-07 by observing Topping's own web app
(`home.toppingaudio.com`) drive the device over WebHID, plus passive HID capture from macOS. That
pass was clean-room — no vendor code was read, and every field was derived from traffic correlated
against the vendor UI.

**That is no longer true of this document.** On 2026-08-24 it was corrected against the constant
tables and settings parser inside Topping's own web bundle (web v1.10.0). Content marked
_vendor-sourced_ comes from their code, not from observation.

**Status:** decoded and **confirmed on hardware**, then **corrected against Topping's own web
bundle** (home.toppingaudio.com, web v1.10.0) in August 2026. Everything below marked
_vendor-sourced_ comes from their constant tables and settings parser, not from observation. Four
conclusions reached by observation alone turned out to be wrong; they are marked where they appear.
A third-party client ([`toppingctl`](https://github.com/gjcourt/toppingctl)) drove the device on
2026-08-07: volume and gain changes were observed on the front-panel display, including a −45.5 dB
half-step. Writes are accepted with no checksum on every register except power.

The gaps this document once listed — the input enum, the `0x2b`/`0x2d` model, and the scene-slot
mechanism — are all resolved in §5, and the `0x2b`/`0x2d` guess turned out to be wrong rather than
merely incomplete.

---

## 1. Device

|               |                                                          |
| ------------- | -------------------------------------------------------- |
| Product       | Topping DX5 II (DAC + headphone amp)                     |
| USB VID / PID | **`0x152A` / `0x8750`**                                  |
| `bcdDevice`   | `0x0239` — matches "Firmware 2.39" in the vendor UI      |
| Vendor of VID | Thesycon — the XMOS USB-audio stack, shared by many DACs |

### Interfaces

| #     | Class / Subclass | Purpose                       |
| ----- | ---------------- | ----------------------------- |
| 0     | 1 / 1            | USB Audio Control             |
| 1     | 1 / 2            | USB Audio Streaming           |
| **2** | **3 / 0**        | **HID — the control channel** |

### HID report descriptor

```text
05 01  Usage Page (Generic Desktop)
09 00  Usage (0x00)                 <- undefined: a raw vendor pipe
a1 01  Collection (Application)
15 00  Logical Minimum (0)
25 ff  Logical Maximum (255)
19 01  Usage Minimum (1)
29 08  Usage Maximum (8)
95 10  Report Count (16)
75 08  Report Size (8)
81 02  Input                        <- device -> host
19 01
29 08
91 02  Output                       <- host -> device
c0     End Collection
```

16-byte input and output reports, **no report IDs**, no feature reports
(`MaxFeatureReportSize = 0`). Output reports are the only write path.

---

## 2. Frame format

Both directions use a fixed 16-byte frame.

```text
 offset  0  1   2    3    4    5     6     7  8  9 10   11 12   13 14  15
        22 33  20  <ln> <ln> <reg> <sub>  <value BE32>  <ck>   66 77  00
        \___/                                           \___/  \___/
        magic                                          checksum footer
```

| Bytes | Meaning                                                                    |
| ----- | -------------------------------------------------------------------------- |
| 0–1   | `22 33` start-of-frame magic, constant                                     |
| 2     | **Direction / opcode** — `20` = write, `10` = read (see below)             |
| 3–4   | Length/selector. `01 01` on writes; `02`/`08` seen on device status frames |
| 5     | **Register**                                                               |
| 6     | **Sub-index** (parameter within the register)                              |
| 7–10  | **Value, signed big-endian int32**                                         |
| 11–12 | Checksum — populated by the device, **left `00 00` on host writes**        |
| 13–14 | `66 77` end-of-frame magic, constant                                       |
| 15    | `00` padding                                                               |

> **Writes need no checksum.** Every captured host→device frame carries `00 00` at 11–12 and the
> device accepts them. This removes the usual barrier to writing a third-party client.

### Read vs write (byte 2)

Almost every frame uses `0x20` = write. Two frames in the settings capture used **`0x10` with a zero
payload**, which reads as a **read/query**:

```text
22 33 10 01 01 71 0c 00 00 00 00 00 00 66 77 00
22 33 10 01 01 71 37 00 00 00 00 00 00 66 77 00
```

**Tested from a third-party client 2026-08-07: reads do NOT return state.** A read request is
answered with an _echo of the request_, value still zero, but with the **checksum filled in**:

```text
sent: 22 33 10 01 01 91 02 00 00 00 00 00 00 66 77 00
recv: 22 33 10 01 01 91 02 00 00 00 00 7d 73 66 77 00
                                       ^^^^^ device-computed
```

Band 1 frequency was 200 Hz at the time; the response carried 0. Verified on a single isolated
request with a 3 s window, so it is not a timing artifact.

**Consequence for THIS client:** the `0x10` request form does not return state, so `toppingctl`
caches what it writes.

### The read path: register `0x12` sub `0x06` — bulk state dump

**Found 2026-08-07.** Writing `12 06 = 0` makes the device stream a large structured dump. It is not
a request/response on the queried register; it is a one-shot bulk transfer, which is why probing
individual registers found nothing.

The dump frames use a **different header layout** — this is what made them unrecognisable earlier:

```text
22 33 20 | 4e | 08 | 11 06 | 00 fc 05 01 | ac 16 | 66 77 00
  magic    ^^   ^^   reg/sub   payload      cksum   footer
        count  index
```

Byte 3 is a **record count** (`0x4e` = 78), byte 4 the **record index** — where normal frames carry
`01 01`. All records report `reg=0x11 sub=0x06`.

Payloads are heterogeneous, so this is a serialized structure rather than a register array:

| Example payload               | Reads as                                      |
| ----------------------------- | --------------------------------------------- |
| `61 6e 79 44`                 | ASCII `"anyD"` — text, byte-order swapped     |
| `63 76 65 64` / `69 66 6e 6f` | more ASCII fragments (looks like `devconfig`) |
| `01 6a 77 e5`                 | the preamp value seen in every `9c` write     |
| `00 00 0f a0` / `00 00 13 88` | 4000 / 5000 — plausible frequencies           |

The ASCII strongly suggests the **preset names** ("Bass 1", "Airy", `devconfig6`) live here, which
would explain how the vendor app knows them.

**To trigger it,** replay the app's connect preamble; `12 06` alone is enough in testing, but the
full sequence is what the app sends:

```text
11 01 = 2        71 0c READ (0x10)     71 0f = 0
71 37 READ       11 20 = 1             12 06 = 0     <- dump follows
```

Verified from a third-party client with no vendor software running.

### Dump record layout (78 records × 4 bytes)

| Index      | Content                                                                                                                                      |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `00`–`02`  | **Name string.** ASCII in byte-swapped 32-bit words: `63 76 65 64` → `devc`, `69 66 6e 6f` → `onfi`, `00 00 36 67` → `g6` = **"devconfig6"** |
| `03`       | **Band count** — 11                                                                                                                          |
| `05`, `07` | **Preamp** L/R — `0x016A77C4`, byte-identical to the `9c 01` / `9c 03` writes. This is what anchors the parse                                |
| `09`…      | **Per-band triples**: `(freq, Q, type<<8 \| enabled)`. An unused band reads `632 / 7070 / 0x0100` = 632 Hz, Q 0.707, peaking, disabled       |

Confirmed 2026-08-08 against a _known_ loaded preset (a 10-filter E3 correction): the frequencies
and Q values appeared in order at stride 3, ten for ten. The right channel repeats from index `0x2a`
— consistent with 11 bands x 3 records x 2 channels.

**Gain is still unlocated.** No record matched the expected tenths-of-a-dB values, and a Q25 reading
of the third element does not fit either. Gain is either elsewhere in the structure or absent from
this dump.

> ⚠️ **The capture method is racy — do not trust a single dump run.** The device can emit MORE THAN
> ONE dump in a capture window. Keying records by index alone (`recs[frame[4]] = payload`) lets a
> later dump silently overwrite an earlier one, so two identical runs can disagree: one returned the
> live E3 preset, the next returned factory defaults. Before doing further work here, delimit dumps
> properly (watch for index resetting to `00`) and reject any capture that does not yield exactly
> one complete set.

### Preset names are NOT stored on the device

Tested directly: a preset renamed to `ZZZZTEST` in the vendor app, then dumped, **did not appear**
anywhere in the 78 records — the device still reported `devconfig6`.

So despite the sidebar heading "Local PEQ (**Hardware**)", the preset names (Bass 1, Airy, Warm, …)
live in the web app's browser storage, not on the DAC. The device holds a single active
configuration with its own internal name.

Consequences for a third-party client: preset names cannot be read or written over HID, they do not
survive a change of browser or machine, and any local tool should own its own naming rather than
trying to mirror the app's.

### Earlier note (superseded, kept for context)

after `toppingctl` wrote a band the vendor app had never seen (PK 1 kHz −12 dB Q 2.0), the app
displayed it correctly on reconnect, along with a volume set externally. The app is therefore
reading device state by some mechanism not yet identified. Finding it is the main remaining work if
a third-party client wants true state sync rather than a write-through cache.

### The echo is a checksum oracle — but only for some registers

Sending a frame with opcode `0x10` and `00 00` in bytes 11–12 returns the same frame with a valid
checksum. Useful, but **not universal.**

A read-only sweep of all 64 `0x71` sub-indices (2026-08-07) found **only 5 that answer**: `0x0c`,
`0x0f`, `0x33`, `0x34`, `0x37` — essentially the set the vendor app itself polls. PEQ registers
(`0x91`–`0x9b`) also echo.

**Everything operationally interesting is silent:** power, volume, input, output, gain, scene-save.
So:

- the oracle **cannot** produce the checksum for `71 01` (power); driving sleep/wake still means
  replaying the two captured frames verbatim, which is sufficient because the register is binary;
- silence does **not** prove a register is absent — write-only commands and nonexistent registers
  are indistinguishable, so this is not a way to map the register space.

### Negative numbers

Two's complement. Observed during a gain drag: `ff ff ff ea` = −22 (−2.2 dB).

---

## 3. PEQ — confirmed

### Registers

| Register        | Meaning                                                                                                                                                         |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `0x91` … `0x9b` | **PEQ bands**, one register per band                                                                                                                            |
| `0x9c`          | **Preamp — CONFIRMED.** Linear gain in **Q25 fixed point**: `dB = 20·log10(value / 2^25)`. Subs `01`/`03` carry the value (L/R), `02`/`04` are enable flags = 1 |

### Preamp encoding (register `0x9c`)

```text
value = round( 10^(dB/20) * 2^25 )
dB    = 20 * log10( value / 2^25 )
```

Derived from Topping's own `0x016A77C4` (= −3.0 dB), then **verified by round trip**: the formula
predicted `0x01009B9D` for −6.0 dB, a third-party client wrote it, and the vendor app read it back.

> **The vendor app truncates the display toward zero.** A mathematically exact −6.0000000 dB renders
> as **"−5.9"**. This is a display convention, not an encoding error — a client should not
> compensate for it.
>
> **Band-count discrepancy.** Eleven registers (`0x91`–`0x9b`) accept band writes and the vendor app
> writes all of them on commit, but its UI reports capacity as **"BANDS n / 10"**. Either `0x9b` is
> not a usable band or the app caps below the hardware limit. **Settled 2026-08-24: `0x9b` is
> inert.** A `PK 1 kHz -15 dB Q 0.7` cut on band 10 was plainly audible, the identical filter on
> band 11 was not, and re-applying band 10 brought it back. `toppingctl` now offers 10 bands while
> still writing all 11 registers, so a stale band 11 is cleared.

### Sub-index map (per band register)

Left channel is 01–05, right channel repeats it at 06–0a.

| Sub (L) | Sub (R) | Field       | Encoding                   |
| ------- | ------- | ----------- | -------------------------- |
| `01`    | `06`    | Filter type | enum — see below           |
| `02`    | `07`    | Frequency   | Hz, integer                |
| `03`    | `08`    | Gain        | **tenths of a dB, signed** |
| `04`    | `09`    | Q           | **× 10 000**               |
| `05`    | `0a`    | Enabled     | `0` / `1`                  |

### Filter types

| Value | Type       |
| ----- | ---------- |
| 1     | Peaking    |
| 4     | Low Shelf  |
| 5     | High Shelf |

Confirmed against the vendor UI. The pass/notch filters it also offers will have their own values —
capture one of each to complete the enum. Values 2 and 3 are unclaimed and most likely the pass
filters.

### Worked example — confirmed against the vendor UI

UI showed: Bass 1, **Low Shelf, 200 Hz, +6.0 dB, Q 0.7070**, L+R.

```text
22 33 20 01 01 91 01 00 00 00 04 00 00 66 77 00   type  = 4     Low Shelf
22 33 20 01 01 91 02 00 00 00 c8 00 00 66 77 00   freq  = 200   Hz
22 33 20 01 01 91 03 00 00 00 3c 00 00 66 77 00   gain  = 60    +6.0 dB
22 33 20 01 01 91 04 00 00 1b 9e 00 00 66 77 00   Q     = 7070  0.7070
22 33 20 01 01 91 05 00 00 00 01 00 00 66 77 00   on    = 1
   ... 06-0a repeat the same five for the right channel ...
22 33 20 01 01 71 34 00 00 00 01 00 00 66 77 00   commit
```

Four of five fields verified directly against displayed values; the fifth (enabled) is self-evident
from bands that are off.

### Factory default for an unused band

```text
type = 1 (peaking), freq = 632, gain = 0, Q = 7070, enabled = 0
```

`632` is a default centre frequency, **not** a meaningful setting. It appears in every untouched
band and initially caused a misread during decoding.

---

## 4. Observed client behaviour

**Dragging a control streams live updates.** While a gain knob moves, the app sends only the
changing parameter (`91 03` and `91 08`) repeatedly — a real-time preview with no commit.

**Releasing rewrites the entire bank.** On commit the app writes all 11 bands × 10 sub-indices = 110
frames, then `71 34`. Wasteful, but convenient: one capture of a commit yields complete device
state.

A consequence worth knowing while capturing: the tail of a commit is always the unused default
bands, so a short console scrollback shows only `632 / 0 / 7070` and looks like nothing changed.

---

## 4a. Device control — register `0x71`

Non-PEQ device settings all live on register `0x71`, addressed by sub-index. Captured 2026-08-07 by
driving each control in the vendor UI and correlating against the displayed state.

| Sub        | Value(s) seen | Meaning                                                                                                                                                       | Confidence    |
| ---------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| **`0x02`** | 52–59         | **VOLUME — attenuation in half-dB steps.** `dB = −value / 2`                                                                                                  | **Confirmed** |
| `0x34`     | 1             | ~~Commit / apply~~ → **Heartbeat** (§5). Brackets every transaction                                                                                           | Confirmed     |
| `0x35`     | 1             | **SaveC1** (§5). ~~expect 2 for C2~~ — C2 is its own register `71 36`                                                                                         | High          |
| `0x05`     | 6, 4          | **Output select.** Six UI options; 6 displayed as LINE BAL. Probable order HP ALL / HP SE / HP BAL / LINE ALL / LINE SE / LINE BAL = 1–6, making 4 = LINE ALL | High          |
| `0x04`     | 3, then 2     | **Input select.** Ended on COAX with value 2. Full enum unmapped — capture each of USB / OPT / COAX / BT individually                                         | Medium        |
| **`0x17`** | 0, 1          | **GAIN — headphone amp gain, binary.** Isolated capture: toggling gain alone produced only this register, bracketed by `0x34` commits                         | **Confirmed** |
| `0x2b`     | 1, 2          | ~~Output family~~ → **CrossfeedType** (§5). The guess was wrong                                                                                               | Low           |
| `0x2d`     | 0, 1          | ~~Balanced flag~~ → **CrossfeedSimpleOption** (§5). The guess was wrong                                                                                       | Low           |
| **`0x01`** | 0, 1          | **POWER — 0 = sleep, 1 = wake.** The one register that carries a real checksum (see below)                                                                    | **Confirmed** |
| `0x0c`     | 0 (read)      | **GetSettings** (§5) — full state dump. Issued as a **read**                                                                                                  | Unknown       |
| `0x0f`     | 0             | **GetSampling** (§5)                                                                                                                                          | Unknown       |
| `0x33`     | 0 (read)      | **UsbSerial** (§5) — returns the serial as ASCII. Sensitive                                                                                                   | Unknown       |
| `0x37`     | 0 (read)      | **PeqPreviewState** (§5)                                                                                                                                      | Unknown       |

### Volume — worked example

The UI displayed **−28.5 dB** while the device held value **57** (`0x39`):

```text
57 × 0.5 = 28.5   ->   -28.5 dB      ✓
```

A slow volume ramp upward produced a strictly _decreasing_ sequence (59, 58, 57 … 52 = −29.5 dB →
−26.0 dB), confirming the value is **attenuation**, not gain. Each step is 0.5 dB.

```text
22 33 20 01 01 71 02 00 00 00 39 00 00 66 77 00     set -28.5 dB
```

Volume writes stream continuously while the control is dragged, exactly like PEQ gain, and are
followed by a `71 34` commit.

### Power — the checksum exception

Power is the **only** register observed to carry a real checksum, and it also uses `byte4 = 00`
rather than `01`:

```text
22 33 20 01 00 71 01 00 00 00 00 dc 65 66 77 00     sleep
22 33 20 01 00 71 01 00 00 00 01 1c a4 66 77 00     wake
                             ^^ ^^^^^
                          value  checksum
```

The two checksums differ with the payload, so it is computed, not a constant. **PEQ and volume
writes are accepted with `00 00`** — only power appears to require this. A client that wants to
drive sleep/wake must either solve the checksum or replay these two frames verbatim, which is
sufficient since the register is binary.

Two known plaintext/checksum pairs, for anyone attempting the algorithm:

| Payload tail         | Checksum |
| -------------------- | -------- |
| `…71 01 00 00 00 00` | `dc 65`  |
| `…71 01 00 00 00 01` | `1c a4`  |

### Register `0x11`

Two writes seen alongside output/toggle changes; meaning unknown.

```text
22 33 20 01 01 11 01 00 00 00 02 00 00 66 77 00
22 33 20 01 01 11 20 00 00 00 01 00 00 66 77 00
```

Also seen once at the head of a settings capture, unexplained:

```text
22 33 20 01 01 12 06 00 00 00 00 00 00 66 77 00     register 0x12
```

### Gain is conditional, not missing

The front-panel **GAIN** control is a **headphone-amp** gain stage. When the output is set to any
LINE mode the vendor app **disables** the control, so it emits no frames. To capture it, first set
output to HP BAL or HP SE.

## 5. Resolved against the vendor bundle (2026-08-24)

_Vendor-sourced._ Everything this section previously listed as undecoded is answered by Topping's
own constant table and settings parser. What remains open is listed at the end.

### Reads work, and always did

`byte2` is a **protocolType**: `0x10 readNack`, `0x11 readAck`, `0x20 writeNack`, `0x21 writeAck`.
This spec only ever recorded `0x20` being sent, and sending `0x10` is what makes the device answer.

Measured on hardware: the DX5 II tags its **replies** `0x20` as well — 61 reply frames to one
`GetSettings` request, none of them `0x11`. `readAck` is in the vendor's table but this device does
not emit it.

Send `readNack` for `GetSettings` and the device replies with its **entire configuration** as a
numbered array of 32-bit records — byte 4 of each frame is the record index. The earlier conclusion
that "reads return an echo, not state" was wrong. The device streams **all-zero input reports while
idle**, so listening without asking a question looks exactly like a device that never answers, which
is what "the 11-record status stream never varied" was describing.

### The unknown reads, identified

| Register | Actually                                                                      |
| -------- | ----------------------------------------------------------------------------- |
| `71 0c`  | **GetSettings** — full state dump                                             |
| `71 0f`  | **GetSampling**                                                               |
| `71 33`  | **UsbSerial** — returns the serial as little-endian ASCII. Treat as sensitive |
| `71 37`  | **PeqPreviewState**                                                           |

### Corrections to entries reached by observation

| This spec said                                                                  | Actually                                     | How it went wrong                                                      |
| ------------------------------------------------------------------------------- | -------------------------------------------- | ---------------------------------------------------------------------- |
| `0x34` = "Commit / apply"                                                       | **Heartbeat**                                | It brackets transactions, which reads like a commit                    |
| `0x2b` = output family, `0x2d` = balanced flag                                  | **CrossfeedType**, **CrossfeedSimpleOption** | Both tentative, both wrong                                             |
| Output select: 6 options, `HP ALL/HP SE/HP BAL/LINE ALL/LINE SE/LINE BAL = 1–6` | **7 options** (below)                        | Built on one observation — `6 = LINE BAL` — which happened to be right |
| Band 11 (`0x9b`) may be usable                                                  | **Inert.** Confirmed by hardware A/B/A test  | Vendor app writes all 11 registers, so traffic implied 11 bands        |

### Scene save and recall

| Register | Function                                                            |
| -------- | ------------------------------------------------------------------- |
| `71 11`  | **CallC1** — recall, previously "unmapped"                          |
| `71 12`  | **CallC2**                                                          |
| `71 35`  | SaveC1                                                              |
| `71 36`  | **SaveC2** — a separate register, not value 2 on `71 35` as guessed |

### Enums

_Vendor-sourced, device value → vendor identifier._

```text
input        0=usb  1=fiber  2=coax  3=bt
output       0=all  1=hp_all  2=line_all  3=hp_single  4=hp_balanced
             5=line_single  6=line_balanced
pcm_filter   0=f1 … 7=f8                      line_mode     0=preamp 1=dac
crossfeed    0=convolution 1=simple 2=off      input_mode    0=auto 1=manual
polarity     0=normal 1=reverse                uac_mode      0=uac1 1=uac2
volume_step  0=half_db 1=one_db                brightness    0=low 1=medium 2=high
home_page    0=normal 1=vu 2=fft               spdif_mode    0=mode1 1=mode2
vu_bar_mode  0=all_on 1=normal 2=fft 3=all_off power_trigger 0=signal 1=trigger12v 2=off
```

Full tables, plus all 64 commands and the settings field order, live in
[`gjcourt/toppingctl` → `vendor_commands.py`](https://github.com/gjcourt/toppingctl/blob/main/vendor_commands.py).

### Still open

| Area                     | Notes                                                                                                                         |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| `outputOptionMask`       | Reads `0b111` against a seven-value output enum, so it is not a bitmask over them                                             |
| Unmapped settings fields | `balance`, `sampleRate` and `dcDetectSensitivity` have no enum table. The three `*Memory` fields read through `memory_mode`   |
| Records 45–47            | `569, 569, 257`. Absent from the vendor parser; look like a version pair                                                      |
| Preset naming            | The device stores _named_ presets under Local PEQ. Names never appeared in any capture and may live only in the app's storage |
| Filter types 2, 3        | Unclaimed PEQ filter type values, probably the pass filters                                                                   |

### Unmapped settings surface (inventoried 2026-08-08)

The vendor app exposes far more than has been captured. Every one of these is reachable with the
same one-change-at-a-time method:

| Group    | Settings                                                                                                                       |
| -------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Input    | Input Detection, Input Options, UAC version, Bluetooth, Bluetooth aptX, SPDIF Mode                                             |
| Output   | Output Options, PCM Filter, Channel Balance, **Volume Step**, Polarity, Line Mode                                              |
| Display  | Language, Theme, Home view, Brightness, Classic VU 0 dB Level, VU Bar                                                          |
| Advanced | Power Trigger, Volume/PEQ/**Xfeed** Memory, Remote, Knob Press Function, Button A, Button B, DC Detect Sens, **Factory Reset** |

**Xfeed** (crossfeed) is an entire feature not yet touched — most likely the `1x1 / OFF` control in
the toolbar.

> ⚠️ **Volume Step is user-configurable (0.5 dB observed).** The volume decode `dB = −value / 2` was
> derived with this setting at 0.5 dB. It is UNKNOWN whether the register is always half-dB (with
> Volume Step only affecting knob and remote increments) or whether the scale follows the setting. A
> client that assumes half-dB could set the wrong level after a user changes this. Test before
> relying on it.
>
> ⚠️ **Factory Reset is in this register space.** Do not sweep unknown registers with writes.
> Read-only probing is safe; blind writes are not.

### Device status stream (device → host)

When a host holds the HID interface open, the device free-streams a fixed set of 11 records at
roughly 500 Hz. These proved **static** across volume changes and PEQ edits, so they are not live
state. Content unidentified.

```text
type30 idx00   22 33 20 02 00 71 30 ff c4 ff c4 87 69 66 77 00
type30 idx01   22 33 20 02 01 71 30 00 00 00 00 cd 48 66 77 00
type31 idx00   22 33 20 08 00 71 31 c4 c4 c4 c4 2c ca 66 77 00
   ... idx01-06 identical payload, differing checksum ...
type31 idx07   22 33 20 08 07 71 31 00 00 c4 c4 21 c0 66 77 00
```

With no host connected the device emits all-zero reports — a usable "idle" signal.

---

## 6. Method, for repeating this on other registers

The vendor app speaks WebHID from the browser, so both directions are observable from devtools with
no USB capture tooling. In the console on `home.toppingaudio.com`:

```js
window.__out = [];
const _s = HIDDevice.prototype.sendReport;
HIDDevice.prototype.sendReport = function (id, data) {
  const b = new Uint8Array(data.buffer || data);
  window.__out.push([...b].map((x) => x.toString(16).padStart(2, '0')).join(' '));
  return _s.apply(this, arguments);
};
```

Then change one control, and `copy(window.__out.join('\n'))`.

**Re-arm after every page reload** — the hook does not survive navigation.

Filter the console on `OUT`; the inbound status stream otherwise buries the writes at ~500 frames/s.

Passive listening alone is insufficient: the device never reports volume or PEQ state back, so the
write side is where the information is.

---

## 7. Writing to the device

A frame is trivial to construct — no checksum required:

```text
22 33 20 01 01 <reg> <sub> <int32 BE> 00 00 66 77 00
```

**First write should be a no-op** — set a parameter to the value it already holds — to confirm the
device accepts third-party framing before changing anything real. Follow any parameter change with
`71 34 = 1` to commit.

Untested and worth caution: whether malformed frames are ignored safely, and whether the device
persists writes across power cycles.
