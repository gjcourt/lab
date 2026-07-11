# La Spaziale Mini Vivaldi II — Control-Board Wiring Reference

Shared electrical reference for the **La Spaziale S1 Mini Vivaldi II** (Clive's **LUCCA A53 Mini**)
control board. Every project that interposes on this machine's mains wiring taps the same board, so
the terminal map, the "no switched rail" gotcha, and the flow-meter pinout live here once:

- [06-001 — ito + `leva!` pressure/flow profiling](../06-001-lucca-a53-mini-leva-firmware-integration.md)
- [06-011 — direct plumb-in (reservoir float-fill)](../06-011-mini-v2-direct-plumb-in.md)
- [06-012 — `leva!` PID temperature takeover](../06-012-leva-pid-temperature-takeover.md)

Everything below is from the **official Owner's Manual** (§6.1 Electrical Connection Diagram, §6.2
Control-Board Connection Diagram, §6.5 legend), cross-checked against `blondica73`'s install
(home-barista t56816 / t61709) and **confirmed by meter on a US 120 V unit (2026-07)**.

> ⚠️ **Mains voltage.** Unplug at the wall before opening — the soft-touch pad does **not** cut mains
> (see below). Let the dual boilers cool + depressurize. Qualified-electrician territory for the
> mains-side work; measure, don't assume.

## The M5 output terminal strip

The control board's main terminal strip (**M5**), **top → bottom** as printed in the manual, with the
wire-ferrule marks seen on a real board:

| Pos       | Manual label | Board mark   | Function                            | Type          |
| --------- | ------------ | ------------ | ----------------------------------- | ------------- |
| 1 (top)   | EV. AL       | `A`          | Autofill (boiler-refill) solenoid   | switched load |
| 2         | EV. H        | `2`          | Hot-water solenoid                  | switched load |
| 3         | **PUMP**     | _(unlabeled)_ | **Vibratory pump**                  | switched load |
| 4         | EV. GR       | `1`          | Group / brew solenoid               | switched load |
| 5         | **PHASE**    | `F`          | **Line / 120 V hot — ALWAYS LIVE**  | mains in      |
| 6         | NEUTRAL      | _(white)_    | Neutral                             | mains in      |
| 7         | NEUTRAL      | _(white)_    | Neutral                             | mains in      |

Earth is a **separate ground stud** (yellow ⏚), not on M5. The strip reconciles with blondica's
bottom-up count: "1st/2nd from bottom = N, 3rd = PHASE, 4th = group solenoid."

## ⚠️ There is NO switched mains rail

The power pad is a **soft-touch logic input** — it only toggles **ON ⇄ Standby**, it is not a mains
switch. The manual's diagram shows **PHASE fused straight off the plug** with no master relay, so
**`F`/PHASE + `N` are live the entire time the machine is plugged in**, in both ON and Standby
(metered: `F` → GND = 120 VAC even in standby). The only things that get switched are the **load
outputs** (PUMP, EV.GR, EV.H, EV.AL) and the two heater triacs — each hot only while the controller
actually drives that load.

**Consequence:** you cannot get a "hot only when the machine is on" L+N pair from F/N. To gate
something on machine activity, either **tap a load output** (the PUMP tab is the useful one — see
below), or power the whole machine from a **switched outlet / smart plug** (La Spaziale's own on/off
method — the "S1 Power Retain Timer" accessory is exactly that).

## Identifying the loads by meter

The pump is the only load that fires in **two** different operations, so cross it. Meter each suspect
tab → a NEUTRAL tab:

| Operation                                              | Loads energized       |
| ------------------------------------------------------ | --------------------- |
| Brew a shot                                            | **PUMP** + EV.GR (`1`) |
| Steam-boiler autofill (draw steam/hot water so it drops) | **PUMP** + EV.AL (`A`) |
| Hot-water tap                                          | EV.H (`2`)            |

- Hot in **both** brew and autofill → **PUMP** (the unlabeled 3rd-from-top tab).
- Hot in brew only → EV.GR (`1`); hot in autofill only → EV.AL (`A`); hot on hot-water only → EV.H (`2`).
- `F`/PHASE + the two `N` tabs stay live throughout — not discriminators.

> **Phantom voltage:** an unconnected tab next to live wiring reads tens of volts (~40 VAC observed)
> on a high-impedance meter — capacitive coupling, not a real source. It collapses to ~0 under any
> load or in the meter's **LoZ** mode. Ignore it.

## The stock GICAR flow meter

3-pin turbine/Hall meter with an **open-collector pulse output**:

| Pin (molded) | Function                                                                          |
| ------------ | --------------------------------------------------------------------------------- |
| `+`          | VCC (~14.3 V) — **Vivaldi-side ONLY; NEVER to a 5 V logic input** (5 V + 0.5 V max) |
| `−`          | GND                                                                               |
| `o`          | Output — **5 V open-collector** pulse (pulled to 5 V inside the Vivaldi)           |

Coarse (~2 pulses/ml) — fine for **display + volume dosing**; leva! 3.0 flow-_tracking_ prefers the
Digmesa nano (48 pulses/ml), adaptable per sandc (t61709 #179): 10 N on C8, 4K7 on R6, set 48000
impulses/L.

## How each project taps this board

- **[06-001] ito + leva! profiling** — cut the **PUMP** wire at the pump → route the control-board
  side to ito **`SNS`** (zero-cross + "pump on"), and drive the pump from ito **`Relay 1`**. Share
  the GICAR **`o` + `−`** into ito's flow input via a **CD4011B buffer on ito's 5 V rail** (keep GICAR
  `+` on the Vivaldi only). Opto optional (isolation).
- **[06-011] plumb-in** — derive the fill-solenoid's 12 VDC PSU from the **PUMP** output (L = PUMP
  tab, N = a white tab). The solenoid then opens **only when the pump draws from the tank** → fail-safe
  (closed when idle/off), and with **no smart-plug dependency**. Same tab does double duty with
  06-001's `SNS` sense (a few-watt PSU is negligible on that relay, behind the 5 A fuse).
- **[06-012] PID takeover** — the boiler/group heating elements switch via the **triac board** (an
  external 20 A SSR driven from ito's `SSR` connector), separate from M5.

## Sources

- La Spaziale S1 Mini Vivaldi II Owner's Manual §6.1–6.5 (Electrical / Control-Board / Triac-Board
  Connection Diagrams + legend): `s1cafe.com/s1v2/MiniV2Manual/Mini_V2_Owners_Manual_RevG.pdf`;
  ManualsLib `manual/749283/...` (~p.19–20).
- `blondica73` install — terminal count, GICAR scope trace, PUMP → `SNS`: home-barista
  [t56816](https://www.home-barista.com/espresso-machines/la-spaziale-mini-vivaldi-and-pressure-profiling-t56816.html)
  #23/#26/#31 and
  [t61709](https://www.home-barista.com/espresso-machines/ito-leva-controller-q-experience-t61709.html)
  #26/#28/#29.
- Metered + confirmed on a US 120 V unit, 2026-07.
