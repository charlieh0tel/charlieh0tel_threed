// --- PRECISE ONEISALL 5L RECTANGULAR HOPPER DIMENSIONS ---
tank_width = 180;         // Left-to-right straight width (mm)
tank_depth = 175;         // Front-to-back straight depth (mm)
tank_corner_radius = 12;  // The actual sharp corner roundness radius (mm)
clamp_height = 36;        // Vertical height of clamp ring (mm)
wall_thickness = 8;       // Structural load thickness (mm)
clearance = 1.5;          // Tolerance gap for easy placement
screw_hole_dia = 5.0;     // #10 Wall screw sizing for backplate

// --- VERTICAL DROP PIN SETTINGS ---
pin_hole_dia = 5.5;       // Enclosed hole diameter for the drop-pin
pin_clearance = 0.4;      // Vertical wiggle room for smooth interlocking

/* [Hidden Internal Calculations] */
$fn = 80;
w_inner = tank_width + clearance*2;
d_inner = tank_depth + clearance*2;
ear_width = 16;
ear_depth = 26; // Spans across the center line to ensure full loops

// --- EXPORT TOGGLE ---
//part = "back_wall_mount"; // ["back_wall_mount", "front_clamp", "print_pins"]
part = "front_clamp";

if (part == "back_wall_mount") back_wall_mount();
if (part == "front_clamp") front_clamp();
if (part == "print_pins") print_pins();

// --- CORE FRAME GENERATOR ---
module raw_collar_profile(w, d, r, wall) {
    difference() {
        minkowski() {
            cube([w + wall*2 - r*2, d + wall*2 - r*2, clamp_height - 1], center=true);
            cylinder(r=r, h=1, center=true);
        }
        minkowski() {
            cube([w - r*2, d - r*2, clamp_height + 5], center=true);
            cylinder(r=r, h=1, center=true);
        }
    }
}

// --- PART 1: BACK WALL MOUNT (Top & Bottom Enclosed Knuckles) ---
module back_wall_mount() {
    difference() {
        union() {
            // Cut ONLY the collar frame in half (keeps Y < 0)
            difference() {
                raw_collar_profile(w_inner, d_inner, tank_corner_radius, wall_thickness);
                translate([0, d_inner, 0]) cube([w_inner*3, d_inner*2, clamp_height + 40], center=true);
            }
            
            // Wall mounting backplate
            translate([0, -(d_inner/2 + wall_thickness + 4), 0])
                cube([w_inner + wall_thickness*2 + 40, 8, clamp_height + 15], center=true);
                
            // Top and Bottom full ear blocks (Centered at Y=0, spanning Y=-13 to Y=+13)
            for (x_sign = [-1, 1]) {
                translate([x_sign * (w_inner/2 + wall_thickness + ear_width/2), 0, 0]) {
                    // Top Knuckle Layer
                    translate([0, 0, clamp_height/3])
                        cube([ear_width, ear_depth, clamp_height/3], center=true);
                    // Bottom Knuckle Layer
                    translate([0, 0, -clamp_height/3])
                        cube([ear_width, ear_depth, clamp_height/3], center=true);
                }
            }
        }
        
        // Wall Plate Mounting Screw Holes
        translate([-(w_inner/2 + 12), -(d_inner/2 + wall_thickness + 4), 0]) rotate([-90,0,0]) cylinder(h=20, d=screw_hole_dia, center=true);
        translate([(w_inner/2 + 12), -(d_inner/2 + wall_thickness + 4), 0]) rotate([-90,0,0]) cylinder(h=20, d=screw_hole_dia, center=true);
        
        // Fully enclosed vertical pin holes drilled straight through the solid ears
        translate([-(w_inner/2 + wall_thickness + ear_width/2), 0, 0]) cylinder(h=clamp_height + 10, d=pin_hole_dia, center=true);
        translate([(w_inner/2 + wall_thickness + ear_width/2), 0, 0]) cylinder(h=clamp_height + 10, d=pin_hole_dia, center=true);
    }
}

// --- PART 2: FRONT CLAMP RETAINER (Middle Enclosed Knuckle) ---
module front_clamp() {
    difference() {
        union() {
            // Cut ONLY the collar frame in half (keeps Y > 0)
            difference() {
                raw_collar_profile(w_inner, d_inner, tank_corner_radius, wall_thickness);
                translate([0, -d_inner, 0]) cube([w_inner*3, d_inner*2, clamp_height + 40], center=true);
            }
            
            // Middle ear blocks (Slides perfectly into the back mount's center gap)
            for (x_sign = [-1, 1]) {
                translate([x_sign * (w_inner/2 + wall_thickness + ear_width/2), 0, 0]) {
                    cube([ear_width, ear_depth, (clamp_height/3) - pin_clearance], center=true);
                }
            }
        }
        
        // Fully enclosed vertical pin holes drilled straight through the middle ears
        translate([-(w_inner/2 + wall_thickness + ear_width/2), 0, 0]) cylinder(h=clamp_height + 10, d=pin_hole_dia, center=true);
        translate([(w_inner/2 + wall_thickness + ear_width/2), 0, 0]) cylinder(h=clamp_height + 10, d=pin_hole_dia, center=true);
    }
}

// --- PART 3: REMOVABLE HINGE PINS ---
module print_pins() {
    for (i = [-1, 1]) {
        translate([i * 15, 0, 0]) {
            cylinder(h = clamp_height + 6, d = pin_hole_dia - 0.4, center=true);
            translate([0, 0, (clamp_height + 6)/2])
                cylinder(h = 4, d = pin_hole_dia + 6, center=true);
        }
    }
}
