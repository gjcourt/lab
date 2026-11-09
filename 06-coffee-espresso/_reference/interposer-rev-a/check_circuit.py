#!/usr/bin/env python3
"""ERC-style checks for circuit.py (06-014 interposer rev A). Exit 0 = all checks pass.

    python3 check_circuit.py            # from this folder
    python3 check_circuit.py -v         # also list every check's detail

Checks (each cites where its rule comes from):
  C1  every part has a vendored KiCad footprint, and every REF.pad named exists in it
  C2  every footprint pad is either on a net or listed in NC (nothing silently floating)
  C3  every net has >= 2 pins; no pin on two nets; no pin both on a net and NC
  C4  GICAR meter supply (N_PLUS) touches only J1.2 / J2.2               (06-015, plan §3.4)
  C5  ito 5 V nets never meet a board rail (+3V3/+5V/VBUS), directly or through any
      two-terminal part; U1 is on ito 5 V and U2 on +3V3                  (plan §3.4)
      (06-015 called N_PLUS +14.3 V; bench Test 36 measured ~3.3 V. The rule stands: it is the
      meter's own supply and must stay pass-through.)
  C6  ESP32 GPIO: each used once, matches the GPIO table, no strapping / octal-PSRAM / UART0 /
      not-led-out pin used, USB only on GPIO19/20, analog nets on ADC1  (module DS v1.8 §3, §4)
  C7  SB/SL probe lines: no DC path -- only the pass-through connectors and the series
      coupling caps touch them; the aux pins are pure pass-through       (plan §3.3)
  C8  S1/S2 NTC feed lines: only the pass-through connectors and the series R (no bias
      injected); the follower input is clamped by a BAV99 to +5V / GND and nothing else; the
      ADS1115 input sits behind a divider whose ratio keeps a +5V follower output under the
      ADS VDD (3V3) + 0.3 V abs max            (plan §3.2, George 2026-11-08, SBAS444E)
  C9  ENC lines: only connectors, FET drains (pull-low only) and LVC inputs; no pull-up or
      push-pull driver; every FET gate has a pull-down; ito-side pin 1 = GND, encoder-side
      pin 1 NC                                                 (plan §3.5, bench Test 33)
  C10 every IC power pin on the intended rail
  C11 M9 tap: the RS-232 transceiver's line pins, its RX output and the passive path reach
      M9 / GPIO38 only through DNP links; DIN1 has its pull-up         (George 2026-11-08)
Info: nets left with a single fitted pin once DNP parts are removed (expected for DNP blocks).
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import circuit as ckt  # noqa: E402

VERBOSE = '-v' in sys.argv
FAILS: list[str] = []
RESULTS: list[tuple[str, bool, str]] = []


def check(code: str, title: str, problems: list[str], detail: str = '') -> None:
    ok = not problems
    RESULTS.append((code, ok, title))
    print(f'[{"PASS" if ok else "FAIL"}] {code} {title}' + (f'  ({detail})' if detail else ''))
    for p in problems:
        print(f'         - {p}')
        FAILS.append(f'{code}: {p}')


def split(pin: str) -> tuple[str, str]:
    ref, pad = pin.split('.', 1)
    return ref, pad


def footprint_pads(fp_name: str) -> set[str]:
    path = HERE / 'footprints' / f'{fp_name}.kicad_mod'
    text = path.read_text()
    # unnamed pads ("") are mechanical / thermal-via pads, not connections
    return {p for p in re.findall(r'\(pad "([^"]*)"', text) if p}


parts = {p.ref: p for p in ckt.PARTS}
pin_net: dict[str, list[str]] = defaultdict(list)
for net, pins in ckt.NETS.items():
    for pin in pins:
        pin_net[pin].append(net)

# ---- C1 footprints + pad names --------------------------------------------------------------
probs = []
if len(parts) != len(ckt.PARTS):
    probs.append('duplicate reference designators in PARTS')
pads_of: dict[str, set[str]] = {}
for p in ckt.PARTS:
    f = HERE / 'footprints' / f'{p.fp_name}.kicad_mod'
    if not f.exists():
        probs.append(f'{p.ref}: footprint file missing: footprints/{p.fp_name}.kicad_mod')
        continue
    pads_of[p.ref] = footprint_pads(p.fp_name)
for pin in list(pin_net) + list(ckt.NC):
    ref, pad = split(pin)
    if ref not in parts:
        probs.append(f'{pin}: unknown part {ref}')
    elif ref in pads_of and pad not in pads_of[ref]:
        probs.append(f'{pin}: pad "{pad}" not in {parts[ref].fp_name} (has {sorted(pads_of[ref])})')
check('C1', 'parts have footprints; every REF.pad exists', probs,
      f'{len(parts)} parts, {len(set(p.fp_name for p in ckt.PARTS))} footprints')

# ---- C2 no unaccounted pad ------------------------------------------------------------------
probs = []
for ref, pads in pads_of.items():
    for pad in pads:
        pin = f'{ref}.{pad}'
        if pin not in pin_net and pin not in ckt.NC:
            probs.append(f'{pin} is on no net and not in NC')
    if not any(split(x)[0] == ref for x in pin_net):
        probs.append(f'{ref} is on no net at all')
check('C2', 'every pad is on a net or explicitly NC', probs, f'{len(ckt.NC)} NC pads')

# ---- C3 net sanity --------------------------------------------------------------------------
probs = []
for net, pins in ckt.NETS.items():
    if len(set(pins)) < 2:
        probs.append(f'net {net} has {len(set(pins))} pin(s)')
    if len(set(pins)) != len(pins):
        probs.append(f'net {net} lists a pin twice')
for pin, nets in pin_net.items():
    if len(set(nets)) > 1:
        probs.append(f'{pin} is on {sorted(set(nets))}')
    if pin in ckt.NC:
        probs.append(f'{pin} is on {nets[0]} and also NC')
check('C3', 'every net >= 2 pins; no pin on two nets', probs, f'{len(ckt.NETS)} nets')

# ---- C4 GICAR meter supply ----------------------------------------------------------------------
plus = set(ckt.NETS[ckt.FLOW_SUPPLY_NET])
probs = [] if plus == {'J1.2', 'J2.2'} else [f'N_PLUS = {sorted(plus)}, must be exactly J1.2, J2.2']
check('C4', 'GICAR meter supply touches only J1.2 / J2.2', probs)

# ---- C5 ito 5 V isolation ---------------------------------------------------------------------
probs = []
for n in ckt.ITO_5V_NETS:
    for pin in ckt.NETS[n]:
        others = set(pin_net[pin]) - {n}
        if others:
            probs.append(f'{pin} joins {n} to {others}')
# any part with exactly two pads on distinct nets is a "bridge"; also check every pad pair of
# passives / jumpers (R, C, D, JP, SW): none may connect an ito 5 V net to a board rail
for ref, p in parts.items():
    if not re.match(r'^(R|C|D|JP|SW)\d+$', ref):
        continue
    nets = {pin_net[f'{ref}.{pad}'][0] for pad in pads_of.get(ref, ()) if pin_net.get(f'{ref}.{pad}')}
    if nets & ckt.ITO_5V_NETS and nets & ckt.BOARD_RAILS:
        probs.append(f'{ref} bridges {sorted(nets & ckt.ITO_5V_NETS)} to {sorted(nets & ckt.BOARD_RAILS)}')
want = {'U1.5': 'V5_ITO', 'U1.3': 'GND', 'U2.5': '+3V3', 'U2.3': 'GND'}
for pin, net in want.items():
    if pin_net[pin] != [net]:
        probs.append(f'{pin} should be on {net}, is on {pin_net[pin]}')
check('C5', 'ito 5 V never meets 3V3 / board 5 V; buffer domains separate', probs)

# ---- C6 ESP32 GPIO rules ----------------------------------------------------------------------
probs = []
gpio_of_pin = {pin: g for g, pin in ckt.ESP32_PIN_OF_GPIO.items()}
used: dict[int, str] = {}
for pin, nets in pin_net.items():
    ref, pad = split(pin)
    if ref != 'U5':
        continue
    n = int(pad)
    if n in gpio_of_pin:
        g = gpio_of_pin[n]
        if g in used:
            probs.append(f'GPIO{g} used twice ({used[g]}, {nets[0]})')
        used[g] = nets[0]
for g, net in used.items():
    if g not in ckt.GPIO:
        probs.append(f'GPIO{g} on {net} is missing from the GPIO table')
    elif ckt.GPIO[g][0] != net:
        probs.append(f'GPIO{g}: table says {ckt.GPIO[g][0]}, netlist says {net}')
    if g in ckt.STRAPPING_GPIO and not (g == 0 and net == 'BOOT'):
        probs.append(f'GPIO{g} is a strapping pin (DS Table 4-1) but carries {net}')
    if g in ckt.OCTAL_PSRAM_GPIO:
        probs.append(f'GPIO{g} is an octal-PSRAM pin on R8 modules (DS Table 3-1 note b)')
    if g in ckt.NOT_LED_OUT_GPIO:
        probs.append(f'GPIO{g} is not a module pin (DS Table 3-1)')
    if g in ckt.UART0_GPIO:
        probs.append(f'GPIO{g} is UART0 (kept free for the ROM console)')
    if g in ckt.USB_GPIO and net != ckt.USB_GPIO[g]:
        probs.append(f'GPIO{g} is USB {ckt.USB_GPIO[g]} but carries {net}')
    if net in ckt.ANALOG_NETS and g not in ckt.ADC1_GPIO:
        probs.append(f'{net} needs ADC1 (GPIO1..10), is on GPIO{g}')
for g in ckt.GPIO:
    if g not in used:
        probs.append(f'GPIO table lists GPIO{g} but no net uses it')
for name, pins in ckt.ESP32_POWER_PINS.items():
    for n in pins:
        want_net = {'GND': 'GND', '3V3': '+3V3', 'EN': 'EN'}[name]
        if pin_net.get(f'U5.{n}') != [want_net]:
            probs.append(f'U5.{n} ({name}) should be on {want_net}')
check('C6', 'ESP32-S3 GPIO allocation (module DS v1.8 Tables 3-1, 4-1)', probs,
      f'{len(used)} GPIO used')

# ---- C7 level probes: no DC path ---------------------------------------------------------------
probs = []
for net, caps in ckt.LEVEL_PROBE_NETS.items():
    for pin in ckt.NETS[net]:
        ref, pad = split(pin)
        if ref.startswith('J'):
            continue
        if ref in caps and ref.startswith('C'):
            continue
        probs.append(f'{net}: {pin} is a DC path (only pass-through J + {sorted(caps)} allowed)')
for net in ckt.LEVEL_AUX_NETS:
    for pin in ckt.NETS[net]:
        if not split(pin)[0].startswith('J'):
            probs.append(f'{net}: {pin} (aux line must be pure pass-through)')
check('C7', 'SB/SL probe lines: pass-through + series coupling C only', probs)

# ---- C8 NTC lines: no bias injected; clamp + divider sized for the ADS ---------------------------
probs = []
for net, r in ckt.NTC_SERIES.items():
    for pin in ckt.NETS[net]:
        ref, _ = split(pin)
        if ref.startswith('J') or ref == r:
            continue
        probs.append(f'{net}: {pin} touches the NTC line (only J + {r} allowed)')
    other = [x for x in pin_net if split(x)[0] == r and pin_net[x][0] != net]
    if len(other) != 1 or pin_net[other[0]][0] not in ckt.NTC_FOLLOWER_IN:
        probs.append(f'{r} must go from {net} straight to a follower input net')
for net in sorted(ckt.NTC_FOLLOWER_IN):
    refs = {split(p)[0] for p in ckt.NETS[net]}
    if 'U6' not in refs:
        probs.append(f'{net} does not reach the U6 follower')
    for ref in refs - {'U6'}:
        if ref.startswith('R'):
            continue  # the series R (checked above)
        if ckt.part(ref).value != 'BAV99':
            probs.append(f'{net}: {ref} is not the series R, the follower or a BAV99 clamp')
            continue
        if pin_net.get(f'{ref}.3') != [net] or pin_net.get(f'{ref}.1') != ['GND'] or pin_net.get(f'{ref}.2') != ['+5V']:
            probs.append(f'{ref} must clamp {net} (pin 3) to GND (pin 1) and +5V (pin 2)')
# divider: follower output (<= +5V) x ratio must stay <= ADS VDD + 0.3 V = 3.6 V
VAL = {'10k': 10e3, '5.1k': 5.1e3, '100k': 100e3, '1M': 1e6}
# series R: a 24 V fault (George: "survive 24 V") into a clamp at +5V + 0.3 V must stay under the
# MCP6004's +-2 mA input-pin rating (DS20001733L abs max)
for r in ckt.NTC_SERIES.values():
    v = VAL.get(ckt.part(r).value)
    if v is None or (24 - 5.3) / v > 2e-3:
        probs.append(f'{r} = {ckt.part(r).value}: 24 V fault current must stay under 2 mA')
for top, bot, adc in (('R9', 'R13', 'S1_ADC'), ('R10', 'R14', 'S2_ADC')):
    rt, rb = VAL.get(ckt.part(top).value), VAL.get(ckt.part(bot).value)
    if rt is None or rb is None or 5.0 * rb / (rt + rb) > 3.6:
        probs.append(f'{top}/{bot}: divider must hold a 5 V follower output under 3.6 V at {adc}')
    if not any(split(p)[0] == 'U7' for p in ckt.NETS[adc]):
        probs.append(f'{adc} does not reach the ADS1115')
check('C8', 'S1/S2 feeds: pass-through + series R + clamp into a follower; ADS input bounded', probs)

# ---- C9 ENC open-drain only ---------------------------------------------------------------------
probs = []
for net in ('ENC_A', 'ENC_B', 'ENC_SW'):
    for pin in ckt.NETS[net]:
        ref, pad = split(pin)
        if ref.startswith('J'):
            continue
        if ref.startswith('Q') and pad == '3':  # drain (AO3400A: 1 G, 2 S, 3 D)
            if pin_net[f'{ref}.2'] != ['GND']:
                probs.append(f'{ref} source is not on GND')
            gate = pin_net[f'{ref}.1'][0]
            if not any(split(x)[0].startswith('R') and pin_net[f'{split(x)[0]}.{"2" if split(x)[1] == "1" else "1"}'] == ['GND']
                       for x in ckt.NETS[gate]):
                probs.append(f'{ref} gate has no pull-down to GND')
            continue
        if ckt.part(ref).value == '74LVC1G17' and pad == '2':  # A input
            continue
        probs.append(f'{net}: {pin} is not a connector, FET drain or LVC input')
# Test 33: the encoder cable has no wire in hole 1; ito ENC pin 1 is GND (our FET return)
if 'J14.1' not in ckt.NC:
    probs.append('J14.1 must be NC (encoder cable hole 1 is empty, Test 33)')
if pin_net.get('J15.1') != ['GND']:
    probs.append('J15.1 (ito ENC pin 1) must be GND')
check('C9', 'ENC lines: pull-low-only injection, high-Z read-back', probs)

# ---- C10 IC power pins ------------------------------------------------------------------------
power = {
    'U4.3': '+5V', 'U4.2': '+3V3', 'U4.1': 'GND',
    'U6.4': '+5V', 'U6.11': 'GND',
    'U7.8': '+3V3', 'U7.3': 'GND', 'U7.1': 'GND',  # ADDR = GND -> 0x48
    'U8.5': '+3V3', 'U9.5': '+3V3', 'U10.5': '+3V3',
    'U11.2': '+3V3', 'U11.1': 'GND', 'U3.5': 'VBUS', 'U3.2': 'GND',
    'U13.16': '+3V3', 'U13.15': 'GND', 'U13.10': 'GND',  # MAX3232; unused DIN2 tied low (SLLS410O §9.2.2)
}
probs = [f'{p} should be {n}, is {pin_net.get(p)}' for p, n in power.items() if pin_net.get(p) != [n]]
check('C10', 'IC power pins on the intended rails', probs)

# ---- C11 M9 tap: nothing fitted reaches the machine until M9 is scoped --------------------------
dnp_refs = {p.ref for p in ckt.PARTS if p.dnp}
probs = []
for net, owner in ckt.M9_LINK_NETS.items():
    for pin in ckt.NETS[net]:
        ref = split(pin)[0]
        if ref != owner and ref not in dnp_refs:
            probs.append(f'{net}: {pin} is fitted; only DNP links may join {owner} here')
for pin in ckt.NETS['M9_P1'] + ckt.NETS['M9_P2'] + ckt.NETS['M9_P3'] + ckt.NETS['M9_P4']:
    if split(pin)[0] not in dnp_refs:
        probs.append(f'{pin} is fitted on an M9 line')
if pin_net.get('U13.11') != ['M9_TX'] or not any(split(p)[0] == 'R55' for p in ckt.NETS['M9_TX']):
    probs.append('U13 DIN1 must be on M9_TX with the R55 pull-up (SLLS410O §9.2.2)')
check('C11', 'M9 tap: machine side reached only through DNP links', probs)

# ---- info: nets that are single-pin once DNP parts are left off --------------------------------
dnp = {p.ref for p in ckt.PARTS if p.dnp}
lonely = []
for net, pins in ckt.NETS.items():
    fitted = [x for x in pins if split(x)[0] not in dnp]
    if len(fitted) == 1:
        lonely.append(f'{net} ({fitted[0]})')
print(f'[INFO] {len(dnp)} DNP parts; nets with one fitted pin (expected for DNP blocks): '
      + ', '.join(lonely))

if VERBOSE:
    for g in sorted(ckt.GPIO):
        print(f'       GPIO{g:<2} module pin {ckt.ESP32_PIN_OF_GPIO[g]:>2}  {ckt.GPIO[g][0]}')

print()
if FAILS:
    print(f'FAILED: {len(FAILS)} problem(s) in {sum(1 for r in RESULTS if not r[1])} check(s)')
    sys.exit(1)
print(f'ALL {len(RESULTS)} CHECKS PASS')
