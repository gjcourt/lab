---
title: 'ESP32 Resonant Chime-Bar Alarm (Software-Configured Gentle Wake, inspired by the Nanu Arc)'
number: '03-031'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-2 weeks'
target_skills:
  'ESP32/ESPHome, MOSFET low-side driving, inductive-load flyback protection, solenoid actuation,
  Home Assistant automations, small-mechanical mounting / acoustics'
status: 'Not Started'
depends_on:
  - hardware/esp32
  - homelab/home-assistant
---

# ESP32 Resonant Chime-Bar Alarm (Software-Configured Gentle Wake, inspired by the Nanu Arc)

## Description

Re-create the one genuinely great thing about the **Nanu Electrics "Arc" alarm clock** — its
**single tuned aluminum-alloy chime bar** that a hammer strikes to produce a rich, resonant, musical
tone, and whose alarm **gradually intensifies** for a calm start to the day — and throw away
everything else. No dial, no hidden OLED, no cast-zinc body, no buttons. The **chime bar and its
striker** are the only parts that survive; an **ESP32 running ESPHome** strikes the bar, and **Home
Assistant** owns all of the timekeeping the clock used to do internally.

The payoff is a "dumb but beautiful" resonant chime that any HASS automation can ring: a gentle
ramping wake-up alarm, laundry/oven timers, doorbell escalation, a "backup job failed" alert, or a
pomodoro focus bell — with the physical presence and musical tone that a phone speaker or a
smart-speaker chime can never match. The signature feature — the tone gradually intensifying —
becomes a **software-defined ramp** the ESP32 controls, which is the whole "software config replaces
the face" story.

> **Design inspiration / reference:** the **Nanu Arc** (`nanuelectrics.com`) — a chime-bar alarm
> clock (cast-zinc body, mineral-glass face, USB-C + ~16 h battery backup, hidden OLED for setting,
> ~185 × 105 × 85 mm). We **discard** the body, face, OLED, dial, buttons, and internal timekeeping,
> and **keep only** the resonating chime bar + striker mechanism. The Arc's actual actuator is
> undisclosed, so the striker below is a DIY reconstruction; if you salvage an Arc, reuse its chime
> bar and adapt the mount.

## Keep vs. discard

**Keep (the mechanism):**

- The **single tuned aluminum-alloy chime / tone bar** — the sound source (glockenspiel-style: one
  metal bar, struck, ringing with sustain and decay).
- The **hammer / mallet striker** and its mount (or a DIY replacement, below).
- Whatever **rigid mounting** holds the bar at its nodal points so it rings freely.

**Discard (the clock):**

- Cast-zinc body / case, mineral-glass **face**, and the **hidden OLED** display.
- All internal **timekeeping** and the battery-backup clock circuit.
- Any physical setting **buttons** / dial and the mechanical alarm trip.

Timekeeping, alarm scheduling, snooze, and the gentle-ramp wake all move into **software (MQTT /
Home Assistant + ESP32 firmware)** — that is the whole point. The clock's face is replaced by a HASS
automation.

## How a chime-bar alarm makes its sound

Understanding the acoustic element drives both the mount and the striker design:

- A **chime bar** (a.k.a. tone bar / resonator bar) is a length of metal — here **aluminum alloy** —
  tuned to a pitch by its length and thickness. Struck by a hammer, it rings at its fundamental with
  long **sustain and decay**, a pleasant musical tone — the opposite of a harsh twin-bell buzz.
- The bar only rings well if it is supported at its **transverse-vibration nodes**, where the
  fundamental mode has (near-)zero displacement. For a free-free bar those nodes sit at **≈ 0.224 ×
  length from each end** (≈ 22.4%). Clamp or pad the bar there and it sustains; support it anywhere
  else and you damp the fundamental and kill the tone.
- **Timbre** is set by the striker tip: a **hard tip** (nylon/metal) is bright and pingy; a **soft
  tip** (rubber/felt) is warmer and rounder. The Arc reads as warm/resonant, so a soft-ish mallet
  tip is the starting point — tunable to taste.
- The Arc's "gentle wake" is not a louder single tone; it is the **strike pattern intensifying**
  over time — start soft and infrequent, ramp up frequency and force. That is exactly what an ESP32
  is good at.

## Resonating element — the chime bar

- **Bar:** a single **aluminum-alloy bar**. Salvage the Arc's bar, or source one: **aluminum bar
  stock** (e.g. 6061, ~6-10 mm thick × ~20-25 mm wide, cut to length for the pitch you want) or an
  off-the-shelf **glockenspiel / chime bar** already tuned.
- **Mount at the nodes:** support the bar at **≈ 0.224 × L from each end**. Practical options: soft
  grommets / O-rings on posts through holes drilled _at the nodes_, or foam/rubber saddles the bar
  rests in at those points. Suspending the bar on a cord through node holes is the highest-sustain
  option.
- **Free ends:** leave the ends unconstrained; the rim/ends must be free to vibrate.
- **Sound board (optional):** a resonator cavity or a wooden base tuned near the bar's pitch boosts
  perceived volume and warmth (ties nicely to the [woodworking](../02-woodworking/projects.md)
  enclosures).

## Striker / actuator options

The Arc's actuator is undisclosed; for a DIY build there are two realistic paths.

### Option A — solenoid / electromagnet-driven hammer (recommended)

A small **push-type solenoid** (or an electromagnet acting on a sprung hammer) drives a **mallet**
that strikes the bar.

- **Crisp, fast, repeatable strikes:** a solenoid gives a clean transient and can repeat quickly —
  essential for the ramping pattern (soft/slow → hard/fast).
- **Force control via PWM:** PWM the solenoid drive to vary strike **energy** (a short/low-duty
  pulse = soft tap; a full pulse = hard strike). Combined with strike **interval**, this gives full
  control of the gentle-wake ramp.
- **Mallet tip:** fix a **rubber/felt tip** to the solenoid plunger; tip hardness sets timbre. Keep
  a small rest gap so the mallet strikes and rebounds cleanly (no dead contact / buzzing).

### Option B — servo + mallet (lower-cost alternative)

A hobby **servo** swings a mallet arm to strike the bar.

- **Pros:** cheap, no separate high-current driver (servo has its own), easy angle control.
- **Cons:** far **slower** repetition and softer transient than a solenoid; the ramp's high end is
  limited by servo travel speed; more mechanical slop. Fine for a slow "ding … ding …" but it cannot
  do a crisp fast tremolo.

### Recommendation

**Use the solenoid (Option A).** It gives the crisp musical strike, fast repetition for the ramp's
peak, and PWM force control — the combination the gentle-wake feature needs. The servo is a
reasonable first-hour prototype if you have one on hand, but the final build wants the solenoid. The
ESP32-side interface is a single GPIO into a low-side MOSFET either way (servo excepted), so you can
swap without rewiring the logic.

## Gradual-intensity wake — the software centerpiece

This is the Arc's signature behavior and the reason the project exists as a _software_ device. The
ESP32 owns the **strike pattern**, and the ramp is fully parameterized:

- **`ramp_duration`** — how long the crescendo takes (e.g. 90 s).
- **`start_interval` → `end_interval`** — strike spacing at the start (slow, e.g. one strike / 4 s)
  ramping to the end (fast, e.g. 3 strikes / s).
- **`start_force` → `max_force`** — PWM duty on the solenoid, soft → hard.
- **`ramp_curve`** — linear vs. exponential/ease-in, so it stays gentle for longer then rises.
- **`total_duration`** — hard ceiling after which it stops (safety).

Firmware interpolates interval + force along the curve over `ramp_duration`, then holds at max until
`total_duration` or a HASS dismiss. Exposing these as HASS/MQTT parameters is the "software config
that replaces the clock face."

## MCU + firmware/control

This fits squarely in the repo's existing **ESP32 / ESPHome** device family — see
[03-027](03-027-xiao-c3-ir-rf-blaster-carrier-pcb.md) (XIAO ESP32-C3 IR/RF blaster) and
[03-030](03-030-xiao-c3-presence-node-enclosures.md) (XIAO C3 presence enclosures). Use a **Seeed
XIAO ESP32-C3** (tiny, USB-C, Wi-Fi, one PWM output is plenty) or any spare **ESP32 dev board**.

The firmware exposes the ringer to Home Assistant and keeps the ramp logic on-device; HASS decides
_when_ to ring:

- **Ring-now control:** a **`button`** (one-shot strike) and/or a **`switch`** / **`siren`** to
  start the ramping alarm.
- **Ramp parameters:** **`number`** entities for `ramp_duration`, `start_interval`, `end_interval`,
  `max_force`, and `total_duration`; optionally a `select` for curve/pattern (single / double /
  gentle-ramp / tremolo).
- **Transport:** MQTT (native ESPHome-MQTT or the HASS API). An **MQTT trigger** on a topic like
  `home/chime-alarm/ring` lets anything in the homelab ring the bar.
- **Safety in firmware:** hard-cap `total_duration` and enforce a **max solenoid duty cycle**
  on-device so a lost network connection or a runaway automation can never leave the coil energized.

Example ESPHome sketch (illustrative — pins/pattern to taste):

```yaml
# XIAO ESP32-C3 — software-driven resonant chime-bar striker
output:
  - platform: ledc
    id: solenoid_pwm
    pin: GPIO4
    frequency: 1000 Hz

number:
  - platform: template
    name: 'Chime Ramp Duration'
    id: ramp_seconds
    optimistic: true
    min_value: 5
    max_value: 300
    initial_value: 90
    step: 5
  - platform: template
    name: 'Chime Max Force'
    id: max_force
    optimistic: true
    min_value: 20
    max_value: 100 # % PWM duty; firmware-enforced ceiling
    initial_value: 100
    step: 5

# one clean strike = a short, force-scaled pulse then release
script:
  - id: strike
    parameters:
      force: float
    then:
      - output.set_level:
          id: solenoid_pwm
          level: !lambda 'return force / 100.0;'
      - delay: 12ms # pull-in; keep short to protect the coil
      - output.turn_off: solenoid_pwm

button:
  - platform: template
    name: 'Chime Test Strike'
    on_press:
      - script.execute: { id: strike, force: 100 }

# gentle-wake alarm: ramp interval + force over ramp_seconds
siren:
  - platform: template
    name: 'Resonant Chime Alarm'
    turn_on_action:
      - repeat:
          count: 9999
          then:
            - script.execute:
                id: strike
                force: !lambda 'return id(max_force).state;' # replace w/ ramped value
            - delay: 1s # replace w/ ramped interval
    turn_off_action:
      - output.turn_off: solenoid_pwm
```

HASS then owns scheduling and snooze — a time-triggered automation calls `siren.turn_on` at the wake
time, an `input_datetime` holds the alarm, and a "snooze" `input_button` re-arms the automation for
+9 minutes. None of that lives on the ESP32.

## Power / driving

The solenoid draws **far more current than an ESP32 GPIO can source** — never drive it from a pin.

- **Separate supply** sized to the solenoid: commonly 5-12 V with an in-rush of an amp or more. Use
  a dedicated 5 V/2 A (or 12 V) brick, **not** the XIAO's 3V3 rail.
- **Common ground** between the ESP32 and the solenoid supply (low-side switching requires it).
- **Low-side N-channel logic-level MOSFET** (AO3400A for small, IRLZ44N / a driver board for
  larger), gate through ~100 Ω with a 10 kΩ pulldown.
- **Flyback (freewheeling) diode across the solenoid — mandatory.** A solenoid is a large inductor;
  on turn-off it kicks a big spike that destroys the MOSFET. Put a **1N4007** (or a Schottky) across
  the coil, cathode to +V. This is the single most important component for MOSFET survival.
- **PWM** the gate to control strike **force**; keep pulse widths short to bound coil heating.
- Optional bulk cap (470-1000 µF) across the solenoid supply to absorb in-rush so Wi-Fi doesn't
  brown out.

## Wiring sketch (ASCII)

```text
                 +V solenoid supply (5-12 V, separate brick)
                        |
                        |----------------+
                        |                |
                    [ SOLENOID ]      --- flyback diode (1N4007 / Schottky)
                    [  (coil)  ]       ^  cathode -> +V
                        |             |   anode   -> MOSFET drain node
                        +-------------+
                        |  (drain)
   ESP32 GPIO4 --[100 Ω]--+---(gate)   N-ch logic-level MOSFET
                          |            (AO3400A / IRLZ44N)
                       [10 kΩ]  (source)
                          |            |
                         GND ==========+========== GND (shared: ESP32 + solenoid supply)
```

## Bill of materials

| Qty | Part                                   | Notes                                                         |
| --- | -------------------------------------- | ------------------------------------------------------------- |
| 1   | Aluminum-alloy chime / tone bar        | Salvaged Arc bar, 6061 bar stock, or a tuned glockenspiel bar |
| 1   | Push-type solenoid _(Option A)_        | Drives the mallet; sized to bar strike (5-12 V)               |
| 1   | Servo + mallet arm _(Option B alt)_    | Lower-cost alternative striker                                |
| 1   | Mallet head + rubber/felt tip          | Fixed to plunger/arm; tip hardness sets timbre                |
| 1   | Seeed XIAO ESP32-C3 (or ESP32)         | ESPHome MCU; USB-C powered                                    |
| 1   | N-channel logic-level MOSFET           | AO3400A (small) or IRLZ44N (larger loads)                     |
| 1   | Flyback diode                          | 1N4007 or a Schottky, across the solenoid coil                |
| 1   | Resistor 100 Ω                         | Gate series resistor                                          |
| 1   | Resistor 10 kΩ                         | Gate pulldown                                                 |
| 1   | Cap 470-1000 µF                        | Bulk across solenoid supply (optional, anti-brownout)         |
| 1   | Solenoid PSU (5 V/2 A or 12 V)         | Separate from the ESP32 rail                                  |
| —   | Node mounts (grommets/O-rings/cord)    | Support the bar at ≈ 0.224 × L from each end                  |
| 1   | Rigid base / sound board               | Holds bar + striker; optional resonator for volume            |
| —   | Wire, JST/screw terminals, heat-shrink | Interconnect                                                  |

## Enclosure / mount notes

The bar only rings with sustain if it is **supported at its nodes and free at the ends**, and the
striker geometry must be repeatable.

- **Mount at the nodes (≈ 0.224 × L from each end):** soft grommets/O-rings on posts, foam saddles,
  or a cord through node holes. Anything touching the bar between the nodes damps it.
- **Set the mallet rest gap** so the strike lands cleanly and rebounds — too close buzzes, too far
  misses or hits soft.
- **Aim the strike near an anti-node** (center or ~free end) for a strong fundamental.
- **Decouple the base** from the surface (rubber feet / mass base) so ringing energy goes into the
  bar, not the desk; optionally couple the bar mount to a **sound board / resonator** to boost
  volume.
- House the ESP32 + MOSFET + diode in a small separate compartment; keep solenoid wiring away from
  the antenna.

## Ring patterns (HASS-defined)

- **Single strike / chime:** one force-scaled pulse — timer/notification "done."
- **Double chime:** two spaced strikes — a softer "attention" ping.
- **Gentle-wake ramp (the Arc signature):** ramp strike interval (slow → fast) and force (soft →
  hard) over `ramp_duration` — the real wake-up alarm.
- **Tremolo / continuous:** fast repeated strikes at max force for urgent alerts.
- **Escalation:** HASS extends the ramp / raises max force if the alarm isn't dismissed within N
  minutes.
- **Snooze:** dismiss stops the strikes; a snooze button re-arms the automation for +9 min. All
  snooze logic lives in Home Assistant, not on the device.

## Safety note

**A resonant metal bar is musical but can get genuinely loud**, and a driven solenoid is a hot
inductive load. Design accordingly:

- **Firmware-enforced maximum ring duration (`total_duration`)** and a **max solenoid duty cycle**
  so no automation (or dropped connection) can leave the coil energized/striking indefinitely —
  coils overheat.
- Keep individual strike pulses **short** (pull-in only, then release) to protect the coil and the
  MOSFET.
- Fail-safe **off** on boot and on Wi-Fi/MQTT loss.
- Mount it where a sudden loud strike won't cause a fall/startle injury; keep the peak volume sane
  at point-blank sleeping range (the ramp helps here — it starts gentle by design).
- Verify the solenoid, MOSFET, and supply stay cool under a worst-case stuck-on test before trusting
  it overnight.

## Exit Criteria

- A tuned aluminum-alloy chime bar is mounted at its nodes (≈ 0.224 × L) and rings with full sustain
  when the striker hits it.
- An ESP32/ESPHome node exposes the striker to Home Assistant (a `siren`, and/or a `button`/`switch`
  plus `number` entities for the ramp parameters) and rings on an **MQTT trigger**.
- A low-side MOSFET driver with a **flyback diode** drives the solenoid from a **separate supply**;
  a worst-case stuck-on test stays within thermal limits and firmware hard-stops at
  `total_duration`.
- The **gentle-wake ramp** works end-to-end: strike interval and PWM strike force ramp soft/slow →
  hard/fast over a configurable duration, driven by a scheduled HASS automation with snooze — all
  scheduling/ramp-trigger logic in Home Assistant, none of the clock face on the device.
- The device fails safe (striker off) on boot and on loss of Wi-Fi/MQTT.

## Status & next steps

- [ ] Source the chime bar (salvage an Arc bar, cut 6061 stock, or buy a tuned bar); find its nodes
      and build a node-supported mount
- [ ] Breadboard the solenoid + low-side MOSFET + flyback + PWM; get one clean, force-controllable
      strike; tune the mallet tip for timbre
- [ ] (Optional) prototype the servo alternative and A/B the transient/repetition speed; confirm the
      solenoid choice
- [ ] Write the ESPHome config: `siren` + `number` ramp params + on-device ramp interpolation +
      safety ceiling; bring up on the XIAO C3
- [ ] MQTT trigger + HASS automations for schedule / snooze / escalation
- [ ] Design and build the node mount + base/resonator; final assembly + stuck-on thermal test
