# ito-flash — CLI flasher for the ito ATMega1284 (leva!/caffè!)

`flash_ito.py` flashes leva!/caffè! firmware onto an **ito** board's **ATMega1284** over the air
(WLAN), from macOS/Linux — a scripted, verifiable alternative to the manual's ZOC/TeraTerm route.
Uses the Python [`xmodem`](https://pypi.org/project/xmodem/) library over a raw TCP socket to the
ito bootloader (port **2323**).

Validated 2026-07-13: flashed leva! **3.1** (rotary-encoder build) onto the ito at `10.42.7.11`.

## Why it's safe

- The ATMega bootloader lives in a **protected section**; only the _application_ region is written.
  A failed/garbled/interrupted transfer is **not** fatal — re-enter the bootloader and re-flash (the
  manual says so: _"if a firmware upgrade fails, just repeat"_). You can always re-enter the
  bootloader via port 2323, the web-UI console → bootloader button, or power-cycle-hold-encoder.
- **XMODEM-CRC** checks every 128-byte block → corruption is caught + retransmitted.
- The transport (this tool vs ZOC) does **not** change the real danger, which is flashing
  **incompatible firmware content** — a `.hex` that drives a hard-wired pin the wrong way can damage
  on-board relays/hardware. That's identical for any tool; the `.hex` choice is the actual safety
  gate (see below).

## Which firmware?

leva!/caffè! ships two builds that are **identical except the default input method** (changeable
later in Setup→Input via the Virtual LCD):

- `firmware/1 - ito with rotary encoder/firmware.hex` — **use this** for a rotary encoder, or no
  display.
- `firmware/2 - ito with buttons/firmware.hex` — for a 2-button "type G" display.

⚠️ **`ito-dvd/AFE1624/firmware.hex` is NOT the ito.** It's a ~10 KB image for a separate USB-flashed
ATtiny accessory (flashed with **Micronucleus**, not OTA). Never send it to the ATMega1284.

## Verification-first workflow

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

HEX="…/leva! (for ito)/firmware/1 - ito with rotary encoder/firmware.hex"

# 1. OFFLINE — prove the .hex round-trips byte-for-byte (never touches the board):
.venv/bin/python flash_ito.py loopback --hex "$HEX"

# 2. LIVE, non-destructive — enter the bootloader, read its menu, quit (no erase).
#    Only side effect: briefly resets the running app into the bootloader and back.
.venv/bin/python flash_ito.py check

# 3. Back up settings first (release notes: flashing resets them if firmware < 3.0):
.venv/bin/python flash_ito.py backup --out ~/leva-settings.txt

# 4. The real flash (requires --yes):
.venv/bin/python flash_ito.py flash --hex "$HEX" --yes
```

Default `--host` is `10.42.7.11`, `--port` `2323`.

## Pre-flight

- ito WiFi mode must be **AP or STA** (not STA+AP — its scans corrupt the transfer); check in the
  web UI.
- **Close** the Status Monitor, Virtual LCD, and any HASS/MQTT poll to the board.
- Needs Status Monitor 4+ for the newer firmware.

## After flashing

The new firmware **restarts WiFi**, so the board drops off the network — this is expected. If it
doesn't rejoin within ~90 s, **power-cycle the ito**; it comes back clean. Verify with
`flash_ito.py backup` (or connect to port 23) — you should see `$id: leva! (x.y)`.

## Known limitation

The `backup` mode's `MCu` settings dump is imperfect — port 23 emits the `$id: leva!` banner as a
heartbeat and the current grabber doesn't fully drive the `MCu` capture. Verify settings survived in
the Virtual LCD / Status Monitor instead.

See [`06-001`](../../06-001-lucca-a53-mini-leva-firmware-integration.md) (leva! firmware) and
[`06-015`](../../06-015-gicar-flow-tap-interposer.md) (flow interposer).
