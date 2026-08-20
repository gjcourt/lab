#!/usr/bin/env python3
"""Curved Elsinore cabinet — parametric section solver and DXF emitter.

Section: flat baffle, two tangent sides, and a stern arc of chosen radius.

  --stern 114.3  (= baffle/2)  degenerates to a STADIUM — parallel sides, no
                 taper, most volume-efficient, exactly the existing footprint.
  --stern  80    30% narrowing — visibly tapered, GamuT-ish, +56 mm depth.
  --stern  60    47% narrowing — strong taper, +97 mm depth.

Taper is not free: it removes area, which must be bought back with depth or
height.  A dramatic stern at useful volume is why the GamuT Zodiac is 1650 mm
tall.  ⚠ Height is CONSTRAINED here — the tweeter sits at seated ear level and
that geometry must be preserved, so extra height can only go BELOW the array as
a plinth, never above.

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


def _section_at(baffle_w, depth, stern_r, n=400):
    """Tapered section: flat baffle, two tangent lines to a stern circle, stern arc.
    Area by shoelace over a densified outline — the closed form is error-prone and
    a simplified version of it produced a 200 mm error once already."""
    hw = baffle_w / 2.0
    cx = depth - stern_r
    if cx <= 0:
        return None
    dd = math.hypot(cx, hw)
    if dd <= stern_r:
        return None
    tl = math.sqrt(dd * dd - stern_r * stern_r)
    th = math.atan2(-hw, cx) + math.asin(stern_r / dd)
    tx = tl * math.cos(th)
    ty = hw + tl * math.sin(th)
    phi = math.atan2(ty, tx - cx)
    pts = [(0.0, 0.0), (0.0, hw), (tx, ty)]
    for i in range(n + 1):
        a = phi * (1 - i / n)
        pts.append((cx + stern_r * math.cos(a), stern_r * math.sin(a)))
    A = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        A += x1 * y2 - x2 * y1
    return dict(area=abs(A), tx=tx, ty=ty, cx=cx, phi=phi, hw=hw, r=stern_r,
                tangent_len=math.hypot(tx, ty - hw))


def solve_depth(baffle_w, height, target_l, stern_r=None):
    """Solve internal depth for a target volume. stern_r=baffle_w/2 -> stadium."""
    if stern_r is None:
        stern_r = baffle_w / 2.0
    stern_r = min(stern_r, baffle_w / 2.0)
    tv = target_l * 1e6
    lo, hi = stern_r * 1.001, 4000.0
    for _ in range(400):
        mid = (lo + hi) / 2
        g = _section_at(baffle_w, mid, stern_r)
        if g is None:
            lo = mid
            continue
        lo, hi = (mid, hi) if g["area"] * height < tv else (lo, mid)
    depth = (lo + hi) / 2
    g = _section_at(baffle_w, depth, stern_r)
    return depth, g, stern_r


def section_metrics(baffle_w, height, target_l, t, stern_r=None):
    depth, g, r = solve_depth(baffle_w, height, target_l, stern_r)
    area = g["area"]
    tl, phi = g["tangent_len"], g["phi"]
    return dict(depth=depth, area=area, vol=area * height / 1e6, r=r, g=g,
                tangent_len=tl, stern_arc_deg=math.degrees(phi) * 2,
                stern_width=2 * r, narrowing=100 * (1 - 2 * r / baffle_w),
                wrap_inner=2 * tl + 2 * r * phi,
                wrap_neutral=2 * tl + 2 * (r + t / 2.0) * phi,
                wrap_outer=2 * tl + 2 * (r + t) * phi)


# ---------- minimal R12 ASCII DXF ----------
def _hdr():  return "0\nSECTION\n2\nENTITIES\n"
def _ftr():  return "0\nENDSEC\n0\nEOF\n"
def _line(x1, y1, x2, y2, layer="0"):
    return (f"0\nLINE\n8\n{layer}\n10\n{x1:.4f}\n20\n{y1:.4f}\n30\n0.0\n"
            f"11\n{x2:.4f}\n21\n{y2:.4f}\n31\n0.0\n")
def _arc(cx, cy, rad, a0, a1, layer="0"):
    return (f"0\nARC\n8\n{layer}\n10\n{cx:.4f}\n20\n{cy:.4f}\n30\n0.0\n"
            f"40\n{rad:.4f}\n50\n{a0:.4f}\n51\n{a1:.4f}\n")

def outline(g, layer="0", close_baffle=True, grow=0.0):
    """Tapered outline: flat baffle at x=0, tangent sides, stern arc.
    grow offsets the stern radius and half-width outward (for an outer shell)."""
    hw, tx, ty, cx, r = g["hw"] + grow, g["tx"], g["ty"], g["cx"], g["r"] + grow
    phi = math.degrees(g["phi"])
    s = ""
    if close_baffle:
        s += _line(-grow, -hw, -grow, hw, layer)
    s += _line(-grow, hw, tx, ty + grow, layer)
    s += _line(-grow, -hw, tx, -(ty + grow), layer)
    s += _arc(cx, 0, r, -phi, phi, layer)
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
    ap.add_argument("--stern", type=float, default=80.0,
                    help="stern radius mm; baffle/2 (114.3) = stadium, no taper")
    ap.add_argument("--springback", type=float, default=1.5,
                    help="%% radius growth to compensate in the former")
    ap.add_argument("--outdir", default=".")
    a = ap.parse_args()

    m = section_metrics(a.baffle, a.height, a.volume, a.thickness, a.stern)
    r, depth, g = m["r"], m["depth"], m["g"]

    print("CURVED ELSINORE SECTION — flat baffle, tangent sides, stern arc\n")
    print(f"  target volume        {a.volume:8.1f} L      (achieved {m['vol']:.2f} L)")
    print(f"  baffle width         {a.baffle:8.1f} mm     FIXED — driver array")
    print(f"  internal height      {a.height:8.1f} mm")
    print(f"  stern radius         {r:8.1f} mm     (stern width {m['stern_width']:.1f} = {m['narrowing']:.1f}% narrowing)")
    print(f"  tangent run          {m['tangent_len']:8.1f} mm     each side")
    print(f"  stern arc            {m['stern_arc_deg']:8.1f} deg")
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
                      outline(g, "INTERNAL")))
    body = outline(g, "INTERNAL")
    body += outline(g, "EXTERNAL", close_baffle=False, grow=a.thickness)
    outs.append(write(os.path.join(od, f"section-shell-{a.thickness:g}mm.dxf"), body))
    _, gf, _ = solve_depth(a.baffle, a.height, a.volume, r / (1 + a.springback / 100.0))
    outs.append(write(os.path.join(od, "former.dxf"), outline(gf, "FORMER")))
    fp = _line(0, 0, blank_w, 0) + _line(blank_w, 0, blank_w, a.height) \
       + _line(blank_w, a.height, 0, a.height) + _line(0, a.height, 0, 0) \
       + _line(m["tangent_len"], 0, m["tangent_len"], a.height, "ROLL_START") \
       + _line(blank_w - m["tangent_len"], 0, blank_w - m["tangent_len"], a.height, "ROLL_END")
    outs.append(write(os.path.join(od, f"flat-pattern-{a.thickness:g}mm.dxf"), fp))
    print("\n  DXF written (import into Onshape as a sketch):")
    for o in outs:
        print(f"    {o}")

if __name__ == "__main__":
    main()
