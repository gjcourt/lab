---
title: 'DIY BLE Espresso Scale (Skale 2-emulating, for leva! gravimetric)'
number: '06-018'
category: 'coffee-espresso'
difficulty: 'Hard'
time_commitment: 'Weeks (design → PCB → firmware → calibration)'
target_skills:
  'Load-Cell Strain Gauging, 24-bit ADC (NAU7802 / I2C), nRF52 BLE (Zephyr / Arduino-nRF), GATT
  Server Emulation, LiPo + USB-C Power, DSP Filtering'
status: 'Not Started'
depends_on:
  - hardware/lucca-a53
  - 06-001-lucca-a53-mini-leva-firmware-integration
---

# DIY BLE Espresso Scale (Skale 2-emulating, for leva! gravimetric)

A **from-scratch, 100%-DIY Bluetooth-LE espresso scale** for the LUCCA A53 Mini (La Spaziale S1 Mini
Vivaldi II) whose single design goal is to **drive
[ito + `leva!`](06-001-lucca-a53-mini-leva-firmware-integration.md)'s native weight-stop** — leva!
cuts the shot at target mass itself. The trick that makes a _DIY_ scale plug into that native path:
the firmware **advertises as, and emits the byte format of, a Skale 2**, so leva! reads it as one of
its three supported scales with **zero leva!-side changes** — _provided leva! binds a scale by
advertised name, not a bonded MAC; that is the make-or-break unknown to verify before building (see
Validation)._ Onboard load cell + 24-bit ADC + nRF52840 BLE; thin enough to sit under the
portafilter on the drip tray; USB-C rechargeable with multi-month standby.

> **What makes this different from [06-007](06-007-smart-scale-integration-via-bluetooth.md).**
> 06-007 _integrates a commercial scale_ (reverse-engineer an Acaia/Timemore and bridge its data).
> **This project _builds_ the scale** — own load cell, own firmware — and has it **impersonate a
> scale leva! already supports**, so no bridge and no leva! patch are needed. 06-007 is the "read
> someone else's scale" path; 06-018 is the "be the scale leva! trusts" path.

## The four requirements (and how each is met)

| #   | Requirement                            | How this design meets it                                                                                                                                                                                                                               |
| --- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | **Plugs into gravimetrics**            | Firmware is a **Skale 2 GATT server** (weight-notify + tare). leva! set to `Method: WEIGHT` + `Stop early` reads it natively — no source scale, no bridge — **if leva! binds by advertised name** (the make-or-break to verify first; see Validation). |
| 2   | **Usable** (fast, low-noise, tolerant) | NAU7802 24-bit at ~80–320 SPS → digital filter → **~10 Hz notify** (leva!'s cadence); tare + auto-tare button; conformal-coated PCB + gasketed enclosure.                                                                                              |
| 3   | **Thin** (fits under portafilter)      | Low-profile single-point load cell + slim platform; XIAO-class module + LiPo pouch; target stack-up **≤ 18–20 mm**.                                                                                                                                    |
| 4   | **Long battery / USB-C**               | nRF52840 (BLE sleep in **µA**) + LiPo pouch + **onboard USB-C LiPo charger**; deep-sleep between shots, wake on button/tap (or duty-cycled poll); fuel gauge over standard BAS.                                                                        |

## Why "emit the Skale 2 protocol" is the winning approach (requirement #1)

leva!'s **native gravimetric stop** reads only a fixed set of scales: **Skale 2 / Felicita Arc /
Eureka** (DiFluid added on leva! 3.2+). A DIY scale gets into that path only by _being_ one of them
on the wire. Of the three, **Skale 2 is the right emulation target**:

- **Published protocol** (Atomax / Decent), so no reverse-engineering guesswork — see
  [Sources](#sources).
- **Near one-way:** the host subscribes to weight notifications and (optionally) writes a **tare**.
  There is no pairing handshake, heartbeat, or rolling auth to spoof (contrast Acaia, which needs a
  periodic keep-alive). That makes a faithful emulator small and robust. _(This is the **data
  protocol** — small to emulate. Whether leva! **binds** by name vs a bonded MAC is a **separate,
  unverified** question that gates the whole approach — see Validation.)_
- It is the **same "emit target" as Path C of the Vibrato shot-feedback-loop roadmap (Phase 2)** —
  which lives in the **`vibrato` repo** (referenced here as a black box; see
  [Cross-links](#positioning--cross-links)). The difference: there, Vibrato re-emits a _separate
  source scale's_ reading as Skale 2; **here the whole scale is DIY, so the load cell _is_ the
  source** — no upstream scale exists.

### Skale 2 BLE contract to implement

All UUIDs are the 16-bit Atomax IDs expanded into the Bluetooth base UUID
(`0000xxxx-0000-1000-8000-00805F9B34FB`).

| Characteristic        | UUID (short) | Dir (from scale) | Role                                                                             |
| --------------------- | ------------ | ---------------- | -------------------------------------------------------------------------------- |
| **Weight**            | `EF81`       | Notify           | Streams weight; host subscribes. **This is what leva! reads.**                   |
| **Command**           | `EF80`       | Write            | Host → scale commands. **Tare = `0x10`.** Also display/units/LED cmds.           |
| **Button** (optional) | `EF82`       | Notify           | Physical button events as single unsigned bytes (not needed by leva!).           |
| **Battery**           | `0x180F`     | Read/Notify      | Standard **Battery Service** (`0x2A19` level %). Skale II fixed the Skale I bug. |

**Weight notification byte layout** (per the Decent `scale_api` description of Skale II): an
**8-byte** packet — **discard the first two bytes, read the next 4 as the weight integer**, the
value carrying **0.1 g resolution** (Skale II's rated step). **Endianness, sign, and the exact scale
factor must be confirmed against a real device or the SkaleKit SDK** before trusting the cut (see
Validation). Note the published "drop-2-read-4" description may describe the BLE **advertisement
manufacturer-data** framing rather than the raw `EF81` **GATT notification** payload a subscriber
receives (dropping two then reading four would leave `ef 81` inside the "four") — resolve that
ad-vs-notification ambiguity with the sniffer capture. Emit at ~**5–10 Hz**; leva! integrates flow
from the mass slope, so cadence + low jitter matter more than raw SPS.

> **Emitter, not parser.** The reference lib [`kstam/esp-arduino-ble-scales`](#sources) (upstream of
> the fork **GaggiMate** builds on — GaggiMate uses Zer0-bit's fork) is written to _read_ these
> scales as a client. Here we run the mirror image: a **GATT _server_** that advertises the Skale 2
> name + service and **produces** EF81 notifications in that byte format, while **consuming** the
> EF80 tare write. The lib is the canonical reference for the exact framing to reproduce; the code
> direction is inverted.

## Hardware architecture

```text
 low-profile single-point load cell (full Wheatstone bridge, ~500 g–1 kg, overload-rated)
        │  (4 wire: E+, E-, S+, S-)
        ▼
   NAU7802  (24-bit ΔΣ ADC, I²C, internal PGA ×128 + LDO/ref)
        │  I²C (SDA/SCL) + DRDY (data-ready IRQ → wake MCU)
        ▼
   nRF52840  (Seeed XIAO nRF52840)  ── digital filter → tare → Skale-2 byte pack
        │                                └─ button (tare / auto-tare), status LED, opt. haptic
        ├── BLE GATT server: advertises "Skale" ; EF80/EF81/EF82 + 0x180F
        └── power: LiPo pouch ── onboard BQ25101 USB-C charger ── fuel gauge
```

### Component decisions

#### MCU / BLE — **Nordic nRF52840 (Seeed XIAO nRF52840)** ✅ recommended

The battery requirement decides this. Honest trade-off:

| Option                          | BLE sleep current            | USB-C charge | Toolchain                             | Verdict                                                                    |
| ------------------------------- | ---------------------------- | ------------ | ------------------------------------- | -------------------------------------------------------------------------- |
| **nRF52840 (XIAO nRF52840)** ✅ | **~µA** (standby < 5 µA)     | **onboard**  | Zephyr / Arduino-nRF / Adafruit nRF52 | Best battery by far; onboard **BQ25101** LiPo charger; BLE 5.4 radio.      |
| ESP32-C3 (XIAO ESP32-C3)        | ~mA-class BLE; heavier modem | needs ext.   | Arduino/ESP-IDF (easiest)             | Easier toolchain, but BLE power is an order worse — wrong for a scale.     |
| nRF52832                        | ~µA                          | needs ext.   | same nRF stack                        | Fine, but the 840 module already integrates USB + charger → less to build. |

**Pick the XIAO nRF52840:** ultra-low-power BLE + **built-in LiPo charger** + castellated module =
the shortest path to requirements #1/#4. Cost is toolchain friction (Zephyr or Adafruit's
Arduino-nRF core vs. ESP32's turnkey Arduino) — acceptable, and the [`kstam`](#sources) framing
ports to ArduinoBLE / NimBLE-style APIs on the nRF core. ESP32-C3 stays the fallback **only** if the
nRF toolchain stalls the build; call that out as a regression on battery life.

#### ADC — **NAU7802** ✅ over HX711

| Trait          | **NAU7802** ✅                                   | HX711                                               |
| -------------- | ------------------------------------------------ | --------------------------------------------------- |
| Interface      | **I²C** (shares the MCU bus; DRDY IRQ)           | Bit-banged 2-wire (timing-sensitive, blocking)      |
| Resolution/PGA | 24-bit, **PGA ×1–128**, internal LDO + ref       | 24-bit, fixed ×128/×64/×32, needs clean ext. supply |
| Rate           | **10–320 SPS** selectable (10 Hz notify is easy) | 10 or 80 SPS only                                   |
| Power          | Low-power modes + PGA/ADC sleep → **µA idle**    | Higher; awkward to sleep                            |
| Fit here       | Espresso-grade quiet reads, I²C, sleeps cleanly  | Cheap/common but noisier, no true I²C, worse sleep  |

The **NAU7802's I²C + internal reference + programmable rate + clean sleep** all serve the "fast,
low-noise, low-power" trio; HX711 is the budget default this design deliberately steps past.

#### Load cell — thin single-point, overload-rated

Thinness is a **hard constraint** (must clear under a portafilter on the drip tray), so the cell +
platform stack is the gating dimension.

| Candidate                                 | Range      | Note                                                                                        |
| ----------------------------------------- | ---------- | ------------------------------------------------------------------------------------------- |
| Mini single-point bar (e.g. TAL221-class) | 100 g–1 kg | Full bridge, compact bar; **~500 g–1 kg** gives espresso headroom (cup + shot) with margin. |
| Low-profile planar / flexure cell         | 500 g–1 kg | Thinnest option; pick one **rated for overload** (portafilter knocks, tamping bumps).       |

- **Range:** size for **~500 g–1 kg** — a double + cup lives near 300–400 g; leave overload margin.
- **Overload:** espresso is an abusive environment (portafilter drops, taps). Choose a cell with a
  **mechanical overstop / high overload rating**, and design the platform to bottom out before the
  gauge yields.
- **Mounting:** classic single-point cantilever — fixed end to the base, free end to the platform,
  with the platform's travel physically limited. Keep the whole sandwich low.
- **Height budget (to hit ≤ ~18–20 mm):** platform (~1–2 mm) + deflection/travel gap (~2–3) + load
  cell body (~4–6) + PCB (~1.6) + LiPo pouch (~4–5) + enclosure floor/lid (~2–3) ≈ **15–20 mm** —
  tight but feasible; the **load-cell body and the LiPo are the two gating dimensions**, so pick the
  thinnest adequately-rated versions of each.

#### Power + USB-C

| Block          | Choice                                                                                                                                                                                                                                                                                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Cell           | **Thin LiPo pouch** (e.g. ~400–600 mAh, single cell) sized to the enclosure floor.                                                                                                                                                                                                                                                                     |
| Charge         | **XIAO's onboard BQ25101 over USB-C** (50/100 mA select via its charge pin). No separate MCP73831/TP4056 needed.                                                                                                                                                                                                                                       |
| Fuel gauge     | Prefer a **MAX17048** (I²C, shares bus) for true SoC; fallback = MCU ADC on a battery divider. Publish via `0x180F`.                                                                                                                                                                                                                                   |
| Sleep strategy | Deep-sleep between shots; **wake on button / tap**, radio idles in µA. (The NAU7802 has only a per-sample **DRDY** IRQ — **no threshold/window comparator** — so true wake-on-load needs either a low-power comparator on a bridge tap **or** an accepted duty-cycled ADC poll; budget that current. Button/periodic-poll wake is the simple default.) |

**Battery math (order-of-magnitude, to substantiate #4):** with the radio in connectable-standby
(~5–20 µA) and the AFE gated off between shots, a **~500 mAh** pouch runs **months on standby**
(self-discharge, not the load, dominates there). A ~30 s shot at ~5–8 mA (ADC + active BLE stream) ≈
**~0.05 mAh/shot**, so streaming costs ~**thousands of shots per charge** — i.e. active brewing is
_not_ the limiter; standby leakage + charge convenience are. Keep the BLE connection interval
relaxed except while streaming. (These are estimates; the exit criterion measures the real numbers.)

### Usability details (requirement #2)

| Concern          | Approach                                                                                                                                                                                                                                                                                                                                            |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Notify rate      | ~**10 Hz** to match leva!; oversample the ADC (80–320 SPS) and decimate.                                                                                                                                                                                                                                                                            |
| Filtering        | Median-of-N despike + light IIR/EMA; keep group delay low so **live flow-rate** (mass slope) stays responsive.                                                                                                                                                                                                                                      |
| Tare / auto-tare | Physical button = tare; **auto-tare** on stable-zero-after-cup-placement; honor the **EF80 `0x10`** tare from leva!.                                                                                                                                                                                                                                |
| Settle time      | Fast settle target so the shot-start tare doesn't lag; report jitter, not just resolution.                                                                                                                                                                                                                                                          |
| Water / steam    | **Conformal-coat the PCB**, gasket the enclosure (IP-ish), recess the USB-C, drain channels — it lives on a drip tray.                                                                                                                                                                                                                              |
| Feedback         | Minimal by design: **status LED** (+ optional haptic). A tiny OLED is optional but costs thinness + power — skip v1.                                                                                                                                                                                                                                |
| Calibration      | Two-point (tare + known mass, e.g. **100 g / 500 g** cal weights); store slope+offset in nRF flash; re-cal command.                                                                                                                                                                                                                                 |
| Drift / creep    | Cheap single-point cells have real **tempco + creep**, and the scale sits on a **warm drip tray** near steam. **Auto-tare at shot start** cancels short-term zero drift over a ~30 s pull; pick a **creep-/tempco-rated cell**. Span drift stays uncompensated — fine for per-shot mass (re-zeroed each shot), not for absolute long-term weighing. |

## Firmware architecture

```text
[ISR] NAU7802 DRDY ─▶ ring buffer ─▶ filter (median + EMA) ─▶ tare/offset ─▶ scale(cal) ─▶ grams
                                                                                   │
                                            (every ~100 ms) ─▶ pack Skale-2 EF81 bytes ─▶ BLE notify
BLE EF80 write ─▶ dispatch: 0x10 tare │ units │ display/LED  ───────────────────────────┘
Battery: MAX17048 (or ADC) ─▶ SoC% ─▶ GATT 0x180F (0x2A19)
Idle: no cup + no BLE activity ─▶ gate AFE, deep-sleep radio ─▶ wake on button / periodic poll
```

- **Advertise** with the Skale 2 device name + the `EF80` service — assuming leva! matches/binds by
  name + service, the make-or-break to confirm first (see Validation).
- **GATT server** exposes `EF81` (notify), `EF80` (write), optional `EF82` (notify), and standard
  `0x180F`.
- **Weight packer** reproduces the exact Skale II framing (the 8-byte, drop-2-read-4, 0.1 g layout)
  — bit-for-bit, validated (below).
- **Tare handler** on `EF80 0x10` zeroes the software offset, so leva!'s own tare button works.
- **Power manager** owns the sleep/wake and the fuel gauge.

### Validation — the make-or-break unknown comes first

Two things must be true, and they are **not** equally settled. Resolve #1 **before spending on the
load cell or PCB** — it can invalidate the whole approach:

1. **Does leva! bind a scale by advertised _name + service_, or by a _bonded MAC_ / BLE pairing?**
   This is the load-bearing assumption, and the Vibrato Path C roadmap flags it as **UNVERIFIED**.
   If leva! rediscovers and connects to _anything_ advertising the Skale name + `EF80` service, a
   name-only emulator works with zero leva!-side setup. If instead it stores a specific **bonded
   MAC** (or requires BLE bonding/pairing) after first pair, a name-only impersonation won't be
   picked up and the design needs a rethink (clone the MAC, or pair once from leva!). **Verify
   before building anything:**
   - Sniff a real Skale 2 ↔ leva! session (nRF Sniffer) — or find it in the spec — and confirm
     leva! discovers/binds by **name + service** and does **not** require bonding to a stored MAC.
   - Then stand up a **name-only advertisement + stub GATT server on a bare dev board** (no sense
     chain yet) and confirm **leva! connects and subscribes**. That one cheap test de-risks the
     whole project.
2. **Are the EF81 weight bytes indistinguishable from a real Skale 2?** Once binding is confirmed,
   match the framing — two paths in order of confidence:
   - **Best — capture a real Skale 2 ↔ leva! session** with an **nRF Sniffer** (nRF52840 dongle +
     Wireshark) if one can be borrowed: record the advertisement, the subscribe, the EF81 notify
     framing across positive/negative/zero weight, and the EF80 tare write; replay-match the
     emulator.
   - **Else — the published spec**: implement to the Decent `scale_api` + SkaleKit SDK + the
     [`kstam`](#sources) parser (read it as the inverse of what to emit), then **A/B against
     leva!**: does it connect, show live weight, tare on command, and **stop a real shot at target
     mass**?

**Bench rig before the machine:** drive known masses onto the cell, confirm leva! (dose
`Method: WEIGHT`, `Stop early`) reads them and fires the stop at the setpoint. Only then wire it
into the shot workflow on the [A53](06-001-lucca-a53-mini-leva-firmware-integration.md).

## Positioning / cross-links

- **Parent:**
  [06-001 — Lucca A53 Mini profiling via ito + `leva!`](06-001-lucca-a53-mini-leva-firmware-integration.md).
  This scale exists to feed **its** native weight-stop.
- **[06-007 — Smart Scale Integration via Bluetooth](06-007-smart-scale-integration-via-bluetooth.md):**
  the sibling that _integrates a **commercial** scale_. **06-018 instead _builds_ a scale that
  impersonates a supported one** for native gravimetric — the complement, not the duplicate, of
  06-007.
- **[06-015 — GICAR Flow-Tap Interposer](06-015-gicar-flow-tap-interposer.md):** a **complementary
  flow source** (volumetric, from the stock meter). This scale gives **gravimetric** flow (mass
  slope); together they cross-check flow two independent ways.
- **Vibrato shot-feedback-loop roadmap, Phase 2 (Path C):** referenced **by name**; it lives in the
  **`vibrato` repo**. This lab doc treats Vibrato as a **black box** — same "emit as Skale 2" idea,
  but Path C re-emits a _separate source scale_, whereas 06-018 has **no source scale** (the DIY
  load cell is the origin). No Vibrato internals are referenced here.

## Build order

0. **De-risk the make-or-break first (no hardware spend):** confirm leva! binds a scale by **name +
   service, not a bonded MAC** — sniff a real Skale 2 ↔ leva! session or the spec, then a name-only
   advertisement + stub GATT server on a bare dev board that leva! actually connects to (see the
   Validation section above). If it binds by MAC / requires bonding, **stop and rethink before
   building anything.**
1. **Breadboard the sense chain:** load cell → NAU7802 → XIAO nRF52840; read stable grams over
   serial; two-point calibrate.
2. **Stand up the Skale 2 GATT server:** advertise as Skale, stream EF81, handle EF80 tare; connect
   from a phone app that speaks Skale 2 to sanity-check framing.
3. **Prove the cut with leva!:** `Method: WEIGHT` + `Stop early`; validate framing (sniffer or
   spec); confirm live weight + tare + a bench stop at setpoint.
4. **Power + sleep:** wire LiPo + USB-C charging + fuel gauge; implement button/poll wake (+
   optional low-power load comparator); measure standby + active current against the battery target.
5. **Mechanical:** low-profile platform + enclosure; conformal-coat; gasket; recess USB-C; verify
   the stack clears under the portafilter on the drip tray.
6. **Field it** on the A53 shot workflow; tune filter/notify cadence for responsive live flow
   without overshooting the mass cut.

## Exit Criteria

- [ ] Sense chain bench-verified: load cell → NAU7802 → nRF52840 reads stable grams; two-point
      calibration (tare + known masses) stored in flash; noise/settle characterized.
- [ ] Firmware advertises as a **Skale 2** and runs a GATT server exposing `EF81` (weight notify),
      `EF80` (command/tare), and `0x180F` battery.
- [ ] **Byte framing validated** as indistinguishable from a real Skale 2 — via nRF Sniffer capture
      of a genuine Skale 2 ↔ leva! session **or** the published spec + a passing leva! A/B.
- [ ] **leva! reads it natively** (`Method: WEIGHT`, `Stop early`): live weight shown, `EF80 0x10`
      tare honored, and a **bench shot stops at target mass**.
- [ ] Usability met: **~10 Hz notifications with notify jitter < ~20 ms and rest noise ≤ ±0.1 g**,
      responsive live flow-rate, physical tare + auto-tare, water/steam-tolerant enclosure
      (conformal-coat + gasket).
- [ ] **Thin:** assembled stack clears under the portafilter on the drip tray (target ≤ ~18–20 mm).
- [ ] **Power:** USB-C LiPo charging works; deep-sleep/wake-on-load verified; measured standby +
      active current project to the multi-day-active / multi-month-standby target on the chosen
      pouch.
- [ ] Integrated on the A53: a real shot cuts at target mass via leva!'s native gravimetric stop.

## Progress

- [ ] Architecture + part selection drafted (this doc): **nRF52840 (XIAO) + NAU7802 + Skale 2
      emulation**, thin single-point cell, onboard USB-C LiPo charging.
- [ ] Skale 2 BLE contract captured (EF80/EF81/EF82 + 0x180F, tare `0x10`, 8-byte weight framing) —
      to be **validated against hardware/SDK** before trusting the cut.
- [ ] Breadboard sense chain + calibration.
- [ ] Skale 2 GATT server + leva! A/B.
- [ ] Power/sleep + mechanical + field integration.

## Sources

- **Skale 2 protocol (emulation target):** Decent Espresso **`scale_api`** (Skale II section: weight
  characteristic `0000EF81-…`, command `0000EF80-…`, tare `CMD 0x10`, button `0000EF82-…`, battery
  on standard `0x180F`; 8-byte weight packet, drop-2-read-4) —
  <https://decentespresso.com/scale_api>; and the Atomax **Skale open SDK / SkaleKit** —
  <https://www.skale.cc/en/skale_open_sdk.html>.
- **Reference BLE-scale library** (canonical framing to mirror; the layer GaggiMate builds on):
  [`kstam/esp-arduino-ble-scales`](https://github.com/kstam/esp-arduino-ble-scales). Emit the
  inverse of its Skale parser (server, not client).
- **MCU / power:** Seeed **XIAO nRF52840** — nRF52840 BLE 5.4, onboard **BQ25101** USB-C LiPo
  charger, standby < 5 µA: <https://wiki.seeedstudio.com/XIAO_BLE/>.
- **ADC:** NAU7802 24-bit I²C load-cell front end (SparkFun Qwiic Scale library / Adafruit NAU7802
  guide) — chosen over HX711 for I²C + programmable rate + clean low-power sleep.
- **DIY-scale prior art (surveyed):** `beeb/coffee-scale-app` (firmware + PWA), the Adafruit **CLUE
  Coffee Scale** (nRF52840 + NAU7802), **EspressiScale** (ESP32 + ADS1232), Hackaday **ESPresso
  Scale** — confirm the nRF52840 + NAU7802 combination is well-trodden; none emulate Skale 2 for
  leva!, which is this project's novel part.
- **leva! gravimetric:** [06-001](06-001-lucca-a53-mini-leva-firmware-integration.md) (native
  weight-stop reads Skale 2 / Felicita Arc / Eureka; DiFluid on 3.2+). Umbrella: the **Vibrato
  shot-feedback-loop roadmap, Phase 2 / Path C** — in the **`vibrato` repo** (black box here).
