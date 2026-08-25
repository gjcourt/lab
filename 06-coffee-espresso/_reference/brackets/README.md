# Mini V2 plumb-in — 3D-printed valve brackets

Two parametric brackets that mount the plumb-in regulation stack (see
[06-011](../../06-011-mini-v2-direct-plumb-in.md)) inside the machine. Both are OpenSCAD source
(`.scad`, edit the CAPS variables at the top) plus a ready-to-slice `.stl` and a preview `.png`.

## Ordering

Printed by **Forge Labs (Canada)**, recalled as glass-filled nylon — the owner's recollection, not a
retained order. Confirm the material and the trade name at order time.

> ⚠️ **v2 has never been fitted.** `scripts/check_brackets.py` proves the exported STL matches the
> `.scad` and the two dimensioned inputs it encodes — stand-off and bolt spacing — not the full
> measured-input table but has not been in the machine. v1 was printed, found too long, and v2
> shortened the ears -- **the clearance that defeated v1 was never recorded**, so 60 mm is a
> reduction from the part, not a fit to the space. If v1 overhung by more than 9 mm, v2 will not fit
> either.
>
> **Measure the available Y run before ordering** and write it here. That is a caliper reading and a
> line of markdown against the cost and lead time of a second print from Canada.

## Material and process

**Ordered as glass-filled nylon (PA12-GF) from a print service.** That is the right call for this
location -- next to the vibratory pump inside a machine that runs warm -- because PA12-GF holds its
shape well above PETG's ~70 °C softening point, and it is stiffer.

The settings below are for the **FDM** fallback and do not apply to a powder process:

| Process                                                      | Settings                                                                                                                                               |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| SLS / MJF, glass-filled nylon (**what is actually ordered**) | none -- the service controls it. No perimeters, no infill, no support.                                                                                 |
| FDM fallback                                                 | **PETG**, ≥4 perimeters, ≥40% infill, no support, delivered orientation (bores vertical, counterbores on the bed). Not PLA: it softens near this pump. |

### Hole fit on a powder process

`M5_CLEAR` and `BASE_HOLE_D` are **5.5 mm -- nominal M5 clearance with no process allowance**, so
0.25 mm a side. Powder processes commonly sinter holes slightly undersize as surrounding powder
part-fuses, and `HEAD_BORE_D` is Ø9.0 for an 8.5 mm socket head — the same 0.25 mm a side, on a
larger diameter.

**This is unresolved, not settled.** What is known is that v1 was printed and failed on length.
Whether its bolts fitted was never recorded, so there is no evidence either way on hole fit in this
process — and the note cannot claim there is while also saying, above, that v1's clearance went
unrecorded.

So: do not widen the holes pre-emptively, because a change with no measurement behind it is a guess
in the other direction. **Check bolt fit on this print and record it here.** If the holes come back
tight, ream to 5.5 rather than editing the model.

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

> **v2 (2026-08-02):** the long-axis (Y) footprint was shortened **69 mm → 60 mm** — the printed v1
> was too long there. The reduction comes entirely off the fixing feet (`EAR_REACH` 16 → 11.5 mm);
> the valve bolt pattern, 32.75 mm body coverage, and 26 mm stand-off are unchanged. STL bbox
> verified **60 × 30 × 26 mm**. The tracked `.png` still shows v1 (OpenSCAD hangs headless in CI/
> podman here) — **trust the `.scad`/`.stl`, not the preview**; regenerate the PNG on a GUI machine.

| Measured input                  | Value                         |
| ------------------------------- | ----------------------------- |
| Stand-off height                | 26 mm                         |
| M5 base holes, centre-to-centre | 23 mm (perpendicular to flow) |
| Valve body width                | 32.75 mm                      |
| Inlet-to-outlet span            | 55 mm                         |

- Coil-up (media stays below the armature). Narrow toward the pump; fixing ears run fore/aft, away
  from it.
- **All four fasteners are the same: M5×12 socket-head cap screws.** Each passes through 7 mm of
  bracket and bites ~5 mm on the far side. The two valve bolts sit in deep Ø9 access bores from
  underneath, so they only grip the 7 mm top flange (no long bolts buried in plastic); the two base
  bolts pass through the feet (flanked by ribs so a driver still reaches them) into the base plate.
- **Assembly:** on the bench, invert the riser onto the valve and drive the two M5×12 up into the
  tapped base (the hex key reaches the head down the Ø9 bore). Flip upright, set on the base plate,
  drive the two base M5×12 down (drill new; tap the plate or use a nut).

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
