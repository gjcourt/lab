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
        "holes": [
            # (z, x, y, diameter, what it is)
            (26.0, 0.0, -11.5, 5.5, "valve bolt, M5 clearance"),
            (26.0, 0.0, 11.5, 5.5, "valve bolt, M5 clearance"),
            (0.0, 0.0, -11.5, 9.0, "socket-head access bore"),
            (0.0, 0.0, 11.5, 9.0, "socket-head access bore"),
            (0.0, 0.0, -24.25, 5.5, "base bolt, M5 clearance"),
            (0.0, 0.0, 24.25, 5.5, "base bolt, M5 clearance"),
        ],
        "bolt_ctc": (23.0, "valve base holes, centre-to-centre"),
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


def ring_at(verts, z, cx, cy, tol=0.05):
    """Mean diameter of the vertex ring around (cx, cy) on plane z, or None."""
    pts = [(x, y) for x, y, zz in verts if abs(zz - z) < tol]
    r = [math.dist(p, (cx, cy)) for p in pts if math.dist(p, (cx, cy)) < 8]
    if len(r) < 12 or max(r) - min(r) > 0.35:
        return None
    return 2 * sum(r) / len(r)


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

    for z, x, y, d, what in spec["holes"]:
        got = ring_at(v, z, x, y)
        if got is None:
            fail.append(f"{name}: no hole at ({x}, {y}) on z={z} -- {what}")
        elif abs(got - d) > TOL:
            fail.append(f"{name}: hole at ({x}, {y}) is Ø{got:.2f}, want Ø{d} -- {what}")

    ctc, label = spec["bolt_ctc"]
    ys = sorted(y for z, x, y, d, w in spec["holes"] if "valve bolt" in w)
    if len(ys) == 2 and abs(abs(ys[1] - ys[0]) - ctc) > TOL:
        fail.append(f"{name}: {label} is {abs(ys[1]-ys[0])}, want {ctc}")
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
