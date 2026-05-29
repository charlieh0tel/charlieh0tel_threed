include <params.scad>
include <ear_knuckle.scad>
include <collar.scad>

front_clamp();

module front_clamp() {
    difference() {
        union() {
            difference() {
                raw_collar_profile(w_inner, d_inner, tank_corner_radius, wall_thickness);
                translate([0, -bisect_half, 0])
                    cube([w_inner*3, bisect_half*2, collar_height + 40], center=true);
            }
            for (x_sign = [-1, 1])
                translate([x_sign * ear_x, 0, 0])
                    ear_knuckle_profile(ear_width, ear_depth, middle_ear_h, ear_corner_radius, x_sign, 0);
        }
        for (x_sign = [-1, 1])
            translate([x_sign * ear_x, 0, 0])
                cylinder(h=collar_height + 10, d=pin_hole_dia, center=true);
    }
}
