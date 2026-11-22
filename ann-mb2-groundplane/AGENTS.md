# ANN-MB2 ground plane and mast mount

IMPORTANT: No agent attributes anywhere (commits, PRs, issues, etc) an
anytime!  NO EXCEPTIONS!

## Goal

A ø120 mm ground plane for a u-blox ANN-MB2 GNSS antenna,
screw-mounted (not magnetic), on a plain 1-1/4" OD tube mast. The disc
is laser-cut sheet from SendCutSend (JLCPCB and PCBWay are the
fallback vendors). It sits on a 3D-printed cap that clamps over the
mast top.

## State

The design is complete on paper and nothing has been ordered, printed,
or built. On 2026-11-22 the sheet-metal bracket and U-bolts were
superseded by the printed mast cap, and the disc dropped to two plain
holes.

The mast OD is the critical dimension: it sets the printed socket
bore. The owner decided (2026-11-22) to use the nominal 1-1/4" (31.75)
rather than a measured value. Any difference on the real tube is taken
up by printing the fit ring first and adjusting `CAP_FIT_CLEAR`.

Fabrication files have NOT been opened in a CAD tool or slicer or
uploaded to SendCutSend.  They were checked only by `src/generate.py
--check` (arithmetic) and `src/cap.py --check` (solid-model
interference checks).

Read these first:

- `docs/DESIGN.md`: requirements, decisions and their reasons, the assembly stack.
- `docs/ORDER_SHEET.md`: disc order details and the cap print procedure.
- `docs/OPEN_ITEMS.md`: everything unverified. Most next work is in this file.

## Layout

| Path | What |
|---|---|
| `Makefile` | `make` regenerates everything in `out/`; `make check` runs both check passes; `make clean` removes the generated files. Needs GNU Make 4.3 or later and `uv`. |
| `src/generate.py` | Single source of truth for every dimension. Parameters at the top; writes the disc DXFs and preview. Stdlib only. |
| `src/cap.py` | CadQuery model of the cap, disc, and assembly. Imports all dimensions from `generate.py`. Run with `uv run src/cap.py`; `uv` fetches CadQuery from the inline script metadata. |
| `out/disc_120mm_cut_only.dxf` | Disc, upload this one. CUT layer only. |
| `out/disc_120mm_with_reference.dxf` | Disc plus SCRIBE and REF layers (antenna footprint, mast OD, north tick). Not for upload. |
| `out/disc_120mm_preview.svg` | Preview drawn from the same entity list. Not a fabrication drawing. |
| `out/mast_cap_fit_ring.stl` | Short slice of the socket. Print this first to tune the fit. |
| `out/mast_cap_print.stl` | Cap in print orientation (top plate on the bed). |
| `out/mast_cap.step`, `out/disc_120mm.step`, `out/assembly.step` | Solids in the assembly frame. The assembly also includes a reference mast tube and a rough antenna with its cable routed to the tie lug; the antenna housing shape is guessed, only its overall sizes come from the datasheet. |
| `ref/ann-mb2_datasheet_fig1_mechanical_drawing.png` | Datasheet Figure 1, the source for all antenna dimensions. |
| `third_party/` | The u-blox datasheet PDF, with a `NOTICE.md` stating whose it is. |

## Rules for working here

- Change geometry only in the PARAMETERS block of `src/generate.py`, then run `make`.
  Never hand-edit `out/`. Do not put dimensions in `src/cap.py`.
- Run `make check` after any parameter change; it exits non-zero on a failed check.
- If a script gains or loses an output file, update the file lists in the `Makefile`.
- `out/` is git-ignored. It holds only generated files; run `make` to create them after a fresh checkout.
- Units are millimeters everywhere. The mast and sheet stock are nominally inch sizes.
- Keep the disc a plain flat ø120 circle. The datasheet's phase-center offsets were
  measured on that shape; a different size or shape invalidates them (see DESIGN.md).
- Nothing conductive may sit above the disc's top face except the antenna and its two screws.
  The top must be flush under the antenna footprint.
- The cap must stay inside the disc outline and below the disc.
- SendCutSend uploads must contain cut paths only: no text, dimensions, or reference geometry.
- Do not treat `CAP_FIT_CLEAR` as settled. It is a starting guess to be tuned with the fit ring.

## Suggested next tasks, in order

1. Have the fit ring printed and tried on the mast. Adjust `CAP_FIT_CLEAR` from the result,
   regenerate, then print the cap.
2. Get the owner's confirmation of the assumed cap details (OPEN_ITEMS.md item 11).
3. Validate the DXFs by loading them with `ezdxf`: expected entity counts, units. Open the
   STL in a slicer and confirm it prints without supports.
4. Apply the remaining measurements from OPEN_ITEMS.md (hole spacing, ear thickness).
5. Produce a dimensioned PDF drawing of both parts.

Ask the owner before changing any decision recorded in DESIGN.md.

@../AGENTS.md
