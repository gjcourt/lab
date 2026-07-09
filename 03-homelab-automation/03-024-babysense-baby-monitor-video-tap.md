---
title: 'Babysense Baby-Monitor Video Tap (teardown → homelab stream)'
number: '03-024'
category: 'homelab-automation'
difficulty: 'Hard'
time_commitment: 'Weeks'
target_skills:
  'Hardware teardown, Logic analyzer/FPGA, SPI flash dump, Parallel-RGB (DPI) capture, SDR
  (optional), go2rtc/MediaMTX'
status: 'In Progress'
depends_on:
  - hardware/babysense-unit
  - hardware/sacrificial-parent-unit
  - homelab/home-assistant
---

# Babysense Baby-Monitor Video Tap (teardown → homelab stream)

## Description

Get the Babysense camera feed into the homelab as a network stream (RTSP/WebRTC → Home Assistant),
ideally without the head unit. The monitor is a **local-only 2.4 GHz digital video tx/rx** device
(no WiFi/cloud). This project is the _hacking_ path; the pragmatic fallback (a $30 LAN-only RTSP
cam) is noted at the end.

## Key findings (RF/hardware recon, 2026-06-27)

**Over-the-air interception is effectively infeasible** for a homelab tinkerer — three stacked
walls:

1. **Bandwidth:** the FHSS hop band is ~64–83 MHz wide; the widest affordable SDRs (bladeRF 2.0
   ~56–61 MHz, USRP B210 ~56 MHz) can't span it, and HackRF (20 MHz) isn't close. One missed hop
   corrupts frames.
2. **Hop sequence:** proprietary, pairing-derived — needs a firmware dump to recover.
3. **Codec:** undocumented proprietary video codec in the SoC; no open decoder. Never cracked
   publicly for this device class.

**Silicon (uniform across modern V43 / V24 / HD S2 / MaxView line):**

- **SONiX SN93xxx** multimedia SoC — H.264 + software-driven adaptive FHSS
- **AMICCOM A71xx** — 2.4 GHz GFSK RF PHY (⚠️ newer **A7157** adds hardware AES-128)
- **External SPI NOR flash** — confirmed **Winbond W25Q128 (16 MB)** on the MaxView parent (dump
  target)
- **LCD = ~40-pin parallel RGB888 (DPI)** — _not_ MIPI-DSI → tappable with a logic analyzer/FPGA
- _(V65 is an older Hisense lineage — none of the above confirmed for it.)_

> ⚠️ **Superseded in part by the teardown below** — the RX unit on hand is MIPI-DSI (via a bridge),
> the flash is 32 MB, and there's a labeled UART. See the confirmed values next.

## Teardown — actual hardware (parent / RX unit, 2026-07-08)

Physically opened the **parent/receiver** unit. Board: **`VB55-PCB-RX-MAIN-V1.8_2L`**, dated
2023-10-10. Confirms the silicon family and pins exact part numbers — with three corrections to the
recon assumptions above.

**Confirmed / identified:**

- **Main SoC: SONiX `SN93701AFG`** (100-pin QFP) — the H.264 + FHSS controller. ✅ as predicted.
- **RF: `DW-V7130-B-V02`** shielded can + antenna wire = the 2.4 GHz radio. The PHY die (AMICCOM
  A71xx-class) is _inside the shield_ — PN not yet visible; open the can or pull the FCC report to
  settle **A7121 (plaintext)** vs **A7157 (AES-128)**.
- **SPI NOR flash: Winbond `W25Q256JV` (32 MB)** — 2× the assumed size (recon guessed W25Q128 / 16
  MB). A second Winbond 25-series part sits near the RF can → possibly separate RF-module firmware.
  Re-spec the reader for 25Q256 (>16 MB addressing).

**Corrections that change the tap plan:**

- ⚠️ **The panel is MIPI-DSI, _not_ parallel-RGB at the flex.** There's a Solomon **`SSD2828QN4`**
  on the board = a **parallel-RGB → MIPI-DSI bridge**, and the LCD flex is **24-pin MIPI**. So do
  **not** tap the LCD connector. **But the RGB bus still exists** — as the **SoC → SSD2828 input**
  on the PCB. That becomes the new tap point: the parallel-RGB (PCLK / HSYNC / VSYNC / DE / data)
  lines between `SN93701` and `SSD2828`, reachable at the dense test-point field around both chips.
  The display-tap strategy survives; only the tap point relocates from the flex to the SoC-side bus.
- 🎯 **Labeled UART present.** A silkscreened **`GND / RX / TX / 3.3V`** pad group sits near the SoC
  — a real console candidate. Upgrades "no shell expected" → **boot log likely, shell possible**.
  This is now the cheapest first move.
- **USB-C has `DM/DP` pads populated** → a USB-device / DFU path worth probing, beyond the DC4.7V
  charge rail. (The unit is a portable parent: LiPo `BAT+`, speaker, mic, Vol± / RST / PWR.)

**Revised attack ladder (cheapest → destructive):**

1. **UART** on the `GND/RX/TX/3.3V` header — solder a header, USB-TTL at 3.3 V, sweep bauds
   (115200-8N1 first), capture the boot log, ID the SoC/SDK, look for a shell.
2. **USB-C `DM/DP`** — check for USB enumeration / DFU / mass-storage exposed by the SoC.
3. **SPI dump** the `W25Q256` (in-circuit SOIC-8 clip, else desolder) — pull firmware; hunt the hop
   table, pairing key, and codec/SDK strings.
4. **RGB tap** at the `SoC → SSD2828` bus on a _sacrificial_ unit — frames → ffmpeg → go2rtc → HA.

## Recommended path — display-bus tap (bypass RF entirely)

The parent unit already follows the hops, demodulates, and decodes the codec into pixels for its
LCD. **Tap the decoded video off the parallel-RGB bus** on a _sacrificial_ parent unit: parallel-RGB
(pixel clock, HSYNC, VSYNC, DE, data) → logic analyzer / FPGA / Pi DPI pins → reconstruct frames →
encode (ffmpeg) → restream via **go2rtc / MediaMTX** → Home Assistant. This is mechanical +
logic-analyzer work (days–weeks), high success probability, no RF/codec RE.

> **Tap point (per teardown):** on this RX unit the RGB bus is **`SN93701` SoC → `SSD2828` bridge
> input** (the panel itself is MIPI — don't tap the 24-pin flex). Probe the test-point field between
> those two chips. But work the UART/flash rungs of the attack ladder _first_ — a firmware dump or a
> shell may expose the video far more cheaply than the destructive RGB tap.

## Step 0 (before buying anything)

Read the **model # / FCC ID** off the unit's housing label (the PCB is `VB55-PCB-RX-MAIN-V1.8`, but
the product model / FCC ID lives on the case), then pull the **FCC test report** (fcc.report,
grantee `2AQVL`) — it hands you the hop parameters (channels/spacing/dwell/span) for free, and lets
you confirm the PHY inside the `DW-V7130` can: **A7121** (plaintext era) vs **A7130/A7157**
(possible AES-128).

## UART bring-up (rung 1) — adapter + checklist

The board's labeled `GND / RX / TX / 3.3V` pad group is the manufacturer's debug console — cheapest,
non-destructive way in. **Must use a 3.3 V-logic adapter** (5 V can damage the SoC).

**Adapter picks:**

- **Best all-rounder — Tigard (~$35–40):** FT2232H multitool, switchable 1.8/3.3/5 V; does UART now
  **and** the `W25Q256` SPI dump later (rung 3, via `flashrom`) + JTAG/SWD. One buy covers two
  rungs; great macOS support.
- **Foolproof — genuine FTDI `TTL-232R-3V3` cable (~$20):** 3.3 V _fixed_ (can't mis-set to 5 V),
  flying leads, native macOS driver.
- **Cheap — Adafruit CP2104 Friend / any CP2102 (~$8):** 3.3/5 V jumper → set 3.3 V and **verify on
  VCCIO with a meter** first.
- **Avoid CH340** boards on macOS (extra WCH driver). CP210x / FTDI enumerate cleanly.

**Hookup:** solder a 4-pin 0.1″ header to the pads (or pogo/test-hooks for read-only). Wire
**GND→GND, board TX→adapter RX, board RX→adapter TX; leave `3.3V` unconnected** (it's the board's
own rail — the unit self-powers from battery/USB-C).

**Checklist:**

- [ ] Adapter set/verified to **3.3 V** (meter on VCCIO)
- [ ] GND + board-TX→adapter-RX only (receive-only first, zero risk)
- [ ] `picocom -b 115200 /dev/tty.usbserial-*`; power-cycle; watch the boot log
- [ ] Garbage → sweep baud (57600 / 9600 / 921600); silent → swap TX/RX
- [ ] Capture log; ID SoC/SDK + OS (RTOS vs Linux); note any U-Boot autoboot prompt
- [ ] Only if a shell / U-Boot appears: add adapter-TX→board-RX and interact

## Exit Criteria

- [ ] Model # / FCC ID confirmed; FCC test report pulled; transceiver PN identified
- [ ] UART boot log captured; SoC/SDK + OS identified (shell / U-Boot reachable?)
- [ ] Decoded frames captured off the parent-unit parallel-RGB bus (proof of concept image)
- [ ] Continuous frame reconstruction → encoded stream
- [ ] Stream restreamed (go2rtc/MediaMTX) and visible as a camera in Home Assistant
- [ ] Documented; decide whether it's reliable enough to replace the head unit

## Shopping list (~$80)

- SOIC-8 test clip + CH341A programmer (~$15) — SPI flash dump. **Confirmed target: `W25Q256` (32
  MB)** — use a reader/software that handles >16 MB (4-byte addressing)
- **3.3 V** USB-TTL / debug adapter for the labeled `GND/RX/TX/3.3V` header — **Tigard (~$35, also
  does the SPI dump)**, FTDI `TTL-232R-3V3` cable (~$20, foolproof), or a CP2102/CP2104 module
  (~$8). Avoid CH340 on macOS. See _UART bring-up_ below
- Cheap logic analyzer (Saleae clone) or ~$50 FPGA — the `SoC → SSD2828` parallel-RGB capture
- A **second/sacrificial parent unit** for the destructive display tap

## Pragmatic fallback (the "cheating" win)

If the goal is just _a baby cam in the homelab_, skip all of the above: buy a **$25–40 LAN-only
ONVIF/RTSP cam** (Tapo C120 / Reolink), quarantine it on the IoT VLAN with **WAN egress blocked**,
and restream via go2rtc → HA. One hour, better image quality. (Keep a baby cam LAN-only — no cloud.)

## Cautions

- The best public teardown (noobie.dog, near-identical Victure hardware) reportedly carries an
  injected malicious script on its host page — read findings in reader mode, run nothing from it.
- Confirm the transceiver isn't an AES-128 A7157 before assuming a flash dump yields cleartext.

## Progress

- [x] Feasibility + silicon recon (2026-06-27) — display tap is the achievable path
- [x] Teardown of the RX/parent unit (2026-07-08) — PNs confirmed (`SN93701AFG`, `SSD2828QN4`,
      `W25Q256JV`, `DW-V7130` RF can); panel is MIPI (tap relocates to SoC→bridge); **labeled UART
      found**
- [ ] Step 0: product model / FCC ID off the housing label + FCC test report
- [ ] UART boot-log recon on the `GND/RX/TX/3.3V` header (+ USB-C DM/DP probe)
- [ ] SPI dump the `W25Q256` + firmware analysis
- [ ] Parallel-RGB capture POC at the `SoC → SSD2828` bus
- [ ] Reconstruct → restream → HA
