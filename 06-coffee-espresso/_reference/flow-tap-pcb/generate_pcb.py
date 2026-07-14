#!/usr/bin/env python3
"""Native (kiutils) generator for the GICAR flow-tap interposer (06-015).
Signals on F.Cu (routed around pad rows), GND on B.Cu (never crosses signals).
No zone fill needed. Validate with kicad-cli."""
import math, sys, uuid
def uid(): return str(uuid.uuid4())
from kiutils.board import Board
from kiutils.footprint import Footprint
from kiutils.items.common import Position, Net
from kiutils.items.brditems import Segment, Via
from kiutils.items.gritems import GrLine

FPDIR = sys.argv[1] if len(sys.argv) > 1 else "fps"
OUT = sys.argv[2] if len(sys.argv) > 2 else "flow-tap.kicad_pcb"

board = Board().create_new()
board.generator = "kiutils-flowtap"

netnames = ["", "GND", "N_PLUS", "N_O", "V5", "N_OUT"]
board.nets = [Net(i, n) for i, n in enumerate(netnames)]
NUM = {n: i for i, n in enumerate(netnames)}

def load(name): return Footprint.from_file(f"{FPDIR}/{name}.kicad_mod")
def place(name, ref, val, x, y, rot=0):
    fp = load(name)
    fp.position = Position(x, y, rot if rot else None)
    fp.version = None; fp.generator = None; fp.tedit = None   # strip standalone-lib tokens
    fp.tstamp = uid()
    fp.properties["Reference"] = ref
    fp.properties["Value"] = val
    # keep the silk ${REFERENCE} fp_text in sync so the render shows the designator
    for gi in fp.graphicItems:
        if getattr(gi, "type", None) == "reference":
            gi.text = ref
    board.footprints.append(fp)
    return fp

J1 = place("JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "J1", "GICAR_meter", 5, 3)
J2 = place("JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "J2", "to_Vivaldi", 5, 19)
U1 = place("SOT-23-5", "U1", "74LVC1G17", 18, 11)
C1 = place("C_0603_1608Metric", "C1", "100nF", 22.5, 11)
J3 = place("JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical", "J3", "to_ito", 28, 14)

def setnet(fp, num, netname):
    for p in fp.pads:
        if p.number == str(num):
            p.net = Net(NUM[netname], netname); return
    raise SystemExit(f"{fp.entryName}: no pad {num}")

for J in (J1, J2):                       # XH-4: 1 keyed-blank(NC), 2 +14.3V, 3 GND, 4 signal
    setnet(J, 2, "N_PLUS"); setnet(J, 3, "GND"); setnet(J, 4, "N_O")
setnet(U1, 2, "N_O"); setnet(U1, 3, "GND"); setnet(U1, 4, "N_OUT"); setnet(U1, 5, "V5")  # 1=NC
setnet(C1, 1, "V5"); setnet(C1, 2, "GND")
setnet(J3, 1, "GND"); setnet(J3, 2, "N_OUT"); setnet(J3, 3, "V5")

def abspad(fp, num):
    for p in fp.pads:
        if p.number == str(num):
            a = math.radians(fp.position.angle or 0)
            px, py = p.position.X, p.position.Y
            return (fp.position.X + px*math.cos(a) - py*math.sin(a),
                    fp.position.Y + px*math.sin(a) + py*math.cos(a))
    raise SystemExit("no pad")

def route(points, netname, layer="F.Cu", w=0.35):
    for a, b in zip(points, points[1:]):
        board.traceItems.append(Segment(start=Position(round(a[0],4), round(a[1],4)),
                                         end=Position(round(b[0],4), round(b[1],4)),
                                         width=w, layer=layer, net=NUM[netname], tstamp=uid()))
def via(p, netname):
    board.traceItems.append(Via(position=Position(round(p[0],4), round(p[1],4)),
                                size=0.7, drill=0.35, layers=["F.Cu", "B.Cu"], net=NUM[netname], tstamp=uid()))

# ---- F.Cu signals ----
route([abspad(J1, 2), abspad(J2, 2)], "N_PLUS")                       # +14.3 straight-through
no_x = abspad(J1, 4)[0]
route([abspad(J1, 4), abspad(J2, 4)], "N_O")                         # signal straight-through
route([(no_x, abspad(U1, 2)[1]), abspad(U1, 2)], "N_O")             # branch to U1 input (T)
j33 = abspad(J3, 3)
route([abspad(U1, 5), (20.5, 10.05), (20.5, 11.0), abspad(C1, 1),    # V5: U1.VCC -> C1 -> J3.3
       (21.725, 8.5), (j33[0], 8.5), j33], "V5")
j32 = abspad(J3, 2)
route([abspad(U1, 4), (19.137, 13.0), (j32[0], 13.0), j32], "N_OUT")  # buffered out

# ---- B.Cu GND (own layer -> free of signal crossings) ----
g13, g23 = abspad(J1, 3), abspad(J2, 3)   # x-aligned spine, x = 10
sx = g13[0]
route([g13, g23], "GND", "B.Cu")                                     # spine J1.3 <-> J2.3
route([(sx, 16.0), abspad(J3, 1)], "GND", "B.Cu")                    # branch (leaves spine at y16) -> J3.1
u3 = abspad(U1, 3); via(u3, "GND"); route([u3, (sx, u3[1])], "GND", "B.Cu")   # U1 GND -> spine
c2 = abspad(C1, 2); via(c2, "GND"); route([c2, abspad(J3, 1)], "GND", "B.Cu")  # C1 GND -> J3.1 pad

# ---- board outline (Edge.Cuts) from placement bbox ----
xs, ys = [], []
for fp in board.footprints:
    for p in fp.pads:
        ax, ay = abspad(fp, p.number)
        xs.append(ax); ys.append(ay)
m = 3.8
x0, y0, x1, y1 = min(xs)-m, min(ys)-m, max(xs)+m, max(ys)+m
corners = [(x0,y0), (x1,y0), (x1,y1), (x0,y1)]
for a, b in zip(corners, corners[1:]+corners[:1]):
    board.graphicItems.append(GrLine(start=Position(round(a[0],3),round(a[1],3)),
                                      end=Position(round(b[0],3),round(b[1],3)),
                                      layer="Edge.Cuts", width=0.15, tstamp=uid()))

board.to_file(OUT)
print(f"saved {OUT}: {len(board.footprints)} fps, {len(board.traceItems)} traces, "
      f"outline {x1-x0:.1f} x {y1-y0:.1f} mm")
