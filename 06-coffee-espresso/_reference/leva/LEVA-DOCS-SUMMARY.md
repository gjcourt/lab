# `leva!` Documentation — Executive Summary & Index

> Crisp articulation of the two dense manuals: **`Firmware manual.pdf`** (v3.1, 245 pp) and
> **`Hardware installation.pdf`** (71 pp), plus the `readme - important.txt` flashing notes. Written
> to make the pieces and touch-points navigable without re-reading 300 pages.
>
> The PDFs and a full index of the home-barista owner thread (365 posts, verbatim — kept out of this
> public repo) live on the NAS at `/Volumes/family/projects/electronics/espresso/`
> (`leva! (for ito)/` and `home-barista-thread-index/INDEX.md`).

---

## 1. What `leva!` is, in one paragraph

`leva!` is **public-domain firmware** (a relabeled `caffè!`, in the lineage since ~2009) that runs
on the **ito microcontroller module** (softwareandcircuits.com) installed inside a classic one- or
two-boiler espresso machine. It turns that machine into a **state-of-the-art PID temperature
controller** _and_ an **electronic pump / pressure-profiling controller** _and_ a doser/shot-timer —
any subset, independently. It is configured over WiFi from a computer/tablet (the **Virtual
Display** and **Status Monitor** apps), so it can run with no visible display at all.

Two engines that share the box but have **separate requirements** and can be used alone:

| Engine                        | What it does                                                       | Needs                                                  |
| ----------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------ |
| **PID temperature**           | Dual-channel PID on up to 2 boilers (or boiler + heated group)     | Heater in a mains thermostat circuit; TSic sensor; SSR |
| **Pump / pressure profiling** | Phase-angle pump control → follow a programmed pressure/flow curve | Vibratory pump; pressure sensor; ideally a flow meter  |

---

## 2. The pieces (feature map)

**PID temperature control** (FW p.3, p.55–72)

- Dual channel: two boilers, or one boiler + one electronically-heated group.
- **TSic306** digital sensors (lower error than Pt100); up to two at once (e.g. boiler + group).
  Type-K thermocouples via an AFE16/24 module.
- **PID parametrization by machine state** — different tunings for warm-up / idle / shot.
- **Ramp & Soak** — setpoint and heating-power curves (also used to cap output during shots).
- Digital filtering, multiple **anti-windup** strategies, 0.1 °C setpoint steps (0.0625 °C
  internal).
- **ECO mode** + auto standby for energy savings.
- Automatic **sensor-failure and SSR-failure detection**.
- Switches the SSR ~once/second; a **lamp-replacement LED** conveys state instead of flickering.

**Electronic pump control / pressure profiling** (FW p.3, p.99–165 — the heart of this project)

- **Phase-angle control** of a vibratory pump → nearly stepless power (0° = full, ~115° = off).
- **Absolute pressure control** via a ratiometric pressure sensor, closed-loop.
- **Variable preinfusion** + **programmable pressure profiles** (lever-style, declining, etc.).
- **Flow-rate tracking** (needs a Digmesa flow meter) — can end a shot on volume/flow targets.
- **Manual** brew-pressure control via rotary encoder or an analog **paddle**.

**Dosing & programs** (FW p.3, p.52)

- **Dosing** by time, by **volume** (flow meter), or by **weight** (gravimetric, BLE scale).
- Built-in **warm-up-with-flush** (up to −50% warm-up time), **grouphead flush**, **descale**,
  **backflush** programs.

**Measurement & monitoring** (FW p.4)

- **Status Monitor** app (Win/Linux/Mac/Android) — real-time plots of temperature, pressure, flow,
  **and the internal PID components (P/I/D)** and **pump phase-angle** — the tuning instrument.
- **Virtual Display** app — drive the menus over WiFi with no physical screen.
- OLED (4 lines) + rotary encoder or 2-button input. WiFi (ESP8266) + **Bluetooth LE**.
- Soft monitors: energy use, water-filter throughput, estimated scale deposit, shot counter.

---

## 3. Hardware touch-points — the ito connector map

Where the module physically meets the machine (HW p.9–31, p.69–71). This is the wiring "API":

| ito connector                  | Connects to                                                   | Purpose                                                                                                                                                           |
| ------------------------------ | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **N / L**                      | Switched mains supply (only live when machine on)             | Powers the module.                                                                                                                                                |
| **SNS (S)**                    | The pump-side mains phase                                     | **Sense** input: detects "pump on" **and** samples the AC waveform for zero-crossing (phase-angle control needs this). Configurable as the pump-control function. |
| **Relays 1 & 2 (clamps 1, 2)** | Pump + 3-way grouphead solenoid valve                         | On-board relays that switch pump and valve (output the L phase when SNS senses "on").                                                                             |
| **SSR connector (+ / −)**      | Control side of an external **20 A SSR**                      | Drives the SSR that switches the **boiler heating element** (red = +, black = −).                                                                                 |
| **20 A SSR (load side)**       | In place of the **brew thermostat**                           | Thermostat disconnected; the SSR now switches the element. Needs a heatsink.                                                                                      |
| **AUX**                        | **TSic** temperature sensor(s)                                | Boiler (and optionally grouphead) temperature. Can also read the old thermostat's state.                                                                          |
| **ADC header**                 | **Pressure sensor**, paddle, 2nd analog sensor, contact leads | Analog inputs. Pressure transducer wiring set in Setup→Wiring (Umin/Umax, valve pos).                                                                             |
| **PWM**                        | Lamp-replacement / status **LED**                             | State signaling in place of the boiler lamp.                                                                                                                      |
| **Flow-meter input**           | **Digmesa** flow meter (tank→pump line)                       | Volume + flow rate.                                                                                                                                               |
| **Display / encoder**          | OLED + rotary encoder or 2 buttons                            | Local UI (optional).                                                                                                                                              |

**Install = a small number of discrete changes:**

- **PID (4 changes, HW p.12–13):** ① N/L to switched mains; ② move the two **brew-thermostat** leads
  to the SSR load side (thermostat retired); ③ SSR control side → ito **SSR** connector (mind
  polarity); ④ **TSic** sensor → **AUX**.
- **Pump/valve for profiling (HW p.19):** sense the pump phase on **SNS**, route pump + 3-way valve
  through **relays 1 & 2**.
- **Sensors (HW p.36–42, p.57–65):** tap the **pressure sensor** into the brew line (rated 125 °C;
  **mount vibration-free**, not at the pump); **flow meter before the pump** (tank→pump line).

⚠️ **Mains voltage. The manual is blunt: "PULL THE PLUG… CAN KILL YOU."** A licensed electrician is
the right call for the mains-side changes.

---

## 4. How pressure profiling actually works (the model to hold in your head)

`Output [°] = Bias + Proportional + Integral` — a **PI-with-bias** controller whose output is a
**pump phase angle** (FW p.99–104, p.165):

- **Bias** — the approximate phase angle needed for the target pressure, read off your pump's
  **characteristic curve**. You supply that curve as three points in the **Pump menu**: `Press max`
  (pressure at full power), `Press OPV`/`Phase OPV` (where the over-pressure valve opens),
  `Phase off` (angle where the vibe pump stops). A one-time **Pressure Test** (FW p.49, pump against
  a blind filter) fills these automatically.
- **Proportional** = `K [°/bar] × error`. Higher K = harder correction; too high = oscillation.
- **Integral** = accumulates `I [°/cycle] × error` every `Cycle` (e.g. 200 ms), bounded by
  `WU-Limit`.
- Tuned **separately below vs. above 2.5 bar** (the sub-2.5 bar band is the preinfusion range where
  overshoot must be avoided — the pump is simply shut to `Phase off` on overshoot there). Above 2.5
  bar you can even split `K>SP` (overshoot) vs `K<SP` (undershoot).
- **Flow Corr** biases for the fact that the pressure test has no flow; **Heat Corr** compensates
  the voltage sag when the heater fires.

A **pressure profile** (FW p.126–150) = a **preinfusion segment** + a **shot segment**, each a
series of pressure setpoints over time, each independently enabled. Presets exist (e.g. `LEVER`);
`Resize` rescales a whole segment to a new peak; `End` chooses full-power / sustain / stop
afterwards; a profile can even carry its own **PID temperature overrides**.

**Tuning workflow (FW p.105):** set the machine **OPV to 10–12 bar** (blind filter, ≥1.5 bar below
sensor max) → run the **Pressure Test** → tune `K`/`I` per band while watching the **Status Monitor
phase-angle trace** → nudge `Flow Corr` so the bias line tracks pump power early in the shot.
Re-tune ~yearly as pump gaskets age. **Defaults will not work** except by luck.

---

## 5. Configuration model

No code — everything is **menus**, reached by the encoder/buttons or the **Virtual Display** app
over WiFi. The major menu branches (FW p.17+):

- **PID** (per channel): setpoints, Ramp & Soak, control mode, Wiring.
- **Pump**: `Press max / OPV / Phase OPV / Phase off / Flow Corr / Heat Corr`, presets (E5, E5 SOFT,
  CP SMART), the PI control sub-menus (`K`, `I`, `Cycle`, `WU-Limit`) for the two pressure bands,
  and Flow control.
- **Profiles**: edit PI + shot segments, pick presets, resize, End behavior, per-profile PID.
- **Dosing programs**; **Contacts** (SNS + input functions); **Input** (encoder/buttons/paddle);
  **Setup→Wiring** (sensor type, valve position vs sensor, Umin/Umax); **Wifi**.

**Flashing** (`readme - important.txt`): back up settings first (`MCu` dump over TCP port 23), then
XMODEM-CRC the `firmware.hex` over port **2323** (TeraTerm on Windows, **ZOC on macOS**). Install
the matching **Status Monitor XML** afterward. Use `firmware/1 - ito with rotary encoder` unless you
have a 2-button "type G" display. Do **not** reflash the ESP8266 WiFi chip.

---

## 6. What this means for the LUCCA A53 Mini specifically

- **Profiling engine: yes.** Vibe pump ✓ (the Mini; **not** the rotary full-size A53). Sensor T-taps
  into the brew line (light filing), flow meter before the pump.
- **PID engine: no (for now).** leva! PID conflicts with the A53's electronic control board (owner
  report) — run profiling only, leave temperature to the stock board. This is why the A53 uses the
  **SNS-sense** path rather than the documented mechanical-switch PID install.
- **The A53 wrinkle** is its **over-pressure bypass valve** (returns water to pump inlet): set it
  > 9 bar and configure `Press OPV`, or it fights the profile and biases the flow meter.
- Full rationale + BOM + install steps live in `lab` `06-001` (profiling) and `06-012` (the blocked
  PID takeover).

---

## 7. Page index (jump-to)

**Firmware manual (245 pp):**

| Pages   | Section                                                           |
| ------- | ----------------------------------------------------------------- |
| 2       | About leva!                                                       |
| 3–5     | **Features** (best one-page overview)                             |
| 9–10    | User interface                                                    |
| 13–16   | **Quickstart guide**                                              |
| 17–72   | **Menus** (full reference)                                        |
| 49      | Pressure Test (auto-characterize the pump)                        |
| 55–72   | PID / temperature menus, Ramp & Soak                              |
| 84–86   | Setup→Wiring: pressure-sensor type, valve position, Umin/Umax     |
| 99–102  | **Pump menu** (Press max/OPV, Phase off, Flow/Heat Corr, presets) |
| 103–104 | **Pump control algorithm** (`K`, `I`, `Cycle`, `WU-Limit`)        |
| 105–111 | **Tutorial: tuning pressure control** (start here to tune)        |
| 112–124 | Pressure / preinfusion mechanics                                  |
| 125     | Flow control / tracking                                           |
| 126–149 | **Pressure profiles** (edit PI + shot, presets, resize, End)      |
| 150–162 | Pressure-point editors; flow tracking targets                     |
| 163     | Paddle configuration                                              |
| 165+    | Phase-fired controller (phase-angle theory)                       |
| 221–244 | Appendix                                                          |

**Hardware installation (71 pp):**

| Pages   | Section                                                                               |
| ------- | ------------------------------------------------------------------------------------- |
| 2–4     | About                                                                                 |
| **5–8** | **Requirements / compatible machines** (read before buying)                           |
| 9–31    | **Theory** — wiring principles + the touch-points                                     |
| 12–13   | **PID wiring: the 4 required changes**                                                |
| 19      | **Pump & valve wiring** (for pressure profiling)                                      |
| 32–52   | **Full installation example** (open p32 · sensors p36 · LED p44 · SSR p46 · tidy p52) |
| 57–65   | **Appendix: pressure-sensor installation**                                            |
| 69–71   | Appendix: wiring diagrams                                                             |

---

## 8. Parameter glossary (the ones you'll actually set)

| Param       | Unit       | Meaning                                                                 |
| ----------- | ---------- | ----------------------------------------------------------------------- |
| `Press max` | bar        | Max pressure at full pump power (0°). Set by Pressure Test.             |
| `Press OPV` | bar        | Pressure where the over-pressure valve opens.                           |
| `Phase OPV` | °          | Phase angle at that OPV point.                                          |
| `Phase off` | °          | Angle at which the vibe pump stops pumping (~115°).                     |
| `Flow Corr` | ° (signed) | Bias to compensate for flow (no-flow test error). Typ. 0 to −15°.       |
| `Heat Corr` | °          | Momentary power bump while the heater fires (voltage-sag compensation). |
| `K`         | °/bar      | Proportional gain (per pressure band; can split >SP / <SP).             |
| `I`         | °/cycle    | Integral gain. **Errata:** pre-Aug-2023 values were ×10 mis-scaled.     |
| `Cycle`     | ms         | Integral update period (e.g. 200 ms).                                   |
| `WU-Limit`  | °          | Anti-windup cap on the integral term.                                   |
