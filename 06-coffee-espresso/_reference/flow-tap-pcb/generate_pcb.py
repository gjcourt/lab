#!/usr/bin/env python3
"""Compact layout for the flow-tap interposer. Connectors rotated (pins facing the
U1/C1 row) and packed in a row; signals on F.Cu, GND on B.Cu. ~half the area."""
import math, sys, uuid
def uid(): return str(uuid.uuid4())
from kiutils.board import Board
from kiutils.footprint import Footprint
from kiutils.items.common import Position, Net
from kiutils.items.brditems import Segment, Via
from kiutils.items.gritems import GrLine

FPDIR = sys.argv[1] if len(sys.argv) > 1 else "fps"
OUT = sys.argv[2] if len(sys.argv) > 2 else "flow-tap.kicad_pcb"
DEBUG = "--debug" in sys.argv

board = Board().create_new()
board.generator = "kiutils-flowtap"
netnames = ["", "GND", "N_PLUS", "N_O", "V5", "N_OUT"]
board.nets = [Net(i, n) for i, n in enumerate(netnames)]
NUM = {n: i for i, n in enumerate(netnames)}

def load(name): return Footprint.from_file(f"{FPDIR}/{name}.kicad_mod")
def place(name, ref, val, x, y, rot=0):
    fp = load(name)
    fp.position = Position(x, y, rot if rot else None)
    fp.version = None; fp.generator = None; fp.tedit = None; fp.tstamp = uid()
    fp.properties["Reference"] = ref; fp.properties["Value"] = val
    for gi in fp.graphicItems:
        if getattr(gi, "type", None) == "reference":
            gi.text = ref
    board.footprints.append(fp)
    return fp

# connectors rot 270 -> pins run upward (-y) from the housing at the bottom
J1 = place("JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "J1", "GICAR_meter", 4, 14, 90)
J2 = place("JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "J2", "to_Vivaldi", 11, 14, 90)
J3 = place("JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical", "J3", "to_ito", 18, 14, 90)
U1 = place("SOT-23-5", "U1", "74LVC1G17", 7, 1.3)
C1 = place("C_0603_1608Metric", "C1", "100nF", 13, 1.3)

def setnet(fp, num, netname):
    for p in fp.pads:
        if p.number == str(num):
            p.net = Net(NUM[netname], netname); return
    raise SystemExit(f"{fp.properties.get('Reference')}: no pad {num}")

for J in (J1, J2):
    setnet(J, 2, "N_PLUS"); setnet(J, 3, "GND"); setnet(J, 4, "N_O")
setnet(U1, 2, "N_O"); setnet(U1, 3, "GND"); setnet(U1, 4, "N_OUT"); setnet(U1, 5, "V5")
setnet(C1, 1, "V5"); setnet(C1, 2, "GND")
setnet(J3, 1, "GND"); setnet(J3, 2, "N_OUT"); setnet(J3, 3, "V5")

def abspad(fp, num):
    for p in fp.pads:
        if p.number == str(num):
            a = math.radians(fp.position.angle or 0)
            px, py = p.position.X, p.position.Y
            # KiCad footprint-rotation convention (y-axis down):
            return (round(fp.position.X + px*math.cos(a) + py*math.sin(a), 4),
                    round(fp.position.Y - px*math.sin(a) + py*math.cos(a), 4))
    raise SystemExit("no pad")

if DEBUG:
    for fp in (J1, J2, J3, U1, C1):
        r = fp.properties["Reference"]
        print(r, {p.number: abspad(fp, p.number) for p in fp.pads})
    sys.exit(0)

def route(points, netname, layer="F.Cu", w=0.35):
    for a, b in zip(points, points[1:]):
        board.traceItems.append(Segment(start=Position(*a), end=Position(*b),
                                         width=w, layer=layer, net=NUM[netname], tstamp=uid()))
def via(p, netname):
    board.traceItems.append(Via(position=Position(*p), size=0.7, drill=0.35,
                                layers=["F.Cu", "B.Cu"], net=NUM[netname], tstamp=uid()))

# F.Cu signals
route([abspad(J1, 2), abspad(J2, 2)], "N_PLUS")                          # +14.3 pass-through
route([abspad(J1, 4), abspad(J2, 4)], "N_O")                            # signal pass-through
u2 = abspad(U1, 2); j14 = abspad(J1, 4)
route([j14, (j14[0], u2[1]), u2], "N_O")                                # branch to U1.2 from the LEFT (clears U1.3)
c1 = abspad(C1, 1); j33 = abspad(J3, 3)
route([abspad(U1, 5), c1, (c1[0], 0.0), (j33[0], 0.0), j33], "V5")     # V5 over the top to J3.3
j32 = abspad(J3, 2)
route([abspad(U1, 4), (16.0, abspad(U1, 4)[1]), (16.0, j32[1]), j32], "N_OUT")

# B.Cu GND (approach J3.1 from the side so it never runs over J3's V5/N_OUT pins)
g1, gj = abspad(J1, 3), abspad(J3, 1)
Y = g1[1]                                                               # spine y = 9
route([(g1[0], Y), (14.0, Y)], "GND", "B.Cu")                          # spine J1.3..J2.3..tap
route([(14.0, Y), (14.0, gj[1]), gj], "GND", "B.Cu")                   # down then across to J3.1
u3 = abspad(U1, 3); via(u3, "GND"); route([u3, (u3[0], Y)], "GND", "B.Cu")
c2 = abspad(C1, 2); via(c2, "GND"); route([c2, (c2[0], Y)], "GND", "B.Cu")

# outline — from pad extents + courtyards (so connector housings aren't clipped)
def fp_extent(fp):
    a = math.radians(fp.position.angle or 0)
    ox, oy = fp.position.X, fp.position.Y
    def tf(px, py): return (ox+px*math.cos(a)+py*math.sin(a), oy-px*math.sin(a)+py*math.cos(a))
    pts = []
    for p in fp.pads:
        cx, cy = tf(p.position.X, p.position.Y); hw, hh = p.size.X/2, p.size.Y/2
        pts += [(cx-hw, cy-hh), (cx+hw, cy+hh), (cx-hw, cy+hh), (cx+hw, cy-hh)]
    for gi in fp.graphicItems:
        if getattr(gi, "layer", "") in ("F.CrtYd", "B.CrtYd") and hasattr(gi, "start"):
            pts.append(tf(gi.start.X, gi.start.Y)); pts.append(tf(gi.end.X, gi.end.Y))
    return pts
xs, ys = [], []
for fp in board.footprints:
    for (px, py) in fp_extent(fp): xs.append(px); ys.append(py)
m = 1.2
x0, y0, x1, y1 = min(xs)-m, min(ys)-m, max(xs)+m, max(ys)+m
corners = [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
for a, b in zip(corners, corners[1:]+corners[:1]):
    board.graphicItems.append(GrLine(start=Position(round(a[0],3),round(a[1],3)),
                                      end=Position(round(b[0],3),round(b[1],3)),
                                      layer="Edge.Cuts", width=0.15, tstamp=uid()))

board.to_file(OUT)
print(f"saved {OUT}: outline {x1-x0:.1f} x {y1-y0:.1f} mm = {(x1-x0)*(y1-y0):.0f} mm^2")
