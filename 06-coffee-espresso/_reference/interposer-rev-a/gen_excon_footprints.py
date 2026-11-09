#!/usr/bin/env python3
"""Write the EXCON 2547 vertical-header footprints into ./footprints (KiCad 9 .kicad_mod).

    python3 gen_excon_footprints.py

Every dimension comes from EXCON drawing C2547WV rev E, part 2547xxWV203
(https://www.excon.com.tw/wp-content/uploads/2547WV.pdf, read 2026-11-08):

* pitch 2.54 mm (+-0.05, non-cumulative); recommended PCB hole 1.00 mm +0.1/-0, PCB 1.0-1.6 mm
* pins 0.64 mm square, 3.5 mm below the board; body 12.6 mm tall above it (16.1 mm overall)
* body width B = A + 5.08 mm (A = pin span): 7.62 mm for 2 pins, 12.70 mm for 4 pins
* body depth 5.0 mm; the pin row sits 2.2 mm from the face with the latch window (front view),
  so 2.8 mm from the back wall

The pad size (1.7 x 2.0 mm) is ours, copied from KiCad's JST XH vertical footprints (same pin and
hole class at a 2.50 mm pitch), and leaves 0.84 mm copper gap at 2.54 mm. The latch-window marker
on silk shows WHICH side the latch is on; its width is not dimensioned on the drawing, so the mark
is not to scale. George's 2026-11-08 identification of the machine's headers as 2547 is probable,
not caliper-confirmed (bench page Test 29): confirm before ordering.

Plain Python, no dependencies; output matches the vendored KiCad 9 files' layout.
"""

from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
PITCH = 2.54
DRILL = 1.0
PAD = (1.7, 2.0)
FRONT = 2.2  # pin row -> latch-window face
BACK = 2.8  # pin row -> back wall (5.0 - 2.2)
SIDE = 2.54  # pin centre -> body end ((B - A) / 2)
SILK_OFF = 0.11
CRT_OFF = 0.5


def f(v: float) -> str:
    s = f'{v:.3f}'.rstrip('0').rstrip('.')
    return '0' if s == '-0' else s


def line(x1, y1, x2, y2, layer, w):
    return (f'\t(fp_line\n\t\t(start {f(x1)} {f(y1)})\n\t\t(end {f(x2)} {f(y2)})\n'
            f'\t\t(stroke\n\t\t\t(width {w})\n\t\t\t(type solid)\n\t\t)\n\t\t(layer "{layer}")\n\t)\n')


def rect(x1, y1, x2, y2, layer, w):
    return (f'\t(fp_rect\n\t\t(start {f(x1)} {f(y1)})\n\t\t(end {f(x2)} {f(y2)})\n'
            f'\t\t(stroke\n\t\t\t(width {w})\n\t\t\t(type solid)\n\t\t)\n\t\t(fill no)\n'
            f'\t\t(layer "{layer}")\n\t)\n')


def text(kind, value, x, y, layer):
    head = f'\t(property "{kind}" "{value}"' if kind else f'\t(fp_text user "{value}"'
    return (f'{head}\n\t\t(at {f(x)} {f(y)} 0)\n\t\t(layer "{layer}")\n'
            '\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1 1)\n\t\t\t\t(thickness 0.15)\n\t\t\t)\n\t\t)\n\t)\n')


def footprint(n: int) -> tuple[str, str]:
    name = f'EXCON_2547-{n:02d}_WV'
    span = (n - 1) * PITCH
    x0, x1 = -SIDE, span + SIDE
    y0, y1 = -BACK, FRONT
    mid = span / 2
    descr = (f'EXCON 2547 series wafer, 2547{n:02d}WV203, 1x{n:02d} P2.54mm vertical, shrouded, latch window '
             f'(dimensions: EXCON drawing C2547WV rev E, https://www.excon.com.tw/wp-content/uploads/2547WV.pdf: '
             f'pitch 2.54, hole 1.00 +0.1, pin 0.64 sq, body {x1 - x0:.2f} W x 5.0 D x 12.6 H, pin row 2.2 from '
             f'the latch-window face). Mates 2547{n:02d}HA203 housing + 254700TC351/TC501 terminals. '
             f'Probable match to Mini Vivaldi II S1 Universal Board v.05.01 sensor headers: confirm by calipers')
    o = [f'(footprint "{name}"\n\t(version 20241229)\n\t(generator "lab-gen_excon_footprints")\n'
         f'\t(layer "F.Cu")\n\t(descr "{descr}")\n\t(tags "connector EXCON 2547 wafer vertical 2.54mm")\n']
    o.append(text('Reference', 'REF**', mid, y0 - 1.6, 'F.SilkS'))
    o.append(text('Value', name, mid, y1 + 1.7, 'F.Fab'))
    o.append('\t(attr through_hole)\n')
    # silkscreen: body outline, latch-window marker on the front face, pin-1 corner mark
    s0, s1, t0, t1 = x0 - SILK_OFF, x1 + SILK_OFF, y0 - SILK_OFF, y1 + SILK_OFF
    o.append(rect(s0, t0, s1, t1, 'F.SilkS', 0.12))
    o.append(rect(mid - 1.0, t1 - 0.6, mid + 1.0, t1, 'F.SilkS', 0.12))  # latch window (not to scale)
    o.append(line(s0 - 0.3, t1 + 0.3, s0 - 0.3, t1 - 1.2, 'F.SilkS', 0.12))  # pin 1: front-left
    o.append(line(s0 - 0.3, t1 + 0.3, s0 + 1.2, t1 + 0.3, 'F.SilkS', 0.12))
    # courtyard
    o.append(rect(round(x0 - CRT_OFF, 2), round(y0 - CRT_OFF, 2), round(x1 + CRT_OFF, 2), round(y1 + CRT_OFF, 2),
                  'F.CrtYd', 0.05))
    # fab: body outline, latch face, pin-1 chevron
    o.append(rect(x0, y0, x1, y1, 'F.Fab', 0.1))
    o.append(line(mid - 1.0, y1 - 0.5, mid + 1.0, y1 - 0.5, 'F.Fab', 0.1))
    o.append(line(-0.625, y1, 0, y1 - 1.0, 'F.Fab', 0.1))
    o.append(line(0, y1 - 1.0, 0.625, y1, 'F.Fab', 0.1))
    o.append(text(None, '${REFERENCE}', mid, y0 + 1.0, 'F.Fab'))
    for i in range(n):
        shape = 'rect' if i == 0 else 'oval'
        o.append(f'\t(pad "{i + 1}" thru_hole {shape}\n\t\t(at {f(i * PITCH)} 0)\n\t\t(size {PAD[0]} {PAD[1]})\n'
                 f'\t\t(drill {DRILL})\n\t\t(layers "*.Cu" "*.Mask")\n\t\t(remove_unused_layers no)\n\t)\n')
    o.append('\t(embedded_fonts no)\n)\n')
    return name, ''.join(o)


if __name__ == '__main__':
    for n in (2, 4):
        name, body = footprint(n)
        (HERE / 'footprints' / f'{name}.kicad_mod').write_text(body)
        print(f'wrote footprints/{name}.kicad_mod')
