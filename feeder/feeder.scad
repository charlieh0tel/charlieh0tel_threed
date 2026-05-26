// --- PRECISE ONEISALL 5L RECTANGULAR HOPPER DIMENSIONS ---
tank_width         = 180;  // Left-to-right straight width (mm)
tank_depth         = 175;  // Front-to-back straight depth (mm)
tank_corner_radius = 12;   // Corner roundness radius (mm)
clamp_height       = 36;   // Vertical height of clamp ring (mm)
wall_thickness     = 8;    // Structural load thickness (mm)
clearance          = 1.5;  // Tolerance gap for easy placement (mm)
backplate_offset   = 4;    // Extra Y gap between collar rear and backplate (mm)
screw_hole_dia     = 5.0;  // #10 wall screw diameter (mm)

// --- VERTICAL DROP PIN SETTINGS ---
pin_hole_dia  = 5.5;  // Enclosed hole diameter for the drop-pin (mm)
pin_clearance = 0.4;  // Vertical clearance so middle ear slides freely (mm)

// --- HINGE SMOOTHING ---
ear_corner_radius = 5;  // Rounded radius for outer hinge knuckle corners (mm)

// --- PART SELECTOR ---
// Uncomment the line you want to render:
/* [Part] */
part = "back_wall_mount"; // ["back_wall_mount", "front_clamp", "print_pins"]
// part = "front_clamp";
// part = "print_pins";

// --- RENDER QUALITY ---
// $fn = 20 for fast preview; 80 for final export.
$fn = 80;

/* [Hidden] */
// ---------- derived values ----------
w_inner = tank_width  + clearance * 2;
d_inner = tank_depth  + clearance * 2;

ear_width = 16;
ear_depth = 26;  // straddles the split line so both halves get full knuckle

// Knuckle layer heights
knuckle_layer_h = clamp_height / 3;               // 12 mm at defaults
middle_ear_h    = knuckle_layer_h - pin_clearance; // 11.6 mm — vertical clearance

// Bisection cut half-extent: must clear the full outer collar radius plus margin.
bisect_half = d_inner / 2 + wall_thickness * 2 + 30;

// Repeated X centre for ears and pin holes (same for both parts)
ear_x = w_inner / 2 + wall_thickness + ear_width / 2;

// Backplate Y centre
backplate_y = -(d_inner / 2 + wall_thickness + backplate_offset);


// ---------- dispatch ----------
if (part == "back_wall_mount") back_wall_mount();
if (part == "front_clamp")     front_clamp();
if (part == "print_pins")      print_pins();


// ============================================================
// CORE FRAME GENERATOR
//
// Minkowski cylinder uses h=0.001 (effectively a 2D disk) so the
// sum produces flat top/bottom faces with only XY corner rounding.
// A finite h=1 cylinder would add an unwanted Z chamfer on both
// the outer and inner walls.
// ============================================================
module raw_collar_profile(w, d, r, wall) {
    difference() {
        minkowski() {
            cube([w + wall*2 - r*2, d + wall*2 - r*2, clamp_height - 1], center=true);
            cylinder(r=r, h=0.001, center=true);
        }
        minkowski() {
            cube([w - r*2, d - r*2, clamp_height + 5], center=true);
            cylinder(r=r, h=0.001, center=true);
        }
    }
}


// ============================================================
// ROUNDED HINGE KNUCKLE PROFILE
//
// Generates a D-shaped knuckle block: flat inner face (glues to
// collar body) and rounded outer corners.  x_sign drives which
// direction the rounded face points (+1 = right, -1 = left).
// ============================================================
module ear_knuckle_profile(w, d, h, r, x_sign) {
    linear_extrude(height = h, center = true) {
        hull() {
            // Inner flat edge — thin strip at the collar-facing side
            translate([-x_sign * w/2, -d/2]) square([0.1, d]);
            // Outer rounded corners
            translate([x_sign * (w/2 - r), -d/2 + r]) circle(r);
            translate([x_sign * (w/2 - r),  d/2 - r]) circle(r);
        }
    }
}


// ============================================================
// PART 1 — BACK WALL MOUNT
// Top knuckle: centred at z = +knuckle_layer_h, height knuckle_layer_h
//              → spans z = +knuckle_layer_h/2 .. +3*knuckle_layer_h/2
// Bottom knuckle: centred at z = -knuckle_layer_h, same height
//              → spans z = -3*knuckle_layer_h/2 .. -knuckle_layer_h/2
// Centre slot (z = ±knuckle_layer_h/2) receives the front clamp ear.
// ============================================================
module back_wall_mount() {
    difference() {
        union() {
            // Rear half of collar (Y ≤ 0)
            difference() {
                raw_collar_profile(w_inner, d_inner, tank_corner_radius, wall_thickness);
                translate([0, bisect_half, 0])
                    cube([w_inner*3, bisect_half*2, clamp_height + 40], center=true);
            }

            // Backplate
            translate([0, backplate_y, 0])
                cube([w_inner + wall_thickness*2 + 40, 8, clamp_height + 15], center=true);

            // Top and bottom rounded knuckle blocks
            for (x_sign = [-1, 1]) {
                translate([x_sign * ear_x, 0, 0]) {
                    // Top layer
                    translate([0, 0,  knuckle_layer_h])
                        ear_knuckle_profile(ear_width, ear_depth, knuckle_layer_h,
                                            ear_corner_radius, x_sign);
                    // Bottom layer
                    translate([0, 0, -knuckle_layer_h])
                        ear_knuckle_profile(ear_width, ear_depth, knuckle_layer_h,
                                            ear_corner_radius, x_sign);
                }
            }
        }

        // Backplate mounting screws
        for (x_sign = [-1, 1])
            translate([x_sign * (w_inner/2 + 12), backplate_y, 0])
                rotate([-90, 0, 0])
                    cylinder(h=20, d=screw_hole_dia, center=true);

        // Vertical pin holes through both ears
        for (x_sign = [-1, 1])
            translate([x_sign * ear_x, 0, 0])
                cylinder(h=clamp_height + 10, d=pin_hole_dia, center=true);
    }
}


// ============================================================
// PART 2 — FRONT CLAMP RETAINER
// Middle knuckle slides into the centre slot of the back mount.
// Height = knuckle_layer_h - pin_clearance → 0.2 mm gap each side.
// ============================================================
module front_clamp() {
    difference() {
        union() {
            // Front half of collar (Y ≥ 0)
            difference() {
                raw_collar_profile(w_inner, d_inner, tank_corner_radius, wall_thickness);
                translate([0, -bisect_half, 0])
                    cube([w_inner*3, bisect_half*2, clamp_height + 40], center=true);
            }

            // Middle rounded knuckle blocks
            for (x_sign = [-1, 1])
                translate([x_sign * ear_x, 0, 0])
                    ear_knuckle_profile(ear_width, ear_depth, middle_ear_h,
                                        ear_corner_radius, x_sign);
        }

        // Vertical pin holes through middle ears
        for (x_sign = [-1, 1])
            translate([x_sign * ear_x, 0, 0])
                cylinder(h=clamp_height + 10, d=pin_hole_dia, center=true);
    }
}


// ============================================================
// PART 3 — REMOVABLE HINGE PINS
// Thumbtack profile: head wider at top than base, overhangs
// neck — pinch the rim to pull.  No boolean ops, no artifacts.
// ============================================================
module print_pins() {
    shaft_r = (pin_hole_dia - 0.4) / 2;
    pin_len = clamp_height + 6;
    neck_r  = 4;   // neck radius
    neck_h  = 5;   // neck height
    head_r  = 11;  // head outer radius
    head_h  = 7;   // head height
    chamfer = 2;   // top edge chamfer

    module one_pin() {
        union() {
            cylinder(r=shaft_r, h=pin_len);
            translate([0, 0, pin_len]) {
                cylinder(r=neck_r, h=neck_h);
                translate([0, 0, neck_h])
                    hull() {
                        cylinder(r=neck_r+1,        h=0.01);
                        translate([0,0,head_h-chamfer]) cylinder(r=head_r,          h=0.01);
                        translate([0,0,head_h])          cylinder(r=head_r-chamfer,  h=0.01);
                    }
            }
        }
    }

    translate([-15, 0, 0]) one_pin();
    translate([ 15, 0, 0]) one_pin();
}
