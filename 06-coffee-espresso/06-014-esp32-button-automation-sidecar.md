---
title: 'ESP32 Button-Automation Sidecar (Mini V2 Panel → Home Assistant)'
number: '06-014'
category: 'coffee-espresso'
difficulty: 'Medium'
time_commitment: '1-4 weeks'
target_skills:
  'ESP32 / ESPHome, Optocoupler Interfacing, Button-Matrix Reverse-Engineering, Home Assistant'
status: 'Not Started'
depends_on:
  - hardware/lucca-a53
---

# ESP32 Button-Automation Sidecar (Mini V2 Panel → Home Assistant)

## Description

Turn the Mini V2's front-panel buttons into **programmable, Home-Assistant-controllable** inputs by
paralleling each button contact with an **optocoupler** driven by an **ESP32** (ESPHome). Closing an
opto = a simulated press, so the stock board behaves exactly as if a human pressed the button. This
is a **non-destructive interposition** — you add across the switches, you don't modify the board.
Enables scheduled pre-heat, remote/timed shot start, dosing presets, hot water, and standby from
Home Assistant.

> **This is not needed for shot delivery.** In a full leva! install
> ([06-001](06-001-lucca-a53-mini-leva-firmware-integration.md)) ito already owns the pump **and**
> the 3-way brew valve, so leva! delivers a profiled shot itself. This sidecar targets the buttons
> ito _doesn't_ touch — temp presets, hot water, dosing, standby.

## Relationship to 06-012 (can be superseded by the thermal override)

The sidecar's headline value — **programmable temperature** — is a _workaround_: injecting the
temp-select buttons only cycles the board's **preset** temperature steps, not arbitrary setpoints.
**Successful completion of
[06-012 leva! PID Temperature Takeover](06-012-leva-pid-temperature-takeover.md) gives direct,
continuous, arbitrary temperature control, which supersedes the sidecar's temperature role
entirely.**

So treat them as **alternatives for the temperature goal**:

|               | This sidecar (06-014)                     | Thermal override (06-012)                      |
| ------------- | ----------------------------------------- | ---------------------------------------------- |
| Temp control  | Cycles the board's **presets** only       | **Arbitrary / continuous** setpoints           |
| Risk          | Low (paralleling switches; board unaware) | High (reverse-engineer + intercept the heater) |
| Effort / cost | Medium / ~$20 + optional spare panel      | Hard / Months + spare CPU board                |

**If 06-012 succeeds, this project's temperature role is redundant** — keep the sidecar only for the
_non-temperature_ buttons (hot water, dosing, standby) and Home Assistant integration, if you still
want those. If 06-012 is deferred (its default), the sidecar is the cheap, low-risk way to get
_some_ programmable temperature now.

## How it works

- **One optocoupler across each button's contacts.** ESP32 GPIO → opto LED → opto output across the
  button pads. Use **optocouplers (not bare transistors)** — they isolate the ESP32 from the board's
  logic and don't care about the board's reference or polarity. The board sees a normal press.
- **ESPHome exposes each button** as a momentary switch/entity to Home Assistant. Read-back of the
  human presses is optional (tap the same lines as inputs).
- **Non-conflicting:** you're adding in parallel, so normal front-panel use is unaffected.

## Pre-flight — the one real unknown

**Are the buttons discrete or a scanned matrix?** Probe the button board:

- **Discrete** (each button a direct input to the board) → dead simple: one opto per button, static
  closure = press.
- **Scanned matrix** (rows × columns strobed) → trickier: an opto must close only during that
  button's scan window, or you emulate the matrix. A scope/logic-analyzer on the button lines tells
  you which.

**De-risk on a spare button board** (~$65, La Spaziale touchpanel PN 7390 / SP9807) — bench the
opto-injection there before touching the machine, exactly like the
[06-012](06-012-leva-pid-temperature-takeover.md) spare-board approach.

## Bill of materials

| Item                      | Notes                                                                                   |
| ------------------------- | --------------------------------------------------------------------------------------- |
| ESP32 dev board           | Any ESP32 / ESP32-C3 with enough GPIO (one per button); Wi-Fi + optional BLE            |
| Optocouplers              | One per button (e.g. PC817), or a small opto/SSR relay board; + current-limit resistors |
| Wiring / perfboard / box  | Tap pads on the button board; enclose the sidecar; low-voltage, no mains here           |
| **Optional:** spare panel | La Spaziale touchpanel (~$65) to bench the injection off-machine                        |

## Exit Criteria

- [ ] Each targeted panel function (temp presets, hot water, dosing, standby) is **HA-controllable**
      and physically registers as a press; normal manual use still works.
- [ ] At least one useful automation live (e.g. scheduled pre-heat, or a timed morning shot).

## Progress

- [ ] Probe the button board: discrete vs scanned matrix (scope/logic analyzer)
- [ ] Bench opto-injection on a spare touchpanel
- [ ] Wire optocouplers across each target button on the machine
- [ ] Flash ESPHome; expose each button to Home Assistant
- [ ] Verify every button + confirm no interference with manual use
- [ ] Add automations (pre-heat schedule / remote shot start)

## Related projects

- **[06-001 Pressure & Flow Profiling](06-001-lucca-a53-mini-leva-firmware-integration.md)** — shot
  delivery is already leva!'s job; this sidecar covers the buttons ito doesn't.
- **[06-012 leva! PID Temperature Takeover](06-012-leva-pid-temperature-takeover.md)** — supersedes
  this project's temperature role if completed.

## Sources

- [ESPHome](https://esphome.io/) — the firmware/HA-integration layer.
- Community espresso button-injection mods (Gaggiuino-style opto interposition on the control
  panel).
