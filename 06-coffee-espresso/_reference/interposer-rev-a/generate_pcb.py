#!/usr/bin/env python3
"""06-014 unified ESP32 interposer, rev A: generate the PCB from circuit.py (KiCad 9 pcbnew API).

Runs inside the kicad/kicad:9.0 container (see README "Layout"). Three stages, all deterministic:

  python3 generate_pcb.py dsn     place + net the board from circuit.py, write
                                  build/interposer-rev-a-placed.kicad_pcb and build/interposer-rev-a.dsn
  (Freerouting, in a Java container: build/interposer-rev-a.dsn -> routing/interposer-rev-a.ses)
  python3 generate_pcb.py finish  re-place (identical), import routing/interposer-rev-a.ses, add the
                                  GND pours, fill, write interposer-rev-a.kicad_pcb (+ .kicad_pro)
  python3 generate_pcb.py fab     BOM + CPL for JLCPCB from circuit.py and the finished board

The routing session (routing/interposer-rev-a.ses) is committed, so `finish` reproduces the board
without re-running the autorouter. Re-route only when placement changes.

Everything electrical comes from circuit.py (PARTS, NETS, NC). This file adds only layout:
placement, the outline, mounting holes, test pads, rules, pours and silkscreen. The layout-only
additions (test pads TP1..TP7, holes H1..H4) are listed in LAYOUT_PARTS / LAYOUT_NETS below.
"""

from __future__ import annotations

import csv
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pcbnew  # noqa: E402

from circuit import NC, NETS, PARTS, Part  # noqa: E402

FPDIR = os.path.join(HERE, 'footprints')
BUILD = os.path.join(HERE, 'build')
ROUTING = os.path.join(HERE, 'routing')
FAB = os.path.join(HERE, 'fab')
NAME = 'interposer-rev-a'

# ---------------------------------------------------------------------------------------------
# Board: 90 x 60 mm, 2-layer, 1.6 mm. Local coordinates: origin = top-left corner, x right, y down.
# The tank-side site (Test 37: ~130 x 120 mm, >= 30 mm deep) is the target; see README "Layout".
# ---------------------------------------------------------------------------------------------
W, H = 100.0, 60.0
OX, OY = 100.0, 100.0  # where local (0, 0) sits on the KiCad sheet
CORNER_R = 2.0

# JLCPCB standard 2-layer capability: 6/6 mil track/space for everything routed (netclasses below),
# 0.3 mm minimum drill. The board-wide clearance floor is 0.15 mm only because the KiCad VSSOP-8
# 2.3x2 land (U11, DNP) has 0.15 mm pad gaps; a custom rule (DRU below) scopes that to U11's own
# pads. 0.15 mm is still above JLC's 0.127 mm (5 mil) 2-layer capability.
RULES = dict(
    min_clearance=0.15, min_track=0.1524, min_via_dia=0.5, min_drill=0.3, min_annular=0.13,
    hole_to_hole=0.25, hole_clearance=0.2, copper_edge=0.3, silk_h=0.8, silk_t=0.15,
)
DRU = """(version 1)
(rule "U11 KiCad VSSOP-8 2.3x2 land: 0.15 mm pad gaps (DNP; compare with TI DCU before fitting)"
  (condition "A.memberOfFootprint('U11') && B.memberOfFootprint('U11')")
  (constraint clearance (min 0.15mm)))
(rule "JLC 6 mil floor everywhere else"
  (condition "!(A.memberOfFootprint('U11') && B.memberOfFootprint('U11'))")
  (constraint clearance (min 0.1524mm)))
"""
# Every footprint is vendored in ./footprints; the project's own library table points there.
FP_LIBS = ['lab', 'Resistor_SMD', 'Capacitor_SMD', 'Package_TO_SOT_SMD', 'Package_SO', 'Diode_SMD',
           'RF_Module', 'Connector_USB', 'Button_Switch_SMD', 'Connector_JST', 'Connector_Molex',
           'Connector_PinHeader_2.54mm', 'Jumper', 'Package_DIP']
# name: (clearance, track, via dia, via drill, nets)
NETCLASSES = {
    'Default': (0.16, 0.2, 0.6, 0.3, []),
    # widths the router can still take into 0.5 mm-pitch supply pins (ADS1115 VDD, SOT-23-5 VCC);
    # 0.3 mm of 1 oz copper carries the ESP32's 0.5 A requirement over these lengths. GND is poured.
    'Power5': (0.2, 0.4, 0.7, 0.35, ['+5V', 'VBUS']),
    # (GND stays in Default: it is poured, and a class whose net has no pins in the DSN breaks the
    # router for every other net in that class)
    'Power3': (0.16, 0.3, 0.65, 0.3, ['+3V3']),
    # Machine harness lines (pass-through copper) and the 1 Mohm follower inputs: a wider gap than
    # the minimum. All low voltage (no mains on this board, plan §3.1).
    'Machine': (0.25, 0.3, 0.6, 0.3, ['N_PLUS', 'N_O', 'S1_FEED', 'S2_FEED', 'S1_IN', 'S2_IN',
                                      'SB_PROBE', 'SB_AUX', 'SL_PROBE', 'SL_AUX',
                                      'M9_P1', 'M9_P2', 'M9_P3', 'M9_P4', 'V5_ITO']),
}


def mm(v: float) -> int:
    return pcbnew.FromMM(v)


def pt(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))


# ---------------------------------------------------------------------------------------------
# Layout-only parts (not in circuit.py): mounting holes and test pads.
# U5.36 / U5.37 (UART0) are NC in circuit.py with the note "add a test pad at layout"; the pads
# below are those test pads, plus pads on existing nets for bench flashing over UART0.
# ---------------------------------------------------------------------------------------------
FP_HOLE = 'lab:MountingHole_3.2mm_M3'
FP_TP = 'lab:TestPoint_Pad_D1.5mm'
LAYOUT_PARTS = [
    Part('H1', 'M3', FP_HOLE, 'mech', note='NPTH, no copper: the board GND is earth, so no extra bond'),
    Part('H2', 'M3', FP_HOLE, 'mech'),
    Part('H3', 'M3', FP_HOLE, 'mech'),
    Part('H4', 'M3', FP_HOLE, 'mech'),
    Part('TP1', 'TXD0', FP_TP, 'test', note='U5.37 GPIO43 U0TXD (ROM console)'),
    Part('TP2', 'RXD0', FP_TP, 'test', note='U5.36 GPIO44 U0RXD'),
    Part('TP3', 'EN', FP_TP, 'test'),
    Part('TP4', 'BOOT', FP_TP, 'test', note='GPIO0: hold low during EN rise for UART download'),
    Part('TP5', '+3V3', FP_TP, 'test'),
    Part('TP6', '+5V', FP_TP, 'test'),
    Part('TP7', 'GND', FP_TP, 'test'),
]
LAYOUT_NETS = {
    'U0TXD': ['U5.37', 'TP1.1'],
    'U0RXD': ['U5.36', 'TP2.1'],
    'EN': ['TP3.1'],
    'BOOT': ['TP4.1'],
    '+3V3': ['TP5.1'],
    '+5V': ['TP6.1'],
    'GND': ['TP7.1'],
}

# ---------------------------------------------------------------------------------------------
# Placement. (x, y, rotation deg) in local mm; the footprint origin goes at (x, y).
# Edges: machine side (EXCON, to the control board) = bottom edge, one bank; ito side (KK ENC,
# XH IMPULSE, EXPANSION) = top-left; ESP32 antenna = top-right edge; USB-C = right edge;
# 5 V in + Qwiic = left edge.
# ---------------------------------------------------------------------------------------------
BANK_Y = 56.4  # pin 1 row of the EXCON bank (rot 90: pins run up from the edge, latch face right)
FIXED = {
    'H1': (3.5, 3.5, 0), 'H2': (3.5, 56.5, 0), 'H3': (96.5, 56.5, 0), 'H4': (96.5, 30.0, 0),
    # ESP32-S3-WROOM-1: antenna end flush with the top edge; its keep-out zone covers y < 6.
    'U5': (84.0, 12.75, 0),
    # ito side, top-left (pins run down from the top edge)
    'J14': (11.0, 2.0, 270), 'J15': (18.4, 2.0, 270), 'J3': (26.1, 3.2, 270),
    'J17': (32.5, 3.0, 90),
    # left edge
    'J4': (4.5, 15.0, 270), 'J16': (3.6, 27.0, 270),
    'J18': (3.4, 34.0, 0),  # SER stub (DNP), toward the panel
    # machine bank, bottom edge. In/out pairs side by side so the pass-through copper is a straight
    # hop between neighbours: S1 | S2+SB | flow | SL | M9
    # 7.6 mm pitch leaves a 1.6 mm column beside each header for its legend
    'J6': (12.3, BANK_Y, 90), 'J7': (19.9, BANK_Y, 90),
    'J8': (28.9, BANK_Y, 90), 'J9': (36.5, BANK_Y, 90),
    'J1': (45.5, BANK_Y, 90), 'J2': (53.1, BANK_Y, 90),
    'J12': (62.1, BANK_Y, 90), 'J13': (69.7, BANK_Y, 90),
    'J20': (78.7, BANK_Y, 90),
    # USB-C on the right edge, receptacle face at the edge
    'J5': (96.1, 40.0, 90),
    # power: LDO beside the module's 3V3 pin, bulk + decoupling in a column at the module edge
    'U4': (67.0, 10.5, 0), 'C3': (61.3, 10.5, 90), 'C4': (69.5, 15.9, 0),
    # (R3/C7 at 270 so their EN ends face each other; R3's 3V3 end meets C6's)
    'C5': (73.1, 8.2, 90), 'C6': (73.1, 11.5, 90), 'R3': (73.1, 14.6, 270), 'C7': (73.1, 17.7, 270),
    'TP3': (72.8, 21.6, 0),  # EN test pad beside the EN RC, module side
    'SW1': (68.0, 31.0, 0), 'SW2': (88.5, 31.0, 0),
    # F1/F2 follower, rotated so pins 1-7 (IN+A = 3, IN+B = 5) face the probe headers below
    'U6': (20.0, 41.0, 90),
    # ADS1115 rotated: ADDR/ALERT/AIN0/AIN1 (pins 1-5) face down toward the dividers, I2C + VDD up
    'U7': (14.0, 28.0, 90),
    # F8b MAX3232
    'U13': (56.0, 40.0, 0),
    # UART0 flash / rail test pads down the right channel beside the module
    'TP1': (98.0, 8.5, 0), 'TP2': (98.0, 11.0, 0), 'TP4': (98.0, 16.0, 0),
    'TP5': (98.0, 18.5, 0), 'TP7': (98.0, 21.0, 0),
    'TP6': (61.3, 14.3, 0),  # +5V test pad at the LDO input
}

# Blocks: region (x0, y0, x1, y1) packed in rows, in the order given (signal-flow order), with
# per-ref rotation overrides. ICs first so they take the region's top-left.
BLOCKS = [
    # ito-domain flow buffer under J3 (V5_ITO stays local to J3)
    ('flow-ito', (22.0, 12.9, 30.0, 17.0), ['U1', 'C1'], {}),
    # F7 I2C: pull-ups, Qwiic side, DNP PCA9306 + jumpers toward J17 (EXPANSION)
    ('i2c', (8.0, 12.9, 21.6, 23.4), ['R34', 'R35', 'U11', 'R36', 'R37', 'R38', 'JP2', 'JP3'], {}),
    # F6 ENC: FET + gate R + pull-down per line, LVC read-back per line
    ('enc', (30.0, 7.6, 60.0, 22.0),
     ['Q1', 'R28', 'R31', 'Q2', 'R29', 'R32', 'Q3', 'R30', 'R33',
      'U8', 'C16', 'U9', 'C17', 'U10', 'C18'], {}),
    # F8 SER stub (all DNP) toward GPIO13/14/17/18
    ('ser', (38.0, 22.2, 63.8, 34.0),
     ['R39', 'R40', 'R44', 'D8', 'R41', 'R45', 'D9', 'R42', 'R46', 'D10', 'R43', 'R47', 'D11'], {}),
    # F1/F2 analog. The 1 Mohm follower inputs stay short: S1 series R + clamp right above J6/J7 and
    # under U6 pin 3; S2 series R + clamp beside U6 above J8/J9 (with the DNP SB front-end).
    ('s1-front', (8.5, 45.9, 22.0, 50.6), ['R5', 'D2'], {}),
    ('s2-front', (24.9, 37.4, 37.5, 45.5), ['R6', 'D3', 'C14', 'R22', 'R24', 'R26', 'D6'],
     {'R6': 90, 'C14': 90, 'R22': 90, 'R24': 90, 'R26': 90}),
    # then the divider + RC and the ADS1115 above U6
    ('analog', (17.0, 24.0, 37.5, 37.0),
     ['C13', 'R21', 'C8', 'R9', 'R13', 'C9', 'R10', 'R14', 'C10'], {}),
    # F5 ESP32-side flow buffer above J1/J2
    ('flow-esp', (38.0, 36.0, 51.8, 43.8), ['U2', 'C2'], {}),
    # F4 SL front-end (DNP) above the 2-pin J12/J13
    ('sl-front', (58.0, 45.9, 72.0, 50.6), ['C15', 'R23', 'R25', 'R27', 'D7'],
     {'C15': 90, 'R23': 90, 'R25': 90, 'R27': 90}),
    # F8b M9: charge pump, links, passive path, link headers beside U13; F9 contact header
    ('m9', (60.0, 34.2, 84.4, 45.6),
     ['C19', 'C20', 'C21', 'C22', 'C23', 'R55', 'R52', 'R53', 'R54', 'R49', 'R50', 'R51', 'D12',
      'J21', 'J22'], {'J21': 90, 'J22': 90}),
    # F9 photorelay + contact header (DNP) in the free top band left of the antenna keep-out;
    # its LED resistor between the reset buttons, next to GPIO12
    ('onoff', (44.9, 0.3, 59.8, 6.6), ['U12', 'J19'], {}),
    ('onoff-r', (72.0, 26.6, 85.4, 33.8), ['R48'], {}),
    # USB: ESD + CC resistors + OR-ing diode beside the receptacle
    ('usb', (84.6, 34.2, 90.6, 52.6), ['U3', 'R1', 'R2', 'D1'], {'D1': 90, 'U3': 90}),
    # GPIO0 pull-up near SW2 / pin 27
    ('boot', (86.0, 26.4, 93.0, 28.2), ['R4'], {}),
]

# Silkscreen legends. Bank headers: legend in the column beside each header, refdes on its body.
BANK = ['J6', 'J7', 'J8', 'J9', 'J1', 'J2', 'J12', 'J13', 'J20']
LEGEND = {
    'J6': 'S1 IN', 'J7': 'S1 OUT>M2', 'J8': 'S2+SB IN', 'J9': 'S2+SB OUT>M3', 'J1': 'GICAR IN',
    'J2': 'FLOW OUT>M6', 'J12': 'SL IN', 'J13': 'SL OUT>M10', 'J20': 'M9 RS232',
    # everything else: "REF legend", placed clear of every courtyard
    'J17': 'ito EXP', 'J14': 'ENC', 'J15': '>ito', 'J3': 'IMP', 'J4': '5V IN', 'J16': 'I2C',
    'J5': 'USB', 'J18': 'SER', 'J19': 'ON/OFF', 'J21': 'M9 LINK', 'J22': 'RS232',
    'SW1': 'EN', 'SW2': 'BOOT',
}
TP_LABEL = {'TP1': 'TX0', 'TP2': 'RX0', 'TP3': 'EN', 'TP4': 'IO0', 'TP5': '3V3', 'TP6': '5V', 'TP7': 'GND'}
SILK = 0.8  # text height, mm (JLC legible minimum)


# ---------------------------------------------------------------------------------------------
def all_parts() -> list[Part]:
    return PARTS + LAYOUT_PARTS


def all_nets() -> dict[str, list[str]]:
    nets = {k: list(v) for k, v in NETS.items()}
    for k, v in LAYOUT_NETS.items():
        nets.setdefault(k, []).extend(v)
    nc_used = {p for v in LAYOUT_NETS.values() for p in v if p in NC}
    assert nc_used <= {'U5.36', 'U5.37'}, nc_used
    return nets


def load_fp(p: Part) -> pcbnew.FOOTPRINT:
    fp = pcbnew.FootprintLoad(FPDIR, p.fp_name)
    if fp is None:
        raise SystemExit(f'{p.ref}: footprint {p.fp_name} not in {FPDIR}')
    fp.SetFPID(pcbnew.LIB_ID(p.footprint.split(':')[0], p.fp_name))
    return fp


def courtyard_bbox(fp: pcbnew.FOOTPRINT) -> tuple[float, float, float, float]:
    cy = fp.GetCourtyard(pcbnew.F_CrtYd)
    bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False)
    return (pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()),
            pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))


def place_at(fp, x, y, rot):
    fp.SetOrientationDegrees(rot)
    fp.SetPosition(pt(x, y))


def pack_blocks(fps: dict[str, pcbnew.FOOTPRINT], placement: dict, gap=0.5):
    for name, (x0, y0, x1, y1), refs, rots in BLOCKS:
        cx, cy, row_h = x0, y0, 0.0
        for ref in refs:
            fp = fps[ref]
            rot = rots.get(ref, 0)
            place_at(fp, 0, 0, rot)
            bx0, by0, bx1, by1 = courtyard_bbox(fp)
            w, h = bx1 - bx0, by1 - by0
            if cx + w > x1 + 1e-6 and cx > x0:
                cx, cy, row_h = x0, cy + row_h + gap, 0.0
            if cy + h > y1 + 1e-6 or cx + w > x1 + 1e-6:
                raise SystemExit(f'block {name}: {ref} ({w:.1f} x {h:.1f}) does not fit at ({cx:.1f}, {cy:.1f})')
            # bbox was taken with the origin at local (0, 0): offset = -(bbox origin - OX/OY)
            px, py = cx - (bx0 - OX), cy - (by0 - OY)
            placement[ref] = (round(px, 3), round(py, 3), rot)
            cx += w + gap
            row_h = max(row_h, h)


def set_text_size(t, size=0.8, thick=0.15):
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(thick))


def add_text(board, text, x, y, layer=pcbnew.F_SilkS, size=0.8, rot=0, thick=0.15):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(pt(x, y))
    t.SetLayer(layer)
    t.SetTextAngleDegrees(rot)
    set_text_size(t, size, thick)
    board.Add(t)
    return t


def add_field(fp, name, value):
    f = pcbnew.PCB_FIELD(fp, fp.GetNextFieldId(), name)
    f.SetText(value)
    f.SetVisible(False)
    f.SetLayer(pcbnew.F_Fab)
    fp.AddField(f)


def outline(board):
    r = CORNER_R
    segs = [((r, 0), (W - r, 0)), ((W, r), (W, H - r)), ((W - r, H), (r, H)), ((0, H - r), (0, r))]
    for a, b in segs:
        s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pt(*a)); s.SetEnd(pt(*b))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1))
        board.Add(s)
    k = r * (1 - 0.5 ** 0.5)
    for s, m, e in [((0, r), (k, k), (r, 0)), ((W - r, 0), (W - k, k), (W, r)),
                    ((W, H - r), (W - k, H - k), (W - r, H)), ((r, H), (k, H - k), (0, H - r))]:
        a = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_ARC)
        a.SetArcGeometry(pt(*s), pt(*m), pt(*e))
        a.SetLayer(pcbnew.Edge_Cuts); a.SetWidth(mm(0.1))
        board.Add(a)


def setup_rules(board):
    ds = board.GetDesignSettings()
    ds.m_MinClearance = mm(RULES['min_clearance'])
    ds.m_TrackMinWidth = mm(RULES['min_track'])
    ds.m_ViasMinSize = mm(RULES['min_via_dia'])
    ds.m_MinThroughDrill = mm(RULES['min_drill'])
    ds.m_ViasMinAnnularWidth = mm(RULES['min_annular'])
    ds.m_HoleToHoleMin = mm(RULES['hole_to_hole'])
    ds.m_HoleClearance = mm(RULES['hole_clearance'])
    ds.m_CopperEdgeClearance = mm(RULES['copper_edge'])
    ds.m_MinSilkTextHeight = mm(RULES['silk_h'])
    ds.m_MinSilkTextThickness = mm(RULES['silk_t'])
    ds.SetBoardThickness(mm(1.6))
    ns = ds.m_NetSettings
    for name, (clr, trk, vd, vdr, nets) in NETCLASSES.items():
        nc = ns.GetDefaultNetclass() if name == 'Default' else pcbnew.NETCLASS(name)
        nc.SetClearance(mm(clr)); nc.SetTrackWidth(mm(trk))
        nc.SetViaDiameter(mm(vd)); nc.SetViaDrill(mm(vdr))
        if name != 'Default':
            ns.SetNetclass(name, nc)
            for n in nets:
                ns.SetNetclassPatternAssignment(n, name)


def write_project_files(path: str):
    d = os.path.dirname(path)
    rel = os.path.relpath(FPDIR, d)
    with open(os.path.join(d, 'fp-lib-table'), 'w') as f:
        f.write('(fp_lib_table\n  (version 7)\n')
        for lib in FP_LIBS:
            f.write(f'  (lib (name "{lib}")(type "KiCad")(uri "${{KIPRJMOD}}/{rel}")(options "")'
                    f'(descr "vendored, see README"))\n')
        f.write(')\n')
    with open(os.path.splitext(path)[0] + '.kicad_dru', 'w') as f:
        f.write(DRU)


def build(path: str) -> pcbnew.BOARD:
    pcbnew.KIID.SeedGenerator(14)  # deterministic UUIDs: same inputs -> byte-identical board
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for ext in ('.kicad_pro', '.kicad_prl', '.kicad_pcb'):  # NewBoard would inherit a stale project
        stale = os.path.splitext(path)[0] + ext
        if os.path.exists(stale):
            os.remove(stale)
    write_project_files(path)
    board = pcbnew.NewBoard(path)
    board.SetCopperLayerCount(2)
    setup_rules(board)

    parts = all_parts()
    nets = all_nets()
    netinfo = {}
    for name in sorted(nets):
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netinfo[name] = ni
    pad_net = {pin: net for net, pins in nets.items() for pin in pins}

    fps = {}
    for p in parts:
        fp = load_fp(p)
        fp.SetReference(p.ref)
        fp.SetValue(p.value)
        fps[p.ref] = fp

    placement = dict(FIXED)
    pack_blocks(fps, placement)
    missing = [p.ref for p in parts if p.ref not in placement]
    if missing:
        raise SystemExit(f'unplaced: {missing}')

    for p in parts:
        fp = fps[p.ref]
        x, y, rot = placement[p.ref]
        place_at(fp, x, y, rot)
        for pad in fp.Pads():
            key = f'{p.ref}.{pad.GetNumber()}'
            if pad.GetNumber() and key in pad_net:
                pad.SetNet(netinfo[pad_net[key]])
            if key == 'J4.2':  # 5 V return: solid to the pours (a thermal here lands on a sliver)
                pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                pad.SetLocalClearance(mm(0.35))  # pours stand off mounting / locating holes
        ref_t = fp.Reference()
        set_text_size(ref_t, 0.8, 0.15)
        # Silk refdes only on parts big enough to carry one; every ref stays on F.Fab
        # (footprints carry ${REFERENCE} there) for the assembly drawing.
        small = p.footprint.split(':')[1].startswith(('R_0603', 'C_0603', 'C_0805', 'SOT-23', 'SolderJumper',
                                                      'TestPoint', 'VSSOP'))
        if small or p.ref.startswith('H') or (p.ref in LEGEND and p.ref not in BANK):
            ref_t.SetVisible(False)
        fp.Value().SetVisible(False)
        if p.lcsc:
            add_field(fp, 'LCSC', p.lcsc)
        if p.mpn:
            add_field(fp, 'MPN', p.mpn)
        if p.dnp:
            # DNP attribute: kept out of the CPL, crossed out on the F.Fab assembly drawing
            fp.SetDNP(True)
            fp.SetExcludedFromPosFiles(True)
        if p.func in ('mech', 'test'):
            fp.SetExcludedFromBOM(True)
            fp.SetExcludedFromPosFiles(True)
        board.Add(fp)

    # every pad named in the netlist exists on the board
    have = {f'{fp.GetReference()}.{pad.GetNumber()}' for fp in fps.values() for pad in fp.Pads()}
    lost = sorted(set(pad_net) - have)
    if lost:
        raise SystemExit(f'netlist pads missing on the board: {lost}')

    outline(board)
    silk(board, fps)
    return board, fps


def _overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def silk(board, fps):
    """Place every silk label where it overlaps no courtyard, no other label and stays on the
    board: try above / below / left / right of the part's courtyard, in that order."""
    boxes = {}
    for ref, fp in fps.items():
        x0, y0, x1, y1 = courtyard_bbox(fp)
        boxes[ref] = (x0 - OX, y0 - OY, x1 - OX, y1 - OY)
    ux, uy, _ = FIXED['U5']  # module body only (its courtyard bbox also spans the antenna clearance)
    boxes['U5'] = (ux - 9.75, 0.0, ux + 9.75, uy + 13.45)
    taken = []

    def free(r, own):
        if r[0] < 0.4 or r[1] < 0.4 or r[2] > W - 0.4 or r[3] > H - 0.4:
            return False
        if any(_overlap(r, b) for k, b in boxes.items() if k != own) or _overlap(r, boxes[own]):
            return False
        return not any(_overlap(r, t) for t in taken)

    def place(own, text, size=SILK, sides=False):
        x0, y0, x1, y1 = boxes[own]
        w, h = len(text) * size * 0.95, size  # KiCad stroke font ~0.9 x height per glyph
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        g = 0.2
        spots = [(cx, y0 - g - h / 2), (cx, y1 + g + h / 2), (x0 - g - w / 2, cy), (x1 + g + w / 2, cy)]
        if sides:  # test pads: beside the pad, so a column of pads reads unambiguously
            spots = spots[2:] + spots[:2]
        for x, y in spots:
            r = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            if free(r, own):
                taken.append(r)
                return x, y
        r = (cx - w / 2, y1 + g, cx + w / 2, y1 + g + h)
        why = [k for k, b in boxes.items() if _overlap(r, b)] + ['label' for t in taken if _overlap(r, t)]
        print(f'  silk: no clear spot for "{text}" ({own}); below blocked by {why}')
        return None

    # bank: legend up the 1.6 mm column left of each header; refdes on the header body
    for ref in BANK:
        x0, y0, x1, y1 = boxes[ref]
        add_text(board, LEGEND[ref], x0 - 0.6, (y0 + y1) / 2, rot=90, size=SILK)
        taken.append((x0 - 1.0, y0, x0 - 0.2, y1))
        t = fps[ref].Reference()
        t.SetTextAngleDegrees(0)
        t.SetPosition(pt((x0 + x1) / 2 - 0.3, y1 - 1.35))
    for ref, text in LEGEND.items():
        if ref in BANK:
            continue
        xy = place(ref, f'{ref} {text}')
        if xy:
            add_text(board, f'{ref} {text}', *xy, size=SILK)
    for ref, text in TP_LABEL.items():
        xy = place(ref, text, sides=True)
        if xy:
            add_text(board, text, *xy, size=SILK)
    # remaining visible refdes (ICs, switches, diode, USB-C ...)
    for ref, fp in sorted(fps.items()):
        t = fp.Reference()
        if ref in BANK or not t.IsVisible():
            continue
        xy = place(ref, ref)
        if xy:
            t.SetTextAngleDegrees(0)
            t.SetPosition(pt(*xy))
        else:
            t.SetVisible(False)
    # bottom side: title + the two warnings from the plan (mirrored, reads from below)
    for i, line in enumerate(['06-014 ESP32 INTERPOSER REV A  (DRAFT 2026-11-08)',
                              'gjcourt/lab  06-coffee-espresso/_reference/interposer-rev-a',
                              'GND = MACHINE EARTH (M3 pin 4). NEVER USB WHILE MACHINE IS PLUGGED IN.',
                              'No mains on this board. 5 V in from an isolated PSU only.']):
        t = add_text(board, line, W / 2, 24.0 + i * 1.6, layer=pcbnew.B_SilkS, size=1.0 if i == 0 else SILK)
        t.SetMirrored(True)


# ---------------------------------------------------------------------------------------------
# GND fan-out: every SMD GND pad gets a short stub and a via to the B.Cu pour, placed before
# routing. The autorouter sees them as obstacles and routes signals only; the pours join GND.
# ---------------------------------------------------------------------------------------------
VIA_D, VIA_DRILL, STUB_W, FAN_CLR = 0.6, 0.3, 0.25, 0.22
KEEPOUT_RECTS = [(59.5, -1.0, W + 1, 6.5)]  # ESP32 antenna keep-out on the board (local mm)
FAN_INWARD = {'U7', 'U11', 'U3'}  # 0.5 / 0.95 mm pitch with GND pins between signals
FAN_META: list = []  # (keep-out start, via centre) per fan-out, local mm
# B.Cu strips kept free of tracks so the bottom pour joins pockets the router would wall in:
# the LDO / module-decoupling corner down past the module to the main pour
GND_CORRIDORS = [(71.4, 18.0, 72.6, 28.0)]


def _rect_dist(px, py, r):
    x0, y0, x1, y1 = r
    dx = max(x0 - px, 0, px - x1)
    dy = max(y0 - py, 0, py - y1)
    return (dx * dx + dy * dy) ** 0.5


def _seg_rect_dist(a, b, r, n=12):
    return min(_rect_dist(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n, r) for i in range(n + 1))


def gnd_fanout(board, fps):
    gnd = board.FindNet('GND')
    obstacles = []  # (rect local mm, netname)
    for fp in fps.values():
        for pad in fp.Pads():
            bb = pad.GetBoundingBox()
            r = (pcbnew.ToMM(bb.GetLeft()) - OX, pcbnew.ToMM(bb.GetTop()) - OY,
                 pcbnew.ToMM(bb.GetRight()) - OX, pcbnew.ToMM(bb.GetBottom()) - OY)
            obstacles.append((r, pad.GetNetname(), pad))
    vias = []
    n = 0
    for ref in sorted(fps, key=lambda r: (r.rstrip('0123456789'), int(r[len(r.rstrip('0123456789')):]))):
        fp = fps[ref]
        c = fp.GetPosition()
        fcx, fcy = pcbnew.ToMM(c.x) - OX, pcbnew.ToMM(c.y) - OY
        for pad in fp.Pads():
            if pad.GetNetname() != 'GND' or pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                continue
            if ref == 'U5' and pad.GetNumber() == '41':
                continue  # EPAD: its own thermal vias reach B.Cu
            p = pad.GetPosition()
            px, py = pcbnew.ToMM(p.x) - OX, pcbnew.ToMM(p.y) - OY
            bb = pad.GetBoundingBox()
            hw, hh = pcbnew.ToMM(bb.GetWidth()) / 2, pcbnew.ToMM(bb.GetHeight()) / 2
            # outward from the part first, then the other directions; fine-pitch ICs fan in, under
            # the body, so the vias don't wall in the signal pins beside each GND pin
            ox, oy = px - fcx, py - fcy
            sign = 1 if ref in FAN_INWARD else -1
            dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
            dirs.sort(key=lambda d: sign * (d[0] * ox + d[1] * oy) / ((d[0] ** 2 + d[1] ** 2) ** 0.5))
            placed = None
            for extra in (0.0, 0.3, 0.6, 0.9, 1.2, 1.6, 2.0):
                for dx, dy in dirs:
                    norm = (dx * dx + dy * dy) ** 0.5
                    pad_part = (abs(dx) * hw + abs(dy) * hh) / norm
                    reach = pad_part + VIA_D / 2 + 0.35 + extra
                    vx, vy = px + dx / norm * reach, py + dy / norm * reach
                    if not (1.0 < vx < W - 1.0 and 1.0 < vy < H - 1.0):
                        continue
                    if any(_rect_dist(vx, vy, k) < VIA_D / 2 + 0.3 for k in KEEPOUT_RECTS):
                        continue
                    ok = True
                    for r, net, op in obstacles:
                        if op is pad:
                            continue
                        if _rect_dist(vx, vy, r) < VIA_D / 2 + FAN_CLR + (0 if net == 'GND' else 0.05):
                            ok = False; break
                        if net != 'GND' and _seg_rect_dist((px, py), (vx, vy), r) < STUB_W / 2 + 0.18:
                            ok = False; break
                    if ok and all(((vx - a) ** 2 + (vy - b) ** 2) ** 0.5 >= VIA_D + 0.3 for a, b in vias):
                        placed = (vx, vy)
                        # where the stub leaves the pad (+0.25): the DSN keep-out starts there, so
                        # it never sits against the neighbouring pins
                        s = pad_part + 0.25
                        FAN_META.append(((px + dx / norm * s, py + dy / norm * s), placed))
                        break
                if placed:
                    break
            if not placed:
                print(f'  fanout: no room for a via at {ref}.{pad.GetNumber()} (pour must reach it)')
                continue
            vx, vy = placed
            vias.append(placed)
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pt(px, py)); t.SetEnd(pt(vx, vy))
            t.SetWidth(mm(STUB_W)); t.SetLayer(pcbnew.F_Cu); t.SetNet(gnd)
            board.Add(t)
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(pt(vx, vy)); v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DRILL)); v.SetNet(gnd)
            board.Add(v)
            n += 1
    return n


def strip_gnd(board):
    """For the DSN only: GND pads become net-less obstacles, so the router leaves GND to the pours,
    and each fan-out stub + via becomes a keep-out area (KiCad does not export net-less copper)."""
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() == 'GND':
                pad.SetNetCode(0)
            # Freerouting refuses an entire net if any of its pins starts in a clearance violation.
            # U11's KiCad land has 0.15 mm gaps (< the 0.16 mm classes), so the router sees
            # 0.34 mm-wide pads (0.16 mm gaps); tracks then stay >= 0.155 mm from the real 0.35 mm
            # pads, and the board keeps the real land (DRU rule above).
            if fp.GetReference() == 'U11':
                s = pad.GetSize()
                pad.SetSize(pcbnew.VECTOR2I(min(s.x, mm(0.34)), s.y) if s.x < s.y
                            else pcbnew.VECTOR2I(s.x, min(s.y, mm(0.34))))
    for (ax, ay), (bx, by) in FAN_META:
        L = max(((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5, 1e-6)
        ux, uy = (bx - ax) / L, (by - ay) / L
        # stub on F.Cu: a strip from just outside the pad to the via; the via: a square, both layers
        r = STUB_W / 2 + 0.16
        strip = [(ax - uy * r, ay + ux * r), (bx - uy * r, by + ux * r),
                 (bx + uy * r, by - ux * r), (ax + uy * r, ay - ux * r)]
        q = VIA_D / 2 + 0.16
        square = [(bx - q, by - q), (bx + q, by - q), (bx + q, by + q), (bx - q, by + q)]
        for poly, layers in ((strip, [pcbnew.F_Cu]), (square, [pcbnew.F_Cu, pcbnew.B_Cu])):
            z = pcbnew.ZONE(board)
            z.SetIsRuleArea(True)
            z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
            z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False); z.SetDoNotAllowCopperPour(False)
            ls = pcbnew.LSET()
            for lay in layers:
                ls.AddLayer(lay)
            z.SetLayerSet(ls)
            o = z.Outline(); o.NewOutline()
            for x, y in poly:
                o.Append(mm(OX + x), mm(OY + y))
            board.Add(z)
    # B.Cu pour corridors the router must leave open (the pour itself is added after routing)
    for x0, y0, x1, y1 in GND_CORRIDORS:
        z = pcbnew.ZONE(board)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
        z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False); z.SetDoNotAllowCopperPour(False)
        z.SetLayer(pcbnew.B_Cu)
        o = z.Outline(); o.NewOutline()
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            o.Append(mm(OX + x), mm(OY + y))
        board.Add(z)
    for t in list(board.GetTracks()):
        if t.GetNetname() == 'GND':
            board.Remove(t)


def _seg_point_dist(ax, ay, bx, by, px, py):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return ((ax + t * dx - px) ** 2 + (ay + t * dy - py) ** 2) ** 0.5


def stitch(board, pitch=1.0, spacing=3.5, clr=0.3):
    """GND stitching vias on a fixed grid wherever there is room: ties the F.Cu and B.Cu pours
    together so no pour island floats. Run after routing; deterministic for a given routing."""
    gnd = board.FindNet('GND')
    segs, pts = [], []
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            q = t.GetPosition()
            pts.append((pcbnew.ToMM(q.x) - OX, pcbnew.ToMM(q.y) - OY, pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu)) / 2))
        else:
            a, b = t.GetStart(), t.GetEnd()
            segs.append((pcbnew.ToMM(a.x) - OX, pcbnew.ToMM(a.y) - OY, pcbnew.ToMM(b.x) - OX,
                         pcbnew.ToMM(b.y) - OY, pcbnew.ToMM(t.GetWidth()) / 2, t.GetNetname()))
    rects = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            bb = pad.GetBoundingBox()
            rects.append((pcbnew.ToMM(bb.GetLeft()) - OX, pcbnew.ToMM(bb.GetTop()) - OY,
                          pcbnew.ToMM(bb.GetRight()) - OX, pcbnew.ToMM(bb.GetBottom()) - OY))
    r = VIA_D / 2
    n = 0
    mine = []
    y = 2.0
    while y < H - 1.5:
        x = 2.0
        while x < W - 1.5:
            ok = all(((x - a) ** 2 + (y - b) ** 2) ** 0.5 >= spacing for a, b in mine)
            ok = ok and not any(_rect_dist(x, y, k) < r + 0.5 for k in KEEPOUT_RECTS)
            ok = ok and not any(_rect_dist(x, y, k) < r + clr for k in rects)
            ok = ok and all(((x - a) ** 2 + (y - b) ** 2) ** 0.5 >= r + w + clr for a, b, w in pts)
            ok = ok and all(_seg_point_dist(ax, ay, bx, by, x, y) >= r + w + clr for ax, ay, bx, by, w, _ in segs)
            if ok:
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(pt(x, y)); v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DRILL)); v.SetNet(gnd)
                board.Add(v)
                pts.append((x, y, r))
                mine.append((x, y))
                n += 1
            x += pitch
        y += pitch
    return n


def _pour_components(board):
    """Filled GND fragments on both layers, grouped by the vias / PTH pads that tie the layers."""
    ties = []
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == 'GND':
            ties.append(t.GetPosition())
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == 'GND' and p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                ties.append(p.GetPosition())
    nodes = []
    for z in board.Zones():
        if z.GetIsRuleArea():
            continue
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            if z.IsOnLayer(layer):
                ps = z.GetFilledPolysList(layer)
                for i in range(ps.OutlineCount()):
                    nodes.append((layer, ps.Outline(i)))
    par = list(range(len(nodes)))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for q in ties:
        hit = [k for k, (_, ol) in enumerate(nodes) if ol.PointInside(q)]
        for k in hit[1:]:
            par[find(k)] = find(hit[0])
    comps: dict[int, list[int]] = {}
    for k in range(len(nodes)):
        comps.setdefault(find(k), []).append(k)
    main = max(comps.values(), key=lambda ks: sum(abs(nodes[k][1].Area()) for k in ks))
    return nodes, main, [ks for ks in comps.values() if ks is not main]


def tie_islands(board, step=0.25):
    """For each floating GND fragment, put one via where it overlaps the main pour on the other
    layer and the spot is clear of every other net. Returns the number of vias added."""
    gnd = board.FindNet('GND')
    nodes, main, floats = _pour_components(board)
    obstacles = []
    for t in board.GetTracks():
        if t.GetNetname() == 'GND':
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            q = t.GetPosition()
            obstacles.append(('c', pcbnew.ToMM(q.x), pcbnew.ToMM(q.y), pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu)) / 2))
        else:
            a, b = t.GetStart(), t.GetEnd()
            obstacles.append(('s', pcbnew.ToMM(a.x), pcbnew.ToMM(a.y), pcbnew.ToMM(b.x), pcbnew.ToMM(b.y),
                              pcbnew.ToMM(t.GetWidth()) / 2))
    rects = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() == 'GND' and pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD:
                continue
            bb = pad.GetBoundingBox()
            rects.append((pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()),
                          pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom())))
    r, clr = VIA_D / 2, 0.25
    added = 0
    for ks in floats:
        done = False
        for k in ks:
            layer, ol = nodes[k]
            other = [nodes[m][1] for m in main if nodes[m][0] != layer]
            bb = ol.BBox()
            x0, y0, x1, y1 = (pcbnew.ToMM(v) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom()))
            y = y0 + r
            while y < y1 - r and not done:
                x = x0 + r
                while x < x1 - r and not done:
                    p = pcbnew.VECTOR2I(mm(x), mm(y))
                    if ol.PointInside(p) and any(o.PointInside(p) for o in other):
                        ok = not any(_rect_dist(x, y, q) < r + clr for q in rects)
                        for o in obstacles if ok else ():
                            d = (((x - o[1]) ** 2 + (y - o[2]) ** 2) ** 0.5 - o[3] if o[0] == 'c'
                                 else _seg_point_dist(o[1], o[2], o[3], o[4], x, y) - o[5])
                            if d < r + clr:
                                ok = False; break
                        if ok:
                            v = pcbnew.PCB_VIA(board)
                            v.SetPosition(p); v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DRILL)); v.SetNet(gnd)
                            board.Add(v)
                            added += 1
                            done = True
                    x += step
                y += step
            if done:
                break
        if not done:
            bb = nodes[ks[0]][1].BBox()
            # diagnostic only (this probe ignores same-layer GND tracks); kicad-cli DRC is the check
            print(f'  note: pour fragment at ({pcbnew.ToMM(bb.GetLeft()) - OX:.1f}, '
                  f'{pcbnew.ToMM(bb.GetTop()) - OY:.1f}) has no extra tie via')
    return added


def prune_vias(board, keep):
    """Drop stitching / tie vias that don't sit in the main GND pour on both layers (a via the
    fill left on one layer only is a dangling via); fan-out vias in `keep` stay. Refill after."""
    removed = 0
    for _ in range(3):
        nodes, main, _ = _pour_components(board)
        mains = {pcbnew.F_Cu: [nodes[k][1] for k in main if nodes[k][0] == pcbnew.F_Cu],
                 pcbnew.B_Cu: [nodes[k][1] for k in main if nodes[k][0] == pcbnew.B_Cu]}
        bad = [v for v in board.GetTracks()
               if v.Type() == pcbnew.PCB_VIA_T and v.GetNetname() == 'GND'
               and (v.GetPosition().x, v.GetPosition().y) not in keep
               and not all(any(o.PointInside(v.GetPosition()) for o in mains[l]) for l in mains)]
        if not bad:
            break
        for v in bad:
            board.Remove(v)
        removed += len(bad)
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    return removed


def zones(board):
    gnd = board.FindNet('GND')
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(gnd)
        z.SetLocalClearance(mm(0.25))
        z.SetMinThickness(mm(0.25))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(mm(0.3))
        z.SetThermalReliefSpokeWidth(mm(0.4))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        o = z.Outline()
        o.NewOutline()
        for x, y in [(0, 0), (W, 0), (W, H), (0, H)]:
            o.Append(mm(OX + x), mm(OY + y))
        board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


def stage_dsn():
    path = os.path.join(BUILD, f'{NAME}-placed.kicad_pcb')
    board, fps = build(path)
    print(f'GND fan-out vias: {gnd_fanout(board, fps)}')
    pcbnew.SaveBoard(path, board)
    strip_gnd(board)
    dsn = os.path.join(BUILD, f'{NAME}.dsn')
    if not pcbnew.ExportSpecctraDSN(board, dsn):
        raise SystemExit('DSN export failed')
    print(f'wrote {path}\nwrote {dsn}')


def stage_finish():
    path = os.path.join(HERE, f'{NAME}.kicad_pcb')
    board, fps = build(path)
    ses = os.path.join(ROUTING, f'{NAME}.ses')
    if not pcbnew.ImportSpecctraSES(board, ses):
        raise SystemExit(f'SES import failed: {ses}')
    gnd_fanout(board, fps)  # same positions the router saw as obstacles
    fanout = {(v.GetPosition().x, v.GetPosition().y) for v in board.GetTracks()
              if v.Type() == pcbnew.PCB_VIA_T and v.GetNetname() == 'GND'}
    print(f'GND stitching vias: {stitch(board)}')
    zones(board)
    for _ in range(3):  # tie any pour fragment the routing walled in, then refill
        n = tie_islands(board)
        if not n:
            break
        print(f'GND island ties: {n}')
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    print(f'GND vias pruned (not in the main pour on both layers): {prune_vias(board, fanout)}')
    pcbnew.SaveBoard(path, board)
    with open(path) as f:
        txt = f.read()
    if '(remove_unused_layers)' in txt:  # the 06-015 kiutils bug: never ship a bare flag
        raise SystemExit('bare (remove_unused_layers) in the board file')
    print(f'wrote {path}')


def board_fps(path):
    board = pcbnew.LoadBoard(path)
    return board, {fp.GetReference(): fp for fp in board.GetFootprints()}


def stage_fab():
    """BOM + CPL for JLCPCB SMT assembly: fitted parts with an LCSC number only."""
    board, fps = board_fps(os.path.join(HERE, f'{NAME}.kicad_pcb'))
    os.makedirs(FAB, exist_ok=True)
    fitted = [p for p in PARTS if not p.dnp and p.lcsc]
    groups: dict[tuple, list[str]] = {}  # one line per LCSC part (JLC loads one reel per line)
    values: dict[tuple, list[str]] = {}
    for p in fitted:
        groups.setdefault((p.fp_name, p.lcsc), []).append(p.ref)
        if p.value not in values.setdefault((p.fp_name, p.lcsc), []):
            values[(p.fp_name, p.lcsc)].append(p.value)
    groups = {(' / '.join(values[k]),) + k: v for k, v in groups.items()}

    def refkey(r):
        i = len(r.rstrip('0123456789'))
        return (r[:i], int(r[i:]))

    with open(os.path.join(FAB, f'{NAME}-BOM.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
        for (value, fpn, lcsc), refs in sorted(groups.items(), key=lambda kv: refkey(sorted(kv[1], key=refkey)[0])):
            w.writerow([value, ','.join(sorted(refs, key=refkey)), fpn, lcsc])
    # CPL: origin = board bottom-left corner, +Y up (JLC convention; the 06-015 Y-sign lesson).
    with open(os.path.join(FAB, f'{NAME}-CPL.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
        for p in sorted(fitted, key=lambda p: refkey(p.ref)):
            fp = fps[p.ref]
            pos = fp.GetPosition()
            x = pcbnew.ToMM(pos.x) - OX
            y = (OY + H) - pcbnew.ToMM(pos.y)
            rot = round(fp.GetOrientationDegrees()) % 360
            w.writerow([p.ref, f'{x:.3f}mm', f'{y:.3f}mm', 'Top', rot])
    # gerbers + drill (exported by kicad-cli into fab/gerbers) -> one zip, fixed timestamps
    gdir = os.path.join(FAB, 'gerbers')
    if os.path.isdir(gdir):
        with zipfile.ZipFile(os.path.join(FAB, f'{NAME}-gerbers.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
            for fn in sorted(os.listdir(gdir)):
                info = zipfile.ZipInfo(fn, date_time=(2026, 11, 8, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                with open(os.path.join(gdir, fn), 'rb') as f:
                    z.writestr(info, f.read())
    hand = [p.ref for p in PARTS if not p.dnp and not p.lcsc and p.jlc != 'none']
    print(f'BOM: {len(fitted)} parts in {len(groups)} lines; hand-solder (not in BOM): {" ".join(hand)}')


if __name__ == '__main__':
    stage = sys.argv[1] if len(sys.argv) > 1 else 'dsn'
    {'dsn': stage_dsn, 'finish': stage_finish, 'fab': stage_fab}[stage]()
