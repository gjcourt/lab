---
title: 'DIY Digital-Domain Streamer (Snapcast to External DAC/DSP)'
number: '01-016'
category: 'audio-midi'
difficulty: 'Medium'
time_commitment: '1-4 weeks'
target_skills:
  'Snapcast, ALSA, DietPi/Raspberry Pi OS, digital audio interfaces (S/PDIF, USB, AES, I2S)'
status: 'In Progress'
depends_on:
  - homelab/snapcast
  - hardware/raspberry-pi
---

# DIY Digital-Domain Streamer (Snapcast to External DAC/DSP)

## Description

Decision record + meta-analysis for revamping the multi-room audio endpoints: retire the per-room
HiFiBerry **DAC+ DSP** HATs in favour of a pure digital transport off each Raspberry Pi feeding an
**external DAC that has its own DSP** (reference target: Topping **D90 III Discrete**). Keep
Snapcast as the multi-room sync engine. The core question — "which HiFiBerry digital-output HAT do I
need?" — turns out to be the wrong question once the DSP moves into the DAC.

**Bottom line:** for a Snapcast endpoint feeding a modern external DAC, the best answer is usually
**no HAT at all** — `snapclient` on a minimal Linux OS, USB straight into the DAC. See
[Recommendation](#recommendation).

## Current architecture (prior art)

This is not greenfield — it revamps the working multi-room system already documented in `homelab`:

- **Snapserver** runs in-cluster (`apps/base/snapcast/`, ns `snapcast-prod`), exposed on a LAN
  `LoadBalancer` IP via Cilium L2, Snapweb at `snapcast.burntbytes.com`. Stream sources: Spotify
  (`go-librespot`), Mopidy/Navidrome.
- **Endpoints today:** two HiFiBerryOS devices — kitchen `10.42.2.38`, living-room `10.42.2.39` —
  each running `snapclient` as a HiFiBerryOS **Docker extension** that outputs to a local HiFiBerry
  **DAC+ DSP** HAT.
- Getting Snapcast working on HiFiBerryOS required a **patched extension image**
  (`homelab/images/snapcast-hifiberry/`): upstream `ghcr.io/hifiberry/extension_snapcast:0.28.0`
  ships without the runtime codec libs and hardcodes the wrong `snapclient` path. That patched image
  is ongoing maintenance we own.

Prior-art references:

- `homelab/docs/plans/2026-05-03-snapcast-hifiberry-rollout.md` — the client rollout plan
- `homelab/images/snapcast-hifiberry/README.md` — why the upstream image had to be patched
- `homelab/docs/operations/hifiberry-os-spotify-setup.md`, `hifiberry-os-watchdog.md` — endpoint ops
- [`01-004-multi-room-audio-sync-protocol.md`](01-004-multi-room-audio-sync-protocol.md) — the
  from-scratch sync-protocol sibling (Snapcast is the off-the-shelf answer to that)

## The reframe: the DAC already solved the hard parts

Two things a modern DAC like the D90 III Discrete does that make the audiophile "digital transport"
HAT category largely moot in this system:

1. **Jitter.** The Discrete pairs Topping's fully discrete 1-bit (PSRM) converter with a **CPLD
   jitter-reduction** stage that re-clocks incoming S/PDIF, AES and USB. The dual-clock / galvanic
   isolation / exotic-PSU features these HATs compete on all target source jitter — a problem the
   DAC already handles internally. Between competent transports into this DAC, audible differences
   should be negligible.
2. **DSP.** The Discrete carries a **10-band parametric EQ** (Topping Tune app: 5 filter types,
   room-correction import/export, 5 profiles stored on-board, set once over USB). That is exactly
   the function being retired from the HiFiBerry DAC+ DSP — **the DSP moves into the DAC.** One
   catch that quietly settles the interface question: the on-board EQ applies to every input
   **except I2S**.

So the decision collapses from "which transport sounds best" to four practical axes: **where the DSP
lives**, **interface**, **format ceiling**, and **endpoint OS**.

## Where the DSP lives (three placements)

Retiring the HiFiBerry DAC+ DSP does not force the DSP into the external DAC. There are three places
it can live, and a multi-room system can mix them per room:

1. **In the DAC** — e.g. the D90 III Discrete's 10-band PEQ. Self-contained, but PEQ /
   room-correction only (no active crossover), needs a DSP-capable (~$1k) DAC per room, configured
   out-of-band via the Topping Tune app, and bypassed on the I2S input.
2. **In a dedicated USB DSP appliance — DSPi** (`~/src/DSPi`, [ASR thread][dspi]). Firmware for a
   Raspberry Pi **Pico** (RP2040/RP2350, ~$5) — _not_ a Linux Pi. It appears as a USB sound card
   with an on-board DSP engine and outputs **S/PDIF** (up to 4 stereo pairs / 8 ch on RP2350) plus a
   PDM subwoofer channel, bringing PEQ, room correction, time alignment, loudness, crossfeed and
   **active crossovers** to _any_ plain DAC. Caps at **24-bit / 48 kHz** and does **not** stream —
   it is a USB DSP stage fed by the streaming Pi. Configured via the DSPi Console app
   (`~/src/DSPi-Console`).
3. **In software on the streaming Pi** — CamillaDSP after `snapclient`. Most flexible (convolution,
   arbitrary crossovers, per-room correction), but uses Pi CPU and is the most hand-assembled
   option.

DSPi answers two things directly: it **cannot** do the streaming part (no networking — the Pi hosts
it over USB), and it **is** the ideal way to give DSP to DACs that lack it — uniquely enabling
**active multi-way / subwoofer** rooms the D90 III's simple PEQ can't. Its chain:
`Pi (snapclient) → USB → DSPi (DSP) → S/PDIF → any DAC(s)`.

[dspi]:
  https://www.audiosciencereview.com/forum/index.php?threads/introducing-dspi-a-powerful-user-friendly-and-open-source-dsp-for-less-than-a-cup-of-coffee.69343/

## The DAC's inputs set the ceiling (Topping D90 III Discrete)

| Input     | Connector   | PCM ceiling | DSD         | Notes                                       |
| --------- | ----------- | ----------- | ----------- | ------------------------------------------- |
| USB       | USB-B       | 32 / 768k   | DSD512      | Highest ceiling; async; **no HAT required** |
| I2S       | HDMI (LVDS) | 32 / 768k   | DSD512      | Full bandwidth — but **bypasses the PEQ**   |
| AES / EBU | XLR         | 24 / 192k   | DSD64 (DoP) | Balanced 110 Ω cousin of coax               |
| Coaxial   | RCA S/PDIF  | 24 / 192k   | DSD64 (DoP) | The workhorse                               |
| Optical   | Toslink     | 24 / 192k   | DSD64 (DoP) | Full galvanic isolation; bandwidth-limited  |

Architecture: discrete 1-bit PSRM (16 phases), not ESS Sabre. Preamp mode (variable output) can
drive a power amp directly. ~$999.

## Interface layer — pick the wire first

If 24/192 covers the library (it covers all Snapcast-streamed sources here), **coax or USB** are the
sane picks. Reach past S/PDIF only for DSD or >192 kHz PCM — which only USB or I2S can carry.

| Interface     | Ceiling          | For                                           | Against                                       |
| ------------- | ---------------- | --------------------------------------------- | --------------------------------------------- |
| Coaxial       | 24 / 192k        | Robust, universal, cheap; every Digi HAT      | Caps at 192k                                  |
| AES/EBU       | 24 / 192k        | Balanced XLR, long runs                       | No audible edge over coax here; few HATs      |
| Optical       | 24 / 192k        | Total galvanic isolation (kills ground loops) | Highest jitter (moot here); bandwidth ceiling |
| I2S over HDMI | 32 / 768k        | Full bandwidth, no S/PDIF round-trip          | **Pinout roulette** + **bypasses the PEQ**    |
| USB           | 32 / 768k DSD512 | Highest ceiling, **zero boards**, keeps PEQ   | Needs a USB-capable OS (trivial on Linux)     |

## Hardware universe — the HATs, and the no-HAT path

Nearly all of these are the same WM8804 S/PDIF transmitter with different clocking and connectors.
Given the DAC's reclocking, those differentiators matter far less than connectors / ceiling / driver
support / price. Verdicts are weighted for _this_ system.

| Board                        | Outputs                      | Ceiling | ≈ Price   | Status     | Verdict for this system                              |
| ---------------------------- | ---------------------------- | ------- | --------- | ---------- | ---------------------------------------------------- |
| HiFiBerry Digi2 Pro          | Coax + optical (+BNC solder) | 24/192  | ~$45      | Current    | Dual clocks + isolation. Native ecosystem. Fine pick |
| Pi2AES 2.0                   | Coax + optical + AES + I2S   | 24/192  | ~$175     | Current    | Only board with AES + I2S. Buy for I/O, not sound    |
| Allo DigiOne / Signature     | Coax                         | 24/192  | ~$120–260 | Legacy/EOL | Reference jitter for a problem you don't have        |
| Audiophonics Digi Pro        | Coax + optical               | 24/192  | ~$40      | Niche      | WM8804 clone of the Digi2 Pro                        |
| Raspberry Pi / IQaudio Digi+ | Coax + optical               | 24/192  | ~$30      | Budget     | Cheapest mainline S/PDIF HAT; adequate               |
| **USB direct (no HAT)**      | USB-B → DAC                  | 32/768  | $0        | Path       | Highest ceiling, fewest parts, keeps the PEQ         |

## Endpoint OS — Snapcast changes the question

The endpoints are Snapcast **clients**; the streaming sources live on the in-cluster Snapserver. So
each Pi's only jobs are **run `snapclient`** and **expose the DAC to ALSA**. A full streamer OS
(HiFiBerryOS / moOde / Volumio) bundles source apps (Spotify/AirPlay/Roon) that a _client_ doesn't
use. `snapclient` is a tiny service that writes to any ALSA device — HAT or USB — so "which streamer
OS" is the wrong frame for an endpoint.

| Endpoint OS             | Snapcast                                | USB DAC                   | Verdict                                 |
| ----------------------- | --------------------------------------- | ------------------------- | --------------------------------------- |
| **DietPi / Pi OS Lite** | one-command install (`dietpi-software`) | native ALSA               | **Least lifetime work, most durable**   |
| HiFiBerryOS             | patched extension image (we own it)     | unofficial hack + **EOL** | Least _change_; on frozen + hacked base |
| Volumio                 | community plugin                        | native                    | Middling; semi-maintained plugin        |
| moOde                   | none native (hand-rolled unit)          | native                    | Most work; you own the integration      |

Notes:

- HiFiBerryOS was **announced EOL in Feb 2025** (Pi-OS-based successor `hbosng` still WIP). USB-DAC
  output on it is an unofficial hack (edit `/opt/hifiberry/bin/reconfigure-players`).
- Going DietPi **also retires the patched `snapcast-hifiberry` image** — on DietPi, `snapclient` is
  the stock package writing straight to the USB card; no custom image to maintain.
- Any Linux OS _can_ run `snapclient`; on a streamer OS that's bolted-on maintenance across updates,
  on a minimal OS it's the whole point.

## Recommendation

**Per-room endpoint = Raspberry Pi (no HAT) + DietPi + `snapclient` → USB → external DAC-with-DSP.**

- **No HAT.** The DAC's reclocking makes the HAT jitter story moot, and USB carries the highest
  format ceiling with zero added boards.
- **DSP in the DAC.** The D90 III Discrete's 10-band PEQ replaces the HiFiBerry DSP; set once via
  the Topping Tune app, stored on-board. Avoid I2S (the one input that bypasses the PEQ).
- **DietPi.** `snapclient` is a first-class install, USB DAC is native ALSA, no vendor-OS EOL risk,
  and it removes the patched HiFiBerry snapclient image from the maintenance surface.

Fallback / least-change path: keep HiFiBerryOS + the USB hack on the existing devices — works today,
but builds on an EOL OS + two hacks (USB reconfigure, patched extension image).

**The Pi is always the same; the DSP + DAC vary per room.** DietPi + `snapclient` is the constant.
Downstream, pick per room:

- **Reference room** — `Pi → USB → D90 III Discrete`. DSP (PEQ) in the DAC, hi-res, ~$1k. For the
  one room that warrants it.
- **Standard room, plain DAC** — `Pi → USB → DSPi (Pico, ~$5) → S/PDIF → any DAC`. Adds room
  correction / PEQ for pocket change; 24/48 ceiling.
- **Active / multi-way room** —
  `Pi → USB → DSPi → multiple S/PDIF (+ PDM sub) → per-driver DACs/amps`. DSPi does the active
  crossover the D90 III's PEQ can't.
- **Budget / unchanged room** — keep the existing HiFiBerry DAC+ DSP HAT; nothing to do.

Snapcast mixes these freely — every client is independent, so the house can be heterogeneous.

## Test plan (validate on a spare Pi, zero risk to the 2 live rooms)

1. Flash **DietPi** on a spare Pi.
2. `dietpi-software` → install **Snapcast Client**.
3. Connect a USB DAC (the D90 III if available, else any USB DAC to prove the path).
4. Point it at the Snapserver LAN IP and select the USB card:
   `snapclient --host <snapserver-ip> -s <usb-alsa-card>`.
5. Confirm it joins the group in Snapweb, plays **in sync** with kitchen/living-room, and audio
   exits the USB DAC.
6. If green: this is the migration recipe for the other rooms.

## Exit Criteria

- [ ] Spare-Pi test passes: DietPi + `snapclient` + USB DAC joins the existing Snapcast group and
      plays in sync with the two HiFiBerry rooms.
- [ ] D90 III Discrete on-board PEQ configured (Topping Tune) and confirmed applied on the USB
      input.
- [ ] Decision recorded: which rooms move to external-DAC-via-USB vs. stay HAT-based.
- [ ] Migration runbook written into `homelab` (supersedes the patched `snapcast-hifiberry` image
      for migrated rooms).

## Progress

- [x] Meta-analysis of the digital-output HAT universe + interface/OS layers
- [x] DAC identified (D90 III Discrete: discrete 1-bit PSRM, CPLD jitter reduction, 10-band PEQ)
- [ ] Spare-Pi DietPi + snapclient + USB validation
- [ ] Per-room rollout decision + homelab runbook

## References

- HiFiBerry Digi2 Pro — <https://www.hifiberry.com/shop/boards/digi2-pro/>
- HiFiBerryOS EOL notice — <https://www.hifiberry.com/blog/hifiberryos-quo-vadis/>
- Topping D90 III Discrete — <https://www.headfonia.com/topping-d90-iii-discrete-review/>
- Pi2AES 2.0 — <https://www.pi2design.com/pi2aes.html>
- Volumio Snapcast plugin — <https://github.com/Saiyato/volumio-snapcast-plugin>
- Snapcast — <https://github.com/snapcast/snapcast>
- DSPi (RP2040/RP2350 USB DSP firmware) — `~/src/DSPi` + [ASR thread][dspi]; console
  `~/src/DSPi-Console`
- CamillaDSP (software DSP alternative) — <https://github.com/HEnquist/camilladsp>
