# Order and print sheet

Hardware is in `docs/BOM.md`.

## Disc (SendCutSend)

- File: `out/disc_120mm_cut_only.dxf`. Cut paths only.
- Material: 0.060" 304 stainless. Quantity 1. No finish, no added operations.
- Two ø4.5 holes at (0, ±47.5), origin at center.
- Ordered 2026-11-22.

## Mast cap (3D print)

| File | Use |
|---|---|
| `out/mast_cap_fit_ring.stl` | 12 tall slice of the socket: bore, lead-in, slit. Print first. |
| `out/mast_cap_print.stl` | The cap, in print orientation (top face on the bed). |
| `out/mast_cap.step` | The cap in the assembly frame. |

- PETG, Prusa MK3.5S. About 62 × 111 × 54 in print orientation. No supports intended.
- Untested starting point: 4 perimeters, 40% infill, 0.2 layers.
- The bore is the nominal mast OD plus `CAP_FIT_CLEAR` (0.4). Adjust that from the fit
  ring, then `make`.
