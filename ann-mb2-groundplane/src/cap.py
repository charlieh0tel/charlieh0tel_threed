#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["cadquery>=2.5"]
# ///
"""Model the printed mast cap, plus the disc and a rough antenna for reference, with CadQuery.

    uv run src/cap.py            # writes STEP/STL files into ./out next to src/
    uv run src/cap.py --check    # build and verify the solids, write nothing

Every dimension comes from src/generate.py; there are no numbers to edit here.

Model frame: origin on the mast axis, Z = 0 at the disc underside (the cap's top
face), cap extending to -Z, +X = North. STEP files use this frame. The STL files
are flipped into print orientation: top plate on the bed, socket mouth and nut
pockets facing up, no supports needed.
"""
import argparse
import math
import os

import cadquery as cq

import generate as G


# Colors written into assembly.step (RGB, 0 to 1). Display only; they say nothing about
# the real materials. The cap is the part under design, so it gets the color that stands out.
ASSEMBLY_COLORS = {
    "disc": (0.78, 0.80, 0.84),
    "cap": (1.00, 0.50, 0.05),
    "mast": (0.45, 0.55, 0.65),
    "antenna": (0.95, 0.95, 0.90),
    "cable": (0.10, 0.10, 0.10),
}


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def _cyl(r, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).circle(r).extrude(z1 - z0)


def _slit_and_bore(body, g, z_bottom, z_top, x_outer, slit_top=None):
    """Cut the mast bore (with a lead-in chamfer at the mouth) and the clamp slit on -X.

    The slit runs up to slit_top (default: z_top, the top of the bore)."""
    slit_top = z_top if slit_top is None else slit_top
    body = body.cut(_cyl(g["bore_r"], z_bottom, z_top))
    lead = cq.Solid.makeCone(g["bore_r"] + G.CAP_LEAD_IN, g["bore_r"], G.CAP_LEAD_IN,
                             pnt=cq.Vector(0, 0, z_bottom), dir=cq.Vector(0, 0, 1))
    body = body.cut(cq.Workplane("XY").add(lead))
    return body.cut(_box(x_outer - 1, 0, -G.CAP_SLIT_W / 2, G.CAP_SLIT_W / 2, z_bottom - 1, slit_top))


def build_cap():
    g = G.cap_geometry()
    h = G.ANT_HOLE_SPACING / 2
    pt = G.CAP_PLATE_T
    zb = -g["height"]                       # socket mouth
    sr = g["socket_r"]
    x_ear = -(sr + G.CAP_EAR_LEN)

    # Top plate: arms along Y under the antenna holes, plus the socket roof.
    body = (cq.Workplane("XY").workplane(offset=-pt)
            .slot2D(2 * g["arm_tip_r"], G.CAP_ARM_W, 90).extrude(pt))
    body = body.union(_cyl(sr, zb, 0))
    # Clamp ears on -X. Full height so they start on the bed when printed upside down.
    body = body.union(_box(x_ear, 0, -g["ear_half"], g["ear_half"], zb, 0))
    # Cable tie lug on +X. Full height for the same reason.
    body = body.union(_box(0, g["lug_x"], -G.CAP_LUG_T / 2, G.CAP_LUG_T / 2, zb, 0))
    # Gussets under the arms, in the YZ plane.
    # Each end of the slope sweeps tangent into the arm / socket (see generate.gusset_profile).
    gp = g["gusset"]
    for sign in (1, -1):
        p = lambda rd: (sign * rd[0], -pt - rd[1])      # (radius, depth) -> (y, z)
        rib = (cq.Workplane("YZ").moveTo(*p((sr - 3, 0))).lineTo(*p(gp["a_out"]))
               .threePointArc(p(gp["a_mid"]), p(gp["a_in"])).lineTo(*p(gp["b_in"]))
               .threePointArc(p(gp["b_mid"]), p(gp["b_out"])).lineTo(*p((sr - 3, gp["drop"])))
               .close().extrude(G.CAP_GUSSET_T / 2, both=True))
        body = body.union(rib)

    # Rounds and fillets, all before the bore, slit, and holes are cut.
    def pick(test):
        return body.newObject([e for e in body.val().Edges() if test(e)])

    def vertical(e):
        a, b = e.startPoint(), e.endPoint()
        return e.geomType() == "LINE" and abs(a.x - b.x) < 1e-6 and abs(a.y - b.y) < 1e-6

    def level(e, z):
        return abs(e.startPoint().z - z) < 1e-6 and abs(e.endPoint().z - z) < 1e-6 and abs(e.Center().z - z) < 1e-6

    def on_socket(e):
        return all(abs(math.hypot(p.x, p.y) - sr) < 1e-4 for p in (e.startPoint(), e.endPoint()))

    # Outside vertical corners of the ear and lug tips.
    def tip(e):
        x = e.startPoint().x
        return vertical(e) and (abs(x - x_ear) < 1e-6 or abs(x - g["lug_x"]) < 1e-6)
    if G.CAP_CORNER_R > 0:
        body = pick(tip).fillet(G.CAP_CORNER_R)

    # Inside corners against the socket: ears, lug, and arms. The gusset roots are not
    # filleted; the gussets get their smooth ends from the tangent arcs in their profile.
    def inside(e):
        if vertical(e) and on_socket(e):
            on_gusset = abs(abs(e.startPoint().x) - G.CAP_GUSSET_T / 2) < 1e-6
            return not on_gusset
        if e.geomType() == "CIRCLE" and on_socket(e):          # arm underside against the socket
            return level(e, -pt)
        return False
    if G.CAP_FILLET_R > 0:
        body = pick(inside).fillet(G.CAP_FILLET_R)

    # Round the outer edges at the bottom, before the bore and slit are cut, so only the
    # outside outline (socket, ears, lug) is affected.
    if G.CAP_BOTTOM_R > 0:
        body = body.faces("<Z").edges().fillet(G.CAP_BOTTOM_R)

    # The slit stops at the keyhole's center so the keyhole's upper half stays a full round.
    body = _slit_and_bore(body, g, zb, -pt, x_ear, slit_top=-pt - G.CAP_KEYHOLE_DIA / 2)

    # Keyhole: a round relief across the closed end of the slit, just under the top plate,
    # through the ears and the socket wall. Replaces the slit's two sharp internal corners.
    kr = G.CAP_KEYHOLE_DIA / 2
    body = body.cut(cq.Workplane("YZ").workplane(offset=x_ear - 1).center(0, -pt - kr)
                    .circle(kr).extrude(1 - x_ear))

    # Antenna screw holes and captive nyloc nut pockets (open to the arm underside).
    holes = cq.Workplane("XY").workplane(offset=-pt - 1).pushPoints([(0, h), (0, -h)])
    body = body.cut(holes.circle(G.M4_CLEAR / 2).extrude(pt + 2))
    pockets = cq.Workplane("XY").workplane(offset=-pt - 1).pushPoints([(0, h), (0, -h)])
    body = body.cut(pockets.polygon(6, g["pocket_ac"]).extrude(G.NUT_POCKET_DEPTH + 1))

    # Tie slots through the lug, leaving an outer bar for the tie to wrap.
    x1 = g["lug_x"] - G.CAP_LUG_BAR
    for z in G.CAP_LUG_Z:
        body = body.cut(_box(x1 - G.TIE_SLOT_W, x1, -G.CAP_LUG_T, G.CAP_LUG_T,
                             -z - G.TIE_SLOT_H / 2, -z + G.TIE_SLOT_H / 2))

    # Pinch screw along Y through both ears, hex nut pocket in the +Y face.
    px, pz = g["pinch_x"], -G.CAP_PINCH_Z
    body = body.cut(cq.Workplane("XZ").center(px, pz).circle(G.M4_CLEAR / 2)
                    .extrude(g["ear_half"] + 1, both=True))
    hexbar = (cq.Workplane("XZ").center(px, pz).polygon(6, g["pocket_ac"])
              .extrude(g["ear_half"] + 1, both=True))
    # Corners up and down, so the pocket roof prints as two slopes, not a bridge.
    hexbar = hexbar.rotate((px, 0, pz), (px, 1, pz), 30)
    y_seat = g["ear_half"] - G.CAP_PINCH_NUT_DEPTH
    body = body.cut(hexbar.intersect(_box(px - 10, px + 10, y_seat, g["ear_half"] + 2, pz - 10, pz + 10)))
    return body


def build_fit_ring():
    """Short slice of the socket (same bore, wall, lead-in, and slit) for tuning CAP_FIT_CLEAR."""
    g = G.cap_geometry()
    ring = _cyl(g["socket_r"], 0, G.FIT_RING_H)
    return _slit_and_bore(ring, g, 0, G.FIT_RING_H + 1, -g["socket_r"])


def build_disc():
    h = G.ANT_HOLE_SPACING / 2
    return (cq.Workplane("XY").circle(G.DISC_DIA / 2).extrude(G.T)
            .pushPoints([(0, h), (0, -h)]).circle(G.M4_CLEAR / 2).cutThruAll())


def build_antenna():
    """Rough ANN-MB2 for the assembly: overall sizes from Fig. 1, housing shape guessed.

    Base slab with the two mounting ears, a tapered housing above it, and the cable boss
    on +X. Sits on the disc top face. The cable is separate: see build_cable().
    """
    z0 = G.T
    b, et = G.ANT_BODY, G.ANT_EAR_T
    h = G.ANT_HOLE_SPACING / 2
    base = (cq.Workplane("XY").workplane(offset=z0).rect(b, b).extrude(et)
            .edges("|Z").fillet(G.ANT_CORNER_R))
    ears = (cq.Workplane("XY").workplane(offset=z0)
            .slot2D(G.ANT_HOLE_SPACING + 2 * G.ANT_EAR_R, 2 * G.ANT_EAR_R, 90).extrude(et))
    housing = (cq.Workplane("XY").workplane(offset=z0 + et).rect(b - 4, b - 4)
               .workplane(offset=G.ANT_HEIGHT - et).rect(G.ANT_TOP, G.ANT_TOP).loft()
               .edges("not(#Z)").fillet(G.ANT_CORNER_R))
    boss = _box(b / 2 - 1, G.ANT_BOSS_REACH, -G.ANT_BOSS_W / 2, G.ANT_BOSS_W / 2, z0, z0 + G.ANT_BOSS_H)
    ant = base.union(ears).union(housing).union(boss)
    holes = cq.Workplane("XY").workplane(offset=z0 - 1).pushPoints([(0, h), (0, -h)])
    return ant.cut(holes.circle(G.ANT_HOLE_DIA / 2).extrude(et + 2))


def build_cable():
    """Illustrative cable route in the XZ plane: out of the boss, around the disc edge,
    back in under the disc, then down the outer face of the tie lug."""
    g = G.cap_geometry()
    r, a = G.CABLE_BEND_R, G.CABLE_LOOP_X
    zc, cx = g["cable_z"], g["cable_x"]
    x0 = G.ANT_BOSS_REACH
    k = r / 2 ** 0.5
    path = (cq.Workplane("XZ").moveTo(x0, zc).lineTo(a, zc)
            .threePointArc((a + r, zc - r), (a, zc - 2 * r))
            .lineTo(cx + r, zc - 2 * r)
            .threePointArc((cx + r - k, zc - 3 * r + k), (cx, zc - 3 * r))
            .lineTo(cx, -g["height"] - G.CABLE_TAIL))
    return (cq.Workplane("YZ").workplane(offset=x0).center(0, zc)
            .circle(G.CABLE_DIA / 2).sweep(path))


def build_mast(length=150.0, wall=1.65):
    """Reference tube: actual MAST_OD, top butted against the socket roof. Wall is a guess."""
    top = -G.CAP_PLATE_T
    return _cyl(G.MAST_OD / 2, top - length, top).cut(_cyl(G.MAST_OD / 2 - wall, top - length - 1, top + 1))


def volume(wp):
    return sum(s.Volume() for s in wp.solids().vals())


def verify(cap, ring, disc, mast, antenna, cable):
    g = G.cap_geometry()
    results = []

    def chk(name, value, ok):
        results.append((name, value, ok))

    for name, part in (("cap", cap), ("fit ring", ring), ("disc", disc), ("antenna (rough)", antenna)):
        n = len(part.solids().vals())
        chk(f"{name} is one valid solid", n, n == 1 and part.val().isValid())
    bb = cap.val().BoundingBox()
    chk("cap height matches parameters", bb.zlen, abs(bb.zlen - g["height"]) < 1e-6 and abs(bb.zmax) < 1e-6)
    chk("cap span across arms matches parameters", bb.ylen, abs(bb.ylen - 2 * g["arm_tip_r"]) < 1e-6)
    chk("cap does not intersect the mast", volume(cap.intersect(mast)), volume(cap.intersect(mast)) < 1e-6)
    chk("antenna (rough) does not intersect the disc", volume(antenna.intersect(disc)),
        volume(antenna.intersect(disc)) < 1e-6)
    ab = antenna.val().BoundingBox()
    chk("antenna (rough) sits on the disc top face", ab.zmin, abs(ab.zmin - G.T) < 1e-6)
    chk("antenna (rough) height matches datasheet", ab.zlen, abs(ab.zlen - G.ANT_HEIGHT) < 1e-6)
    hit = volume(cable.intersect(cap)) + volume(cable.intersect(disc)) + volume(cable.intersect(mast))
    chk("cable route clears cap, disc, and mast", hit, volume(cable) > 0 and hit < 1e-6)
    cb = cable.val().BoundingBox()
    chk("cable runs down the lug face, gap < 0.5", cb.xmin - g["lug_x"], 0 <= cb.xmin - g["lug_x"] < 0.5)
    ties = None
    for z in G.CAP_LUG_Z:      # a 1.2 x 2.5 tie through each slot
        x1 = g["lug_x"] - G.CAP_LUG_BAR
        t = _box(x1 - G.TIE_SLOT_W + 0.4, x1 - 0.4, -G.CAP_LUG_T, G.CAP_LUG_T, -z - 1.25, -z + 1.25)
        ties = t if ties is None else ties.union(t)
    chk("zip ties pass through the lug slots", volume(cap.intersect(ties)), volume(cap.intersect(ties)) < 1e-6)
    chk("cap does not intersect the disc", volume(cap.intersect(disc)), volume(cap.intersect(disc)) < 1e-6)
    # A solid mast at bore diameter must also fit: confirms the bore is clear to full depth.
    plug = _cyl(g["bore_r"] - 0.01, -g["height"], -G.CAP_PLATE_T - 0.01)
    chk("socket bore clear to full depth", volume(cap.intersect(plug)), volume(cap.intersect(plug)) < 1e-6)
    # M4 screws must pass: antenna holes through plate and disc, pinch hole through both ears.
    h = G.ANT_HOLE_SPACING / 2
    rods = (cq.Workplane("XY").workplane(offset=-G.CAP_PLATE_T - 5).pushPoints([(0, h), (0, -h)])
            .circle(2.0).extrude(G.CAP_PLATE_T + G.T + G.ANT_EAR_T + 10))
    blocked = volume(cap.intersect(rods)) + volume(disc.intersect(rods)) + volume(antenna.intersect(rods))
    chk("antenna screws pass through antenna, disc, and cap", blocked, blocked < 1e-6)
    pin = (cq.Workplane("XZ").center(g["pinch_x"], -G.CAP_PINCH_Z).circle(2.0)
           .extrude(g["ear_half"] + 5, both=True))
    chk("pinch screw passes through both ears", volume(cap.intersect(pin)), volume(cap.intersect(pin)) < 1e-6)

    kr = G.CAP_KEYHOLE_DIA / 2 - 0.05
    probe = (cq.Workplane("YZ").workplane(offset=-(g["socket_r"] + G.CAP_EAR_LEN)).center(0, -G.CAP_PLATE_T - kr - 0.05)
             .circle(kr).extrude(G.CAP_EAR_LEN + G.CAP_WALL))
    chk("keyhole open through ears and socket wall", volume(cap.intersect(probe)),
        volume(probe) > 0 and volume(cap.intersect(probe)) < 1e-6)
    # The keyhole's upper half must be a true round: solid in the corners a square slit end would cut.
    hw, top = G.CAP_SLIT_W / 2, -G.CAP_PLATE_T
    full_r = G.CAP_KEYHOLE_DIA / 2
    rise = full_r - math.sqrt(max(full_r ** 2 - (hw - 0.3) ** 2, 0))    # how far the round drops below the plate there
    corner = _box(-(g["socket_r"] + G.CAP_EAR_LEN) + 2, -g["socket_r"] - 1, hw - 0.3, hw - 0.05,
                  top - rise + 0.05, top - 0.02)
    corner = corner.union(corner.mirror("XZ"))
    chk("keyhole top is round (slit ends at its center)", volume(corner) - volume(cap.intersect(corner)),
        rise > 0.15 and abs(volume(corner) - volume(cap.intersect(corner))) < 1e-6)
    roof = _box(-(g["socket_r"] + G.CAP_EAR_LEN) + 0.1, -g["socket_r"], -1, 1, -G.CAP_PLATE_T + 0.1, -0.1)
    chk("top plate solid above the keyhole", volume(roof) - volume(cap.intersect(roof)),
        abs(volume(roof) - volume(cap.intersect(roof))) < 1e-6)

    # Washer under the pinch screw head (-Y ear face) and the nut in its pocket must seat flat.
    px, pz = g["pinch_x"], -G.CAP_PINCH_Z
    washer = (cq.Workplane("XZ").center(px, pz).circle(G.M4_WASHER_OD / 2).circle(G.M4_CLEAR / 2 + 0.1)
              .extrude(G.M4_WASHER_T).translate((0, -g["ear_half"] - 0.01, 0)))
    wb = washer.val().BoundingBox()
    chk("pinch washer seats flat on the ear, clear of the fillet", volume(cap.intersect(washer)),
        wb.ymax < -g["ear_half"] and volume(cap.intersect(washer)) < 1e-6)
    seat = (cq.Workplane("XZ").center(px, pz).circle(G.M4_WASHER_OD / 2).circle(G.M4_CLEAR / 2 + 0.1)
            .extrude(0.2).translate((0, -g["ear_half"] + 0.25, 0)))
    chk("ear is solid under the whole pinch washer", volume(seat) - volume(cap.intersect(seat)),
        abs(volume(seat) - volume(cap.intersect(seat))) < 1e-6)

    # Gusset ends must feather out: nothing of the rib beyond its blend arcs.
    gp = g["gusset"]
    past = None
    for sign in (1, -1):
        for box in (_box(-3, 3, gp["reach"] + 0.05, gp["reach"] + 1, -G.CAP_PLATE_T - 3, -G.CAP_PLATE_T - 0.02),
                    _box(-3, 3, g["socket_r"] + 0.05, g["socket_r"] + 3,
                         -G.CAP_PLATE_T - gp["drop"] - 1, -G.CAP_PLATE_T - gp["drop"] - 0.05)):
            if sign < 0:
                box = box.mirror("XZ")
            past = box if past is None else past.union(box)
    chk("gussets feather out at both ends", volume(cap.intersect(past)), volume(cap.intersect(past)) < 1e-6)

    v = volume(cap)
    print(f"cap volume {v / 1000:.1f} cm^3, about {v / 1000 * G.PRINT_DENSITY:.0f} g solid in "
          f"{G.PRINT_MATERIAL} (less at normal infill)")
    all_ok = True
    for name, value, ok in results:
        all_ok &= ok
        print(f"  [{'ok' if ok else 'FAIL'}] {name}: {value:.3f}")
    return all_ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="build and verify only")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out"))
    args = ap.parse_args()

    if not G.run_checks():
        raise SystemExit("parameter checks FAILED (see src/generate.py --check)")
    cap, ring, disc, mast = build_cap(), build_fit_ring(), build_disc(), build_mast()
    antenna, cable = build_antenna(), build_cable()
    ok = verify(cap, ring, disc, mast, antenna, cable)
    if args.check:
        raise SystemExit(0 if ok else 1)
    if not ok:
        raise SystemExit("solid model checks FAILED, nothing written")

    os.makedirs(args.out, exist_ok=True)
    p = lambda name: os.path.join(args.out, name)
    flip = lambda wp: wp.rotate((0, 0, 0), (1, 0, 0), 180)     # top plate onto the bed
    names = ["mast_cap.step", "mast_cap_print.stl", "mast_cap_fit_ring.stl", "disc_120mm.step", "assembly.step"]
    cq.exporters.export(cap, p(names[0]))
    cq.exporters.export(flip(cap), p(names[1]), tolerance=0.01, angularTolerance=0.1)
    cq.exporters.export(ring, p(names[2]), tolerance=0.01, angularTolerance=0.1)
    cq.exporters.export(disc, p(names[3]))
    assy = (cq.Assembly(name="ann_mb2_mast_mount")
            .add(disc, name="disc", color=cq.Color(*ASSEMBLY_COLORS["disc"]))
            .add(cap, name="mast_cap", color=cq.Color(*ASSEMBLY_COLORS["cap"]))
            .add(mast, name="mast_reference", color=cq.Color(*ASSEMBLY_COLORS["mast"]))
            .add(antenna, name="antenna_reference", color=cq.Color(*ASSEMBLY_COLORS["antenna"]))
            .add(cable, name="cable_reference", color=cq.Color(*ASSEMBLY_COLORS["cable"])))
    assy.export(p(names[4]))
    print("wrote:", ", ".join(names))


if __name__ == "__main__":
    main()
