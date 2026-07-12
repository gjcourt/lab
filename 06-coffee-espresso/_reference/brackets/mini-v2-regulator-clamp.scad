// =====================================================================
// Winters PEM-LF pressure-regulator bracket  (Chris' Coffee, threadless)
// Split-ring C-clamp on a screw-to-frame arm.
//   Orientation when mounted:  knob UP (+Z), gauge faces OUT (+Y),
//   push-fit ports run left/right (X).  Clamp grips the black barrel
//   just under the knob — the only non-rotating cylinder on the valve.
// Print: PETG, >=4 perimeters, >=40% infill.  One M3 pinch bolt clamps
//   the valve; two M5 screws fix the plate to the machine frame.
// Units: mm.  All CAPS vars up top are the ones to verify with calipers.
// =====================================================================

/* ---------- MEASURED (calipers, 2026-07-11) ---------- */
BARREL_D   = 29.5;   // clamp-area dia just below the knob   << measured
BARREL_H   = 9.3;    // clamp-area height (knob -> body)     << measured

/* ---------- FRAME MOUNT (from your machine) -------------------------- */
ARM_LEN    = 18.0;   // standoff: ring face -> frame face
FRAME_BOLT_D  = 5.5; // M5 clearance
FRAME_HOLE_DX = 20.0;// horizontal spacing between the two frame screws
MOUNT_SLOTS   = true;// true = vertical slots (height-adjustable on frame)

/* ---------- clamp ring ----------------------------------------------- */
CLEARANCE  = 0.4;    // slip fit before pinching
RING_WALL  = 5.0;    // radial wall (front/sides)
RING_H     = 8.5;    // ring height — capped to the 9.3 mm clamp area (~0.4 mm top+bottom margin)
SLOT_W     = 3.0;    // pinch gap
BACK_CLEARANCE = 3.2;// measured barrel-surface -> regulator body behind it. The ring's
                     // rear is flattened to this so it can't foul the body; the thin
                     // back also acts as the flex hinge, front pinch does the clamping.

/* ---------- pinch bolt (M3, squeezes the ring shut) ------------------ */
PINCH_D    = 3.4;    // M3 clearance
NUT_AF     = 5.5;    // M3 nut across-flats
NUT_T      = 2.6;    // M3 nut thickness
EAR_TH     = 6.0;    // each ear wall thickness (X)
EAR_LEN    = 13.0;   // ear reach past the bore (+Y)

/* ---------- plate ---------------------------------------------------- */
PLATE_W    = 34.0;
PLATE_H    = 24.0;
PLATE_TH   = 5.0;

/* ---------- reference ghost of the valve (visual only) --------------- */
SHOW_VALVE = true;
KNOB_D     = 30.0;
KNOB_H     = 20.0;
GAUGE_D    = 40.0;
BODY_W     = 38.0;
PORT_D     = 15.0;

$fn = 120;

// -------- derived ----------------------------------------------------
bore_d    = BARREL_D + CLEARANCE;
ring_od   = bore_d + 2*RING_WALL;
ear_w     = SLOT_W + 2*EAR_TH;          // total ear block width (X)
y_bolt    = ring_od/2 + EAR_LEN*0.55;   // pinch-bolt centre along +Y
plate_y   = -(ring_od/2 + ARM_LEN);     // front face of plate
y_back_cut = -(BARREL_D/2 + BACK_CLEARANCE); // rear flat plane (~3 mm wall left at centre)

echo(str("bore=", bore_d, "  ring_od=", ring_od, "  ring_h=", RING_H));

// -------- clamp ring with pinch ears (opening at +Y) -----------------
module clamp_ring() {
  difference() {
    union() {
      cylinder(h=RING_H, d=ring_od);
      // ear block on +Y
      translate([-ear_w/2, ring_od/2 - 2, 0])
        cube([ear_w, EAR_LEN + 2, RING_H]);
    }
    // bore
    translate([0,0,-1]) cylinder(h=RING_H+2, d=bore_d);
    // pinch slot (thin slab in X, through the +Y ear)
    translate([-SLOT_W/2, 0, -1])
      cube([SLOT_W, ring_od/2 + EAR_LEN + 3, RING_H+2]);
    // pinch bolt hole (axis along X)
    translate([0, y_bolt, RING_H/2]) rotate([0,90,0])
      cylinder(h=ear_w + 2, d=PINCH_D, center=true, $fn=40);
    // captive nut pocket on the -X ear
    translate([-ear_w/2 - 0.1, y_bolt, RING_H/2]) rotate([0,90,0])
      cylinder(h=NUT_T, d=NUT_AF/cos(30), $fn=6, center=false);
    // flatten the rear to BACK_CLEARANCE so the ring can't foul the body
    translate([-50, y_back_cut - 100, -1]) cube([100, 100, RING_H+2]);
  }
}

// -------- frame plate + arm web (behind, -Y) -------------------------
module mount() {
  // plate (vertical, in X-Z plane; thin in Y)
  difference() {
    translate([-PLATE_W/2, plate_y - PLATE_TH, RING_H/2 - PLATE_H/2])
      cube([PLATE_W, PLATE_TH, PLATE_H]);
    // frame fixings
    for (sx = [-1, 1])
      translate([sx*FRAME_HOLE_DX/2, plate_y - PLATE_TH - 1, RING_H/2])
        rotate([-90,0,0]) {
          if (MOUNT_SLOTS)
            hull() for (dz = [-4, 4])
              translate([0, dz, 0]) cylinder(h=PLATE_TH+2, d=FRAME_BOLT_D);
          else
            cylinder(h=PLATE_TH+2, d=FRAME_BOLT_D);
        }
  }
  // arm web joining the flattened ring back to plate
  hull() {
    translate([-ear_w/2, y_back_cut, 0]) cube([ear_w, 0.1, RING_H]);
    translate([-PLATE_W/2, plate_y, RING_H/2 - PLATE_H/2 + 3])
      cube([PLATE_W, 0.1, PLATE_H - 6]);
  }
}

// -------- valve ghost (visual reference only) ------------------------
module valve_ghost() {
  %union() {
    // barrel (clamped section)
    cylinder(h=BARREL_H, d=BARREL_D);
    // knob on top
    translate([0,0,BARREL_H]) cylinder(h=KNOB_H, d=KNOB_D);
    // body block below barrel
    translate([-BODY_W/2, -BODY_W/2, -BODY_W]) cube([BODY_W, BODY_W, BODY_W]);
    // gauge out the front (+Y)
    translate([0,0,-BODY_W/2]) rotate([-90,0,0])
      cylinder(h=BODY_W/2 + 22, d=GAUGE_D);
    // ports left/right (X)
    for (sx=[-1,1]) translate([0,0,-BODY_W*0.7]) rotate([0, sx*90, 0])
      cylinder(h=BODY_W/2 + 14, d=PORT_D);
  }
}

// -------- assembly ---------------------------------------------------
clamp_ring();
mount();
if (SHOW_VALVE) valve_ghost();
