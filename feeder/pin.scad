include <params.scad>

print_pin();

module print_pin() {
    shaft_r = (pin_hole_dia - 0.4) / 2;
    pin_len = collar_height + 15;
    base_r  = 7; waist_r = 4; top_r = 10;
    bell_h  = 4; waist_h = 8; neck_h = 5; top_h = 4; edge_r = 1.5;
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
		       [[shaft_r,0],[shaft_r,pin_len],[base_r,pin_len]], 
		       [for(a=[0:2:a1_bell])
			   [cx_bell+R_bell*cos(a), pin_len+R_bell*sin(a)]],
		       [[waist_r, pin_len+bell_h+waist_h]],
		       [for(a=[180:-2:a1_neck])
			   [cx_neck+R_neck*cos(a),
			    pin_len+z_wt+R_neck*(sin(a)-sin(180))]],
		       [[top_r, pin_len+z_wt+neck_h+top_h-edge_r]],
		       [for(a=[0:3:90])
			   [top_r-edge_r+edge_r * cos(a),
			    pin_len+z_wt+neck_h+top_h-edge_r+edge_r * sin(a)]],
		       [[0.01, pin_len+z_wt+neck_h+top_h]]));
}
