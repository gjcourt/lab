# XIAO ESP32-C3 presence-node enclosures

3D-printed cases for the wall-wart XIAO ESP32-C3 presence nodes. The node plugs into a USB power
brick via a **180° USB-C adapter** (keeps the board tight to the brick); the case caps and retains
the board and manages the WiFi antenna lead.

## Deployment geometry

- **Brick:** 32 × 32 × 32.5 mm cube, US folding prongs on one face, USB-C on the opposite face.
- **Adapter:** 180° USB-C, 11 mm tall — the board sits ~5 mm off the brick's room-facing side (the
  face between prongs and USB-C).
- **Board:** Seeed XIAO ESP32-C3, 21 × 17.8 mm. u.FL WiFi connector at the **center-rear** of the
  board.
- **Antenna:** Seeed **XIAO FPC Antenna A-01**, 20 × 40 mm, 3M-backed. Coax solders to the **center
  of one short (20 mm) side**. It is a _flexible_ PCB antenna — it wants to lie flat or conform to a
  **gentle curve**, never a sharp crease.

## rev 4 — `xiao-c3-presence-node.{scad,stl}` (variant 1: plain C3 + WiFi antenna)

An **L** that grips the brick's right corner:

- **Leg 1** caps the board on the room face (open at the back toward the brick for the adapter;
  USB-C throat at the bottom; retention lips hold the board in).
- **Leg 2** wraps onto the brick's right face — this is the mechanical grip so the case doesn't hang
  off the plug alone.
- The **outer corner between the legs is a generous round** (`CORNER_R = 7 mm`) and the outer skin
  is **continuous — no recess**. The 20 × 40 FPC antenna adheres across leg 1 → curved corner → leg
  2 as one surface, conforming to the curve (no crease, no "speed bump"). Developed skin ≈ leg1
  (~16) + arc (~11) + leg2 (~18) ≈ 45 mm, so the 40 mm antenna fits with margin.
- **Wire-catch:** two snap combs on the back wall at center-rear give **strain relief** for the
  fragile u.FL coax — a tug loads the plastic, not the connector. The coax exits up through a
  top-center notch to the antenna.

Envelope ≈ 25.6 × 29.5 × 23.6 mm.

### Print settings

- **Material:** PETG (or PLA). PETG preferred for the warm spot next to a PSU.
- **Layers:** 0.2 mm, **3 perimeters**, **20 % infill** (walls dominate at this size; 40 % is fine
  and near-free on time — no meaningful strength gain).
- **Orientation:** room face (the big flat leg-1 outer) **down on the bed** — best flat surface for
  antenna adhesion, and the cavity/throat open sideways so no supports are needed. The small
  retention/wire-catch lips bridge fine.

### Parameters worth tuning after a test fit

- `CLR` — board cavity clearance (0.6 mm); loosen/tighten to the print.
- `CORNER_R` — antenna wrap radius; larger = gentler wrap.
- `LEG2` — how far leg 2 grips the right face.

## Planned variants (not yet built)

- **Variant 2 — mmWave hat.** Seeed 24 GHz mmWave hat stacks ~21 mm on the C3 headers, radar facing
  the room. Needs a **deeper cavity** (~22–24 mm) and a **thin flat radome** (≈1.5 mm PETG passes 24
  GHz) or open window over the patch antennas. Everything else (L, antenna corner, WiFi wrap,
  wire-catch, throat) carries over — it is a parametric sibling of rev 4.
- **Variant 3 — IR/RF blaster** (see [03-027](../../03-027-xiao-c3-ir-rf-blaster-carrier-pcb.md)).
  Reuses the case family with an IR/RF-transparent front.

## Rendering

Local OpenSCAD hangs headless — render via Docker:

```sh
docker run --rm -v "$PWD":/work openscad/openscad \
  openscad -o /work/out.stl /work/xiao-c3-presence-node.scad
```
