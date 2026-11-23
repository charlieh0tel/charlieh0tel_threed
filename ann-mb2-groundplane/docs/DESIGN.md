# Design

A ø120 ground plane for a u-blox ANN-MB2 GNSS antenna, on a 3D-printed cap that clamps over
the top of a 1-1/4" tube mast. Permanent outdoor installation.

All dimensions in mm unless marked. Every dimension lives in `src/generate.py`; the numbers
here are a description of it, not a second source.

## Antenna (u-blox ANN-MB2)

From the datasheet and its Figure 1 (`ref/ann-mb2_datasheet_fig1_mechanical_drawing.png`).
Datasheet: https://cdn.sparkfun.com/assets/3/3/f/a/f/ANN-MB2_DataSheet_UBXDOC-GPS-27500.pdf
(a copy is in `third_party/`; see the `NOTICE.md` there).

| Item | Value | Source |
|---|---|---|
| Body | 84.0 ±0.5 square | Fig. 1 |
| Overall across ears | 108.5 ±1 | Fig. 1 |
| Overall across cable boss | 92.9 ±1 | Fig. 1 |
| Height | 24.7 ±0.7 | Fig. 1 |
| Ear thickness | 6.0 ±0.5 | Fig. 1 |
| Mounting holes | 2 × ø5.5 ±0.3 through, in the ears | Fig. 1 |
| Hole center-to-center | 95.0 ±0.5 | Fig. 1; measured 95 on the antenna |
| Hole construction | Non-threaded metal inserts (compression limiters), apparently brass | Inspection |
| Housing plastic | Possibly GF PA6 | Guess |
| Mounting | Magnetic base, or 2 × M4 screws | Datasheet Table 3 |
| Antenna reference point (ARP) | Center of the body, at the base | Fig. 1 |
| "North" | Toward the cable connector | Datasheet phase-center section |
| Cable | RG174, 5 m, SMA plug, exits one side of the body | Datasheet |
| Bands | L/L1 1535–1602 MHz; L5/L2/B3/E6 1166–1285 MHz | Datasheet |

## Why ø120 and flat

The datasheet states the patch and RF specifications were measured on a ø12 cm ground plane,
that phase-center offsets were measured on a circular 120 mm ground plane, and that changing
the size or shape may affect the phase-center offset. Typical "Up" offsets from the ARP on
that plane: L1 9.10, L2 6.99, L5 6.37, E6 7.66, B3 7.52. Horizontal offset under 6.

Consequences:

- The disc is a plain flat circle: no skirt, flange, notch, or rolled edge.
- The ARP is on the disc axis. The antenna body's corners reach r = 59.4, so it fits inside
  the disc with about 0.6 to spare. A larger plane would be electrically acceptable, but the
  published offsets would no longer strictly apply.
- Nothing conductive sits above the disc's top face except the antenna and its two screws.
- The cap is plastic and stays under the disc, inside its outline.
- Keep the assembly off larger conductive surfaces, which would become the effective
  ground plane.

## Coordinates

Origin = disc center = ARP = mast axis. +X = North = cable side. Top view.
Z = 0 is the disc underside, which is also the cap's top face.

- Antenna holes are on the Y axis; the cap's arms run along Y under them.
- The cap's clamp ears and slit are on −X.
- The cap's cable tie lug is on +X, under the cable exit.

## Parts

Quantities, materials, and hardware to buy are in `docs/BOM.md`.

### Disc

- ø120, 0.060" (1.524) 304 stainless sheet, no finish. About 138 g.
- Two plain ø4.5 holes at (0, ±47.5). Laser cut only.
- A scribed north tick on +X at the edge, if wanted, is done by hand. It is not in the cut file.

### Mast cap

One PETG part, about 76 g if solid. It slips over the top of the mast and carries the disc.
Modeled in `src/cap.py` (CadQuery).

- **Socket.** Bore = mast OD + `CAP_FIT_CLEAR` (31.75 + 0.4 = ø32.15), wall 5, 45 deep, with
  a 1 lead-in chamfer at the mouth. The mast top butts against the socket roof, 9 below the
  disc underside.
- **Clamp.** A 3 wide slit on −X between two ears, each 6 thick and standing 13 off the
  socket. One M4 pinch screw closes it, 40 below the disc and 7 out from the socket, with a
  hex pocket for its nut in the +Y ear. Closing the slit fully takes about 0.95 off the
  bore diameter, which is the whole adjustment range. The slit stops at the center of a ø5
  keyhole just under the roof, so its closed end is a full round.
- **Arms.** 16 wide, 9 thick, along ±Y to r = 55.5. Each has a ø4.5 hole under an antenna
  hole and a hex pocket below it for a captive M4 nyloc nut, leaving 4 of plastic between
  the disc and the nut.
- **Gussets.** A 5 thick rib under each arm, running 36 out along the arm and 25 down the
  socket. Each end of its slope sweeps tangent into the arm or the socket on an 8 radius.
- **Cable tie lug.** A 6 thick rib on +X standing 8 off the socket, with two 2 × 3.5 slots
  at 42.5 and 49 below the disc. The cable goes out over the disc edge, curves back in
  under the disc, and is zip-tied to the lug's outer face before running down the mast.
  The curve keeps cable weight and wind load off the antenna's cable boss, and its low
  point is a drip loop.
- **Fillets and rounds.** 2 fillets in the inside corners where the ears, lug, and arms
  meet the socket. 1.5 rounds on the outside corners of the ears and lug and around the
  bottom edge. The gusset roots, the top face, and the arm edges are sharp.

The cap is 111 across the arms and 54 tall, with nothing beyond r = 55.5.

Printed top face down, no supports intended; the pinch hole, nut pocket, tie slots, and
keyhole shoulders bridge. `out/mast_cap_print.stl` is in that orientation, about
62 × 111 × 54. `out/mast_cap_fit_ring.stl` is a 12 tall slice of the socket.

### Reference models

`out/assembly.step` also contains a mast tube, the antenna, and its cable, for checking fit
by eye. They are not parts.

- Mast: the OD is the real parameter; the wall and length are placeholders.
- Antenna: overall sizes are from the datasheet, but the housing shape is guessed and
  simplified. Do not judge clearance against the housing from it.
- Cable: the route is illustrative.
- Colors are for display only.

## Assembly

Stack at each antenna screw, top to bottom:

1. M4 pan head screw and washer.
2. Antenna ear, through its metal insert.
3. Disc, through a plain hole.
4. Cap arm.
5. M4 nyloc nut, captive in the hex pocket under the arm.

The same two screws hold the antenna to the disc and the disc to the cap. The stack is
17.32, so an M4 × 20 leaves 2.7 of thread beyond the nut.

Then the cap slips over the mast until the mast top meets the socket roof, the pinch screw
is tightened, and the cable is tied to the lug.

- Antenna screw torque: about 0.8–1 N·m (estimate; u-blox gives none). The joint clamps
  through 4 of PETG, which creeps.
- No liquid threadlocker: stress-cracking risk to the housing and the cap.

## Decisions and reasons

Mounting:

| Decision | Reason |
|---|---|
| Screw mount, not the magnet | Frees the material choice: no ferromagnetic plate needed. |
| Screws go top-down through the ears | The ear holes are plain ø5.5 through-holes, not threads. |
| M4, not M5 | The datasheet says M4. M5 would locate better in ø5.5 but binds at worst-case tolerance (±0.5 spacing, ±0.3 bore). |
| Antenna screws continue through the disc into the cap | The disc has two holes only. No separate disc-to-mount fasteners, and the top stays flush. |

Disc:

| Decision | Reason |
|---|---|
| ø120 flat circle | Matches the datasheet's reference ground plane. See above. |
| 304 stainless, no finish | Permanent outdoor installation. The antenna's inserts look like brass, and bare aluminum corrodes galvanically against brass, plated steel, or stainless alike. Stainless needs no coating. DC contact to the plate is not needed; coupling is capacitive. |
| 0.060" sheet | Thickness makes no difference to the antenna at these sizes, and thinner sheet keeps the mass on the printed clamp down. |
| SendCutSend | A plain laser-cut circle with two holes. |

Cap:

| Decision | Reason |
|---|---|
| Printed cap over the mast top | One part, no bends, and no hardware on the disc. |
| Mast OD taken as the nominal 1-1/4" (31.75) | Not measured. It sets the printed bore directly; the fit ring and `CAP_FIT_CLEAR` take up the difference on the real tube. |
| Split socket with a pinch screw | Takes up print and tube tolerance and grips without point-loading the tube, unlike a plain slip fit or set screws. |
| Keyhole at the closed end of the slit | Removes the sharp internal corners where a printed clamp would start to crack. |
| Captive nyloc nuts in the arms | Steel thread and prevailing-torque locking with no threadlocker and no insertion tooling, unlike heat-set inserts or printed threads. |
| Fillets at the ear, lug, and arm junctions; tangent blends at the gusset ends | Printed PETG is notch-sensitive. The gusset roots are left sharp because a fillet cannot follow them out to the thin ends of the rib. |
| Zip-tie lug for the cable | The cable has a captive SMA plug, so the feature must be open-sided, and a tie does not depend on print tolerance. Adds nothing above the disc. |
| Mast top stops 9 below the disc | The socket roof thickness. The mast is a conductor on the axis, under the plane. |
| PETG | The printer is an open-frame Prusa MK3.5S, where ASA tends to warp and split between layers without an enclosure. PETG handles outdoor heat and moisture; it is less UV-stable than ASA, but the cap is shaded under the disc. |

## Unverified

- Antenna: ear thickness 6.0, inserts flush with both ear faces, base flat. Taken from Fig. 1.
- Mast OD: nominal. A tube more than 0.4 over will not enter; more than about 0.55 under
  and the clamp bottoms out.
- `CAP_FIT_CLEAR = 0.4` and `NUT_POCKET_CLEAR = 0.3` are untested.
- The cap has not been sliced or printed.
- No stress or creep analysis of the clamp or arms.
- The cap closes the mast top; condensation in the tube has no outlet there.
- Cable bend radius of 15 is assumed for RG174. Tie slots assume a 2.5 wide tie.
- No RF verification. The screw heads stand about 9 above the plane at r = 47.5.
- The DXFs are hand-written R12 ASCII. They open in LibreCAD and parse with `ezdxf`.
- Antenna dimensions came from a screenshot of Fig. 1 and a text extraction; the PDF in
  `third_party/` has not been re-read against them.

## Alternatives not taken

- Sheet-metal L-bracket with U-bolts: needs a bend, countersinks, and clinch nuts.
- Anodized 5052 H32 disc: a third of the mass, but relies on a thin coating under the
  clamped inserts, with bare rack marks.
- 5/8"-11 center hub, if the mast ever becomes a survey pole.
- PCB ground plane: fine electrically, weak mechanically on a mast.
- One-piece CNC-turned disc with integral boss. Not priced.
