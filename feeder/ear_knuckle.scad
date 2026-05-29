include <params.scad>

module raw_collar_profile(w, d, r, wall) {
    difference() {
        union() {
            // 1. Pristine rounded hopper profile ring core
            difference() {
                minkowski() {
                    cube([w + wall*2 - r*2, d + wall*2 - r*2, collar_height], center=true);
                    cylinder(r=r, h=0.001, center=true);
                }
                minkowski() {
                    cube([w - r*2, d - r*2, collar_height + 5], center=true);
                    cylinder(r=r, h=0.001, center=true);
                }
            }
            // 2. Integrated flat mounting wall flange (Kept sharp and flat)
            translate([0, back_y_outer + wall/2, 0])
                cube([backplate_w, wall, collar_height], center=true);
        }
        // Clean out any inner wall bleed from the flat flange block
        minkowski() {
            cube([w - r*2, d - r*2, collar_height + 5], center=true);
            cylinder(r=r, h=0.001, center=true);
        }
    }
}

// Symmetrical layout math prevents all distortion, fins, and steps
module ear_knuckle_profile(w, d, h, r, x_sign, clear_inner = 0) {
    overlap = 2.0; 
    mirror([x_sign == -1 ? 1 : 0, 0, 0]) {
        linear_extrude(height = h, center = true) {
            difference() {
                // Combine the rounded ear profile with a rock-solid wall anchor pad
                union() {
                    hull() {
                        translate([-w/2, -d/2]) square([0.1, d]);
                        translate([w/2 - r, -d/2 + r]) circle(r);
                        translate([w/2 - r,  d/2 - r]) circle(r); 
                    }
                    translate([-w/2 - overlap, -d/2]) square([overlap + 0.1, d]);
                }
                // Crisp 90-degree rectangle cutout for the slider clearance face (Y >= 0)
                if (clear_inner > 0) {
                    translate([-w/2 - overlap - 0.1, -0.01]) 
                        square([overlap + clear_inner + 0.1, d/2 + 0.1]);
                }
            }
        }
    }
}

