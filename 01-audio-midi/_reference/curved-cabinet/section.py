#!/usr/bin/env python3
"""Curved Elsinore cabinet — parametric section solver and DXF emitter.

The solved section is a STADIUM (capsule): a flat baffle, two straight parallel
sides, and a semicircular rear.  That falls out of choosing rear radius = half
the baffle width, which is simultaneously the most volume-efficient curve, the
cheapest to roll (one constant radius, one roller setting) and the simplest
former to cut.

Serves both 01-020 (bent lamination) and 01-021 (rolled aluminium) from one
model: they share the section and differ only in the manufacturing output.

Usage:  python3 section.py            # summary + all DXF
        python3 section.py --volume 75 --thickness 5
"""
import argparse, math, os

# --- as-built reference, from the Onshape model "Elsinore v6.1" (see 01-017)
BAFFLE_W   = 228.6     # mm  FIXED: Joe's driver-array spacing
INT_HEIGHT = 1099.8    # mm  as-built
TARGET_L   = 78.1      # L   internal gross, matches the existing cabinet
EXT_DEPTH_EXISTING = 380.9


def solve_depth(baffle_w, height, target_l):
    """Stadium section: rear radius = baffle_w/2.  Solve internal depth."""
    r = baffle_w / 2.0
    area_needed = target_l * 1e6 / height           # mm^2
    semi = math.pi * r * r / 2.0
    straight = (area_needed - semi) / baffle_w      # length of parallel run
    if straight < 0:
        raise SystemExit("target volume too small for this baffle width")
    return straight + r, straight, r


def section_metrics(baffle_w, height, target_l, t):
    depth, straight, r = solve_depth(baffle_w, height, target_l)
    area = straight * baffle_w + math.pi * r * r / 2.0
    vol = area * height / 1e6
    wrap_inner = 2 * straight + math.pi * r
    wrap_neutral = 2 * straight + math.pi * (r + t / 2.0)
    wrap_outer = 2 * straight + math.pi * (r + t)
    return dict(depth=depth, straight=straight, r=r, area=area, vol=vol,
                wrap_inner=wrap_inner, wrap_neutral=wrap_neutral,
                wrap_outer=wrap_outer)


# ---------- minimal R12 ASCII DXF ----------
def _hdr():  return "0\nSECTION\n2\nENTITIES\n"
def _ftr():  return "0\nENDSEC\n0\nEOF\n"
def _line(x1, y1, x2, y2, layer="0"):
    return (f"0\nLINE\n8\n{layer}\n10\n{x1:.4f}\n20\n{y1:.4f}\n30\n0.0\n"
            f"11\n{x2:.4f}\n21\n{y2:.4f}\n31\n0.0\n")
def _arc(cx, cy, rad, a0, a1, layer="0"):
    return (f"0\nARC\n8\n{layer}\n10\n{cx:.4f}\n20\n{cy:.4f}\n30\n0.0\n"
            f"40\n{rad:.4f}\n50\n{a0:.4f}\n51\n{a1:.4f}\n")

def stadium(cx0, r, straight, layer="0", close_baffle=True):
    """Stadium outline with the flat face at x=0, opening to +x."""
    s = ""
    if close_baffle:
        s += _line(0, -r, 0, r, layer)                     # baffle
    s += _line(0, r, straight, r, layer)                   # top side
    s += _line(0, -r, straight, -r, layer)                 # bottom side
    s += _arc(straight, 0, r, -90, 90, layer)              # rear semicircle
    return s


def write(path, body):
    with open(path, "w") as f:
        f.write(_hdr() + body + _ftr())
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--volume", type=float, default=TARGET_L)
    ap.add_argument("--baffle", type=float, default=BAFFLE_W)
    ap.add_argument("--height", type=float, default=INT_HEIGHT)
    ap.add_argument("--thickness", type=float, default=4.0, help="shell wall, mm")
    ap.add_argument("--springback", type=float, default=1.5,
                    help="%% radius growth to compensate in the former")
    ap.add_argument("--outdir", default=".")
    a = ap.parse_args()

    m = section_metrics(a.baffle, a.height, a.volume, a.thickness)
    r, straight, depth = m["r"], m["straight"], m["depth"]

    print(f"CURVED ELSINORE SECTION — stadium (flat baffle + parallel sides + semicircular rear)\n")
    print(f"  target volume        {a.volume:8.1f} L      (achieved {m['vol']:.2f} L)")
    print(f"  baffle width         {a.baffle:8.1f} mm     FIXED — driver array")
    print(f"  internal height      {a.height:8.1f} mm")
    print(f"  rear radius          {r:8.1f} mm     = baffle/2, full bullnose")
    print(f"  straight run         {straight:8.1f} mm     each side")
    print(f"  internal depth       {depth:8.1f} mm")
    print(f"  section area         {m['area']/100:8.1f} cm2")
    ext_depth = depth + 19.05 + 25.4
    print(f"\n  external depth       {ext_depth:8.1f} mm     "
          f"(vs existing {EXT_DEPTH_EXISTING}: {ext_depth-EXT_DEPTH_EXISTING:+.1f} mm)")
    print(f"\n  wrap, inner surface  {m['wrap_inner']:8.1f} mm")
    print(f"  wrap, neutral axis   {m['wrap_neutral']:8.1f} mm   <- ROLLING BLANK at t={a.thickness} mm")
    print(f"  wrap, outer surface  {m['wrap_outer']:8.1f} mm")

    blank_w = m["wrap_neutral"]
    for name, (sw, sl) in {"1220 x 2440": (1220, 2440), "1500 x 3000": (1500, 3000)}.items():
        n = max(int(sl // blank_w) if a.height <= sw else 0,
                int(sw // blank_w) if a.height <= sl else 0)
        print(f"    sheet {name:12} -> {n} blank(s) of {a.height:.0f} x {blank_w:.0f} mm   (need 2)")

    former_r = r / (1 + a.springback / 100.0)
    print(f"\n  former radius        {former_r:8.2f} mm     "
          f"({a.springback}% springback allowance, from {r:.1f})")

    od = a.outdir
    os.makedirs(od, exist_ok=True)
    outs = []
    outs.append(write(os.path.join(od, "section-internal.dxf"),
                      stadium(0, r, straight, "INTERNAL")))
    body = stadium(0, r, straight, "INTERNAL")
    body += stadium(0, r + a.thickness, straight, "EXTERNAL", close_baffle=False)
    outs.append(write(os.path.join(od, f"section-shell-{a.thickness:g}mm.dxf"), body))
    outs.append(write(os.path.join(od, "former.dxf"),
                      stadium(0, former_r, straight, "FORMER")))
    fp = _line(0, 0, blank_w, 0) + _line(blank_w, 0, blank_w, a.height) \
       + _line(blank_w, a.height, 0, a.height) + _line(0, a.height, 0, 0) \
       + _line(straight, 0, straight, a.height, "ROLL_START") \
       + _line(blank_w - straight, 0, blank_w - straight, a.height, "ROLL_END")
    outs.append(write(os.path.join(od, f"flat-pattern-{a.thickness:g}mm.dxf"), fp))
    print("\n  DXF written (import into Onshape as a sketch):")
    for o in outs:
        print(f"    {o}")

if __name__ == "__main__":
    main()
