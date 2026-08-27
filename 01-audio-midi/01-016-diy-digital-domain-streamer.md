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

**For a Snapcast endpoint the format ceiling barely matters.** Snapserver streams a single fixed PCM
format (commonly 48 kHz) to every client, so no client DAC ever sees >48 kHz _from Snapcast_ — the
high USB/I2S ceilings below only pay off for a hypothetical non-Snapcast/direct-hi-res path this
system doesn't have. Usefully, that also means **DSPi's 24/48 cap costs nothing here.** The table
below is for completeness; in practice the choice reduces to a robust, low-fuss wire — **coax or
USB**.

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

**The price of that heterogeneity: per-client latency calibration.** Different chains have different
output latency — `Pi → USB → D90 III` vs. `Pi → USB → DSPi (up to 85 ms delay + processing) → DAC`
vs. a HAT room — so rooms will drift out of sync unless each client's Snapcast **`latency` offset**
is tuned to a common target. "In sync" across mixed topologies is a calibration step, not automatic.

## Retiring the living-room HAT: what the USB optical capture has to replace

A **USB audio interface with optical input** (delivered 2026-08) lets the living-room TV feed the Pi
directly, which is the missing piece for finally retiring that room's HiFiBerry HAT:

```text
TV ──optical──▶ USB capture ──▶┐
                               ├──▶ DietPi (mix + volume) ──USB──▶ DAC
Snapcast / go-librespot ──────▶┘
```

Per [As-built](#as-built-deployed-2026-07), the HAT is currently doing **two** jobs for that room —
it is the TV's S/PDIF input _and_ the room's volume stage (SigmaDSP master, driven by
`snap-dsp-volume-bridge`). The capture device replaces the first. **The second still needs an
answer**, and it is the harder one.

Not because the D30 Pro lacks a volume control — it has one, adjustable, on by default (see
[`_reference/topping-dac-capabilities.md`](_reference/topping-dac-capabilities.md)). The open
question is whether the **host** can reach it.

**⚠️ Test this before designing around it.** The kitchen routes its one knob to the D50s' UAC2 mixer
over USB (`--mixer "hardware:D50s"`). Whether the D30 Pro advertises an equivalent control is
**untested** — it has never been connected over USB in this house, and the belief that it does not
came from the manual's silence rather than a measurement. The test is two commands, and it is only
valid with the unit in `m-p` Pre-Amp mode:

```bash
aplay -l && amixer -c <card> scontrols
```

**The result changes the design:**

- **If a UAC2 control appears** — the room needs no digital-domain volume at all. It becomes
  `--mixer "hardware:<D30Pro>"`, identical to the kitchen, and everything below about float
  pipelines is unnecessary.
- **If it does not** — IR is the only remote path, and IR volume is relative up/down with no state
  readback, so it cannot back an absolute slider. Only then does digital-domain volume become the
  sane default, and the section below applies.

### The alternative the D30 Pro's own optical input allows

The D30 Pro has a **Toslink input of its own**. The TV can feed it directly — no capture device, no
computer in the audio path, no resampling, no lip-sync exposure. The cost is that the DAC _switches_
inputs rather than _mixing_ them: TV and Snapcast become mutually exclusive, selected over IR,
instead of playing together. That is a real trade and worth deciding deliberately rather than
discovering after the mix is built.

### Doing digital volume without paying for it

The usual objection is bit loss: attenuating a 16-bit stream by −30 dB discards ~5 bits (6.02 dB per
bit), leaving ~11 effective — audible on quiet dialogue, which is most of what TV audio is.

**That cost is avoidable, and the avoidance is the whole design requirement.** It applies to 16-bit
_integer_ attenuation. If the mix and volume stage run in **32-bit float** (PipeWire does natively)
and the result is sent to the DAC as **24-bit** over USB, the attenuation happens with enormous
headroom and the only quantisation is the final one. Sources here are 44.1/16 and 48/16 while USB
into these DACs carries up to 32/768 — there is room to spend and no reason not to.

**Requirement, therefore: float mix → 24-bit USB out. Never attenuate in 16-bit integer.** A
`softvol` plugin operating at source bit depth is the wrong implementation of the right idea.

### Ordering constraint the one-knob UX imposes

The knob must sit **after** the mix. `snapclient --mixer software` attenuates only the Snapcast
stream — the as-built already records that it "doesn't touch the p2p go-librespot path", and TV
capture is a third source it likewise never sees. Whatever combines the three owns the volume.

### TV-path gotchas

- **Set the TV's optical output to PCM, not Dolby/bitstream.** A TV defaulting to Dolby Digital
  sends encoded AC-3 down Toslink and the capture yields undecodable data. First thing to check when
  the capture "works" but sounds like noise or silence. (The existing HAT path already required
  this, so it may already be set on that TV.)
- **Do not route TV audio through Snapserver.** Snapcast deliberately buffers for multi-room sync,
  and that buffer destroys lip sync. TV audio must take the local mix path straight out. The
  consequence — TV audio is living-room only — is a design decision, not a defect to fix later.
- **Sample-rate agreement.** TV optical is typically 48 kHz; go-librespot and Navidrome are 44.1
  kHz. The mixer must resample one of them. Decide where, rather than letting whichever component
  cares first make the choice.

### Does `toppingctl` change this?

Only for rooms whose DAC has a volume the host can reach. `toppingctl` reads and writes device-side
volume over USB HID — a connected DX5 II reports `volume 60 = -30.0 dB` live — which offers a third
option beyond "UAC2 mixer" and "software attenuation" for the **Office / D90 III** row still marked
TBD above. It helps only where the DAC both has a volume and exposes it to the host — see
[`_reference/topping-dac-capabilities.md`](_reference/topping-dac-capabilities.md) before assuming
either.

⚠️ The D90 III is not a confirmed model in `toppingctl`'s device table and its register map must not
be assumed to match the DX5 II's. See [`01-022`](01-022-multi-dac-control-plane.md): the agent that
would own such a USB connection is the one that design describes, and its rule is that unconfirmed
models stay read-only until driven.

## Volume control (Home Assistant)

> **As-built note:** the deployment chose a _single merged knob_ per room (see
> [As-built](#as-built-deployed-2026-07)), not the two independent layers this section originally
> proposed — the goal became one Snapcast/HASS control over Snapcast + p2p Spotify + TV. The
> analysis below is retained as the original reasoning.

The one thing worth preserving from the HiFiBerry WebUI is its volume slider — and it drove the
card's **ALSA hardware mixer**, not a Snapcast control, so it doesn't come for free with the
streamer OS. There are two independent volume layers, and both can live in HASS (the house control
plane):

| Layer        | What it is                                                                                       | Path into HASS                                                                                      |
| ------------ | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| **Software** | Snapcast per-client digital volume (Snapweb at `snapcast.burntbytes.com`, usually left at 100 %) | Native **HASS Snapcast integration** (server control port `1705`) — each client is a `media_player` |
| **Hardware** | The Pi's **ALSA mixer** volume (the DAC/card's own level — what the HiFiBerry WebUI drove)       | A small **MQTT bridge** on each endpoint → a HASS `number` slider (via MQTT discovery)              |

**Keep them independent:** run snapclient with `--mixer software` (default).
`--mixer hardware:'<control>'` would make the Snapcast slider _become_ the ALSA hardware control —
one merged slider, the opposite of exposing both.

**Hardware slider — MQTT bridge.** A small systemd service per endpoint, reusing the existing
mosquitto + HASS MQTT stack (no SSH-from-HASS):

1. On start, publish a HASS discovery config → a slider auto-appears:
   `homeassistant/number/<room>_hw_vol/config` with `command_topic`/`state_topic`, `min:0 max:100`.
2. On command: `amixer -c <card> set '<control>' <value>%`.
3. Publish state from `amixer get` (on change / periodic).

Result: two sliders per room — `<Room> Volume` (Snapcast/software) and `<Room> HW Volume`
(ALSA/hardware) — both in HASS.

**Per-room caveat.** The hardware slider only exists where the output device exposes an ALSA volume
— confirm with `amixer -c <card> scontrols`:

- USB DAC with UAC volume, or a HiFiBerry DAC+ chip → both sliders.
- **D90 III (likely no host volume) or a Digi/S-PDIF output** → no ALSA control to bridge; that room
  gets the **software slider only**, and its true analog volume lives on the DAC's knob/remote
  (bring that into HASS via an IR blaster if wanted).

So "expose both" is really _software everywhere, hardware where the device exposes a mixer_.

## Test plan (validate on a spare Pi, zero risk to the 2 live rooms)

1. Flash **DietPi** on a spare Pi.
2. `dietpi-software` → install **Snapcast Client**.
3. Connect a USB DAC (the D90 III if available, else any USB DAC to prove the path).
4. Point it at the Snapserver LAN IP and select the USB card:
   `snapclient --host <snapserver-ip> -s <usb-alsa-card>`.
5. Confirm it joins the group in Snapweb, plays **in sync** with kitchen/living-room, and audio
   exits the USB DAC.
6. Calibrate the client's Snapcast **`latency` offset** so it aligns with the existing rooms (the
   USB/DAC chain latency differs from the HAT chain — expect to nudge this).
7. If green: this is the migration recipe for the other rooms.

## As-built (deployed 2026-07)

The rollout diverged from the original plan in two deliberate ways, both driven by real per-room
needs:

1. **Living-room keeps its HiFiBerry DAC+ DSP** (the plan was to retire all HATs). That room's TV
   (Samsung S95C) feeds **optical S/PDIF into the HiFiBerry**, and the downstream DAC (Topping **D30
   Pro**) has no _host-controllable_ volume. The HiFiBerry DSP is therefore the room's volume stage
   _and_ its TV-input path — the two things a bare digital transport can't do — so the DSP stays on
   the HAT, feeding the D30 Pro over S/PDIF.

   > **Correction (2026-08-27).** This entry previously said the D30 Pro "is a fixed-output DAC with
   > no volume." **That is wrong.** Per its manual the D30 Pro has two output modes — `m-p` Pre-Amp
   > (volume adjustable, **the factory default**) and `m-d` DAC (fixed at maximum) — and its volume
   > is adjustable by front knob or IR remote. Its house IR codes are already deployed
   > (`homelab/firmware/esphome/ir-blaster.yaml`, "D30 Pro / D50s Volume Up"/"Down").
   >
   > The real constraint is narrower and it is about **addressability, not capability**: the D30 Pro
   > exposes no host-side volume, and IR volume is **relative up/down with no state readback**, so
   > an absolute "set to 40%" slider cannot be built on it. That — not an absent volume control — is
   > why the DSP became the room's volume stage. Capabilities recorded in
   > [`_reference/topping-dac-capabilities.md`](_reference/topping-dac-capabilities.md).

2. **Volume became one merged knob per room, not two independent layers.** The plan kept
   `--mixer software` plus a separate MQTT ALSA-hardware slider. In practice the wanted UX was a
   _single_ Snapcast/HASS volume controlling **everything in the room — Snapcast + p2p Spotify
   (go-librespot) + TV** — so each room routes that one control to whatever stage sits under all its
   sources. `--mixer software` alone was insufficient: it doesn't touch the p2p go-librespot path.

**Per-room as-built:**

| Room            | DAC / DSP                                                                     | One-knob volume mechanism                                                                                                                                                                  | Network              | Status         |
| --------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------- | -------------- |
| **Kitchen**     | USB → Topping **D50s**                                                        | `snapclient --mixer "hardware:D50s "` → the DAC's UAC2 volume (sits under snapclient + go-librespot)                                                                                       | wired **10.42.2.38** | ✅ done        |
| **Living-room** | HiFiBerry **DAC+ DSP** HAT → S/PDIF → **D30 Pro**; TV optical → HAT S/PDIF-in | Snapcast→**DSP master** bridge (`snap-dsp-volume-bridge`): subscribes to snapserver `Client.OnVolumeChanged`, sets the SigmaDSP master via `dsptoolkit` → covers stream + Spotify + **TV** | wired **10.42.2.39** | ✅ done        |
| **Office**      | USB → Topping **D90 III Discrete** (reference room)                           | TBD — `--mixer hardware` if the D90 III exposes a UAC volume, else **softvol**. ⚠️ D90 III volume support is **unverified** — do not infer it from a sibling model                         | pending              | 🔧 in progress |

Implementation notes captured for reuse:

- **DietPi minimal has no sftp-server** → `scp` fails; deploy files via
  `cat file | ssh host 'cat > dest'`.
- **HiFiBerry DSP is SPI-controlled** (not I2C): `dtparam=spi=on`; toolkit = `hifiberry-dsp` from
  GitHub `./src` (build deps `build-essential libasound2-dev python3-spidev python3-alsaaudio`);
  `sigmatcpserver` needs TCP enabled (drop the `--disable-tcp` the shipped unit sets, for the
  `dsptoolkit` CLI) + `Restart=always`. Stock profile `dacdsp-default.xml` gives master volume +
  S/PDIF-in routing.
- **After the WiFi→wired cutover, restart `go-librespot`** or its Spotify Connect device stays
  advertised on the dead wlan0 IP and vanishes from the app.
- **`--mixer hardware` preserves DAC auto-sleep** (only the mixer/control endpoint is held open; the
  audio PCM still closes on idle).
- Endpoints are on 10.42.2.x; when disabling WiFi add an `eth0` default route + verify
  `ping -I eth0 <mac>` first (control host is on another subnet) or the node strands.

## Exit Criteria (revised to as-built)

- [ ] All endpoints on **DietPi + `snapclient`** (retires HiFiBerryOS + the patched
      `snapcast-hifiberry` image) — kitchen ✅, living-room ✅, **office ⬜ (last node)**.
- [x] **Per-room DAC/DSP topology decided** — kitchen USB→D50s, living-room keeps HiFiBerry DAC+ DSP
      (TV + D30 Pro), office USB→D90 III (implementation: office pending).
- [ ] **One Snapcast/HASS volume per room controls all sources** (Snapcast + p2p Spotify + TV where
      present) — kitchen ✅, living-room ✅, office ⬜ (`--mixer hardware` vs softvol TBD).
- [ ] **Wired ethernet + static IP + WiFi disabled** per room — kitchen ✅ (.38), living-room ✅
      (.39), office ⬜ (verify wired drop).
- [ ] **Office / D90 III**: snapclient joins on USB, volume wired, **PEQ configured** (Topping
      Tune) + confirmed on the USB input.
- [ ] **Per-client Snapcast `latency` offset calibrated** across all rooms (chains differ → they
      drift otherwise).
- [ ] **Migration runbook in `homelab`** — the reusable bundle exists at
      `homelab/hosts/dietpi-audio/`; write it up as the canonical runbook that supersedes the
      patched image (add the HiFiBerry-DSP and `--mixer hardware`/softvol volume recipes).

## Progress

- [x] Meta-analysis of the digital-output HAT universe + interface/OS layers
- [x] DAC identified (D90 III Discrete) + per-room DACs deployed (D50s kitchen; D30 Pro + HiFiBerry
      DSP living-room)
- [x] Kitchen + living-room fully migrated (DietPi, wired, one-knob volume; Spotify + Snapcast [+ TV
      living-room] verified)
- [ ] Office / D90 III node (last endpoint) — USB DAC + volume + PEQ
- [ ] Per-client latency-offset calibration across rooms
- [ ] homelab migration runbook (supersedes patched `snapcast-hifiberry` image)

## References

- HiFiBerry Digi2 Pro — <https://www.hifiberry.com/shop/boards/digi2-pro/>
- HiFiBerryOS EOL notice — <https://www.hifiberry.com/blog/hifiberryos-quo-vadis/>
- Topping D90 III Discrete — <https://www.headfonia.com/topping-d90-iii-discrete-review/>
- Pi2AES 2.0 — <https://www.pi2design.com/pi2aes.html>
- Volumio Snapcast plugin — <https://github.com/Saiyato/volumio-snapcast-plugin>
- Snapcast — <https://github.com/snapcast/snapcast>
- DSPi (RP2040/RP2350 USB DSP firmware) — `~/src/DSPi` + [ASR thread][dspi]; console
  `~/src/DSPi-Console`. Enclosure + I/O-board index (95-page ASR crawl, with buy links):
  [`_reference/dspi-asr-index.md`](_reference/dspi-asr-index.md)
- CamillaDSP (software DSP alternative) — <https://github.com/HEnquist/camilladsp>
