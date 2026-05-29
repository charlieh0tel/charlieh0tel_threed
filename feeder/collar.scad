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

