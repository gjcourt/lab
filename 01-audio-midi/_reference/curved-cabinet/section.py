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


def _bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        m = 1 - t
        out.append((m**3 * p0[0] + 3*m*m*t * p1[0] + 3*m*t*t * p2[0] + t**3 * p3[0],
                    m**3 * p0[1] + 3*m*m*t * p1[1] + 3*m*t*t * p2[1] + t**3 * p3[1]))
    return out


def _hull_at(baffle_w, max_w, depth, stern_r, peak=0.55, tension=0.55, n=200):
    """Bulged hull: baffle stays baffle_w, cabinet widens to max_w behind it, then
    a smooth cubic runs tangent into the stern arc.

    Widening BEHIND the baffle adds volume without touching baffle width — and
    baffle width is the one dimension carrying acoustic design (driver-to-edge
    distance sets diffraction; Joe measured a 750 Hz dip he attributes to it)."""
    hw = baffle_w / 2.0
    hm = max_w / 2.0
    cx = depth - stern_r
    xp = peak * depth
    dd = math.hypot(cx - xp, hm)
    if cx <= 0 or dd <= stern_r:
        return None
    tl = math.sqrt(dd * dd - stern_r * stern_r)
    th = math.atan2(-hm, cx - xp) + math.asin(stern_r / dd)
    tx = xp + tl * math.cos(th)
    ty = hm + tl * math.sin(th)
    phi = math.atan2(ty, tx - cx)
    up = _bezier((0.0, hw), (tension * xp, hm),
                 (tx - tension * (tx - xp), ty + (hm - ty) * 0.6), (tx, ty), n)
    arc = [(cx + stern_r * math.cos(phi * (1 - i / n)),
            stern_r * math.sin(phi * (1 - i / n))) for i in range(n + 1)]
    pts = [(0.0, 0.0)] + up + arc
    A = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        A += x1 * y2 - x2 * y1
    wrap = 0.0
    outline_pts = up + arc
    for i in range(len(outline_pts) - 1):
        wrap += math.hypot(outline_pts[i+1][0] - outline_pts[i][0],
                           outline_pts[i+1][1] - outline_pts[i][1])
    return dict(area=abs(A), tx=tx, ty=ty, cx=cx, phi=phi, hw=hw, hm=hm,
                r=stern_r, up=up, arc=arc, wrap_half=wrap,
                tangent_len=math.hypot(tx, ty - hw))


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


def solve_depth(baffle_w, height, target_l, stern_r=None, max_w=None, peak=0.55):
    """Solve internal depth for a target volume.

    max_w=None            -> tangent taper from the baffle (stern_r = baffle_w/2 is a stadium)
    max_w > baffle_w      -> bulged hull; baffle untouched, cabinet widens behind it
    """
    if stern_r is None:
        stern_r = baffle_w / 2.0
    bulged = max_w is not None and max_w > baffle_w
    if not bulged:
        stern_r = min(stern_r, baffle_w / 2.0)
    tv = target_l * 1e6
    lo, hi = stern_r * 1.001, 4000.0
    for _ in range(400):
        mid = (lo + hi) / 2
        g = (_hull_at(baffle_w, max_w, mid, stern_r, peak) if bulged
             else _section_at(baffle_w, mid, stern_r))
        if g is None:
            lo = mid
            continue
        lo, hi = (mid, hi) if g["area"] * height < tv else (lo, mid)
    depth = (lo + hi) / 2
    g = (_hull_at(baffle_w, max_w, depth, stern_r, peak) if bulged
         else _section_at(baffle_w, depth, stern_r))
    return depth, g, stern_r


def section_metrics(baffle_w, height, target_l, t, stern_r=None, max_w=None, peak=0.55):
    depth, g, r = solve_depth(baffle_w, height, target_l, stern_r, max_w, peak)
    if "wrap_half" in g:            # bulged hull: wrap measured along the outline
        wi = 2 * g["wrap_half"]
        achieved = 2 * max(abs(y) for _, y in (g["up"] + g["arc"]))
        return dict(depth=depth, area=g["area"], vol=g["area"] * height / 1e6, r=r, g=g,
                    tangent_len=g["tangent_len"], stern_arc_deg=math.degrees(g["phi"]) * 2,
                    stern_width=2 * r, max_w=max_w, achieved_w=achieved,
                    narrowing=100 * (1 - 2 * r / achieved),
                    wrap_inner=wi, wrap_neutral=wi + math.pi * t,
                    wrap_outer=wi + 2 * math.pi * t)
    area = g["area"]
    tl, phi = g["tangent_len"], g["phi"]
    return dict(depth=depth, area=area, vol=area * height / 1e6, r=r, g=g,
                tangent_len=tl, stern_arc_deg=math.degrees(phi) * 2,
                stern_width=2 * r, narrowing=100 * (1 - 2 * r / baffle_w),
                wrap_inner=2 * tl + 2 * r * phi,
                wrap_neutral=2 * tl + 2 * (r + t / 2.0) * phi,
                wrap_outer=2 * tl + 2 * (r + t) * phi)


# ---------- minimal R12 ASCII DXF ----------
def _hdr():
    """R12 header declaring MILLIMETRES.

    Without $INSUNITS the importer has to guess, and a wrong guess scales the
    part by 25.4.  This bit me: the first DXFs shipped with no HEADER at all."""
    return ("0\nSECTION\n2\nHEADER\n"
            "9\n$INSUNITS\n70\n4\n"          # 4 = millimeters
            "9\n$MEASUREMENT\n70\n1\n"       # 1 = metric
            "0\nENDSEC\n"
            "0\nSECTION\n2\nENTITIES\n")
def _ftr():  return "0\nENDSEC\n0\nEOF\n"
def _line(x1, y1, x2, y2, layer="0"):
    return (f"0\nLINE\n8\n{layer}\n10\n{x1:.4f}\n20\n{y1:.4f}\n30\n0.0\n"
            f"11\n{x2:.4f}\n21\n{y2:.4f}\n31\n0.0\n")
def _arc(cx, cy, rad, a0, a1, layer="0"):
    return (f"0\nARC\n8\n{layer}\n10\n{cx:.4f}\n20\n{cy:.4f}\n30\n0.0\n"
            f"40\n{rad:.4f}\n50\n{a0:.4f}\n51\n{a1:.4f}\n")

def outline_hull(g, layer="0", close_baffle=True):
    """Polyline outline for the bulged hull (Bezier + arc), mirrored."""
    top = g["up"] + g["arc"]
    pts = top + [(x, -y) for x, y in reversed(top)]
    s = ""
    if close_baffle:
        s += _line(0, -g["hw"], 0, g["hw"], layer)
    for i in range(len(pts) - 1):
        s += _line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], layer)
    return s


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
    ap.add_argument("--maxwidth", type=float, default=280.0,
                    help="max cabinet width mm (bulges BEHIND the baffle). "
                         "Set equal to --baffle for no bulge.")
    ap.add_argument("--peak", type=float, default=0.55,
                    help="where max width sits, as a fraction of depth")
    ap.add_argument("--springback", type=float, default=1.5,
                    help="%% radius growth to compensate in the former")
    ap.add_argument("--outdir", default=".")
    a = ap.parse_args()

    mw = a.maxwidth if a.maxwidth > a.baffle else None
    m = section_metrics(a.baffle, a.height, a.volume, a.thickness, a.stern, mw, a.peak)
    r, depth, g = m["r"], m["depth"], m["g"]

    print("CURVED ELSINORE SECTION — flat baffle, tangent sides, stern arc\n")
    print(f"  target volume        {a.volume:8.1f} L      (achieved {m['vol']:.2f} L)")
    print(f"  baffle width         {a.baffle:8.1f} mm     FIXED — driver array")
    print(f"  internal height      {a.height:8.1f} mm")
    if mw:
        print(f"  max width ACHIEVED   {m['achieved_w']:8.1f} mm     bulges behind the baffle (baffle untouched)")
        print(f"    (--maxwidth {mw:.0f} is a Bezier CONTROL value; the curve does not")
        print(f"     reach it — it is bounded by the control hull)")
        print(f"  bulge peak at        {a.peak*100:8.0f} %      of depth")
    print(f"  stern radius         {r:8.1f} mm     (stern width {m['stern_width']:.1f} = {m['narrowing']:.1f}% narrowing)")
    print(f"  tangent run          {m['tangent_len']:8.1f} mm     each side")
    print(f"  stern arc            {m['stern_arc_deg']:8.1f} deg")
    print(f"  internal depth       {depth:8.1f} mm")
    print(f"  section area         {m['area']/100:8.1f} cm2")
    # External depth = internal + baffle stack + STERN WALL.
    # The stern wall was missing from an earlier version of this: the existing
    # cabinet is internal 311.05 + front 19.05 + front-sub 25.4 + REAR 25.4 =
    # 380.9, and a curved shell still has thickness at the stern even though it
    # has no flat rear panel.
    BAFFLE_STACK = 19.05 + 25.4
    ext_depth = depth + BAFFLE_STACK + a.thickness
    print(f"\n  baffle stack         {BAFFLE_STACK:8.2f} mm     (front 19.05 + sub 25.4)")
    print(f"  stern wall           {a.thickness:8.2f} mm")
    print(f"  external depth       {ext_depth:8.1f} mm     "
          f"(vs existing {EXT_DEPTH_EXISTING}: {ext_depth-EXT_DEPTH_EXISTING:+.1f} mm)")
    for t_alt, label in ((4.0, "aluminium 4 mm"), (25.4, "laminated 1 in")):
        e = depth + BAFFLE_STACK + t_alt
        print(f"    as {label:16} -> {e:7.1f} mm ({e-EXT_DEPTH_EXISTING:+.1f})")
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
    draw = outline_hull if mw else outline
    outs.append(write(os.path.join(od, "section-internal.dxf"), draw(g, "INTERNAL")))
    body = draw(g, "INTERNAL")
    if not mw:
        body += outline(g, "EXTERNAL", close_baffle=False, grow=a.thickness)
    outs.append(write(os.path.join(od, f"section-shell-{a.thickness:g}mm.dxf"), body))
    _, gf, _ = solve_depth(a.baffle, a.height, a.volume,
                           r / (1 + a.springback / 100.0), mw, a.peak)
    outs.append(write(os.path.join(od, "former.dxf"), draw(gf, "FORMER")))
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
