# Mini V2 plumb-in — 3D-printed valve brackets

Two parametric brackets that mount the plumb-in regulation stack (see
[06-011](../../06-011-mini-v2-direct-plumb-in.md)) inside the machine. Both are OpenSCAD source
(`.scad`, edit the CAPS variables at the top) plus a ready-to-slice `.stl` and a preview `.png`.

Print both in **PETG, ≥4 perimeters, ≥40% infill**. Both print in the delivered orientation with
**no support** (bores and fastener holes run vertical; counterbores land on the bed).

## Regulator clamp — `mini-v2-regulator-clamp`

Split-ring C-clamp that grips the threadless barrel just under the adjustment knob of the Chris'
Coffee (Winters PEM-LF) pressure regulator and bolts to a **vertical wall/frame**.

| Measured input                | Value                          |
| ----------------------------- | ------------------------------ |
| Clamp-area (barrel) diameter  | 29.5 mm → bore Ø29.9 (0.4 fit) |
| Clamp-area height             | 9.3 mm → ring 8.5 mm tall      |
| Barrel-to-body rear clearance | 3.2 mm → rear flattened to fit |

- Grips the barrel — the only non-rotating cylinder — so the knob, gauge, and both push-fit ports
  stay clear. Knob up, gauge out.
- Rear of the ring is flattened to the 3.2 mm the body allows; the thin back doubles as the flex
  hinge, and a single **M3 pinch bolt + captive nut** at the front does the clamping.
- Mounting plate has two vertical **M5** slots (height-adjustable) into the wall.

## Solenoid riser — `mini-v2-solenoid-riser`

Solid pedestal that stands the WIC 2BCK-1/4-24VDC-D fill solenoid **25–28 mm off the horizontal base
plate**, next to the vibratory pump.

| Measured input                  | Value                         |
| ------------------------------- | ----------------------------- |
| Stand-off height                | 26 mm                         |
| M5 base holes, centre-to-centre | 23 mm (perpendicular to flow) |
| Valve body width                | 32.75 mm                      |
| Inlet-to-outlet span            | 55 mm                         |

- Coil-up (media stays below the armature). Narrow toward the pump; fixing ears run fore/aft, away
  from it.
- **All four fasteners are the same: M5×10 socket-head cap screws.** Each passes through 5 mm of
  bracket and bites ~5 mm on the far side. The two valve bolts sit in deep Ø9 access bores from
  underneath, so they only grip the 5 mm top flange (no long bolts buried in plastic); the two base
  bolts pass through the feet (flanked by ribs so a driver still reaches them) into the base plate.
- **Assembly:** on the bench, invert the riser onto the valve and drive the two M5×10 up into the
  tapped base (the hex key reaches the head down the Ø9 bore). Flip upright, set on the base plate,
  drive the two base M5×10 down (drill new; tap the plate or use a nut).

## Regenerating the STL/PNG

The Homebrew OpenSCAD on macOS may hang headless; render via the Docker image:

```bash
# STL (no display needed)
docker run --rm -v "$PWD":/work openscad/openscad \
  openscad -o /work/mini-v2-solenoid-riser.stl -D 'SHOW_VALVE=false' \
  /work/mini-v2-solenoid-riser.scad
# PNG preview (xvfb bundled in the image)
docker run --rm -v "$PWD":/work openscad/openscad bash -lc \
  'xvfb-run -a openscad -o /work/mini-v2-solenoid-riser.png --imgsize=1200,900 \
   -D "\$fn=48" --camera=0,0,13,58,0,30,240 /work/mini-v2-solenoid-riser.scad'
```

The `.png` files include a translucent valve ghost for reference; the `.stl` files (exported with
`SHOW_VALVE=false`) contain only the printable part.
