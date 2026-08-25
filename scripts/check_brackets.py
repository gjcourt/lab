#!/usr/bin/env python3
"""Verify the printed brackets' STL geometry against their measured inputs.

These meshes get sent to a print service and bolted to a machine. A stale STL,
a wrong bolt pattern or an accidental valve-ghost export all look fine in a file
listing and only fail once the part is in your hand.

Each SPEC below restates the numbers from the bracket's "Measured input" table
in _reference/brackets/README.md. The check is that the mesh AGREES with them --
it cannot tell you the measurements match the machine, only that the part
matches what was measured.

Run: python3 scripts/check_brackets.py
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

BRACKETS = Path("06-coffee-espresso/_reference/brackets")

SPECS = {
    "mini-v2-solenoid-riser": {
        "bbox": (60.0, 30.0, 26.0),          # v2: Y shortened 69 -> 60
        "z_planes": [0.0, 7.0, 26.0],        # bottom, flange thickness, top
        # (x, y, diameter, z_face, what it is)
        #
        # Only OUTER faces are listed. Where the Ø9 bore meets the Ø5.5 hole
        # inside the solid there is no tessellated ring -- the cylinder walls
        # are continuous vertical facets -- so an internal transition cannot be
        # checked this way. The through path is established by the pair: Ø9 up
        # from the bottom face and Ø5.5 down from the top, coaxial.
        "holes": [
            (0.0, -11.5, 5.5, 26.0, "valve bolt, M5 clearance"),
            (0.0, 11.5, 5.5, 26.0, "valve bolt, M5 clearance"),
            (0.0, -11.5, 9.0, 0.0, "socket-head access bore"),
            (0.0, 11.5, 9.0, 0.0, "socket-head access bore"),
            (0.0, -24.25, 5.5, 0.0, "base bolt, M5 clearance"),
            (0.0, 24.25, 5.5, 0.0, "base bolt, M5 clearance"),
        ],
        # Coaxial pairs that together form one through path.
        "coaxial": [((0.0, -11.5), 26.0, 0.0), ((0.0, 11.5), 26.0, 0.0)],
        # Measured FROM THE MESH, not restated from the hole list above.
        "bolt_ctc": (23.0, 26.0, "valve base holes, centre-to-centre"),
        # The valve ghost is ~42 mm of coil on top of the 26 mm stand-off. If it
        # is in the mesh the export forgot -D SHOW_VALVE=false and the part is
        # not printable.
        "max_z": 30.0,
    },
}

TOL = 0.15


def load(stl: Path):
    txt = stl.read_text(errors="replace")
    if not txt.lstrip().startswith("solid"):
        raise SystemExit(f"{stl}: expected an ASCII STL")
    return [
        (float(a), float(b), float(c))
        for a, b, c in re.findall(
            r"vertex\s+(-?[\d.eE+-]+)\s+(-?[\d.eE+-]+)\s+(-?[\d.eE+-]+)", txt
        )
    ]


def ring_at(verts, z, cx, cy, d_hint, tol=0.05):
    """(diameter, centre) of the vertex ring near (cx, cy) on plane z, or None.

    The centre is recomputed from the matched points rather than assumed, so a
    hole that drifted from its nominal position is measurable rather than just
    absent.
    """
    # Deduplicate: a vertex appears once per facet that shares it, so a raw
    # list weights the centroid by facet count and drifts it off centre. That
    # read a true 23.000 mm bolt spacing as 22.713.
    pts = list({(round(x, 4), round(y, 4)) for x, y, zz in verts if abs(zz - z) < tol})
    # Capture window scales with the hole. A fixed radius reaches the core edge
    # (y = +/-18.5 on the top face) and drags face vertices into the centroid,
    # which shifted a measured 23.000 mm bolt spacing to 22.713.
    near = [p for p in pts if math.dist(p, (cx, cy)) < d_hint * 0.9]
    if len(near) < 12:
        return None
    mx = sum(p[0] for p in near) / len(near)
    my = sum(p[1] for p in near) / len(near)
    r = [math.dist(p, (mx, my)) for p in near]
    if max(r) - min(r) > 0.35:
        return None
    return 2 * sum(r) / len(r), (mx, my)


def check(name, spec) -> list[str]:
    stl = BRACKETS / f"{name}.stl"
    if not stl.exists():
        return [f"{name}: {stl} missing"]
    v = load(stl)
    fail = []

    dims = [max(a[i] for a in v) - min(a[i] for a in v) for i in range(3)]
    for got, want, ax in zip(sorted(dims, reverse=True),
                             sorted(spec["bbox"], reverse=True), "XYZ"):
        if abs(got - want) > TOL:
            fail.append(f"{name}: bbox {got:.3f} != {want} mm")

    zmax = max(a[2] for a in v)
    if zmax > spec["max_z"]:
        fail.append(
            f"{name}: Z reaches {zmax:.1f} mm (limit {spec['max_z']}). The valve "
            f"ghost is probably in the mesh -- re-export with -D SHOW_VALVE=false"
        )

    planes = {round(a[2], 2) for a in v}
    for z in spec["z_planes"]:
        if not any(abs(z - p) < 0.05 for p in planes):
            fail.append(f"{name}: no geometry on the z={z} plane")

    for x, y, d, z, what in spec["holes"]:
        got = ring_at(v, z, x, y, d)
        if got is None:
            fail.append(f"{name}: no opening at ({x}, {y}) on z={z} -- {what}")
            continue
        if abs(got[0] - d) > TOL:
            fail.append(
                f"{name}: hole at ({x}, {y}) z={z} is Ø{got[0]:.2f}, want Ø{d} -- {what}"
            )
        # The centre is recomputed from the matched points, so a displaced hole
        # is FOUND at its true position rather than reported missing. Without
        # this the finder silently self-corrects and a shifted bolt pattern
        # passes.
        off = math.dist(got[1], (x, y))
        if off > TOL:
            fail.append(
                f"{name}: hole at z={z} sits {off:.3f} mm from its nominal "
                f"({x}, {y}) -- {what}"
            )

    # A bolt only passes if the two openings are coaxial.
    for (x, y), z_top, z_bot in spec.get("coaxial", []):
        a = ring_at(v, z_top, x, y, 5.5)
        b = ring_at(v, z_bot, x, y, 9.0)
        if a is None or b is None:
            # Not measurable is a failure, not a pass. Skipping here would let a
            # missing opening slip through as silence.
            fail.append(
                f"{name}: cannot measure the through path at ({x}, {y}) -- "
                f"expected openings on z={z_top} and z={z_bot}"
            )
        elif math.dist(a[1], b[1]) > TOL:
            fail.append(
                f"{name}: openings at ({x}, {y}) are offset "
                f"{math.dist(a[1], b[1]):.3f} mm -- not a straight through path"
            )

    ctc, z_ctc, label = spec["bolt_ctc"]
    centres = []
    for x, y, d, z, what in spec["holes"]:
        if "valve bolt" not in what:
            continue
        r = ring_at(v, z_ctc, x, y, d)
        if r:
            centres.append(r[1])
    if len(centres) == 2:
        got = math.dist(centres[0], centres[1])
        if abs(got - ctc) > TOL:
            fail.append(f"{name}: {label} measures {got:.3f}, want {ctc}")
    else:
        fail.append(f"{name}: could not measure {label} from the mesh")
    return fail


def main() -> int:
    if not BRACKETS.is_dir():
        print(f"no {BRACKETS} -- run from the repo root", file=sys.stderr)
        return 2
    bad = []
    for name, spec in SPECS.items():
        f = check(name, spec)
        print(f"  {'FAIL' if f else 'ok  '}  {name}")
        bad += f
    for f in bad:
        print(f"    {f}")
    print(f"\n{'OK' if not bad else str(len(bad)) + ' problem(s)'}: "
          f"{len(SPECS)} bracket(s) checked against their measured inputs.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
