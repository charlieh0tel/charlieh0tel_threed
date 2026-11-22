# Design

All dimensions in mm unless marked.

## Antenna facts (u-blox ANN-MB2)

From the datasheet text and Figure 1 (`ref/ann-mb2_datasheet_fig1_mechanical_drawing.png`).
Datasheet: https://cdn.sparkfun.com/assets/3/3/f/a/f/ANN-MB2_DataSheet_UBXDOC-GPS-27500.pdf

| Item | Value | Source |
|---|---|---|
| Body | 84.0 ±0.5 square | Fig. 1 |
| Overall across ears | 108.5 ±1 | Fig. 1 |
| Overall across cable boss | 92.9 ±1 | Fig. 1 |
| Height | 24.7 ±0.7 | Fig. 1 |
| Ear thickness | 6.0 ±0.5 | Fig. 1 |
| Mounting holes | 2 × ø5.5 ±0.3 through, in the ears | Fig. 1 |
| Hole center-to-center | 95.0 ±0.5 | Fig. 1, READ FROM THE DRAWING, not labelled as hole spacing. Unverified. |
| Hole construction | Non-threaded brass inserts (compression limiters) | Owner, inspecting the part |
| Housing plastic | Possibly GF PA6 | Owner's guess |
| Mounting | Magnetic base, or 2 × M4 screws | Datasheet Table 3 |
| Antenna reference point (ARP) | Center of the body, at the base | Fig. 1 |
| "North" | Toward the cable connector | Datasheet phase-center section |
| Cable | RG174, 5 m, SMA plug, exits one side of the body | Datasheet |
| Bands | L/L1 1535–1602 MHz; L5/L2/B3/E6 1166–1285 MHz | Datasheet |

The 95.0 reading rests on arithmetic: (108.5 − 95.0) / 2 = 6.75 ear radius, which fits a
ø5.5 hole. Confirm with calipers before ordering.

## Why ø120 and flat

The datasheet states the patch and RF specifications were measured on a ø12 cm ground plane,
that phase-center offsets were measured on a circular 120 mm ground plane, and that changing
the size or shape may affect the phase-center offset. Typical "Up" offsets from the ARP on
that plane: L1 9.10, L2 6.99, L5 6.37, E6 7.66, B3 7.52. Horizontal offset under 6.

Consequences:

- Plain flat circle, no skirt, flange, or rolled edge. The cap under it is printed plastic and stays inside the disc outline.
- ARP on the disc axis. The body corners reach r = 59.4, so the antenna fits inside the disc
  with about 0.6 to spare. The owner expected the plane to extend further; it was left at 120
  to match the reference condition. A larger plane is electrically acceptable but the
  published offsets would no longer strictly apply.
- Keep the assembly off larger conductive surfaces, which would become the effective ground plane.

## Coordinates

Origin = disc center = ARP = mast axis. +X = North = cable side. Top view.
Antenna holes on the Y axis; the cap arms run along Y under them. The cap's clamp ears
and slit are on the −X side. Z = 0 is the disc underside (the cap's top face).

## Parts

### Disc

- ø120.0, 0.125" (3.175) sheet. 5052 aluminum, or 304 stainless for permanent outdoor use.
- 2 plain ø4.5 holes at (0, ±47.5). Cut only: no clinch nuts, no countersinks, no bend.
- Scribed north tick on +X at the edge (manual; not part of the cut file).

### Mast cap (3D printed)

One printed part that slips over the top of the mast and carries the disc. Modeled in
`src/cap.py` (CadQuery) from the parameters in `src/generate.py`.

- Socket: bore = nominal mast OD + `CAP_FIT_CLEAR` (31.75 + 0.4 = ø32.15 as drawn), wall 5,
  45 deep, 1 lead-in chamfer at the mouth. The mast top butts against the socket roof,
  9 below the disc underside.
- Clamp: a 3 wide slit on the −X side between two 6 thick ears, closed by one M4 pinch
  screw 40 below the disc, with a hex pocket for its nut in the +Y ear. Closing the slit
  fully takes about 0.95 off the bore diameter, which is the whole adjustment range. The
  slit ends under the top plate in a ø5 keyhole rather than square corners.
- Arms: 16 wide, 9 thick, along ±Y to r = 55.5, with a ø4.5 hole and a hex pocket for a
  captive M4 nyloc nut under each antenna hole. A 5 thick gusset under each arm.
- Cable tie lug: a 6 thick rib on the +X side of the socket, directly under the cable exit,
  standing 8 off the socket with two 2 × 3.5 slots at 41 and 49 below the disc. The cable
  goes out over the disc edge, curves back in under the disc, and is zip-tied to the lug's
  outer face before running down the mast. The curve keeps cable weight and wind load off
  the antenna's cable boss, and its low point acts as a drip loop.
- Fillets and rounds: 2 fillets in the inside corners where the ears, lug, and arms meet
  the socket (the gusset roots are not filleted; instead each end of a
  gusset's slope sweeps tangent into the arm or the socket on an 8 radius); 1.5 rounds on the outside corners of the ears and lug and around
  the bottom edge. The top face (on the print bed) and the arm edges are left sharp.
- Everything stays inside the disc outline (largest radius 55.5).
- Printed upside down, top plate on the bed: the socket mouth and arm nut pockets face up,
  so no supports are needed. `out/mast_cap_print.stl` is already in that orientation.
- `out/mast_cap_fit_ring.stl` is a 12 tall slice of the socket for tuning the fit first.

### Hardware

| Use | Part |
|---|---|
| Antenna through disc into cap | 2 × M4 × 25 A2 pan head, 2 × M4 washer, 2 × M4 nyloc nut |
| Cap clamp | 1 × M4 × 20 A2 socket head, 1 × M4 washer, 1 × M4 nyloc nut |
| Cable to lug | 2 × zip tie, 2.5 wide, UV-resistant (black) for outdoor use |

Screw lengths are computed by `src/generate.py --check` from the stack. The antenna screw
stack is 18.98, so an M4 × 20 would leave only 1.0 beyond the nyloc; × 25 is selected and
stands about 6 below the arm.

## Assembly stack, top to bottom

1. M4 pan head and washer, down through the antenna ear (brass limiter).
2. Antenna, base on the disc top face.
3. Disc. The screws pass through plain holes.
4. Cap arm, 4 of plastic between the disc and the nut.
5. M4 nyloc nut, captive in the hex pocket under the arm.

The same two screws hold the antenna to the disc and the disc to the cap. Then the cap
slips over the mast until the mast top meets the socket roof, and the pinch screw is tightened.

## Decisions and reasons

| Decision | Reason |
|---|---|
| Screw mount, ignore the magnet | Owner's instruction. Frees the material choice (no ferromagnetic plate needed). |
| Screws go top-down through the ears | The ear holes are plain ø5.5 through-holes, not threads. |
| M4, not M5 | Datasheet says M4. M5 would locate better in ø5.5 but binds at worst-case tolerance (±0.5 spacing, ±0.3 bore). |
| Printed mast cap replaces the sheet-metal bracket and U-bolts | Owner's instruction (2026-11-22). Removes the bend, the bend-deduction uncertainty, the countersinks, and the clinch nuts. |
| Disc has two holes only | Owner's instruction. The antenna screws continue through the disc into the cap, so no separate disc-to-mount fasteners are needed and the top stays flush. |
| Mast OD is the critical dimension, taken as the nominal 1-1/4" (31.75) | It sets the printed socket bore directly. Owner's decision (2026-11-22) to use the nominal rather than a caliper measurement; the fit ring and `CAP_FIT_CLEAR` take up the difference on the real tube. |
| Split socket with a pinch screw, not a plain slip fit or set screws | Takes up print and tube tolerance (about 0.95 on diameter) and grips without point-loading the tube. ASSUMED; not yet confirmed by the owner. |
| Keyhole at the closed end of the clamp slit | Owner's choice (2026-11-22). Removes the sharp internal corners where a printed clamp would start to crack. |
| Captive nyloc nuts in the cap arms, not heat-set inserts or printed threads | Steel thread, prevailing-torque locking without threadlocker, no insertion tooling. ASSUMED; not yet confirmed by the owner. |
| Zip-tie lug on the cap for the cable, not a snap clip or a guide arm | Owner's choice (2026-11-22). The cable has a captive SMA plug, so the feature must be open-sided; a tie does not depend on print tolerance. Adds nothing above the disc and leaves the disc a plain circle. |
| Moderate torque on the antenna screws | The clamp path now includes 4 of printed plastic, which creeps; the brass limiters no longer make it an all-metal joint. Snug plus the nyloc, about 0.8–1 N·m, and recheck after the first hot days. This figure is an estimate. |
| No liquid threadlocker | Risk of stress-cracking the antenna housing and the printed cap. Use nyloc nuts. |
| Mast top stops 9 below the disc | Socket roof thickness. The mast is a conductor on the axis under the plane, as it was with the bracket. |
| 0.125" sheet | Carried over. It was chosen as the thinnest stock SendCutSend countersinks, which no longer applies; see OPEN_ITEMS.md. |
| Anodize or paint aluminum, or use 304 | Brass limiter on bare aluminum is a poor galvanic pair outdoors. DC contact to the plate is not needed; coupling is capacitive. |
| SendCutSend for the disc | Plain laser-cut circle with two holes. |

## Rejected or parked alternatives

- Sheet-metal L-bracket with U-bolts (superseded 2026-11-22 by the printed cap). One 90° bend
  in 0.125" sheet, 70 wide: a flange under the disc held by three countersunk M4 flat-heads
  at r = 24, a relief window across the bend so the mast could butt the flange, and a leg
  with two rows of 8.5 wide U-bolt slots (38–52 center to center) at 25 and 65 below the
  flange. The disc carried M4 clinch nuts for the antenna screws. Its generator code and
  DXF were removed.
- 5/8"-11 center hub (ø40 × 12.7 puck, tapped). Valid if the mast ever becomes a survey pole.
- PCB as the ground plane (ø120 two-layer, copper pours) from JLCPCB or PCBWay. Fine
  electrically, weak mechanically on a mast. Reasonable for bench use.
- One-piece CNC-turned disc with integral boss from JLCPCB or PCBWay CNC. Not priced.
