// =====================================================================
// WIC 2BCK-1/4-24VDC-D fill-solenoid RISER  (06-011 plumb-in)
// Solid boxy pedestal that stands the valve 25-28 mm off the horizontal
// base plate, next to the vibratory pump.
//
// FASTENERS: all four are the SAME standard bolt — 2x M5x10 socket-head
// cap screws up into the valve's tapped base, 2x M5x10 down into the base
// plate. Each passes through 5 mm of bracket and bites ~5 mm on the far
// side. The valve bolts sit in deep access bores from underneath so they
// only grip the 5 mm top flange (no long bolts buried in plastic).
//
// Assembly: on the bench, invert the riser onto the valve, drop the two
// M5x10 bolts down through the top flange into the valve base and tighten
// (hex key reaches the head down the Ø9 access bore). Flip upright, set on
// the base plate, drive the two base M5x10 down through the feet.
//
// Print: PETG, >=4 perimeters, >=40% infill. Prints as-is, no support.
// Units: mm.
// =====================================================================

/* ---------- HEIGHT ---------- */
STAND_H  = 26.0;   // valve base above base plate (target 25-28)   << set

/* ---------- VALVE SIDE (measured) ---------- */
HOLE_CTC = 23.0;   // M5 hole spacing in the valve base            << measured
BODY_W   = 32.75;  // valve body width                            << measured
PORT_SPAN = 55.0;  // inlet-to-outlet span (tube clearance)       << measured
M5_CLEAR = 5.5;    // M5 through-clearance
HOLES_ALONG_Y = true; // 23 mm line runs fore/aft (Y); ports run across (X)

/* ---------- FASTENERS (all 4 identical) ---------- */
// M5x10 socket-head cap screws throughout. Bracket grip is FLANGE_TH; the
// far-side bite is (bolt length - grip) ~= 5 mm into valve / base plate.
FLANGE_TH   = 5.0; // top-flange & foot thickness the bolt grips
HEAD_BORE_D = 9.0; // Ø of the deep access bore for the M5 socket head (8.5 head)

/* ---------- FOOTPRINT (boxy = stiff next to the pump) ---------- */
CORE_X   = 30.0;   // riser width (toward the pump) — shrink if the gap is tight << pump clearance
EDGE     = 7.0;    // margin around each M5 hole (also clears the Ø9 head bore)

/* ---------- BASE-PLATE FIXING (drill new) ---------- */
EAR_REACH   = 16.0;// foot length beyond the core, each end (Y)
BASE_HOLE_D = 5.5; // M5 clearance (drill + bolt the base plate; tap it or use a nut)
GUSSET      = true;

$fn = 96;

// ---- derived ----
core_y   = HOLE_CTC + 2*EDGE;            // fore/aft length (covers the 32.75 body)
core_x   = max(CORE_X, HEAD_BORE_D + 8); // width
ear_y    = core_y/2 + EAR_REACH;         // foot tip in Y
base_ctc = core_y + EAR_REACH;           // base fixing hole c/c (Y)

// valve bolt: Ø5.5 through the top flange + deep Ø9 access bore from below
module valve_bolt_hole() {
  translate([0,0,STAND_H - FLANGE_TH]) cylinder(h=FLANGE_TH + 1, d=M5_CLEAR);   // flange clearance
  translate([0,0,-1])                  cylinder(h=STAND_H - FLANGE_TH + 1, d=HEAD_BORE_D); // head access
}

module riser() {
  difference() {
    union() {
      // solid boxy core
      translate([-core_x/2, -core_y/2, 0]) cube([core_x, core_y, STAND_H]);
      // fore/aft feet
      for (sy=[-1,1])
        translate([-core_x/2, sy>0 ? core_y/2 : -ear_y, 0])
          cube([core_x, EAR_REACH, FLANGE_TH]);
      // gusset ribs: two per foot, flanking the base hole so a driver reaches it
      if (GUSSET)
        for (sy=[-1,1]) for (rx=[-1,1]) {
          gt   = 4;
          xoff = rx*(BASE_HOLE_D/2 + gt/2 + 2);
          y_core = sy*(core_y/2 - 1);
          y_ear  = sy*(core_y/2 + EAR_REACH*0.70);
          hull() {
            translate([xoff - gt/2, y_core - 1, 0]) cube([gt, 2, 0.55*STAND_H]);
            translate([xoff - gt/2, y_ear  - 1, 0]) cube([gt, 2, FLANGE_TH]);
          }
        }
    }
    // 2x valve bolts (M5x10 up into the tapped base)
    for (i=[-1,1]) {
      pos = HOLES_ALONG_Y ? [0, i*HOLE_CTC/2, 0] : [i*HOLE_CTC/2, 0, 0];
      translate(pos) valve_bolt_hole();
    }
    // 2x base bolts (M5x10 down into the base plate) — plain through, head proud
    for (sy=[-1,1])
      translate([0, sy*base_ctc/2, -1]) cylinder(h=FLANGE_TH + 2, d=BASE_HOLE_D);
  }
}

// ---- valve ghost (visual only) ----
SHOW_VALVE = true;
BODY_D = BODY_W; COIL_D = 36.0; COIL_H = 42.0;
module valve_ghost() {
  %union() {
    translate([0,0,STAND_H]) cylinder(h=8, d=BODY_D);
    translate([0,0,STAND_H+8]) cylinder(h=COIL_H, d=COIL_D);
  }
}

riser();
if (SHOW_VALVE) valve_ghost();
