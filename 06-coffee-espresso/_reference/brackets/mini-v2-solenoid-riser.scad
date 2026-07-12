// =====================================================================
// WIC 2BCK-1/4-24VDC-D fill-solenoid RISER  (06-011 plumb-in)
// Solid pedestal that stands the valve 25-28 mm off the horizontal base
// plate, next to the vibratory pump.  Valve bolts DOWN into the riser:
// 2x M5 socket-head screws pass up through the riser (counterbored heads
// at the bottom) into the valve's 2x M5x0.8 base holes (23 mm c/c).
// Riser then screws to the base plate via fore/aft flange ears (drill new).
// Narrow in X so it tucks beside the pump; ears run in Y, away from it.
// Print: PETG, >=4 perimeters, >=40% infill (solid core = stiff, low buzz).
// Assembly: bolt valve to riser on the bench first, THEN fix riser down.
// Units: mm.
// =====================================================================

/* ---------- HEIGHT ---------- */
STAND_H  = 26.0;   // valve base above base plate (target 25-28)   << set

/* ---------- VALVE SIDE (measured / verify) ---------- */
HOLE_CTC = 23.0;   // M5 hole spacing in the valve base            << measured (confirmed)
BODY_W   = 32.75;  // valve body width                            << measured
PORT_SPAN = 55.0;  // inlet-to-outlet span (tube clearance either end) << measured
M5_CLEAR = 5.5;    // M5 through-clearance
CBORE_D  = 9.5;    // M5 socket-head counterbore dia
CBORE_H  = 5.5;    // counterbore depth (head sinks below the base)
HOLES_ALONG_Y = true; // 23 mm line runs fore/aft (Y) — set false for across (X)

/* ---------- FOOTPRINT ---------- */
CORE_X   = 32.75;  // riser width — defaults to body width; shrink toward the pump << pump clearance
EDGE     = 9.0;    // material margin around each M5 hole
WALL_MIN = 6.0;    // min core thickness on the non-hole axis

/* ---------- BASE-PLATE FIXING (drill new) ---------- */
BASE_TH     = 5.0; // flange-ear thickness
EAR_REACH   = 15.0;// ear length beyond the core, each end (Y)
BASE_HOLE_D = 5.5; // M5 clearance (drill + bolt the base plate)
BASE_SLOTS  = true;// slots let you slide it fore/aft before locking
GUSSET      = true;

$fn = 96;

// ---- derived ----
core_y   = (HOLES_ALONG_Y ? HOLE_CTC : 0) + 2*EDGE;   // fore/aft length
core_x   = HOLES_ALONG_Y ? max(CORE_X, WALL_MIN)      // width
                         : max(CORE_X, HOLE_CTC + 2*EDGE);
ear_y    = core_y/2 + EAR_REACH;                       // ear tip in Y
base_ctc = 2*(core_y/2 + EAR_REACH/2);                 // fixing hole c/c (Y)

module m5_bolt_hole() {
  translate([0,0,-0.01]) cylinder(h=STAND_H+1, d=M5_CLEAR);   // through
  translate([0,0,-0.01]) cylinder(h=CBORE_H, d=CBORE_D);      // head pocket (bottom)
}

module riser() {
  difference() {
    union() {
      // solid core
      translate([-core_x/2, -core_y/2, 0]) cube([core_x, core_y, STAND_H]);
      // fore/aft base ears
      for (sy=[-1,1])
        translate([-core_x/2, sy>0 ? core_y/2 : -ear_y, 0])
          cube([core_x, EAR_REACH, BASE_TH]);
      // gussets ear -> core: manifold-safe wedge, hull of a tall slab embedded
      // in the core face and a short slab embedded in the ear (overlaps both).
      if (GUSSET)
        for (sy=[-1,1]) {
          gt = min(core_x, 8);                    // gusset thickness (X)
          y_core = sy*(core_y/2 - 1);             // 1 mm inside the core face
          y_ear  = sy*(core_y/2 + EAR_REACH*0.75);// within the ear
          hull() {
            translate([-gt/2, y_core - 1, 0]) cube([gt, 2, 0.6*STAND_H]);
            translate([-gt/2, y_ear  - 1, 0]) cube([gt, 2, BASE_TH]);
          }
        }
    }
    // 2x M5 clearance + counterbore
    for (i=[-1,1]) {
      pos = HOLES_ALONG_Y ? [0, i*HOLE_CTC/2, 0] : [i*HOLE_CTC/2, 0, 0];
      translate(pos) m5_bolt_hole();
    }
    // 2x base fixings (fore/aft)
    for (sy=[-1,1])
      translate([0, sy*base_ctc/2, -1]) {
        if (BASE_SLOTS)
          hull() for (dx=[-3,3]) translate([dx,0,0]) cylinder(h=BASE_TH+2, d=BASE_HOLE_D);
        else cylinder(h=BASE_TH+2, d=BASE_HOLE_D);
      }
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
