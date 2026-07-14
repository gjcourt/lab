# DSPi — ASR Thread Index (Enclosures + I/O Boards focus)

**Project:** DSPi — audio DSP firmware by WeebLabs turning a Raspberry Pi Pico (RP2040) / Pico 2
(RP2350) into a USB sound card with onboard DSP (room correction, active crossovers, PEQ, time
alignment, loudness comp, crossfeed), outputting S/PDIF or I2S (runtime-switchable) plus a mono PDM
subwoofer output.

## Sources (canonical URLs)

- **Primary ASR thread (indexed in full, 95 pages, posts #1–#1885, Feb 5 2026 → Jul 2026):**
  <https://www.audiosciencereview.com/forum/index.php?threads/introducing-dspi-a-powerful-user-friendly-and-open-source-dsp-for-less-than-a-cup-of-coffee.69343/>
  - Page N: append `page-N` to the URL (e.g. `.../69343/page-85`).
  - Post refs below are `#<postnumber>` — find them via the page containing that post (≈20
    posts/page: page-N covers roughly posts 20·(N−1)+1 … 20·N).
- **diyAudio pointer thread** (returned HTTP 403, not crawlable; appears to be a "look at this ASR
  thread" pointer, not an independent hardware thread):
  <https://www.diyaudio.com/community/threads/weeb-labs-dspi-at-asr.437360/>
- GitHub firmware: <https://github.com/WeebLabs/DSPi> (console:
  <https://github.com/WeebLabs/DSPi-Console>)
- Official Discord: <https://discord.gg/RCyqxAQ5xS>
- Coverage: All 95 pages fetched and scanned for enclosure / I/O-board content. Last post at time of
  crawl: #1885 (Kingsnake).

### Key firmware hardware facts (from local repo README, for wiring context)

- **Default output pins:** SPDIF/I2S data on GPIO 6/7/8/9 (slots 0–3); PDM sub on GPIO 10; I2S BCK
  GPIO 14 (shared), LRCK = BCK+1 = GPIO 15 (fixed), optional MCK GPIO 13 (128×/256× Fs). All output
  pins runtime-reassignable via Console; **reserved:** GPIO 12 (UART TX), 23–25 (power/LED).
- **SPDIF output** needs either a TOSLINK TX module or a passive resistor divider + cap; **coax** =
  series resistor (330Ω common) + 100nF cap. **I2S** = standard 24-bit-in-32-bit left-justified;
  wires straight into most I2S DACs. **PDM sub** = RC low-pass (3.3kΩ + 47nF typical) to analog.
- **SPDIF input** (added ~v1.1.4): default GPIO 11, runtime-assignable; needs a TTL SPDIF source
  (coax→TOSLINK adaptor, TOSLINK RX module, or Schmitt-trigger/inverter conditioning). **I2S input**
  / multichannel (2/4/6/8ch) added later (~v1.1.5+, DSPi as clock master; slave mode later). ADC
  support via PCM1808 modules.

---

## ENCLOSURES

| Enclosure / approach                     | Material & size                                      | Vendor / price                                                                   | Mods / mounting                                                                                                                                             | Verdict / who                                                     | Source                        |
| ---------------------------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ----------------------------- |
| Hinged clear-cover project box           | ~5.9"×3.9"×2.8" (150×100×70mm), plastic w/ clear lid | ~$14 (Amazon)                                                                    | None — no-solder build (Pico + breakout + SPDIF card)                                                                                                       | TheMusicListener's ~$63 beginner BOM                              | #693                          |
| 7"×4"×3" project case w/ mounting plate  | ~178×102×76mm                                        | Amazon **B0FHVBWY21** (case); breakout **B0BFB53Y2N**; SPDIF card **B0B2QQWG38** | Remove SPDIF board's metal face plate; secure with narrow cable ties; SPDIF→GP6, GND→GND, +5V→VBUS/VSYS                                                     | Rocky Maine's validated no-solder build; says smaller cases work  | #695, #1025                   |
| Generic Alibaba box w/ pre-fitted knob   | metal, ~compact                                      | Alibaba ~$14 + UK delivery                                                       | Pre-installed rotary knob hole; laser-engraved rear plate                                                                                                   | Kingsnake 4×PCM5102 build                                         | #1663                         |
| Custom CNC aluminium-alloy case          | aluminium, custom                                    | **JLCPCB / JLCFA** (jlcpcb.com, ke.jlcfa.com) ~$10                               | Design in JLC's tool; CNC + PCB + SMT all one vendor                                                                                                        | zergxia — clean result, cheap                                     | #1797                         |
| Recycled "CCC" DAC rear panel            | reused metal chassis                                 | salvage                                                                          | Reused existing RCA/TOSLINK cutouts & connectors; sub out = 1kΩ series + 100nF to GND                                                                       | Kingsnake early build                                             | #531                          |
| Steel PC/SSD-bay case (amp + DSPi combo) | steel case + 2mm alu plate                           | salvage + enclosed Mean Well PSU                                                 | DSPi + DACs + TPA3255 amp on grounded 2mm alu plate; 48V twisted + ferrites                                                                                 | Kingsnake integrated amp                                          | #840, #843, #1314             |
| 3D-printed cases (multiple users)        | PLA/PETG, custom                                     | self-printed                                                                     | TurtlePaul: light print couldn't hold thick TOSLINK cable weight; m_g_s_g: printed too small, had to trim; Tell & Red_Red: designing for Pico2 + I2S boards | Iterating; watch cable strain-relief & tolerances                 | #436, #717, #725, #799, #1001 |
| Pico breakout-board "chassis"            | breakout ~2× Pico width                              | AliExpress/generic                                                               | No-solder GPIO access via screw/pin terminals; yellow LEDs show active GPIO                                                                                 | Sonic-Wall & Barrelhouse Solly recommend breakout for prototyping | #434, #978                    |
| Aluminium-lid box + RF remote            | aluminium lid                                        | generic                                                                          | Aluminium lid kills RF range (3m open → 0.5m closed); ext. antenna needed; 6mm D-shaft encoder for standard knobs                                           | Kingsnake                                                         | #1422, #1799                  |

### Enclosure notes/open items

- No official DSPi enclosure or shared STL/STEP as of end of thread — all cases are DIY/one-off.
  Repeated asks for a shared 3D-print file remain **open**.
- AndreaT (#100) requested a commercial finished box (AES/EBU + TOSLINK + S/PDIF I/O + PSU) at ~$149
  — no product exists; WeebLabs' answer is the planned custom PCB (see I/O boards), not a case.
- Practical cautions from builders: give TOSLINK cables strain relief (they're heavy), keep the
  SPDIF-out GPIO away from I2S pins to avoid EMI on breadboards (#1698), and leave room for a rotary
  encoder + optional RF/IR remote.

---

## I/O BOARDS

### A. I2S DAC boards (output)

| Board / chipset                                      | Function / ch               | DSPi compat & wiring                                                                                                                                                                                                        | Vendor / price                               | Verdict / caveats                                                                                                                              | Source                                                                       |
| ---------------------------------------------------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **PCM5102 / PCM5102A "purple" module** (TI PCM5102A) | Stereo I2S DAC out          | Hardware mode, no I2C/MCLK needed. DIN←GPIO7 (or data slot), BCK←GPIO14, LRCK←GPIO15, VIN←**5V (VBUS/VSYS)**. **Must pull XSMT/XMT high (3.3V) to un-mute**; cheap boards ship with mislabeled/un-bridged jumpers (H1L–H4L) | AliExpress/Temu/Amazon **~€2–5**             | The default community DAC. Sounds "as it should," quieter than a MiniDSP 2x4HD; label printing often reversed — ignore silkscreen, verify pins | #61, #231, #279–285, #494, #502, #1114, #1304–1306, #1389–1391, #1985, #2465 |
| **Dollatek PCM5102A**                                | Stereo I2S DAC out          | 3.3V, **no setting solder-links** (simplest)                                                                                                                                                                                | Amazon                                       | Kingsnake's pick to avoid jumper hassle                                                                                                        | #1305                                                                        |
| **Adafruit I2S Stereo DAC (PCM5102 / PCM5122)**      | Stereo I2S DAC out          | Works at 3.3V; PCM5122 needs no MCLK/I2C                                                                                                                                                                                    | Adafruit, ~+$2 over generic                  | markz: noticeably higher quality caps than random AliExpress; recommended over no-name                                                         | #1117–1118, #1357, #1698                                                     |
| **Innomaker PCM5122 board**                          | Stereo I2S DAC out          | 5V (Vsys); dual onboard oscillators for jitter reduction; tested 48/96k                                                                                                                                                     | Innomaker                                    | markz building an improved balanced variant off this                                                                                           | #1324, #1337, #1595                                                          |
| **Waveshare Pico Audio (HAT, PCM5101)**              | Stereo I2S DAC HAT          | Plugs onto Pico; I2S on default pins; verified w/ v1.1.3-beta                                                                                                                                                               | Waveshare                                    | Confirmed working (JuanjoS); WeebLabs referenced early                                                                                         | #74, #282, #878, #1119                                                       |
| **Pimoroni Pico Audio Pack**                         | Stereo I2S DAC HAT          | I2S_DATA=GPIO9, BCK=GPIO10, LRCK=GPIO11 (reassign in Console)                                                                                                                                                               | Pimoroni, **<£20**, no-solder                | gadget-man, easy                                                                                                                               | #1779                                                                        |
| **ES9018K2M module**                                 | Stereo I2S DAC out          | The **cheap ES9018 modules accept SPDIF directly from Pico** (don't need the "SPDIF version"); or I2S                                                                                                                       | AliExpress **<€12**                          | slunk/capslock analyzed: 7660 inverter, optional 74HC04 buffer, 820Ω diff-amp, ~800Ω Zout, ~15mV DC offset, no output cap                      | #226, #231, #647–652                                                         |
| **Khadas Tone2 Maker Kit**                           | Stereo DAC, I2S+SPDIF in    | 5V USB power; direct I2S or SPDIF in                                                                                                                                                                                        | Khadas                                       | solawind: "good one," low power                                                                                                                | #1006, #1050                                                                 |
| **Khadas Tone2 Pro**                                 | Balanced DAC + 4.4mm HP out | I2S only via their **custom USB-C** port (solder jumpers to break out differential)                                                                                                                                         | Khadas **~$129**                             | "SINAD on par with TOTL DACs"; fiddly USB-C I2S access                                                                                         | #1046, #1050                                                                 |
| **Topping E2x2 / Fosi ZH3**                          | Balanced DAC/interfaces     | I2S-capable options                                                                                                                                                                                                         | ~$138 / $199                                 | Mentioned as nicer I2S-in targets                                                                                                              | #1046                                                                        |
| **Audiophonics EVO Sabre (I2S in)**                  | Full DAC unit               | Fed via I2S; Pico mounted on **Pi-Hut ProtoMate** proto-HAT in place of the Pi                                                                                                                                              | Audiophonics / Pi-Hut                        | olki — works; added BCK/LRCK resistors for future sub DAC                                                                                      | #1307                                                                        |
| **UDA1334A module**                                  | Stereo I2S DAC              | I2S in                                                                                                                                                                                                                      | AliExpress                                   | Tell listed as budget option                                                                                                                   | #787                                                                         |
| **WONDOM TAS5756 / TSA1702B**                        | I2S power-amp / BT-DSP-in   | I2S in; TAS5756 needs I2C register init at startup                                                                                                                                                                          | WONDOM/TinySine                              | TOMSON/JDSP; note I2C-config requirement (not pure hardware-mode)                                                                              | #1117, #1383                                                                 |
| **I2S headphone-amp add-on board**                   | HP amp off I2S              | Direct I2S; 160mW into 32Ω (drives Hifiman Sundara +8dB)                                                                                                                                                                    | AliExpress **€2.50** (item 1005012026272931) | WeebLabs: "perfect little add-on for a DSPi board"                                                                                             | #1545                                                                        |

### B. Custom / community PCBs (the "motherboard for Pico" efforts)

| Board                                               | What it is                                                                                                                             | Cost                                            | Notes                                                                                                                                                  | Source                                      |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------- |
| **WeebLabs official DSPi board** (planned)          | TAC5212/TAC5242 codec(s): DAC+ADC+HP amp. Target config: 4× RCA out, 2× RCA in, 2× XLR out, 3.5mm HP, USB-C; +BT/WiFi (ESP32 over I2C) | Est **$50 (~$70 high-end)**; TAC5212 codec ~€10 | TAC5212 measures ~ -98dB THD+N (ADC) / -104dB (DAC). Plug-and-play, all filtering+connectors onboard. Prototyping via PCBWay TAC5212 breakout          | #74, #792, #801, #812, #823, #1071, #1164   |
| **Red_Red "nanoDigi-like" motherboard**             | Pico carrier: 4× TOSLINK out + 2× SPDIF in (opt+coax), OLED, rotary encoder                                                            | ~$50–60                                         | Uses **FCR684214T (TX) / FCR684214R (RX)** TOSLINK modules; ~50mA USB-powered; runtime-assignable GPIO                                                 | #799, #1076, #1080                          |
| **Ajay KiCad 2.1/2.2 board**                        | Pico carrier: TOSLINK I/O, 2× I2S, PDM sub, internal mains PSU (+12V trigger, +5V)                                                     | —                                               | KiCad files offered (schematic only, no PCB layout yet). Warns 74HC04 can self-oscillate at 240MHz w/ no signal; references ST **AN5073** for SPDIF-in | #1130, #1143                                |
| **markz "4× I2S + optical-in" board + DAC carrier** | Bare motherboard hosting up to 4 I2S DACs + optical input                                                                              | **~80¢ bare, a few $ w/ connectors** (JLCPCB)   | Separate small board wires up three DACs; some configs no-solder                                                                                       | #1762                                       |
| **markz TAD5242 6-channel balanced DAC board**      | TI TAD5242, 6ch balanced, low-noise LDO                                                                                                | **~$12/board** at JLCPCB (qty 10)               | QA403-measured; others asked for gerbers/PCBs (unanswered)                                                                                             | #2629671                                    |
| **bogdansrb custom codec boards**                   | RP2350 + codec: AK4619 (4-in/4-DAC), ES9081Q, AD1938 (4ADC/8DAC), planned 6/8ch                                                        | —                                               | KiCad/PDF schematics shared (Pico2_ESS_DSP.pdf); AD1938 runs hardware-mode                                                                             | #575, #581, #953, #961, #1095, #1403, #1992 |
| **Darren-project custom PCB**                       | 3rd-party DSPi SPDIF PCB                                                                                                               | —                                               | GitHub: `Darren-project/custom_weeb_lab_SDPi_PCB`                                                                                                      | #1139                                       |
| **giubeppe I2S firmware fork** (pre-official I2S)   | RP2350 I2S-out build (foxdac.uf2)                                                                                                      | free                                            | PCM5102: DIN←GPIO22, BCK←GPIO26, LCK←GPIO27; later MCLK GPIO13, 96/24, 4-pin I2S                                                                       | #468, #494, #526, #582, #535289             |

### C. SPDIF / TOSLINK output (transmitters, coax)

| Component                                              | Function                   | Wiring / compat                                                                                                                         | Vendor / price                                           | Source                                 |
| ------------------------------------------------------ | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------- |
| **Toshiba TOTX179 / TX179** TOSLINK TX                 | Optical out                | Onboard driver, VCC(5V, run at 3.3V) + TTL data; 0.1µF decouple cap                                                                     | **EOL / hard to source officially** (eBay/Mouser costly) | #16, #87, #89, #742, #1684             |
| **DLT1160 / DLT1111A** TOSLINK TX                      | Optical out                | 3.3V; +68Ω series + 1µF cap — tested playing music w/ EQ                                                                                | AliExpress                                               | #208, #742                             |
| **Cliff / CN23454 (TX), CN23453 (RX)**                 | Optical TX/RX              | Cliff via **Newark/CPC-Farnell**; CN23454 TX tested-working; 3-pin (Vcc/Gnd/Vin); 68Ω(3.3V) or 220Ω(5V) series, 100nF decouple          | CPC/Farnell / AliExpress                                 | #483, #691, #1542, #1688               |
| **FCR684205T/R, FCR684214T/R** TOSLINK sockets         | PCB optical I/O            | 3.3V compatible (unlike std 5V units); warns of LED damage if miswired                                                                  | **TME.eu / Farnell ~£2 (TX) / £3 (RX)**                  | #810, #1076, #1131–1132                |
| **Audiophonics TOSLINK In/Out sockets-on-PCB**         | Panel optical I/O          | Contain driver IC, +5V + TTL, "just work"                                                                                               | audiophonics.fr (p-19144 input socket)                   | #312, #316, #319, #448                 |
| **PC-motherboard SPDIF daughter card** ("24bit192kHz") | Coax + optical out bracket | Has decoupling caps + TOSLINK TX onboard; unscrew the metal bracket. Wire SPDIF→GP6, +5V→VBUS/VSYS, GND                                 | Newegg/Amazon/AliExpress                                 | #297, #519, #717                       |
| **Coax SPDIF (passive)**                               | Coax out                   | Series R (330Ω) + 100nF cap; or divider (100nF→1K→pico, 2.2K/2.2K to 3.3V/GND). Use 75Ω coax cable, 22µF series on RCA tip for DC block | passives                                                 | #56, #67, #68, #255, #535, #922, #1385 |

### D. SPDIF / I2S / analog INPUT boards & ADCs

| Component                                  | Function                                    | Compat / notes                                                                                                                                                                      | Vendor / price                                                                   | Source                                                |
| ------------------------------------------ | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------- |
| **PCM1808 ADC module**                     | Stereo analog→I2S ADC (turntable/analog in) | Official ADC path; 5V analog + 3.3V digital, x256 MCK; wiregen utility gives pinout; recommend 100pF LPF cap mod                                                                    | AliExpress (cheap)                                                               | #1469, #1592, #1594, #2618186, #2618748, #1743, #1864 |
| **TOSLINKBee** (TinySine)                  | SPDIF/optical→I2S w/ ASRC                   | DIR9001PW (SPDIF→I2S) + CS8421 (ASRC/sample-rate). Two 2.0mm 10-pin headers. **ASRC needed to mix SPDIF with USB**                                                                  | tinysineaudio.com/products/toslinkbee-spdif-to-i2s-digital-audio-receiver-module | #197, #211, #449, #469                                |
| **DIR9001 Fiber/Coax→I2S receiver module** | SPDIF→I2S                                   | Lets any I2S DAC accept coax/optical SPDIF                                                                                                                                          | AliExpress                                                                       | #290                                                  |
| **Wondom AA-AB41133 (WM8804)**             | SPDIF↔I2S transceiver                      | WM8804-based                                                                                                                                                                        | store.sure-electronics.com/product/744                                           | #469                                                  |
| **Audiophonics DAC MS8413 SPDIF**          | Small SPDIF DAC                             | MS8413, 24/192 coax+optical                                                                                                                                                         | audiophonics.fr                                                                  | #312                                                  |
| **TTL TOSLINK RX modules (generic)**       | Optical→TTL into GPIO11                     | Need 3.3V-compatible unit; 100nF decouple close to VCC/GND, opt 4.7–10µF bulk. Direct to GPIO — no extra chip                                                                       | AliExpress (very cheap)                                                          | #1067, #1131, #1283, #1690                            |
| **Schmitt-trigger / inverter for coax-in** | Coax SPDIF→TTL                              | **SN74LVC2GU04DBVT** (TI, Mouser) preferred for spec compliance at 3.3V; SN74HC14N / hex inverter usable but marginal. AC-couple, 0.2–0.6Vpp                                        | Mouser                                                                           | #1624, #1631, #1637                                   |
| **pico_spdif_rx (RP2040 SPDIF RX)**        | SPDIF input reference                       | GitHub project, minimal parts; schematic shared                                                                                                                                     | github (pico_spdif_rx)                                                           | #209, #210, #462                                      |
| **miniDSP PocketADC**                      | USB/analog→SPDIF ADC                        | Known-good ADC once SPDIF-in works                                                                                                                                                  | miniDSP                                                                          | #1040, #1041, #1054                                   |
| **HiFiMeDIY UR23 DDC**                     | Analog-chain DDC (→SPDIF)                   | Used ×3 in john61ct's multi-unit analog chain                                                                                                                                       | HiFiMeDIY                                                                        | #1054                                                 |
| **Cubilux HLMS-C5**                        | USB-C line-in ADC                           | 6.35mm in, 48kHz/16-24b, driverless (likely UAC1)                                                                                                                                   | ~$26                                                                             | #1035                                                 |
| **SRC boards (generic)**                   | Async sample-rate conv                      | <$7 slave-mode SRCs; also HDMI-to-I2S boards for multichannel                                                                                                                       | AliExpress                                                                       | #365, #236                                            |
| **AES/EBU adapters**                       | SPDIF↔AES/EBU                              | Passive: **Neutrik NADITBNC-M**, **Canare BCJ-XJ-TRC**; or set channel-status bit + pulse transformer. Modules: Audiophonics DigiPi AES, Amanero WM8805, LHY Audio (32/384, DSD256) | Neutrik/Canare/etc                                                               | #1875, #1926, #2052, #1723                            |

### E. Pico boards / breakouts / isolation

- **Official Pico 2 / Pico 2 W (RP2350)** recommended over clones — A2 stepping clones have GPIO
  input-leakage issues that bite complex I/O (encoder+RF+SPDIF+DAC+mute). Pico 2 W ~$18; Pico 2
  ~$7–12. (#67, #121, #693, #1337 Pimoroni PicoPlus2 RP2350A2, #2608715)
- **TEENSTAR 2350** clone works with **ADUM3160 USB isolation** to kill PC-borne CPU noise
  (#2608711).
- **Freenove breakout ($12)**, generic Pico breakout (yellow-LED GPIO indicators), **Raspberry Pi
  Zero W2** as a powered USB host/hub front-end (#693, #434, #2606032).
- Note: high overclock can warrant a small heatsink on the RP chip (#2555296, Sergionn).

### F. Alternative MCU port (context, not Pico)

- WeebLabs ported DSPi to **STM32H723** (WeAct / AliExpress ~$30 module; also WeAct STM32H7R3Z8J6,
  600MHz) — hardware SPDIF RX, double-precision FPU, ~5× the RP2350 DSP headroom, AES67 networking
  potential. Z/V pin variants code-compatible; many H7xx variants supported. (#1572–1596)

### I/O open questions

- Group-buy / for-sale bare PCBs (markz TAD5242 gerbers, BossBunos "4×PCM + TOSLINK + ADC" board)
  requested but **not resolved** in-thread (#2630254, #2630384, #1751).
- TOTX/TORX179 EOL sourcing remains a pain point; community steering toward FCR684214 / generic
  AliExpress TTL modules.
- I2S **slave** mode (external clock master) was "coming soon" at end of crawl — DACs needing to be
  clock master not yet plug-and-play (#1863, #1866).

---

## GENERAL INDEX (navigation map)

Firmware / milestones

- OP + intro, €5 Pico, USB in + SPDIF out + PDM sub — #1 (p1, Feb 5 2026)
- Multi-SPDIF (pico_audio_spdif_multi fork), up to 8 digital out ch — #127 (p7)
- v1.0.6 crossfeed; v1.0.8 Matrix Mixer up to 8ch (2×SPDIF+PDM/50 PEQ or 8×SPDIF/100 PEQ) — #123,
  #219 (p6, p11)
- v1.1.0 SPDIF pins → GPIO 6–9; RP2040 & RP2350 both production — #486, p18
- I2S output arrives officially (v1.1.3-beta, MCK 128×/256×, assignable slots) — #994, #1108, #1111
  (p50, p56)
- SPDIF input experimental → v1.1.4-beta1 (TinyUSB/UAC1, WinUSB fix ends Zadig) — #607, #2582 (p31,
  p74)
- I2S input + multichannel (2/4/6/8ch), PCM1808 ADC, control surfaces (encoders/pots/LEDs), external
  mute control — #1469, #1604, #1719, #1792, #1828, #1863 (p74, p78, p85, p88, p92, p94)
- STM32H723 port branch — #1572 (p79)

Measurements / electrical

- SPDIF jitter 250–300ps (APx555) — #567 (p29)
- PDM sub sync <2ms, <1° at 80Hz — #206 (p10); PDM RC = 3.3kΩ+47nF, add 10µF DC-block series
  (#258/#259, p13)
- Cheap optical DAC cap mods (47µF→electrolytic, 22nF→C0G) = 20–30dB distortion drop — #2624916
  (p90)
- PCM5102A purple-board measurement graph posted by WeebLabs — #1700 (p85)

Power / clocking

- USB-powered; VSYS preferred over VBUS (extra protection); iPad may need charger; ~50mA typical —
  #338, #523, #1103, #1698
- Master clock jitter, integer PIO dividers, single input clock + ASRC to mix sources — #211, #1268,
  p6/p61

Notable build write-ups (start here for end-to-end)

- **longts + "Claude" full beginner build guide** — parts BOM (~$25–30), S/PDIF + I2S wiring,
  crossover (LR24 @80Hz), EMC mute, sub delay math — **#1697 (p85)** ← most complete single post
- TheMusicListener no-solder ~$63 BOM — #693 (p35); Rocky Maine validated w/ Amazon links —
  #695/#1025 (p35, p52)
- Kingsnake 4×PCM5102 multi-DAC + encoder + RF remote in Alibaba box — #1661/#1663 (p84); integrated
  TPA3255 amp build — #1314/#840 (p66/p42)
- markz DAC shootout (purple PCM5102 vs Adafruit PCM5122 vs custom, QA403) — #1774 (p90); TAD5242
  6ch balanced board — #2629671 (p91)

Known issues / gotchas

- Windows: pre-v1.1.4 needed Zadig (WinUSB) for control interface; later fixed — #138/#514/#2582
- PCM5102 boards ship muted → tie XSMT/XMT high; silkscreen labels often reversed —
  #1390/#1304/#2470
- Coax-out dropouts on some builds / Windows momentarily losing device on coax — #1406/#2062
- RP2040 SPDIF-in had 12dB input-scaling bug — #1642; 96kHz SPDIF-in flaky (dropouts) — #1657
- Clone RP2350 A2 GPIO leakage → use genuine Pico 2 for complex I/O — #2608715

---

## Purchase & source links

Direct links for the cases and I/O boards above (generic AliExpress/Temu parts have no stable URL —
search by the name/part number given in the tables).

### Primary

- ASR thread:
  [audiosciencereview.com/…/dspi…69343](https://www.audiosciencereview.com/forum/index.php?threads/introducing-dspi-a-powerful-user-friendly-and-open-source-dsp-for-less-than-a-cup-of-coffee.69343/)
- Firmware: [WeebLabs/DSPi](https://github.com/WeebLabs/DSPi) ·
  [DSPi-Console](https://github.com/WeebLabs/DSPi-Console) ·
  [Discord](https://discord.gg/RCyqxAQ5xS)

### Cases

- 7×4×3" project case (Rocky Maine no-solder build):
  [amzn B0FHVBWY21](https://www.amazon.com/dp/B0FHVBWY21) — breakout
  [B0BFB53Y2N](https://www.amazon.com/dp/B0BFB53Y2N), SPDIF card
  [B0B2QQWG38](https://www.amazon.com/dp/B0B2QQWG38)
- Custom CNC aluminium: [JLCPCB](https://jlcpcb.com/) / [JLCFA CNC](https://ke.jlcfa.com/)

### I/O boards — I2S DACs

- [Adafruit I2S Stereo DAC (PCM5102A)](https://www.adafruit.com/product/3678) ·
  [PCM5122 variant](https://www.adafruit.com/product/5764)
- [Waveshare Pico-Audio](https://www.waveshare.com/pico-audio.htm)
- [Pimoroni Pico Audio Pack](https://shop.pimoroni.com/products/pico-audio-pack)
- [Khadas Tone2](https://www.khadas.com/tone2) · [Tone2 Pro](https://www.khadas.com/tone2-pro)
- [Innomaker](https://www.inno-maker.com/) (PCM5122 board) ·
  [Audiophonics](https://www.audiophonics.fr/) (EVO Sabre, TOSLINK sockets, MS8413 DAC)

### Community PCBs

- [Darren-project SPDIF PCB](https://github.com/Darren-project/custom_weeb_lab_SDPi_PCB)

### SPDIF / TOSLINK / input

- [TinySine TOSLINKBee (SPDIF→I2S + ASRC)](https://tinysineaudio.com/products/toslinkbee-spdif-to-i2s-digital-audio-receiver-module)
- [Wondom AA-AB41133 (WM8804 transceiver)](https://store.sure-electronics.com/product/744)
- FCR684214T/R TOSLINK sockets: [TME](https://www.tme.eu/) — search `FCR684214`
- SN74LVC2GU04 coax-in Schmitt: [Mouser](https://www.mouser.com/) — search `SN74LVC2GU04`
- Cliff CN23454 (TX) / CN23453 (RX): [Newark/CPC-Farnell](https://www.newark.com/) — search
  `CN23454`

### Pico boards

- [Raspberry Pi Pico 2 / Pico 2 W (RP2350)](https://www.raspberrypi.com/products/raspberry-pi-pico-2/)
  — genuine recommended over clones for complex I/O
