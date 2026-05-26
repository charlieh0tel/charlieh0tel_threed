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
w_inner = tank_width  + clearance * 2;
d_inner = tank_depth  + clearance * 2;
ear_width = 16;
ear_depth = 26;
knuckle_layer_h = clamp_height / 3;
middle_ear_h    = knuckle_layer_h - pin_clearance;
bisect_half = d_inner / 2 + wall_thickness * 2 + 30;
ear_x = w_inner / 2 + wall_thickness + ear_width / 2;
backplate_y = -(d_inner / 2 + wall_thickness + backplate_offset);

if (part == "back_wall_mount") back_wall_mount();
if (part == "front_clamp")     front_clamp();
if (part == "print_pins")      print_pins();

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

module ear_knuckle_profile(w, d, h, r, x_sign) {
    linear_extrude(height = h, center = true) {
        hull() {
            translate([-x_sign * w/2, -d/2]) square([0.1, d]);
            translate([x_sign * (w/2 - r), -d/2 + r]) circle(r);
            translate([x_sign * (w/2 - r),  d/2 - r]) circle(r);
        }
    }
}

module back_wall_mount() {
    difference() {
        union() {
            difference() {
                raw_collar_profile(w_inner, d_inner, tank_corner_radius, wall_thickness);
                translate([0, bisect_half, 0])
                    cube([w_inner*3, bisect_half*2, clamp_height + 40], center=true);
            }
            translate([0, backplate_y, 0])
                cube([w_inner + wall_thickness*2 + 40, 8, clamp_height + 15], center=true);
            for (x_sign = [-1, 1]) {
                translate([x_sign * ear_x, 0, 0]) {
                    translate([0, 0,  knuckle_layer_h])
                        ear_knuckle_profile(ear_width, ear_depth, knuckle_layer_h, ear_corner_radius, x_sign);
                    translate([0, 0, -knuckle_layer_h])
                        ear_knuckle_profile(ear_width, ear_depth, knuckle_layer_h, ear_corner_radius, x_sign);
                }
            }
        }
        for (x_sign = [-1, 1])
            translate([x_sign * (w_inner/2 + 12), backplate_y, 0])
                rotate([-90, 0, 0]) cylinder(h=20, d=screw_hole_dia, center=true);
        for (x_sign = [-1, 1])
            translate([x_sign * ear_x, 0, 0])
                cylinder(h=clamp_height + 10, d=pin_hole_dia, center=true);
    }
}

module front_clamp() {
    difference() {
        union() {
            difference() {
                raw_collar_profile(w_inner, d_inner, tank_corner_radius, wall_thickness);
                translate([0, -bisect_half, 0])
                    cube([w_inner*3, bisect_half*2, clamp_height + 40], center=true);
            }
            for (x_sign = [-1, 1])
                translate([x_sign * ear_x, 0, 0])
                    ear_knuckle_profile(ear_width, ear_depth, middle_ear_h, ear_corner_radius, x_sign);
        }
        for (x_sign = [-1, 1])
            translate([x_sign * ear_x, 0, 0])
                cylinder(h=clamp_height + 10, d=pin_hole_dia, center=true);
    }
}

module print_pins() {
    shaft_r = (pin_hole_dia - 0.4) / 2;
    pin_len = clamp_height + 6;
    base_r  = 8;    // flat bottom radius
    waist_r = 3.5;  // narrowest point
    lower_h = 5;    // lower cone height
    upper_r = 9;    // upper cone top radius
    upper_h = 6;    // upper cone height

    module one_pin() {
        union() {
            cylinder(r=shaft_r, h=pin_len);
            translate([0, 0, pin_len]) {
                cylinder(r1=base_r,  r2=waist_r, h=lower_h);
                translate([0, 0, lower_h])
                    cylinder(r1=waist_r, r2=upper_r, h=upper_h);
                translate([0, 0, lower_h + upper_h])
                    intersection() {
                        sphere(r=upper_r);
                        cylinder(r=upper_r*2, h=upper_r*2);
                    }
            }
        }
    }

    translate([-15, 0, 0]) one_pin();
    translate([ 15, 0, 0]) one_pin();
}
