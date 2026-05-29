// --- PRECISE ONEISALL 5L RECTANGULAR HOPPER DIMENSIONS ---
tank_width         = 180;
tank_depth         = 175;
tank_corner_radius = 12;
clamp_height       = 36;
wall_thickness     = 8;
clearance          = 1.5;
screw_hole_dia     = 5.0;

// --- VERTICAL DROP PIN SETTINGS ---
pin_hole_dia  = 5.5;
pin_clearance = 0.4;

// --- HINGE KNUCKLE CLEARANCE ---
knuckle_relief = 0.8;

// --- ASSEMBLY CLEARANCE ---
split_chamfer   = 3.0;
hinge_clearance = 0.4; // The exact horizontal gap needed for a clean sliding fit

// --- HINGE SMOOTHING ---
ear_corner_radius = 8;

/* [Hidden] */
w_inner         = tank_width  + clearance * 2;
d_inner         = tank_depth  + clearance * 2;
ear_width       = 16;
ear_depth       = 26;
knuckle_layer_h = clamp_height / 3;
middle_ear_h    = knuckle_layer_h - pin_clearance - knuckle_relief;
bisect_half     = d_inner / 2 + wall_thickness * 2 + 30;
ear_x           = w_inner / 2 + wall_thickness + ear_width / 2;
ear_z_ctr       = knuckle_layer_h + knuckle_relief / 2;

// Dynamic collar height matching the knuckle vertical thresholds perfectly
collar_height   = ear_z_ctr * 2 + knuckle_layer_h; 

// Compact wing width spans exactly to the outer edge of the hinge knuckles
backplate_w     = (ear_x + ear_width/2) * 2;
back_y_outer    = -(d_inner / 2 + wall_thickness);
