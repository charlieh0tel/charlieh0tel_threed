include <params.scad>
include <ear_knuckle.scad>
include <collar.scad>

back_clamp();

module back_clamp() {
    difference() {
        union() {
            // Main unified flat-back hoop body
            difference() {
                raw_collar_profile(w_inner, d_inner, tank_corner_radius, wall_thickness);
                translate([0, bisect_half, 0])
                    cube([w_inner*3, bisect_half*2, collar_height + 40], center=true);
            }
            
            for (x_sign = [-1, 1]) {
                translate([x_sign * ear_x, 0, 0]) {
                    translate([0, 0,  ear_z_ctr])
                        ear_knuckle_profile(ear_width, ear_depth, knuckle_layer_h, ear_corner_radius, x_sign, hinge_clearance);
                    translate([0, 0, -ear_z_ctr])
                        ear_knuckle_profile(ear_width, ear_depth, knuckle_layer_h, ear_corner_radius, x_sign, hinge_clearance);
                }
            }

            // Four corner gussets at backplate/side-wall junctions.
            // Polygon in X-Y plane, extruded in Z.
            // Origin at (x_anchor, back_y_outer): backplate outer face, side wall outer face.
            // Polygon runs +Y along side wall, +X along backplate, with overlap into collar wall.
            stiff_w   = 15; // along backplate in +X
            stiff_d   = 15; // along side wall in +Y
            stiff_h   =  8; // Z height
            overlap_x =  5; // overlap into collar wall in -X to close gap
            x_anchor  = w_inner / 2 + wall_thickness;

            // x_sign = +1
            translate([x_anchor, back_y_outer, collar_height/2 - stiff_h])
                linear_extrude(height = stiff_h)
                    polygon([[0,0],[stiff_w,0],[0,stiff_d],[-overlap_x,0]]);
            translate([x_anchor, back_y_outer, -collar_height/2])
                linear_extrude(height = stiff_h)
                    polygon([[0,0],[stiff_w,0],[0,stiff_d],[-overlap_x,0]]);

            // x_sign = -1: mirror in X
            mirror([1,0,0]) {
                translate([x_anchor, back_y_outer, collar_height/2 - stiff_h])
                    linear_extrude(height = stiff_h)
                        polygon([[0,0],[stiff_w,0],[0,stiff_d],[-overlap_x,0]]);
                translate([x_anchor, back_y_outer, -collar_height/2])
                    linear_extrude(height = stiff_h)
                        polygon([[0,0],[stiff_w,0],[0,stiff_d],[-overlap_x,0]]);
            }
        }
        
        for (x = [-backplate_w/2 + 10, -backplate_w/4, 0, backplate_w/4, backplate_w/2 - 10])
            translate([x, back_y_outer + wall_thickness/2, 0])
                rotate([-90,0,0]) cylinder(h=wall_thickness * 3, d=screw_hole_dia, center=true);
                
        for (x_sign = [-1, 1])
            translate([x_sign * ear_x, 0, 0])
                cylinder(h=collar_height + 10, d=pin_hole_dia, center=true);
        
        for (x_sign = [-1, 1])
            for (z_sign = [-1, 1])
                translate([x_sign * ear_x, (ear_depth/2 - split_chamfer/2) + 0.01, z_sign * ear_z_ctr])
                    cube([ear_width + 2, split_chamfer + 0.02, knuckle_layer_h + 0.1], center=true);
                    
        knuckle_gap  = 2 * (ear_z_ctr - knuckle_layer_h/2);  
        relief_depth = 2;                                    
        for (x_sign = [-1, 1])
            translate([x_sign * (w_inner/2 + wall_thickness - relief_depth/2), -ear_depth/4, 0])
                cube([relief_depth + 0.01, ear_depth/2, knuckle_gap], center=true);
    }
}
