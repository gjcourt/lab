// =====================================================================
// XIAO C3 presence case — L-mount rev 4
//   L that grips the brick's right corner. Leg 1 caps the board on the
//   room face; leg 2 wraps onto the right face. The outer corner between
//   them is a GENEROUS ROUND (CORNER_R) and the outer skin is CONTINUOUS
//   (no recess) — the 20x40 FPC antenna adheres across leg1 → curved
//   corner → leg2, conforming to the curve (no crease, no bump). The u.FL coax
//   exits a top-center notch; a pinch there grips the lead for strain relief.
//   Board captured (open back for the adapter, USB-C throat, retention lips).
// Local axes: +X = room, +Y = right, +Z = up.
// =====================================================================

/* ---- board + fit ---- */
PCB_W = 17.8; PCB_L = 21.0;
STK   = 5.0; CLR = 0.6; WALL = 2.0;
BRICK_HALF = 16.0;              // brick 32 wide -> right face at Y=16

/* ---- antenna corner ---- */
CORNER_R = 7.0;                 // rounded antenna corner (FPC conforms over this)
LEG2     = 18.0;                // right-face leg length (leg1 + arc + LEG2 >= 40mm skin)

/* ---- details ---- */
LIP    = 0.9; COAX_D = 1.35;

$fn = 56;
cav_y0 = -(PCB_W/2+CLR); cav_y1 = (PCB_W/2+CLR);
cav_z1 = PCB_L + CLR;
room_x = STK + CLR + WALL;
right_y = BRICK_HALF + WALL;
case_z = cav_z1 + WALL;

module case_solid() {
  difference() {
    union() {
      // leg 1 — board cap on the room face, full to the right corner
      translate([0, cav_y0-WALL, 0]) cube([room_x, right_y-(cav_y0-WALL), case_z]);
      // leg 2 — wrap onto the right face
      translate([-LEG2, right_y-WALL, 0]) cube([room_x+LEG2, WALL, case_z]);
    }
    // round the outer antenna corner: remove material outside the fillet
    translate([room_x-CORNER_R, right_y-CORNER_R, -1])
      difference() {
        cube([CORNER_R+2, CORNER_R+2, case_z+2]);
        cylinder(h=case_z+2, r=CORNER_R, $fn=64);
      }
    // soften the top outer edge of leg1 a touch (chamfer)
    translate([room_x, 0, case_z]) rotate([0,45,0]) cube([2,200,2], center=true);
  }
}

module body() {
  difference() {
    case_solid();
    // board cavity — open back (-X) + bottom (-Z)
    translate([-1, cav_y0, -1]) cube([STK+CLR+1, cav_y1-cav_y0, cav_z1+1]);
    // USB-C throat (adapter)
    translate([-1, -6, -1]) cube([STK+CLR+2, 12, 4]);
    // coax exit — notch in the top wall, centre (coax up to the antenna corner)
    translate([-1, -COAX_D/2-0.5, cav_z1-1]) cube([STK+2, COAX_D+1.0, WALL+2]);
  }
  // board retention lips at the back opening
  translate([0, cav_y0, cav_z1-LIP]) cube([LIP, cav_y1-cav_y0, LIP]);
  translate([0, cav_y0, 0])          cube([LIP, LIP, cav_z1]);
  translate([0, cav_y1-LIP, 0])      cube([LIP, LIP, cav_z1]);
  // strain relief: a pinch at the coax exit grips the u.FL lead as it leaves,
  // loading the top wall instead of the fragile connector
  coax_pinch();
}

// Two nubs bridge the top exit notch, narrowing it to ~COAX_D-0.25 mm so the
// coax presses in and is retained where it exits — anchored to the top wall,
// clear of the board that fills the cavity below.
module coax_pinch() {
  gap = COAX_D - 0.25;                 // snap gap, just under the coax dia
  half = COAX_D/2 + 0.5;               // notch half-width (matches the exit cut)
  for (sy = [-1, 1])
    translate([3, (sy < 0) ? -half - 0.1 : gap/2, cav_z1])
      cube([2, half - gap/2 + 0.1, 1.6]);
}

module board_ghost(){ %translate([STK-1.3, cav_y0+CLR, CLR]) cube([1.3, PCB_W, PCB_L]); }

body();
board_ghost();
