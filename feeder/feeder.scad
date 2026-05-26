// --- PRECISE ONEISALL 5L RECTANGULAR HOPPER DIMENSIONS ---
tank_width         = 180;
tank_depth         = 175;
tank_corner_radius = 12;
clamp_height       = 36;
wall_thickness     = 8;
clearance          = 1.5;
backplate_offset   = 4;
screw_hole_dia     = 5.0;

// --- VERTICAL DROP PIN SETTINGS ---
pin_hole_dia  = 5.5;
pin_clearance = 0.4;

// --- HINGE SMOOTHING ---
ear_corner_radius = 5;

// --- PART SELECTOR ---
/* [Part] */
// part = "back_wall_mount"; // ["back_wall_mount", "front_clamp", "print_pins"]
// part = "front_clamp";
part = "print_pins";

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

// PINS: classic thumbtack — bell base, waist, concave neck, flat cap
// Outputs ONE pin. Print twice.
module print_pins() {
    shaft_r = (pin_hole_dia - 0.4) / 2;
    pin_len = clamp_height + 6;
    base_r  = 7;
    waist_r = 4;
    top_r   = 10;
    bell_h  = 4;
    waist_h = 8;
    neck_h  = 5;
    top_h   = 4;
    edge_r  = 1.5;
    w_bell  = waist_r - base_r;
    R_bell  = -(w_bell*w_bell + bell_h*bell_h) / (2*w_bell);
    cx_bell = base_r - R_bell;
    a1_bell = atan2(bell_h, waist_r - cx_bell);
    t_neck  = top_r - waist_r;
    R_neck  = (t_neck*t_neck + neck_h*neck_h) / (2*t_neck);
    cx_neck = waist_r + R_neck;
    z_wt    = bell_h + waist_h;
    a1_neck = atan2(neck_h, top_r - cx_neck);
    rotate_extrude($fn=80)
        polygon(concat(
            [[0,0],[shaft_r,0],[shaft_r,pin_len],[base_r,pin_len]],
            [for(a=[0:2:a1_bell])
                [cx_bell+R_bell*cos(a), pin_len+R_bell*sin(a)]],
            [[waist_r, pin_len+bell_h+waist_h]],
            [for(a=[180:-2:a1_neck])
                [cx_neck+R_neck*cos(a), pin_len+z_wt+R_neck*(sin(a)-sin(180))]],
            [[top_r, pin_len+z_wt+neck_h+top_h-edge_r]],
            [for(a=[0:3:90])
                [top_r-edge_r+edge_r*cos(a),
                 pin_len+z_wt+neck_h+top_h-edge_r+edge_r*sin(a)]],
            [[0.01, pin_len+z_wt+neck_h+top_h]]
        ));
}