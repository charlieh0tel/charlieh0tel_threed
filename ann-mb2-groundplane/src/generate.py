#!/usr/bin/env python3
"""Generate fabrication files for the ANN-MB2 120 mm ground plane and printed mast cap.

This file is the single source of truth for every dimension. It is pure standard
library and writes the disc DXFs and preview. The printed mast cap is modeled by
src/cap.py (CadQuery), which imports its parameters from here.

    python3 src/generate.py            # writes the disc files into ./out next to src/
    python3 src/generate.py --check    # run geometry checks only, write nothing
    python3 src/generate.py --bom docs/BOM.md    # write the bill of materials only
    uv run src/cap.py                  # writes the cap STEP/STL files into ./out

All dimensions are millimeters. Edit the PARAMETERS block and re-run both; do not
hand-edit anything in out/.

Coordinate system
-----------------
Origin = disc center = antenna reference point (ARP) = mast axis.
+X = "North" = toward the antenna cable/connector. Top view.
Antenna mounting holes lie on the Y axis; the cap arms run along Y under them.
The cap's clamp ears and slit are on the -X side; its cable tie lug is on +X, under the cable.
Z = 0 is the disc underside = the cap's top face. The cap extends to -Z.
"""
import argparse
import math
import os

# ----------------------------------------------------------------------------
# PARAMETERS
# ----------------------------------------------------------------------------
# Disc
DISC_DIA = 120.0            # datasheet reference ground plane, do not change casually
T = 1.524                   # sheet thickness, 0.060 in
ANT_HOLE_SPACING = 95.0     # ANN-MB2 ear hole center-to-center (datasheet Fig. 1, +/-0.5). Measured.
M4_CLEAR = 4.5              # M4 clearance hole, disc and cap
ANT_BODY = 84.0             # antenna body is 84 x 84 (reference outline only)
ANT_EAR_R = 6.75            # (108.5 - 95.0) / 2, reference outline only
ANT_EAR_T = 6.0             # ear thickness (datasheet Fig. 1, +/-0.5), sets the screw length
ANT_BOSS_REACH = 50.9       # cable boss reach from center: 42 + (92.9 - 84), reference only
ANT_HOLE_DIA = 5.5          # ear through-hole (datasheet Fig. 1, +/-0.3), reference only
ANT_HEIGHT = 24.7           # overall height (datasheet Fig. 1, +/-0.7), reference only

# Rough antenna model for the assembly only. GUESSED by eye from Fig. 1, not dimensioned there.
ANT_BOSS_W = 10.0           # cable boss width
ANT_BOSS_H = 6.0            # cable boss height
ANT_TOP = 62.0              # side of the flat top of the tapered housing
ANT_CORNER_R = 8.0          # housing corner radius in plan
CABLE_DIA = 2.8             # RG174 jacket, nominal
CABLE_BEND_R = 15.0         # bend radius used for the modeled cable route (assumed minimum for RG174)
CABLE_LOOP_X = 58.0         # where the cable starts curving down over the disc edge, from the mast axis
CABLE_TAIL = 25.0           # cable shown continuing below the socket mouth

# Mast. The cap socket is printed to this. Nominal, not measured; tune CAP_FIT_CLEAR
# with the fit ring.
MAST_OD = 31.75             # 1-1/4 in nominal

# Printed mast cap
CAP_FIT_CLEAR = 0.4         # diametral clearance, socket bore over MAST_OD. Tune with the fit ring.
CAP_WALL = 5.0              # socket wall thickness
CAP_SOCKET_DEPTH = 45.0     # mast engagement depth
CAP_PLATE_T = 9.0           # top plate and arm thickness; the mast top stops this far below the disc
CAP_ARM_W = 16.0            # arm width
CAP_ARM_END = 8.0           # arm tip beyond the antenna hole center (= rounded end radius)
CAP_GUSSET_T = 5.0          # rib under each arm: thickness,
CAP_GUSSET_R = 36.0         #   outer radius along the arm (where the straight slope would land),
CAP_GUSSET_H = 25.0         #   height down the socket wall (likewise),
CAP_GUSSET_BLEND_R = 8.0    #   and radius of the arc that sweeps each end of the slope tangent into the arm / socket
CAP_FILLET_R = 2.0          # fillet in the inside corners where the ears, lug, and arms meet the socket
CAP_CORNER_R = 1.5          # round on the outside vertical corners of the ears and lug
CAP_SLIT_W = 3.0            # clamp slit width
CAP_KEYHOLE_DIA = 5.0       # stress-relief hole across the closed end of the slit, under the top plate
CAP_EAR_T = 6.0             # clamp ear thickness, each side of the slit
CAP_EAR_LEN = 13.0          # clamp ear length beyond the socket OD
CAP_PINCH_OFFSET = 7.0      # pinch screw axis beyond the socket OD
CAP_PINCH_Z = 40.0          # pinch screw axis below the disc underside
CAP_PINCH_NUT_DEPTH = 3.0   # hex pocket depth for the pinch nut, in the +Y ear face
CAP_LUG_LEN = 8.0           # cable tie lug on +X: length beyond the socket OD,
CAP_LUG_T = 6.0             #   thickness (across Y),
CAP_LUG_BAR = 3.0           #   and outer bar the tie wraps around
CAP_LUG_Z = (42.5, 49.0)    # tie slot centers below the disc underside
TIE_SLOT_W = 2.0            # tie slot, radial size (tie thickness plus clearance)
TIE_SLOT_H = 3.5            # tie slot, vertical size (for a 2.5 wide zip tie)
CAP_BOTTOM_R = 1.5          # round on the outer edges at the bottom (socket mouth end) of the cap
CAP_LEAD_IN = 1.0           # chamfer at the socket mouth
FIT_RING_H = 12.0           # height of the fit-test ring
PRINT_MATERIAL = "PETG"
DISC_MATERIAL = "304 stainless steel"
DISC_STATUS = "Ordered from SendCutSend 2026-11-22"
PRINT_DENSITY = 1.27        # g/cm^3, for the mass estimate only

# M4 hardware
M4_NUT_AF = 7.0             # hex nut across flats
M4_NYLOC_H = 5.0            # nyloc nut height
M4_WASHER_OD = 9.0
M4_WASHER_T = 0.8
NUT_POCKET_CLEAR = 0.3      # added to the across-flats size for printed hex pockets
NUT_POCKET_DEPTH = 5.0      # arm nut pocket depth, from the arm underside
SCREW_LENGTHS = (12, 16, 20, 25, 30, 35, 40)
SCREW_MIN_PROTRUSION = 1.5  # thread beyond the nyloc nut


# ----------------------------------------------------------------------------
# Derived geometry
# ----------------------------------------------------------------------------
def pick_screw(stack):
    """Shortest standard screw that leaves SCREW_MIN_PROTRUSION beyond the nut, or None."""
    for length in SCREW_LENGTHS:
        if length >= stack + SCREW_MIN_PROTRUSION:
            return length
    return None


def gusset_profile(socket_r):
    """Gusset outline as (radius, depth below the arm underside) segments.

    A straight slope from the arm at CAP_GUSSET_R to the socket at CAP_GUSSET_H, with an arc
    of CAP_GUSSET_BLEND_R at each end that runs out tangent to the arm underside and to the
    socket wall. The socket end aims at the socket surface at the rib's side faces, so the
    rib feathers out flush there. Returns the points and the two arc midpoints.
    """
    r0 = math.sqrt(socket_r ** 2 - (CAP_GUSSET_T / 2) ** 2)
    a, b = (CAP_GUSSET_R, 0.0), (r0, CAP_GUSSET_H)
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    d = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)        # unit vector, arm end toward socket end

    def blend(corner, u, v):
        """Arc tangent to the two rays u and v from corner: (start on u, mid, end on v, setback)."""
        half = math.acos(u[0] * v[0] + u[1] * v[1]) / 2
        t = CAP_GUSSET_BLEND_R / math.tan(half)
        bis = (u[0] + v[0], u[1] + v[1])
        n = math.hypot(*bis)
        bis = (bis[0] / n, bis[1] / n)
        k = CAP_GUSSET_BLEND_R / math.sin(half) - CAP_GUSSET_BLEND_R
        return ((corner[0] + t * u[0], corner[1] + t * u[1]), (corner[0] + k * bis[0], corner[1] + k * bis[1]),
                (corner[0] + t * v[0], corner[1] + t * v[1]), t)

    a_out, a_mid, a_in, ta = blend(a, (1.0, 0.0), d)                 # arm end: tangent to the arm underside
    b_out, b_mid, b_in, tb = blend(b, (0.0, 1.0), (-d[0], -d[1]))    # socket end: tangent to the socket wall
    return dict(r0=r0, a_out=a_out, a_mid=a_mid, a_in=a_in, b_in=b_in, b_mid=b_mid, b_out=b_out,
                reach=a_out[0], drop=b_out[1], slope_left=length - ta - tb)


def cap_geometry():
    bore_r = (MAST_OD + CAP_FIT_CLEAR) / 2
    socket_r = bore_r + CAP_WALL
    pocket_af = M4_NUT_AF + NUT_POCKET_CLEAR
    pocket_ac = pocket_af / math.cos(math.radians(30))   # across corners
    ear_half = CAP_SLIT_W / 2 + CAP_EAR_T
    # Antenna screw: ear + washer + disc + plastic above the nut + nut.
    ant_stack = ANT_EAR_T + M4_WASHER_T + T + (CAP_PLATE_T - NUT_POCKET_DEPTH) + M4_NYLOC_H
    # Pinch screw: washer + both ears and the slit, less the nut pocket, + nut.
    pinch_stack = M4_WASHER_T + 2 * ear_half - CAP_PINCH_NUT_DEPTH + M4_NYLOC_H
    # Cable route: out of the boss, over the disc edge, back in, then down the lug face.
    lug_x = socket_r + CAP_LUG_LEN
    cable_x = lug_x + CABLE_DIA / 2 + 0.2
    cable_z = T + ANT_BOSS_H / 2
    return dict(gusset=gusset_profile(socket_r), lug_x=lug_x, cable_x=cable_x, cable_z=cable_z,
                cable_down_z=cable_z - 3 * CABLE_BEND_R,     # where the cable becomes vertical
                bore_r=bore_r, socket_r=socket_r, pocket_af=pocket_af, pocket_ac=pocket_ac,
                ear_half=ear_half, arm_tip_r=ANT_HOLE_SPACING / 2 + CAP_ARM_END,
                pinch_x=-(socket_r + CAP_PINCH_OFFSET), height=CAP_PLATE_T + CAP_SOCKET_DEPTH,
                ant_stack=ant_stack, ant_screw=pick_screw(ant_stack),
                pinch_stack=pinch_stack, pinch_screw=pick_screw(pinch_stack))


def rect(layer, x1, y1, x2, y2):
    return [("L", layer, x1, y1, x2, y1), ("L", layer, x2, y1, x2, y2),
            ("L", layer, x2, y2, x1, y2), ("L", layer, x1, y2, x1, y1)]


def disc_entities(with_reference=True):
    r = M4_CLEAR / 2
    h = ANT_HOLE_SPACING / 2
    ents = [("C", "CUT", 0, 0, DISC_DIA / 2),
            ("C", "CUT", 0, h, r), ("C", "CUT", 0, -h, r)]   # antenna screws pass through into the cap
    if with_reference:
        b = ANT_BODY / 2
        w = ANT_BOSS_W / 2
        ents += [("L", "SCRIBE", -3, 0, 3, 0), ("L", "SCRIBE", 0, -3, 0, 3),
                 ("L", "SCRIBE", DISC_DIA / 2 - 6, 0, DISC_DIA / 2, 0)]   # north tick
        ents += rect("REF", -b, -b, b, b)
        ents += [("C", "REF", 0, h, ANT_EAR_R), ("C", "REF", 0, -h, ANT_EAR_R),
                 ("C", "REF", 0, 0, MAST_OD / 2)]
        ents += [("L", "REF", b, -w, ANT_BOSS_REACH, -w), ("L", "REF", ANT_BOSS_REACH, -w, ANT_BOSS_REACH, w),
                 ("L", "REF", ANT_BOSS_REACH, w, b, w)]
    return ents


# ----------------------------------------------------------------------------
# Checks
# ----------------------------------------------------------------------------
def run_checks():
    g = cap_geometry()
    disc_r = DISC_DIA / 2
    h = ANT_HOLE_SPACING / 2
    results = []

    def chk(name, value, ok):
        results.append((name, value, ok))

    # Disc and antenna
    chk("antenna body corner radius < disc radius", math.hypot(ANT_BODY / 2, ANT_BODY / 2),
        math.hypot(ANT_BODY / 2, ANT_BODY / 2) < disc_r)
    chk("antenna ear outer reach < disc radius", h + ANT_EAR_R, h + ANT_EAR_R < disc_r)
    chk("antenna hole edge-to-disc-edge >= 8", disc_r - h - M4_CLEAR / 2, disc_r - h - M4_CLEAR / 2 >= 8)

    # Cap stays under the disc
    chk("cap arm tip radius < disc radius", g["arm_tip_r"], g["arm_tip_r"] < disc_r)
    ear_corner = math.hypot(g["socket_r"] + CAP_EAR_LEN, g["ear_half"])
    chk("cap clamp ear corner radius < disc radius", ear_corner, ear_corner < disc_r)
    chk("arm rounded end fits (arm end >= half arm width)", CAP_ARM_END - CAP_ARM_W / 2,
        CAP_ARM_END >= CAP_ARM_W / 2)

    # Socket and clamp
    chk("socket depth >= 1.0 x mast OD", CAP_SOCKET_DEPTH / MAST_OD, CAP_SOCKET_DEPTH >= MAST_OD)
    closure = CAP_SLIT_W / math.pi      # bore diameter lost when the slit closes fully
    chk("slit closure exceeds fit clearance by >= 0.2", closure - CAP_FIT_CLEAR,
        closure - CAP_FIT_CLEAR >= 0.2)
    chk("pinch screw washer clears socket wall >= 0.5", CAP_PINCH_OFFSET - M4_WASHER_OD / 2,
        CAP_PINCH_OFFSET - M4_WASHER_OD / 2 >= 0.5)      # the fillet there is checked on the solid in cap.py
    chk("pinch hole to ear tip >= 3", CAP_EAR_LEN - CAP_PINCH_OFFSET - M4_CLEAR / 2,
        CAP_EAR_LEN - CAP_PINCH_OFFSET - M4_CLEAR / 2 >= 3)
    chk("pinch nut pocket fits ear length, wall >= 1.5", CAP_EAR_LEN - CAP_PINCH_OFFSET - g["pocket_ac"] / 2,
        CAP_EAR_LEN - CAP_PINCH_OFFSET - g["pocket_ac"] / 2 >= 1.5)
    chk("pinch nut pocket leaves ear >= 2.5", CAP_EAR_T - CAP_PINCH_NUT_DEPTH,
        CAP_EAR_T - CAP_PINCH_NUT_DEPTH >= 2.5)
    chk("pinch screw below plate, washer clear >= 5", CAP_PINCH_Z - CAP_PLATE_T - M4_WASHER_OD / 2,
        CAP_PINCH_Z - CAP_PLATE_T - M4_WASHER_OD / 2 >= 5)
    chk("keyhole wider than the slit", CAP_KEYHOLE_DIA - CAP_SLIT_W, CAP_KEYHOLE_DIA > CAP_SLIT_W)
    chk("ear wall beside keyhole >= 3", g["ear_half"] - CAP_KEYHOLE_DIA / 2,
        g["ear_half"] - CAP_KEYHOLE_DIA / 2 >= 3)
    key_gap = CAP_PINCH_Z - M4_WASHER_OD / 2 - (CAP_PLATE_T + CAP_KEYHOLE_DIA)
    chk("keyhole to pinch washer >= 5", key_gap, key_gap >= 5)
    chk("pinch screw above socket mouth >= 8", g["height"] - CAP_PINCH_Z, g["height"] - CAP_PINCH_Z >= 8)

    chk("wall left flat between bottom round and lead-in >= 1", CAP_WALL - CAP_BOTTOM_R - CAP_LEAD_IN,
        CAP_WALL - CAP_BOTTOM_R - CAP_LEAD_IN >= 1)
    chk("bottom round fits the lug and ear thickness", min(CAP_LUG_T / 2, CAP_EAR_T) - CAP_BOTTOM_R,
        CAP_BOTTOM_R < min(CAP_LUG_T / 2, CAP_EAR_T))

    # Cable tie lug and cable route
    chk("tie slot clear of socket wall >= 1.5", CAP_LUG_LEN - CAP_LUG_BAR - TIE_SLOT_W,
        CAP_LUG_LEN - CAP_LUG_BAR - TIE_SLOT_W >= 1.5)
    chk("lug flat face at least as wide as the cable", CAP_LUG_T - 2 * CAP_CORNER_R - CABLE_DIA,
        CAP_LUG_T - 2 * CAP_CORNER_R >= CABLE_DIA)
    chk("arm fillets leave flat arm beside the gusset", CAP_ARM_W / 2 - CAP_GUSSET_T / 2 - CAP_FILLET_R,
        CAP_ARM_W / 2 - CAP_GUSSET_T / 2 - CAP_FILLET_R >= 1)
    chk("corner round fits the lug and ear tips", min(CAP_LUG_T / 2, CAP_EAR_T) - CAP_CORNER_R,
        CAP_CORNER_R < min(CAP_LUG_T / 2, CAP_EAR_T))
    slot_top, slot_bot = min(CAP_LUG_Z) - TIE_SLOT_H / 2, max(CAP_LUG_Z) + TIE_SLOT_H / 2
    chk("first tie slot below where the cable turns vertical", slot_top + g["cable_down_z"],
        slot_top >= -g["cable_down_z"])
    chk("last tie slot to bottom round >= 1.5", g["height"] - slot_bot - CAP_BOTTOM_R,
        g["height"] - slot_bot - CAP_BOTTOM_R >= 1.5)
    web = min(b - a for a, b in zip(CAP_LUG_Z, CAP_LUG_Z[1:])) - TIE_SLOT_H if len(CAP_LUG_Z) > 1 else 99
    chk("web between tie slots >= 3", web, web >= 3)
    chk("cable bend radius >= 5 x cable diameter", CABLE_BEND_R / CABLE_DIA, CABLE_BEND_R >= 5 * CABLE_DIA)
    edge_gap = math.hypot(DISC_DIA / 2 - CABLE_LOOP_X, T - (g["cable_z"] - CABLE_BEND_R))
    chk("cable loop clears the disc edge >= 1", CABLE_BEND_R - CABLE_DIA / 2 - edge_gap,
        CABLE_BEND_R - CABLE_DIA / 2 - edge_gap >= 1)
    chk("cable loop has room to turn in toward the lug", CABLE_LOOP_X - (g["cable_x"] + CABLE_BEND_R),
        CABLE_LOOP_X >= g["cable_x"] + CABLE_BEND_R)
    chk("cable loop starts beyond the boss", CABLE_LOOP_X - ANT_BOSS_REACH, CABLE_LOOP_X >= ANT_BOSS_REACH)

    # Arm nut pockets
    chk("arm wall beside nut pocket >= 2.5", (CAP_ARM_W - g["pocket_ac"]) / 2,
        (CAP_ARM_W - g["pocket_ac"]) / 2 >= 2.5)
    chk("plastic between disc and arm nut >= 3", CAP_PLATE_T - NUT_POCKET_DEPTH,
        CAP_PLATE_T - NUT_POCKET_DEPTH >= 3)
    gp = g["gusset"]
    chk("gusset blend ends short of nut pocket >= 2", h - g["pocket_ac"] / 2 - gp["reach"],
        h - g["pocket_ac"] / 2 - gp["reach"] >= 2)
    chk("gusset starts outside socket", CAP_GUSSET_R - g["socket_r"], CAP_GUSSET_R > g["socket_r"] + 5)
    chk("gusset blend ends above the bottom round >= 5", CAP_SOCKET_DEPTH - CAP_BOTTOM_R - gp["drop"],
        CAP_SOCKET_DEPTH - CAP_BOTTOM_R - gp["drop"] >= 5)
    chk("gusset keeps a straight slope between its blends >= 5", gp["slope_left"], gp["slope_left"] >= 5)

    # Screws
    chk("standard antenna screw exists for stack", g["ant_stack"], g["ant_screw"] is not None)
    chk("standard pinch screw exists for stack", g["pinch_stack"], g["pinch_screw"] is not None)

    print(f"mast OD {MAST_OD:.2f} + fit clearance {CAP_FIT_CLEAR:.2f} = socket bore {2 * g['bore_r']:.2f}"
          f"   socket OD {2 * g['socket_r']:.2f}")
    print(f"cap: {2 * g['arm_tip_r']:.1f} across the arms, {g['height']:.1f} tall; "
          f"mast top sits {CAP_PLATE_T:.1f} below the disc underside")
    print(f"antenna screw: stack {g['ant_stack']:.2f} -> M4 x {g['ant_screw']}   "
          f"pinch screw: stack {g['pinch_stack']:.2f} -> M4 x {g['pinch_screw']}")
    all_ok = True
    for name, value, ok in results:
        all_ok &= ok
        print(f"  [{'ok' if ok else 'FAIL'}] {name}: {value:.2f}")
    return all_ok


# ----------------------------------------------------------------------------
# Writers
# ----------------------------------------------------------------------------
LAYER_COLORS = {"CUT": 7, "SCRIBE": 1, "REF": 5}


def write_dxf(path, ents):
    """Minimal ASCII DXF (R12). Entities: LINE, CIRCLE, ARC only."""
    layers = sorted({e[1] for e in ents}, key=list(LAYER_COLORS).index)
    out = []

    def e(*a):
        for i in range(0, len(a), 2):
            out.append(f"{a[i]}\n{a[i + 1]}")

    e(0, "SECTION", 2, "HEADER", 9, "$ACADVER", 1, "AC1009", 9, "$INSUNITS", 70, 4, 0, "ENDSEC")
    e(0, "SECTION", 2, "TABLES", 0, "TABLE", 2, "LAYER", 70, len(layers))
    for name in layers:
        e(0, "LAYER", 2, name, 70, 0, 62, LAYER_COLORS[name], 6, "CONTINUOUS")
    e(0, "ENDTAB", 0, "ENDSEC", 0, "SECTION", 2, "ENTITIES")
    for t in ents:
        if t[0] == "C":
            _, l, x, y, r = t
            e(0, "CIRCLE", 8, l, 10, x, 20, y, 30, 0, 40, r)
        elif t[0] == "L":
            _, l, a, b, c, d = t
            e(0, "LINE", 8, l, 10, a, 20, b, 30, 0, 11, c, 21, d, 31, 0)
        elif t[0] == "A":
            _, l, x, y, r, s, f = t
            e(0, "ARC", 8, l, 10, x, 20, y, 30, 0, 40, r, 50, s, 51, f)
    e(0, "ENDSEC", 0, "EOF")
    with open(path, "w") as fh:
        fh.write("\n".join(out) + "\n")


SVG_COLORS = {"CUT": "#111", "SCRIBE": "#c0392b", "REF": "#2a6fb0"}


def write_svg(path, ents, labels, scale=4.0, margin=40):
    """Plain preview of the same entity list. Not a fabrication drawing."""
    xs, ys = [], []
    for t in ents:
        if t[0] in ("C", "A"):
            xs += [t[2] - t[4], t[2] + t[4]]
            ys += [t[3] - t[4], t[3] + t[4]]
        else:
            xs += [t[2], t[4]]
            ys += [t[3], t[5]]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    width = (x1 - x0) * scale + 2 * margin
    height = (y1 - y0) * scale + 2 * margin + 30
    X = lambda x: margin + (x - x0) * scale
    Y = lambda y: margin + (y1 - y) * scale
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
         f'font-family="Helvetica,Arial,sans-serif" font-size="13">',
         f'<rect width="{width:.0f}" height="{height:.0f}" fill="#fff"/>']
    for t in ents:
        col = SVG_COLORS[t[1]]
        dash = "" if t[1] in ("CUT", "SCRIBE") else ' stroke-dasharray="6 4"'
        if t[0] == "L":
            o.append(f'<line x1="{X(t[2]):.1f}" y1="{Y(t[3]):.1f}" x2="{X(t[4]):.1f}" y2="{Y(t[5]):.1f}" '
                     f'stroke="{col}" stroke-width="1.6"{dash}/>')
        elif t[0] == "C":
            o.append(f'<circle cx="{X(t[2]):.1f}" cy="{Y(t[3]):.1f}" r="{t[4] * scale:.1f}" fill="none" '
                     f'stroke="{col}" stroke-width="1.6"{dash}/>')
        elif t[0] == "A":
            _, l, cx, cy, r, a0, a1 = t
            p0 = (X(cx + r * math.cos(math.radians(a0))), Y(cy + r * math.sin(math.radians(a0))))
            p1 = (X(cx + r * math.cos(math.radians(a1))), Y(cy + r * math.sin(math.radians(a1))))
            o.append(f'<path d="M{p0[0]:.1f} {p0[1]:.1f} A{r * scale:.1f} {r * scale:.1f} 0 0 0 '
                     f'{p1[0]:.1f} {p1[1]:.1f}" fill="none" stroke="{col}" stroke-width="1.6"/>')
    for x, y, text, anchor in labels:
        o.append(f'<text x="{X(x):.0f}" y="{Y(y):.0f}" fill="#222" text-anchor="{anchor}">{text}</text>')
    legend = "   ".join(sorted({t[1] for t in ents}, key=list(LAYER_COLORS).index))
    o.append(f'<text x="{margin}" y="{height - 12:.0f}" fill="#555">layers: {legend}   |   mm   |   preview only</text>')
    o.append("</svg>")
    with open(path, "w") as fh:
        fh.write("\n".join(o) + "\n")


def write_bom(path):
    """Bill of materials as Markdown. Quantities and screw lengths follow the parameters."""
    g = cap_geometry()
    n_ties = len(CAP_LUG_Z)
    lines = [
        "# Bill of materials",
        "",
        "Generated by `make` from `src/generate.py`. Do not edit by hand.",
        "",
        "Dimensions in mm unless marked.",
        "",
        "## Made parts",
        "",
        "| Qty | Part | Material | Source | File | Status |",
        "|---|---|---|---|---|---|",
        f'| 1 | Ground plane disc, ø{DISC_DIA:g}, 2 × ø{M4_CLEAR:g} holes {ANT_HOLE_SPACING:g} apart | '
        f'{DISC_MATERIAL}, {T / 25.4:.3f}" ({T:g}), no finish | SendCutSend | '
        f"`out/disc_120mm_cut_only.dxf` | {DISC_STATUS} |",
        f"| 1 | Mast cap | {PRINT_MATERIAL} | 3D print | `out/mast_cap_print.stl` | Not printed |",
        "",
        f"Test piece, not in the assembly: `out/mast_cap_fit_ring.stl`, {PRINT_MATERIAL}.",
        "",
        "## Hardware to buy",
        "",
        "| Qty | Part | Use |",
        "|---|---|---|",
        f"| 2 | M4 × {g['ant_screw']} pan head screw, A2 stainless | Antenna, down through the ears and disc into the cap |",
        f"| 1 | M4 × {g['pinch_screw']} socket head cap screw, A2 stainless | Cap clamp (pinch screw) |",
        f"| 3 | M4 flat washer, {M4_WASHER_OD:g} OD, A2 stainless | One under each screw head |",
        f"| 3 | M4 nyloc nut, {M4_NUT_AF:g} across flats, {M4_NYLOC_H:g} high, A2 stainless | "
        "Two captive under the cap arms, one in the clamp ear |",
        f"| {n_ties} | Zip tie, {TIE_SLOT_H - 1:g} wide, black UV-resistant | Antenna cable to the cap's tie lug |",
        "",
        "## Already on hand",
        "",
        "| Qty | Part |",
        "|---|---|",
        "| 1 | u-blox ANN-MB2 antenna, with its attached 5 m RG174 cable and SMA plug |",
        f'| 1 | Mast, 1-1/4" OD tube ({MAST_OD:g} nominal) |',
    ]
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="run geometry checks only")
    ap.add_argument("--bom", metavar="PATH", help="write the bill of materials to PATH and exit")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out"))
    args = ap.parse_args()

    ok = run_checks()
    if args.check:
        raise SystemExit(0 if ok else 1)
    if args.bom:
        if not ok:
            raise SystemExit("geometry checks FAILED, BOM not written")
        write_bom(args.bom)
        print("wrote:", args.bom)
        return

    os.makedirs(args.out, exist_ok=True)
    p = lambda name: os.path.join(args.out, name)
    h = ANT_HOLE_SPACING / 2

    write_dxf(p("disc_120mm_cut_only.dxf"), disc_entities(with_reference=False))
    write_dxf(p("disc_120mm_with_reference.dxf"), disc_entities(with_reference=True))
    write_svg(p("disc_120mm_preview.svg"), disc_entities(with_reference=True), [
        (6, h + 6, "2 x antenna hole: plain M4 clearance, screws pass into the cap", "start"),
        (0, MAST_OD / 2 + 3, "mast OD", "middle"),
        (DISC_DIA / 2 - 8, 4, "N", "end"),
    ])
    print("wrote:", ", ".join(sorted(os.listdir(args.out))))
    if not ok:
        raise SystemExit("geometry checks FAILED")


if __name__ == "__main__":
    main()
