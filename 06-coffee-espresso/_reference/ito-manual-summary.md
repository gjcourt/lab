# ito Hardware Reference Manual — Executive Summary

**Source:** `/Volumes/family/projects/electronics/espresso/ito-dvd/Manual/Manual.pdf`
**Publisher:** Software & Circuits — Dietmar Eilert Systemsoftware, Aachen, Germany (<www.softwareandcircuits.com>)
**Document:** "ito — Hardware Reference Manual," last revised 25 Sep 2024, 75 pages, © 2016 Dietmar Eilert.

> **Important scope note (read first).** This PDF is the *generic hardware reference manual* for the ito board. It is **not** the espresso-specific ("leva!" / "caffè!") firmware/integration guide. It repeatedly says: "This is a generalized installation guide. Please refer to the specific installation guide that came with your firmware…" (p.10). The board is presented as a general-purpose IoT controller; espresso use (PID, shot profiling, pre-infusion, brew control, MQTT/HASS) is a *firmware* concern layered on this hardware and is **not** documented here. The firmware examples in this manual are generic demos (buzzer, UART, encoder, relays, zero-cross, flowmeter, LED, EEPROM, OLED, ADC, TSic) — building blocks, not the espresso application. If you need the espresso PID/profiling/pre-infusion/flow-control specifics, that lives in a separate firmware manual, not this file. Everything below faithfully summarizes what this hardware manual actually contains.

---

## 1. What the ito Is (Concept, p.2)

The ito is a "Pi A+"–sized (65 × 56 mm) IoT controller module built around **two microcontrollers**:

- **ESP8266** (Xtensa LX106, 80–160 MHz, 32-bit) — primarily WLAN (2.4 GHz 802.11 b/g/n, 54 Mbps). Runs factory "ito ESP firmware" based on **esp-link** by Thorsten von Eicken. 4 MB flash (3 MB available for user data / 1 MB for ESP firmware).
- **Atmel AVR ATMega1284** (18 MHz, 8-bit) — runs *your* custom firmware; handles sensors, relays, display. 128 KB flash (124 KB usable; 4 KB is bootloader), 16 KB RAM, 4 KB EEPROM for user data.

The two chips are joined by an **on-board 115200-baud serial bridge**: ESP `uart0` ↔ ATMega `usart0`. The ESP acts like a transparent "cable" between your PC/WLAN and the ATMega, and simultaneously serves a web UI to configure WLAN. **Both chips can be flashed wirelessly.** Note: a specific ATMega firmware may require a specific ESP firmware and vice versa. The ATMega ships **unprogrammed**; an Eclipse-based C SDK and C source examples are on the ito DVD.

### Feature list (p.2)

- WLAN 2.4 GHz b/g/n, 54 Mbps
- Two on-board 1 A solid-state relays for motors/pumps/valves — up to 240 W (8 A surge)
- SSR connector with hardware PWM for two **external** solid-state relays
- SPI bus + ENC connector for OLED displays with rotary encoder
- PWM output for two LEDs, individually dimmable (hardware PWM)
- ADC connector: two 0–5 V / 10-bit analog inputs (e.g. pressure sensors, potentiometers)
- AUX connector: two digital sensors (e.g. TSic306 temperature, switches/contacts, capacitive water-level sensors)
- IMPULSE connector: pulse sensor, e.g. flow meter
- SPI connector with reset line for displays and ISP programmers
- I²C/SPI expansion interface, 4 digital I/O for micro expansion cards (**PCB rev 2.0+ only**)
- SNS input to detect AC zero-crossings for phase-angle control (power control / "dimming")
- Two programmable on-board LEDs; buzzer for feedback
- 4 KB EEPROM (ATMega) for user data; 128 KB flash for user programs
- Optional on-board 100–240 V~ power supply

### Software shipped (p.2, p.5)

- **Status Monitor** app (Windows / Linux / Mac OS X / Android) to visualize module output
- **Virtual Display** to use a wirelessly connected PC/Android device as a display
- Free/open-source SDKs: Eclipse C environment for both chips, WinAVR for ATMega, esp-open-sdk for ESP; ATMega firmware examples with C source

---

## 2. Safety & Compliance (p.3–4)

- **Only a qualified electrician may connect ito to dangerous voltages (anything above 30 V).** Installation risk lies with the installer/user. This warning recurs throughout (p.3, p.8, p.10, p.12).
- Must be installed in a **grounded enclosure** if conductive and if life-threatening voltages are connected. Not for bathrooms/wet locations; dry home/office only; keep away from flammable materials.
- Insulation of all leads must be rated for ambient temperature; the kit's silicone/PTFE leads are rated **180 °C**. Silicone insulation is soft — do not over-tighten cable ties (fire hazard).
- **Do not pull FASTON plugs by the lead** — pull the plug. Do not overload relays/leads beyond current limits (p.70). HLK-PM01 PSU max **60 °C** ambient.
- No power switch is furnished — install one per local code. Disconnect power before changing sensors/cables/maintenance.
- **Compliance:** ito is a *component*, not a consumer end-product; installer must bring the end application into compliance (EU/VDE norms; EN 300 328; EN 301 489). Radio module (ESP-WROOM-02) complies with RED 2014/53/EU; EMC 2014/30/EU compliance depends on installation. Switching PSUs may need a line filter (Schurter) and ferrite rings. **Disposal:** not household waste (WEEE).

---

## 3. Components / Kit Contents (p.5–6)

Notable items: (1) ito module with adhesive PCB supports + acrylic insulation shield (60 °C max); (2) all-voltage PSU 100–240 VAC → **5 V / 600 mA / 3 W** (HLK-PM01, 60 °C max); (3) 128×64 OLED module (70 °C max); (4) 20 A "hockey-puck" SSR (XURUI DA2420); (5) DVD/USB with docs + software; (6) Digmesa flow meter (Ø5×Ø8 mm tube, 65 °C); (7) calibrated digital **TSic** temperature sensor (−50…150 °C) with 2-component glue kit; (8) pressure sensor 0–200 psi/13.8 bar or 0–300 psi/20.1 bar, ±1% FS, 1/8" NPT; (9) fluid kit; (10) capacitive water-level cable (Saeco P14701A1 sensor not included); (11) FASTON cable kit; (12) OLED SPI cable; (14) LED lamp housing; (16) OLED mounting hardware (4× M3×16 DIN912, washers, 12× M3 nuts); (17) **USB-to-Serial cable** for the AUX header.

---

## 4. Board Layout / Connectors

### PCB 2.0 top side (p.7)

Numbered map:

1. **SPI** — header for OLED display and ISP programmers
2. **AUX** — 2 digital sensors (e.g. TSic) or contacts
3. **PWM** — 2 LEDs, dimmable (40 mA max each)
4. **SSR** — 2 external solid-state relays (5 V)
5. **ENC** — rotary encoder or push-buttons
6. **IMPULSE** — pulse-generating sensors (e.g. flow meter)
7. **ADC** — 2 analog inputs (5 V / 10-bit)
8. LED2 — ESP8266 LED (red; function firmware-dependent)
9. Buzzer (SG1)
10. On-board 100–240 V~ PSU (optional)
11. LED1 — ATMega LED (green; firmware-dependent)
12. **FUSE** — 2 A slow-blow for L phase
13. On-board solid-state relays K1/K2 (75–240 V~ / 1 A)
14. ESP8266 WLAN MCU (WIFI, PCB antenna)
15. **SNS** input / zero-cross detection
16. **N / L** power clamps
17. **Relay outputs 1 and 2**
18. Expansion port (PCB rev 2.0+ only)

### PCB 2.0 bottom side (p.9)

1. ATMega1284 MCU (IC3); 2. High-voltage area (insulation shield required); 3. Pull-up resistor R6 + filter cap C8 for flow meters. **Note:** a 4K7 0603 resistor must be installed on **R6** if a flow meter without integrated pull-up is used; cap **C8 (100N/16V)** must be replaced with **10N/16V** for a Digmesa **nano** flow meter (see p.64).

### Mains clamps: SNS N L 1 2 (p.8)

- **SNS** — AC optocoupler input, senses 32–240 VAC. Detects presence of L phase, reads a switch state, and/or detects **zero-crossings** of the AC sine — the basis for **phase-angle control ("dimming")** of relays 1 & 2. (On resistive loads, add a choke for interference suppression.)
- **N, L** — power the board (100–240 VAC / 5 VDC / ≥0.6 A via the on-board PSU module). N and L are arbitrary names, **but** on-board relays 1 & 2 always output the **L** phase, and SNS only detects the L phase. So the circuit into which ito is integrated may demand a specific N/L order.
- **1, 2** — outputs of the two on-board 1 A SSRs. "Instant-on" type → support phase-angle dimming up to 240 V/1 A (only if SNS is connected to L).
- **WARNING:** wiring order matters so that outputting phase L at relay clamps 1/2 does not create a short somewhere in the circuit.

---

## 5. Physical Installation (Quick Start, p.10–20)

**Sensitive components are on the bottom of the PCB** — work on an anti-static surface. Board is not to be mounted with metal screws (insulation distance too small) — use the four supplied adhesive PCB supports (all four required; p.13). Attach the acrylic insulation shield below the board first. Weighs 48.9 g with HLK-PM01.

**Power:** solder the HLK-PM01 (5 V/600 mA) for on-board mains PSU, **or** wire an external 5 V / ≥600 mA supply to the ⊕/⊖ pads. Trim PSU pins; avoid cold joints and solder bridges (the manual warns a +5 V–to–via short is a classic mistake, p.10).

**Integration sequence (p.11–12):** mount board → optionally connect OLED to SPI+ENC headers → optionally connect rotary encoder to ENC (used as UP/DOWN input and to start firmware updates) → connect N/L to power leads (disconnected from mains!) → use an overvoltage-protected outlet strip/surge protector → close & ground the (conductive) enclosure → power up → **flash an ATMega firmware** (p.31; DVD examples e.g. `00-buzzer\Release\00-buzzer.hex`) → power down → connect the sensors/relays that the flashed firmware expects.

Repeated cautions: never attach/detach cables while powered; double-check every connection (wrong header/orientation can damage the board); relays output the L phase — load must be ≤ 240 W (1 A), never wired directly to N (destructive short); only connect devices the installed firmware supports (firmware programs each I/O pin as input or output — mismatch can damage hardware).

**Sensor/display mounting details:**

- **TSic temperature sensor (p.14):** glued with MG Chemicals 8329TCM 2-component heat-conductive adhesive (−40…+150 °C), mixed 1:1 (≤10% error), 45-min pot life; clean both surfaces with isopropyl; cure 24 h at room temp or 1 h at ≥65 °C.
- **OLED display mounting (p.15–19):** four methods — (A) behind a laser-cut steel panel with M3×16 screws + epoxy (cut-outs: 0.96" type "H" = 25×14 mm; 1.54" type "HXL" = 39×20 mm); (B) behind a milled 3 mm aluminum bezel with screws (fits DIN controller holes 47×25 to 60×25 mm; 25×47 mm cut-out); (C) behind a 3D-printed bezel ("Narrow" 53 mm / "Wide" 70 mm; STL via sculpteo); (D) behind foil for type "G" displays. Insert 3 mm clear acrylic window; don't scratch PCB with tools.
- **Display problems (p.20):** SPI over >40 cm is noise-sensitive — don't route display leads parallel to mains/noisy lines, **do NOT bundle display leads with a cable tie** (fan them out or twist), or change the SPI transfer rate in firmware. Protect the fragile chip-on-glass OLED from shock (15 cm drop can crack traces); keep ≤70 °C; avoid high-contrast settings (load-pump current draw); a 230 V neon lamp on the SNS input can inject voltage spikes — remove it.

**External SSR ("hockey puck," p.21–22):** control higher currents (e.g. 20 A). Mount on a heatsink (supplied SSR rated 20 A at 20 °C on heatsink, far less at 70 °C without). Wire the relay **input side** to ito's SSR header: **Pin 1 = GND (−), Pin 2 = +5 V for external relay 1, Pin 3 = +5 V for external relay 2, Pin 4 = VCC (not needed for relays)**. Use the ferrule-terminated kit leads — bare/tinned ends not permitted at screw terminals. AC SSR can't switch DC loads; install a fuse; keep low-voltage and 100–240 VAC leads in separate cable-tie groups (safety + EMI).

---

## 6. WLAN / Networking (p.23–30)

The ESP8266 firmware (esp-link based) runs a **web configuration server** and bridges traffic between your PC and the ATMega over **TCP port 23** (acts as a virtual serial cable; up to **4 simultaneous connections**, **5-minute inactivity timeout**). **Port 2323** is a special port for firmware updates and should be blocked at your router firewall if ito is exposed to the internet.

Desktops without WLAN need a USB WLAN dongle (tested: TP-LINK TL-WN722N v1.10).

### Three WLAN modes (p.24)

- **AP (Access Point) — factory default.** ito creates its own network **SSID "ito Module"**, password **`jukGT54tz9`** (WPA/WPA2-PSK). Web UI at **<http://192.168.4.1>**. No internet in this mode. **Change the default AP password ASAP.**
- **STA (Station).** ito joins your 2.4 GHz router (cannot use 5 GHz), gets an IP via DHCP, becomes a normal network device. Recommended for normal use. Configure a **static DHCP lease** so you can bookmark its IP. If configured for STA but the router is offline, ito boots to STA+AP, then switches to STA within seconds once connected.
- **STA+AP (Mixed) — temporary only.** ito runs its own AP *and* scans/joins your router; auto-switches to STA on success. Slow/unreliable (single RF channel is multiplexed) — use only briefly during initial setup, never permanently. To go from AP → STA you first switch to STA+AP on the "WLAN station" page, pick your network, enter its password; ito switches to STA automatically (192.168.4.1 becomes unresponsive; find the router-assigned IP).

### WLAN LED blink patterns (red LED, p.25)

- Short flash every **2 s** → not connected, running as **AP** (factory).
- Short flash every **1 s** → not connected, running as **STA+AP**.
- Even on/off every 1 s → connected as STA, **no IP yet** (waiting for DHCP).
- Steady on with short off every 3 s → STA connected, IP received; **ito shuts down its AP 60 s after connecting**.
- Irregular → problem (possible boot loop / corrupted ESP config).

### WLAN factory / configuration reset (p.28)

Power off → **press and hold the encoder** → power on → ito beeps, then beeps faster, then stops beeping → **release the encoder**. This sends a 5 s signal to the ESP; it restarts in **AP mode** with SSID **ito Module**, password **`jukGT54tz9`**, IP **192.168.4.1**. (With a two-button "G" display, the right button ▲ = encoder button.) You must then reconnect your PC and, on Windows, choose "Forget" on the old network before re-entering the new password (devices cache WLAN passwords).

### WLAN troubleshooting highlights (p.28–30)

- ito won't reconnect after power-cycle (stays STA+AP, "forgets" router password) → assign ito a static IP in your router instead of relying on DHCP; the ESP8266 DHCP client is known to be incompatible with some routers' DHCP servers. Optionally change the ito hostname to trigger a DHCP reset.
- Windows won't auto-connect to ito's AP → force with `netsh wlan connect name="ito Module"` (can be run at boot via Task Scheduler; "Do not save password").
- Can't reach 192.168.4.1 → if in STA mode the IP is router-assigned, not 192.168.4.1.
- STA+AP web UI slow/incomplete → normal (single RF transmitter multiplexes AP+STA / channel hopping); avoid reloading pages in STA+AP.
- "ito Module" network not found → it's only created in AP or STA+AP mode, never in pure STA; a WLAN config reset (p.28) is the fastest way back to AP.
- ito is 2.4 GHz only (802.11 b/g/n) — will not connect to 5 GHz-only (802.11ac) routers.
- Irregular LED flash = possible boot loop / corrupted ESP config → WLAN config reset; in very rare cases re-flash the ESP8266 configuration (p.40, needs a special USB-serial cable).

---

## 7. Firmware & Flashing (p.31–42)

**Top warning (p.31):** Flashing incompatible firmware can **damage the hardware** — some ATMega pins are hard-wired to on-board components (pin map p.58); driving a pin against another output can destroy the board.

Both MCUs are flashed by **bootloaders** (small programs in protected flash) over WLAN, USB cable, or ISP. Most users only ever flash the **ATMega** custom firmware and keep the factory ESP firmware.

- **ATMega firmware files end in `.hex`; ESP firmware files end in `.bin`.**

### 7a. Flashing ATMega1284 over the air / WLAN (Windows & Linux, p.32)

- Establish WLAN; **ito must be in AP or STA mode, NOT STA+AP** (its network scans interfere with flashing). End all software talking to the module (esp. the Status Monitor).
- Use **TeraTerm** (from DVD; Linux via Wine). Serial-terminal settings: New-Line Receive/Send = **CR+LF**, Local echo = **checked**.
- New connection: Host = ito's IP **without http://** (192.168.4.1 in AP mode), TCP/IP, **port 2323**, IPv4, Service = **Other** (not Telnet).
- Port 2323 auto-resets the ATMega and starts its bootloader: press **RETURN** to jump in. Bootloader menu:
  `(q)uit (c)lear (f)lash (e)eprom (r)eset (p)ass-through (b)ootloader (s)ignal`
- Press **`f`** + RETURN → erases ATMega & enters flash mode → `Waiting for XMODEM-CRC transfer... CCCC…`
- Send the `.hex` via **File → Transfer → Xmodem → Send…**. **You cannot use "File → Send File…"** to flash.
- Exit bootloader: press encoder or enter **`q`**. If a flash fails, just repeat.
- Two alternative entry routes: (1) connect to **port 23** (doesn't auto-start bootloader — start it from the web UI "console" page bootloader button); (2) hold the encoder while power-cycling until ito beeps twice-as-fast (bootloader ready over WLAN), then connect TeraTerm to port 23.

### 7b. Flashing ATMega over the air — Mac OS X (p.33–34)

Same idea using **ZOC terminal** (30-day trial): host = ito IP, port 2323; connection "Telnet"/"Raw socket"; File Transfer = "Xmodem" with "Use CRC (Xmodem-CRC)"; press RETURN → `f` → Upload the `.hex` → `q` to exit.

### 7c. ATMega bootloader commands explained (p.35)

- **q** — quit (= encoder press).
- **c** — clear: erases ATMega flash + EEPROM → restores as-shipped state.
- **f** — flash: erases flash, enters XMODEM-CRC flash mode (up to 4 KB firmware in hex within 60 s of `CCCC`).
- **e / E** — EEPROM write mode (XMODEM-CRC). Use `E` to clear the EEPROM.
- **r / R** — r restarts the ATMega; R restarts the ESP8266 (interrupts WLAN).
- **p / P** — pass-through: ATMega passes ESP data straight to the AUX serial interface (talk to the ESP as if directly connected). Exit = encoder press; P also resets the ESP.
- **b / B** — ESP8266 bootloader: resets the ESP and raises the ESP bootloader signal so ESP-flashing software at AUX can flash the ESP. B disables on-board LED feedback for slightly higher baud.
- **s** — signal: pulls GPIO0 low for 5 s → ESP firmware interprets as **WLAN factory reset** (resets all WLAN settings; interrupts current connection).

**Supported ATMega hex formats:** standard **Intel 8-bit hex** (from WinAVR/AVR Studio) and ito's **proprietary 8-bit hex** (can also carry EEPROM data). Other formats need conversion (bin2hex utilities on DVD). **Content protection:** flash ROM is protected from ISP read-out; the only way to lift it is a chip-erase via ISP (p.42).

### 7d. Flashing ESP8266 over the air (p.36–37)
>
> Strong warning: the ESP is already flashed at the factory; **do not flash it unless you know what you're doing** — the module may have to be returned to the manufacturer to restore it. OTA ESP upgrades only work if supported by the currently-installed ESP firmware; the ito factory firmware supports them.

- Establish WLAN, **AP or STA mode only** (not STA+AP). ESP upgrades are always two parts, **user1.bin** + **user2.bin**.
- Tool: **avr-link** (Windows/Linux, from `gitlab.com/bc547-playground/avr-link`, also on DVD):
  `avr-link esp flash --esp 192.168.4.1 --user1 "user1.bin" --user2 "user2.bin"`
- Watch for "Rebooting into new firmware" / "Waiting for ESP8266 to come back"; you may need to re-associate the WLAN adapter (or force-forget if the SSID/password changed).
- **Alternative with curl:** identify the target slot with `curl -m 10 -s "http://192.168.4.1/flash/next"` → it prints `user1.bin` or `user2.bin`; upload the matching file with `curl -XPOST --data-binary "@user1.bin" "192.168.4.1/flash/upload"`; reboot with `curl -m 10 -v "http://192.168.4.1/flash/reboot"`.

### 7e. Flashing ATMega over USB (cable) (p.38)

Connect PC to ito's **AUX** connector via a **5 V TTL USB-to-Serial ("FTDI"/"USB Arduino") adapter**. TeraTerm serial settings: **115200 baud, 8N1, no parity, no flow control**, New-Line Rx/Tx = CR+LF, local echo on. **Hold the encoder while powering on** until ito beeps (ATMega in bootloader/cable mode) → release. Bootloader menu appears → `f` → send `.hex` via Xmodem → `q` to exit. (Again: not "Send File.")

### 7f. Flashing ESP8266 over USB (p.39)

Enter the ATMega bootloader over USB (7e), press **`b`** (puts ESP in bootloader + ATMega in pass-through = virtual cable between AUX and ESP). Close the terminal to release the serial port, then run the **Espressif ESP Flash Download Tool** (Windows; Linux users use esptool.py). Settings for the WROOM-02: COM = OS port, CrystalFreq = **26M**, SPI SPEED **80 MHz**, SPI mode **QIO**, BAUD **115200**, Flash Size **32 Mbit**. Flash files/addresses:

- `boot_v1.7.bin` → **0x000000**
- firmware `user1.bin` → **0x01000**
- firmware `user2.bin` → **0x81000**
- `blank.bin` (4 KB) → **0x3FE000** (erases WLAN settings)
- `esp_init_data_default_v08.bin` → **0x3fc000** (system parameters)

Paths must be ASCII-only (no umlauts). When done, press the encoder to exit the ESP bootloader and re-enter the ATMega bootloader; press again to exit. esptool.py one-liner is given for Linux.

### 7g. Re-flashing ESP8266 configuration (recovery) (p.40–41)

For rare troubleshooting (try a WLAN config reset p.28 first). Needs a Windows PC + USB-to-Serial adapter on AUX. Obtain Espressif's SDK: **SDK 1.5.4** if the module shipped with WLAN firmware 1.0 (before Jul/19), or **SDK 2.2.1** for firmware 1.1 (firmware version shown in web UI, e.g. "ito 1.1 – 2019-06-30"). Needed files: `boot_v1.7.bin` (or boot_v1.5.bin for fw 1.0), `esp_init_data_default_v08.bin` (or ..._default.bin), `blank.bin`. Boot into ito's boot menu (hold encoder while powering on), press **`b`** for the ESP bootloader, close the terminal, run the Espressif Download Tool with CrystalFreq 26M / SPI 80 MHz / QIO / 32 Mbit, flash:

- `boot_v1.7.bin` → 0x0
- `esp_init_data_default_v08.bin` → 0xFC000
- `blank.bin` → 0xFE000
- `blank.bin` → 0x7E000
- `blank.bin` → 0x7F000

Then TeraTerm → press encoder to leave ESP boot mode and re-enter ito's boot menu → press **`s`** (5 s signal → ESP sets defaults) → **`q`** to exit. Done.

### 7h. Flashing ATMega with ISP programmer (p.42)
>
> **Not recommended.** ISP programmers **erase the ATMega bootloader**; without it you can no longer flash ito-format hex (only Intel hex), and the original ito bootloader cannot be restored by you (must return to manufacturer, for a fee). ito uses a **non-standard single-row 10-pin "SPI" header** (p.66) instead of the usual 10-pin ISP — you must build an adapter cable (p.68). Program via your IDE's "Program AVR" or AVR Dude. **WARNING:** wrong fuse settings (bad clock source, disabled resets) can render the ATMega useless and require chip replacement.

---

## 8. Developing Software (p.43–47)

- **ATMega1284 (p.43–44):** programmable in C/BASIC/Assembler. Windows path: install **WinAVR** (avoid install paths with parentheses, e.g. not "Program Files (x86)"), Java JRE, Eclipse ("Eclipse IDE for C/C++"), and the **AVR Eclipse Plug-in**. Compile with the hammer toolbar button → output `.hex` in the project's `Release/` directory. 64-bit Windows needs the "WinAVR Fix for Windows (64bit)" (replaces msys-1.0.dll) or compilation fails. AVR Dude can be pointed at your ISP programmer (COM port). ATMega I/O pin wiring is in the appendix p.60/p.58.
- **ESP8266 (p.45):** programmable in C via **esp-open-sdk** (`github.com/pfalcon/esp-open-sdk`; needs GNU/POSIX). No editor bundled — Eclipse CDT recommended; Java required.
- **Floating-point math (p.46):** WinAVR defaults to integer-only printf; to print fractional values add `-Wl,-u,vfprintf` under AVR Linker → Other Arguments and add libraries **`m`** and **`printf_flt`** — otherwise floats show as "?".

### Firmware examples on the DVD (ATMega, p.47)

Each project has `module.c`/`module.h` (init) + `main.c`. Load them by pointing Eclipse workspace at `firmware examples/eclipse/workspace`.

- **00-buzzer** — periodic beep
- **01-uart** — sends "Hello world!" to a terminal over WLAN
- **02-encoder** — reads rotary encoder, prints rotation, beeps on press
- **03-relays** — toggles on-board relays periodically
- **04-zerocross** — uses SNS zero-cross detection (toggles buzzer every 100 zero-crossings ≈ every second at 50 Hz); the basis for phase-angle control / lamp dimming via a random-control SSR
- **05-flowmeter** — IMPULSE header; each Digmesa FHKSC flow-meter pulse → buzzer click
- **06-led** — PWM LED brightness from encoder (0–100%)
- **07-eeprom** — writes/reads "Hello World!" to ATMega EEPROM, reports over WLAN
- **08-oled** — drives a 128×64 SSD1306 OLED on the SPI header (**all following examples require the OLED**)
- **09-adc** — reads a 10K pot on the ADC header, shows slider position on OLED
- **10-tsic** — reads a TSic306 (ZACWire protocol) on AUX, shows temperature on OLED and reports to the Status Monitor

> These are the closest the manual comes to "features" like flow, temperature, zero-cross/power control — they are **demo primitives**, not a finished espresso controller.

---

## 9. Status Monitor & Virtual LCD (p.48–57)

The **Status Monitor** app (Win/Linux/Mac/Android) visualizes ito's output over WLAN as plots, numeric displays, and round gauges, and provides a **Virtual LCD** view. Requires Java 7 (Linux) / Java 8 (Win/Mac). ARM Macs not officially supported (run the `statusmonitor` script). It talks to the ATMega via **port 23**.

**Usage:** connect PC to ito by WLAN; flash a Status-Monitor-enabled firmware (the TSic example qualifies); launch, enter ito's IP; the app auto-loads the matching XML config the firmware names; toolbar plot icon (∕\) toggles plots ↔ Virtual LCD.

**Configuration:** driven by **XML files** in the app's `config/` directory (editable in any text editor). At runtime the Status Monitor sends **`MC?`**; the firmware replies with `XML=<name>` and the app loads `config/<name>.xml`. The manual gives a full example (`temperature.xml`, p.50) and an XML primer (p.51–52).

**Supported XML tags (p.53–56):** `<cfg>` (root), `<palettes>`/`<palette>`/`<pen>` (colors as `argb="#AARRGGBB"`; 23 indexed pens for gradients, text, grid, gauges, etc.), `<body>` (window title + fg/bg pens), `<timescale>` (`ms=` = firmware report speed, required), `<legend>`, `<help>`/`<li>`, `<layout>`/`<scale>` (type = axis/numeric/gauge; up to 1 numeric, 3 gauge, 2 axis scales), `<values>`/`<value>` (parse incoming data: `at=` column, `len=`, `type=int/float/string`, `export=`, `unit=`), `<render>`/`<plot>` (bind a value to a scale; `pen=`, `stroke=`, `style="bar"`, `interpolate=`, `trend=`), `<views>`/`<view>` (zoom levels/time ranges; `cycles=`, `step=`, `unit=ms/s/min/h`; activated by F1/F2…).

**Creating Status-Monitor-compatible firmware (p.57):** firmware must (1) answer `MC?` with `XML=<name>\r\n`; (2) start sending on `MCr`; (3) output at the cycle time in `<body>`; (4) output strings wrapped in `{ … }` terminated by CR+LF, 3rd char `-` (or `*` to mark an event on the timeline); values constant-length, space/zero-padded, matching the `<value>` defs; unknown readings sent as `???`; optional 2-digit hex checksum after `~` (binary complement of the 8-bit sum); resend last packet on `MCR`. For the **Virtual LCD**, on `MC@` send a 69-char display string starting `<` ending `>`: position B = backlight (1/0), position L = pressed button (0 none, 1 up, 2 down, 3 select, 4 cancel), and a layout flag.

---

## 10. Appendix — Pinouts & Reference (p.58–71)

### ATMega1284 pin map (p.58) — *critical for custom firmware*

Legend: red = input, dark blue = output, blue = bidirectional, uncolored = not connected.

**Port A:** A0 = IMPULSE pin2 (pulse input); A1 = ENC pin4 (encoder phase B); A2 = ENC pin3 (encoder phase A); A3 = ENC pin2 (encoder button); A4 = ADC pin3 (analog in 2); A5 = ADC pin2 (analog in 1); A6 = Expansion pin6 (/CS)¹; A7 = Expansion pin7 (MISO).

**Port B:** B0 = Buzzer (high = on); B1 = Jumper J1; B2 = Zero-crossing signal (high = ZC); B3 = SPI pin2 (C/D); B4 = SPI pin3 (/CS); B5 = SPI pin4 (MOSI); B6 = SPI pin5 (MISO or OLED /reset); B7 = SPI pin6 (CLK).

**Port C:** C0 = Expansion pin4 (SCK); C1 = Expansion pin5 (SDA/MOSI); C2 = On-board relay 2 (high = on); C3 = On-board relay 1 (high = on); C4 = green on-board LED (high = on); C5 = ESP8266 reset (low = reset); C6 = bootloader signal **for ATMega** (low = run); C7 = bootloader signal **for ESP8266** (low = run).

**Port D:** D0 = RXD0 (← TXD of ESP8266); D1 = TXD0 (→ RXD of ESP8266); D2 = AUX pin3 (digital in OR RXD1); D3 = AUX pin2 (digital in OR TXD1); D4 = PWM pin2 (LED1); D5 = PWM pin3 (LED2); D6 = SSR pin2 (external relay "SSR 3"); D7 = SSR pin3 (external relay "SSR 4").

¹ Expansion interface is PCB rev 2.0+ only; on rev 1.x, A6, A7, C0, C1 are unused.

### ESP8266 pin map (p.59)

GPIO0 = bootloader signal from ATMega (C7); GPIO4 = red on-board LED (high = on); GPIO12 = bootloader signal for ATMega (C6); GPIO14 = ATMega reset (high = reset); RXD ← TXD0 of ATMega; TXD → RXD0 of ATMega; RST = reset signal from ATMega (C5).

### 7-pin expansion port (p.59, PCB rev 2.0+)

Pad 1 = VCC (+5 V); 2 = GND; 3 = +3.3 V; 4 = SCK (C0); 5 = MOSI/SDA (C1); 6 = /CS (A6); 7 = MISO (A7). Two supply rails + 4 digital I/O usable as hardware I²C or software SPI.

### Header pinouts (p.60–66)

- **ADC:** 1 = GND, 2 = Analog in 1, 3 = Analog in 2, 4 = AVCC (+5 V). Two 10-bit 0–5 V inputs; combined draw from AVCC **≤ 300 mA** (filtering inductance limit). Example: ratiometric 5 V pressure sensor (Honeywell MLH016BGD14A, 1/4", 16 bar) — sensor common→GND, output→analog in, excitation→AVCC.
- **AUX:** 1 = GND, 2 = I/O1 or **TXD1**, 3 = I/O2 or **RXD1**, 4 = VCC (+5 V). Two digital inputs; alternatively a serial interface (TXD/RXD). Compatible: switch, Hall sensor, TSic306WTB temperature sensor, RS232-TTL. **TSic306WTB wiring:** GND→pin3, I/O1→pin2 (output), VCC→pin1 (two sensors can share, with GND on 3A+3B). **RS232/USB:** TXD1(I/O1)→ATMega TXD1, RXD1(I/O2)→ATMega RXD1; connect a PC via a 5 V TTL USB-to-Serial (FT232RL) adapter with **crossed** RX/TX (FTDI RX↔AUX TXD1, FTDI TX↔AUX RXD1, GND↔GND, adapter set to 5 V).
- **ENC:** 1 = GND, 2 = SW (push-button), 3 = A, 4 = B. Rotary encoder (2-bit quadrature) or push-buttons. Example: ALPS STEC12E (24 impulses/rev). Two-button "G" displays: right button ▲ → ENC pin2 (SW), left button ▼ → ENC pin3 (A).
- **IMPULSE:** 1 = GND, 2 = Signal, 3 = VCC (+5 V). Digital pulse input with 100N debounce cap. Flow meter (open-collector, e.g. Digmesa FHKSC). Flow meters usually need a pull-up: install a **4.7 kΩ 0603 on R6** if the meter has none (Digmesa 974-xxxx have internal pull-ups → leave R6 empty; Digmesa 932-xxxx and nano have none). Most meters need the 100N filter cap already on **C8**; **Digmesa nano requires C8 replaced with 10N** (won't work with 100N at higher flow).
- **PWM:** 1 = GND, 2 = LED1, 3 = LED2, 4 = VCC. Two PWM outputs, switched 5 V with 110 Ω series resistors; each output can source or **sink 40 mA** (source/sink choice must match firmware or the LED inverts). LED lamp housing: contact 1 = cathode (−), contact 3 = anode (+, yellow dot).
- **SPI:** 1 = GND, 2 = C/D, 3 = /CS, 4 = MOSI, 5 = MISO, 6 = CLK, 7 = /AVR RESET, 8 = VCC. For displays, ISP programmers, reset switch. **5 V-tolerant 0.96" SSD1306 OLED wiring:** GND→GND, C/D→DC, /CS→CS, MOSI→D1, MISO→RST¹, CLK→D0, VCC→VCC (MISO doubles as the OLED reset line since OLED comm is one-way). Reset switch: pin5 (Reset) + pin6 (GND).
- **SSR (external relays):** 1 = GND (switched), 2 = SSR 3 (+5 V), 3 = SSR 4 (+5 V). Two switched 5 V lines for 3–32 V SSRs (add a snubber/varistor across the load; heatsink usually needed). SHARP S202Sxx relays need a **270 Ω** series resistor to their internal optocoupler LED (GND→relay pin4 cathode via 270 Ω, SSR3→relay pin3 anode). Note: on-board relays are "relay 1 & 2"; external ones are "SSR 3 & 4."

### Creating custom leads (p.68)

All ito headers use **Molex KK 100 series (2.54 mm grid)** plugs (2-contact 22-01-2027, 3-contact -2037, 4-contact -2047, 8-contact -3087, 10-contact -3107; cheaper reichelt "PSS"/"PSK-KONTAKTE"). Crimp (reichelt "CRIMPZANGE PSK") or solder; strip 2–3 mm, insert 4–5 mm, contacts click into the housing and can't be pulled out once seated.

### ESP8266 flash layout (p.69)

16 Mbit (2 MB) or 32 Mbit (4 MB) WROOM-02, two-partition OTA layout: 0x0000 bootloader (4 KB); **Partition 1** user1.bin at 0x1000 (492 K) + user params 0x7C000 (16 KB); reserved 0x80000; **Partition 2** user2.bin at 0x81000 (492 K) + user params 0xFC000; free user data from 0x100000; system parameters in the last 16 KB (0x3FC000 for 32 Mbit). The two partitions hold in-use vs. next firmware, swapped on OTA reboot.

---

## 11. Specifications (p.70)

| Item | Value |
|---|---|
| **Power supply required** | **5 V DC, ≥600 mA** (typical PSU HLK-PM01: 100–240 VAC in, 5 V ±0.1 V / 3 W / 600 mA out) |
| **Power consumption** | 1.1 W typical (with PSU + display) |
| **Dimensions** | 65 × 56 mm ("Pi A+ size"); height 18.5 mm (22.5 mm with BLE) |
| **FASTON leads** | 1 mm², 10 A max (optional 1.5 mm², 15 A) |
| **On-board relays** | 2× OMRON, 75–240 VAC / 1 A (8 A surge), instantaneous-on |
| **External relay** | XURUI XSSR-DA2420, 20 A (with heatsink) / 240 VAC, zero-crossing |
| **SNS input** | 48–240 VAC, typ. 0.5–2.5 mA |
| **ADC header** | 2× 10-bit, 0 to +5 V |
| **PWM (LED)** | 2× 5 V with 110 Ω resistors, 16-bit PWM, 40 mA max per output |
| **Pressure sensor** | ratiometric 0.5–4.5 V, 2× overload, ±1% FS, 1 ms response, 316L stainless |
| **Flow meter** | FHKSC series, 1.2 mm nozzle, 75–570 ml/min |
| **WLAN** | 2.4 GHz 802.11 b/g/n, 54 Mbps, PCB antenna |
| **WLAN SSID / default password** | **ito Module** / **jukGT54tz9** (WPA/WPA2-PSK) |
| **ATMega1284** | 18.432 MHz, 128 KB flash, 16 KB RAM, 4 KB EEPROM |
| **ESP8266** | WROOM-02, 80–160 MHz, 4 MB flash, 160 KB RAM |
| **OLED** | 128×64, 7-pin SPI, SSD1306 / SSD1309 / SH1106 |
| **Buzzer** | 87 dB / ~2700 Hz |
| **Overvoltage protection (PSU)** | 380 V / 1200 W (600 W before rev 1.5) |
| **Creepage/clearance** | 3 mm between mains phases; 8 mm between 5 V and mains (or 5 mm + 2 mm air gap) |
| **Pollution degree** | II (IEC 61010-1) |
| **Humidity** | < 85% non-condensing |
| **Ambient temp ranges** | ito −10…60 °C; OLED −30…70 °C; XURUI relay −25…70 °C; FASTON leads −50…180 °C; cable ties −40…105 °C; TSic −50…150 °C; flow meter −10…65 °C; LED −40…85 °C; pressure transducer −40…120 °C |
| **RoHS** | Yes |

**Current budget (600 mA total):** ESP8266 300 mA (typ. <200); ATMega + 2 LED 50 mA; on-board SSR 1&2 30 mA; OLED 30 mA; buzzer 20 mA; SSR header 40 mA (2×20); PWM header 80 mA (2×40); ADC+AUX sensors 40 mA (4×10); expansion port 10 mA.

**Datasheets (p.71):** ATMega1284, Digmesa FHKSC flow meter, ESP8266, OLED SSD1306, Omron G3MC-201PL (on-board relays), TSic/ZACWire, XURUI DA2420 (external SSR).

**Copyright (p.72–74):** © 2016 Dietmar Eilert; all software/plans/schematics/docs copyrighted, redistribution prohibited. ESP firmware derived from **esp-link** (Thorsten von Eicken, BSD) with esphttpd (Beer-ware), Espressif SDK (MIT), Pure CSS (Yahoo BSD), normalize.css (MIT). TSic/ZACWire are ZMD America trademarks; ATMEL/AVR are Atmel trademarks.

---

## 12. Quick Reference

**Network**

- Default mode: **AP**. SSID **`ito Module`**, password **`jukGT54tz9`** (WPA/WPA2-PSK). Web UI **<http://192.168.4.1>**.
- STA mode → router-assigned DHCP IP (use a static lease). 2.4 GHz only (no 5 GHz/ac).
- **Port 23** = transparent serial bridge to ATMega (Status Monitor; 4 conns; 5-min timeout). **Port 2323** = firmware-update port (auto-starts ATMega bootloader; block at firewall if internet-exposed).

**Resets / recovery**

- **WLAN config reset → factory AP:** power off, hold encoder, power on, wait through beep-faster-then-stop, release. Restores SSID `ito Module` / pw `jukGT54tz9` / 192.168.4.1.
- **ATMega firmware reset:** bootloader `c` (clears flash + EEPROM to as-shipped).
- **ESP recovery:** WLAN config reset first; else re-flash ESP config (p.40, needs USB-serial cable + Espressif Download Tool). Do NOT casually flash the ESP.

**Flashing (ATMega, the common case)**

- Files: **`.hex`** (ATMega), **`.bin`** (ESP). Mode must be **AP or STA, never STA+AP**.
- OTA: TeraTerm/ZOC → ito IP, **port 2323**, RETURN → **`f`** → **Xmodem Send** the `.hex` → **`q`**. Never "Send File."
- USB: FTDI 5 V adapter on **AUX**, **115200 8N1**, hold encoder while powering on → bootloader → `f` → Xmodem → `q`.
- Bootloader menu: `q`uit `c`lear `f`lash `e`eprom `r`eset `p`ass-through `b`ootloader(ESP) `s`ignal(WLAN reset).

**Key header pinouts (2.54 mm Molex KK)**

- **ADC:** 1 GND · 2 AnalogIn1 · 3 AnalogIn2 · 4 AVCC(+5 V, ≤300 mA)
- **AUX:** 1 GND · 2 I/O1/TXD1 · 3 I/O2/RXD1 · 4 VCC(+5 V)
- **ENC:** 1 GND · 2 SW · 3 A · 4 B
- **IMPULSE:** 1 GND · 2 Signal · 3 VCC(+5 V) — R6 4K7 pull-up if meter lacks one; C8 10N for Digmesa nano
- **PWM:** 1 GND · 2 LED1 · 3 LED2 · 4 VCC (40 mA/out; source or sink per firmware)
- **SPI (OLED/ISP):** 1 GND · 2 C/D · 3 /CS · 4 MOSI · 5 MISO(=OLED RST) · 6 CLK · 7 /AVR RESET · 8 VCC
- **SSR (external):** 1 GND(switched) · 2 SSR3(+5 V) · 3 SSR4(+5 V)
- **Expansion (rev 2.0+):** 1 +5 V · 2 GND · 3 +3.3 V · 4 SCK · 5 MOSI/SDA · 6 /CS · 7 MISO
- **Mains clamps:** SNS (zero-cross/L-sense, 32–240 VAC) · N · L · 1 (relay1, L phase) · 2 (relay2, L phase)

**Power:** 5 V DC ≥600 mA (external at ⊕/⊖ pads, or on-board HLK-PM01 from 100–240 VAC). ~1.1 W typical.

**Hard-wired ATMega pins to remember (damage risk):** B0 buzzer, C2/C3 on-board relays 1/2, C4 green LED, C5 ESP reset, D0/D1 ↔ ESP serial, D4/D5 PWM LEDs, D6/D7 external SSR, A0 flow pulse, A1–A3 encoder, A4/A5 ADC, B2 zero-cross.

**Gotchas**

- Only a qualified electrician may connect mains (>30 V).
- Wire loads to relay clamps 1/2 (L phase) at ≤240 W/1 A — never to N (short).
- N/L order can matter because relays/SNS only work with the L phase.
- Never flash in STA+AP mode; never bundle OLED SPI leads with a cable tie; don't over-tighten ties on silicone leads.
- ISP programming erases the bootloader (irreversible by you) — avoid unless necessary.
- Firmware programs each I/O as in/out — mismatched wiring can destroy the board.
