# Order and print sheet

## Part 1: disc (SendCutSend)

SendCutSend does not read drawing callouts, and their file guidelines require uploads to
contain only cut paths (no notes, dimensions, borders, or title blocks).

- https://sendcutsend.com/cnc-guidelines

File: `out/disc_120mm_cut_only.dxf`
Material: 0.125" 5052 aluminum (or 0.125" 304 stainless). Quantity 1.

| Holes | Location (mm, origin at center, +X = north) | Operation |
|---|---|---|
| 2 antenna holes, ø4.5 | (0, +47.5), (0, −47.5) | Cut only |

No hardware insertion, countersinking, tapping, or bending. This has not been run through
their configurator; confirm the upload preview reports ø120 mm.

Finish: anodize aluminum, or leave bare and paint. Stainless needs none.

## Part 2: mast cap (3D print)

The files in `out/` use the nominal 1-1/4" (31.75) mast OD, by the owner's decision. The
real tube has not been measured, so print the fit ring before the cap.

| File | Use |
|---|---|
| `out/mast_cap_fit_ring.stl` | Print first. 12 tall slice of the socket, a few minutes of printing. |
| `out/mast_cap_print.stl` | The cap, already in print orientation (top plate on the bed). |
| `out/mast_cap.step` | Same part in the assembly frame, for CAD or a print service. |

Procedure:

1. Run `make` if any parameter has changed.
2. Print the fit ring in the final material and on the final printer. It should slide on
   by hand without rocking, and grip when the slit is squeezed.
3. If it is tight or loose, change `CAP_FIT_CLEAR` (0.4 as drawn), regenerate, reprint the ring.
4. Print the cap.

Suggested settings, not yet tested: ASA or PETG (not PLA outdoors), 4 perimeters, 40% or
more infill, 0.2 layers, no supports. Layers are horizontal, so the arms bend across the
layers rather than peeling them, and the clamp hoop stress runs along the perimeters.

## Buy elsewhere

See the hardware table in DESIGN.md: three M4 screws, three washers, three nyloc nuts, two small zip ties.
