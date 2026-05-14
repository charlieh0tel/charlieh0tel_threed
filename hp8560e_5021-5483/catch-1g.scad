// Catch Latch (Part 15)
// Swapped: 1.5" (38.1mm) Length, 18mm Width

// --- User Parameters ---
hole_spacing = 25.4;       // 1 inch exact spacing
screw_clearance_dia = 2.8; // M2.5 clearance

// Base Rectangular Body
total_width = 18.0;        // 18mm wide
total_height = 38.1;       // 1.5 inches long (tall)
base_thickness = 2.5;

// Thick Section (Front face, right side)
// This is the raised pad the screws go through
thick_width = 6.35;        // Scaled to fit the 18mm total width
thick_extra = 3.175;       // 0.125 inches protrusion
total_thickness = base_thickness + thick_extra;

// Catch Section (Back face, left edge)
catch_depth = 3.0;     // How far back it extends from the base plate
catch_wall_thickness = 1.0; 
catch_lip_width = 1.0; // Overhang hooking inwards (to the right)
catch_lip_thickness = 1.0;

$fn = 64; // High resolution for smooth holes

difference() {
    union() {
        // 1. Base Rectangular Body (The middle layer)
        cube([total_width, total_height, base_thickness]);

        // 2. Thick Section on the FRONT (+Z)
        // Positioned on the right side of the part
        translate([total_width - thick_width, 0, base_thickness])
            cube([thick_width, total_height, thick_extra]);

        // 3. Catch Portion on the BACK (-Z)
        // Positioned on the left edge, extending backwards
        translate([0, 0, -catch_depth])
            cube([catch_wall_thickness, total_height, catch_depth]);

        // 4. Catch Lip (Hooking inwards to the right, towards the chassis)
        translate([catch_wall_thickness, 0, -catch_depth])
            cube([catch_lip_width, total_height, catch_lip_thickness]);
    }

    // --- Screw Holes ---
    // Centered vertically, and centered horizontally within the thick section
    center_x = total_width - (thick_width / 2);
    center_y = total_height / 2;

    // Top Hole
    translate([center_x, center_y + (hole_spacing / 2), -catch_depth - 5])
        cylinder(h = total_thickness + catch_depth + 10, d = screw_clearance_dia);

    // Bottom Hole
    translate([center_x, center_y - (hole_spacing / 2), -catch_depth - 5])
        cylinder(h = total_thickness + catch_depth + 10, d = screw_clearance_dia);
}