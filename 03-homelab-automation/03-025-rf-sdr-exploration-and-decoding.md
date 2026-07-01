---
title: 'RF/SDR Exploration & Decoding (RTL-SDR on-ramp)'
number: '03-025'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-4 weeks'
target_skills:
  'SDR fundamentals, GNU Radio, Universal Radio Hacker, rtl_433, DSP basics, HA/MQTT integration'
status: 'Not Started'
depends_on:
  - hardware/rtl-sdr
  - homelab/home-assistant
---

# RF/SDR Exploration & Decoding (RTL-SDR on-ramp)

## Description

The "Model B" on-ramp to RF: a cheap **RTL-SDR + open PC software** as a transferable foundation,
rather than a locked-in appliance. Key framing — **decouple the radio from the software**: the
software ecosystem (GNU Radio, SDR++, Universal Radio Hacker, rtl_433) is **hardware-agnostic via
SoapySDR**, so the skills carry forward to any future SDR (HackRF/bladeRF) without re-learning. You
do NOT need a specific device for these tools to be useful — unlike Flipper/PortaPack apps, which
are firmware locked to that gadget.

Goal: learn RF hands-on through a progression of receive-and-decode projects, and land real value by
pulling 433 MHz sensors into Home Assistant.

## Why RTL-SDR first

- ~$35, receive-only, 500 kHz–1.7 GHz, ~2.4 MHz BW — perfect to _learn_ on.
- Universal software; skills transfer to every fancier SDR.
- Most of what makes RF fun is **RX** (see TX note below). Buy RX now; add TX only with a goal.
- ⚠️ The Blog **V4 is EOL** (R828D tuner discontinued; a final batch hits Amazon ~July 2026, then
  gone for good). For a fresh buy get the in-production **Blog V3** or the **Nooelec v5**; chase the
  last V4 only if you want its built-in HF upconverter (see shopping list). Buy genuine —
  counterfeits are rampant.

## How RF capture works (the detailed process)

**Software radio vs purpose-built receiver.** Unlike an IR TSOP (which demodulates in hardware and
hands you a clean on/off envelope — see [[03-019]]), the RTL-SDR does the hard part in _software_.
It grabs a raw ~2.4 MHz slice of spectrum as **I/Q samples** (amplitude+phase pairs, ~2.4M/sec) and
streams them over USB; **all demodulation/decoding happens on the PC.** Flexible (receives anything
in range) but PC-dependent.

⚠️ **Capture ≠ re-transmit.** The RTL-SDR is **receive-only** — it's only _half_ the loop. To replay
an RF code you add a transmitter (below). (And note: the audio remotes are **IR**, so RF capture is
for 433 MHz sensors / the odd RF remote / learning — not the remotes.)

**Signal chain:** antenna → tuner downconverts a slice to baseband → 8-bit ADC → USB → PC software
(waterfall / demod / decode).

**Capture workflow:**

1. **See it** — open a waterfall (SDR++/CubicSDR/gqrx), tune **433.92 MHz** (common ISM), trigger
   the device → a burst lights up, confirming frequency + that it's transmitting.
2. **Decode — two paths:**
   - **`rtl_433` (easy win, sensors):** knows hundreds of 433/315/868/915 MHz device protocols.
     `rtl_433 -f 433.92M` prints decoded JSON (`{"model":"Acurite","temperature_C":21.3,...}`) — no
     RE needed if the device is in its DB (most cheap sensors are).
   - **Universal Radio Hacker (unknown signals):** record I/Q, URH auto-detects modulation (usually
     **OOK/ASK**, sometimes FSK), shows the bit pattern → extract preamble/address/command/checksum.
3. **Result:** decoded sensor readings, or a reverse-engineered protocol.

**Capture → Home Assistant (the real payoff, RX-only):** for 433 MHz sensors you _ingest_, not
replay. `rtl_433 -f 433.92M -F mqtt://broker:1883,...` publishes every decoded device to MQTT → HA
auto-discovers them as sensors. One RTL-SDR = a whole-house 433 receiver (temp/humidity/door/leak)
into HA, no per-device hub.

**Re-transmit RF (the other half — needs a TX device):** RTL-SDR can't transmit, so to replay:

- **CC1101 + ESP32 (~$5)** — sub-GHz OOK/FSK TX, runs **ESPHome** → integrates into HA exactly like
  the IR blaster ([[03-019]]). This is the RF "capture-and-replay into HA" path: capture with
  RTL-SDR/URH, replay via CC1101.
- **Flipper / Broadlink RM4 Pro** — handheld / plug-and-play TX.
- Division of labor: **RTL-SDR = listen & understand; CC1101/Broadlink = transmit.**

**Gotchas:** find the frequency first (FCC ID on fccid.io, or scan 433.92/315/915); antenna length
matters (433 vs 915); 8-bit/2.4 MHz is fine for narrow OOK but **can't** do wideband FHSS (the
[[03-024]] baby monitor); most cheap gear is OOK/ASK (easy), some FSK.

## Progression (each a self-contained win)

1. **ADS-B** — decode aircraft (dump1090) and plot live planes. Classic first success, ~1 afternoon.
2. **Broadcast/NOAA** — FM, then decode NOAA weather-satellite APT images (antenna matters).
3. **rtl_433 → HA** — receive your 433 MHz sensors (weather stations, TPMS, door sensors) and pipe
   them into Home Assistant via **rtl_433 → MQTT → HA auto-discovery**. _This is the homelab
   payoff._
4. **Pagers/ships** — POCSAG (paging) and AIS (ship transponders) for variety.
5. **Protocol RE** — capture an unknown signal and reverse it in **Universal Radio Hacker** (auto
   modulation detect). Note: URH went read-only/archived Mar 2026 — still the best tool,
   unmaintained.
6. **GNU Radio** — build a simple flowgraph; this is the skill that scales to wideband SDRs later.

## When TX earns its keep (the upgrade decision)

RX = observe/learn/decode. **TX = control/emulate/act.** Only add a transmitter for a specific
act-on-the-air goal. Genuinely useful TX cases:

- **Control no-smart-integration devices** — transmit 433 MHz/IR to garage/blinds/fans/RF outlets →
  into HA. _(The main everyday win — overlaps with [[03-019]] IR blaster.)_
- **Security-test your _own_ fobs/locks** — replay to learn fixed-code vs rolling-code.
- **Ham radio** _(license required)_ — digital modes, APRS, satellites, repeaters.
- **Prototype your own RF devices** (LoRa/sensor nets) · **RF signal-generator** test bench.

**Buy implication:** for practical "control my stuff" TX you do **not** need a HackRF — a **$5
CC1101/ESP32** or **$40 Broadlink** does sub-GHz TX better and integrates with HA. Wideband SDR TX
(HackRF/bladeRF) is for research/ham/odd frequencies only.

⚖️ **Responsible use:** TX is regulated. Stay on **your own devices, ISM bands (433/915 MHz, 2.4
GHz), low power**, or get a ham license for amateur bands. Never transmit on
cellular/aviation/public-safety/licensed bands, never jam, never replay others' devices.

## Exit Criteria

- [ ] Genuine RTL-SDR (Blog V3 / Nooelec v5 / last-batch V4) + a decent antenna set in hand
- [ ] At least 3 RX wins decoded (e.g. ADS-B, NOAA APT, rtl_433 sensors)
- [ ] 433 MHz sensors flowing into Home Assistant via rtl_433 → MQTT
- [ ] One protocol reverse-engineered in URH (or one GNU Radio flowgraph built)
- [ ] A written decision on whether/what TX hardware to add (and for which concrete goal)

## Shopping list (~$35–60)

**Just the dongle — nothing from Mouser.** This is a buy-a-receiver + open-software project: the
antenna ships with the kit and there are no discrete components to source. (Contrast the IR blaster
[[03-019]], which _is_ a Mouser BoM.)

- **RTL-SDR dongle + antenna kit (~$35–40)** — pick one:
  - **Nooelec v5** — in stock now; better heat management + TCXO stability for a 24/7 `rtl_433`→HA
    receiver. HF via direct sampling. **Best default for this plan** (its RX wins are all VHF/UHF).
  - **RTL-SDR Blog V3** — the canonical reference dongle, in stable production; same VHF/UHF
    performance, HF via direct sampling.
  - **RTL-SDR Blog V4** — **EOL**: a final batch hits Amazon ~July 2026, then gone. Worth chasing
    only for its built-in **HF upconverter** (cleaner shortwave/ham) — nothing in this plan's RX
    progression (ADS-B, NOAA, 433 MHz) needs it. Don't mix up the (unreleased) _Blog_ V5 with the
    _Nooelec_ v5 above.
  - All kits include a dipole antenna set → no separate antenna purchase.
- (later, only with a concrete TX goal) CC1101/ESP32 (~$5–35) or Broadlink RM4 Pro (~$40), or a
  HackRF/bladeRF for research/ham. None are Mouser parts (CC1101 breakouts are Amazon/AliExpress).

**Batching tip:** SparkFun carries the RTL-SDR kit, and the IR blaster [[03-019]] already sources
its breadboard + jumpers from SparkFun — so you can add the dongle to that SparkFun order and keep
the Mouser order to the IR semiconductors. Or buy the dongle direct from rtl-sdr.com (free
shipping).

## Progress

- [x] Framing: Model-B (decoupled HW/SW) on-ramp; TX decision deferred to a concrete goal
      (2026-06-27)
- [ ] Acquire RTL-SDR + antennas
- [ ] Work the RX progression
- [ ] rtl_433 → HA integration
- [ ] TX decision
