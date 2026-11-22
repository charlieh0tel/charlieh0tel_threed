# Open items

Nothing here has been verified against hardware. Items marked OWNER need a physical
measurement or a decision.

## Measurements (OWNER)

| # | Item | Assumed | Affects |
|---|---|---|---|
| 1 | **Mast OD. Critical.** DECIDED by the owner (2026-11-22): use the nominal 1-1/4", not a measurement. The actual tube is still unmeasured, so the fit ring is the only check. | 31.75 nominal | The printed socket bore directly. A tube oversize by more than the 0.4 clearance, or a weld seam or burr, means the cap will not go on; undersize by more than about 0.55 means the clamp closes fully without gripping. |
| 2 | Antenna hole center-to-center | 95.0, read from the datasheet drawing | `ANT_HOLE_SPACING`: disc holes and cap arm holes |
| 3 | Antenna holes lie on the axis perpendicular to the cable, symmetric about the ARP | Yes, per Fig. 1 | Hole placement, north mark |
| 4 | Brass limiter flush or proud on both ear faces; limiter OD | Flush, OD about 8 | Washer size, torque |
| 5 | Antenna base is flat and sits fully on the disc | Yes | Flush-top requirement |
| 6 | Antenna ear thickness | 6.0, from the datasheet drawing | `ANT_EAR_T`: antenna screw length |

## Decisions (OWNER)

| # | Item | Options |
|---|---|---|
| 7 | Disc material | 5052 aluminum (lighter, needs finish outdoors) or 304 stainless (no finish, about 3× the mass) |
| 8 | Deployment | Bench or temporary vs permanent outdoor; drives items 7 and 9 |
| 9 | Print material | ASA (UV and heat resistant) or PETG assumed. PLA will creep and soften in sun. |
| 10 | Disc thickness | 0.125" was chosen only because it is the thinnest stock SendCutSend countersinks. With no countersinks a thinner sheet would work; changing `T` changes the antenna screw length. Left at 0.125". |
| 11 | Cap details assumed without owner input: split socket with one M4 pinch screw; captive nyloc nuts in the arms; clamp ears on −X; socket 45 deep with a 5 wall; mast stops 9 below the disc | Confirm or change. All are parameters in `src/generate.py`. |

## Print fit

| # | Item | Why it matters |
|---|---|---|
| 12 | `CAP_FIT_CLEAR = 0.4` (diametral) is a starting guess | Printed holes usually come out undersize by a printer-dependent amount. Tune with `out/mast_cap_fit_ring.stl` before printing the cap. |
| 13 | Hex pocket clearance `NUT_POCKET_CLEAR = 0.3` is a guess | The nyloc nuts should push in by hand and not spin. The pinch-nut pocket prints with its axis horizontal, so its upper faces may sag slightly. |
| 14 | Clamp grip and arm stiffness are not analyzed | No stress or creep calculation was done. The antenna is light, but the joint relies on printed plastic in compression under the antenna screws and in hoop tension around the mast. Check screw tightness after the first hot days. |
| 15 | The cap closes the top of the mast under the disc | Water is kept out from above; condensation inside the tube has no drain at the top. Not addressed. |

| 16 | Cable route and bend radius are illustrative | The modeled route uses a 15 bend radius, assumed as the minimum for RG174 and not checked against the cable's datasheet. The tie slots are sized for a 2.5 wide tie by guess. |

## Vendor checks (SendCutSend)

| # | Item | Why it matters |
|---|---|---|
| 17 | Minimum hole size and hole-to-edge distance at 0.125" in the chosen material | Antenna holes are ø4.5, 10.25 edge to disc edge. Expected to pass; not confirmed. |
| 18 | Whether the disc upload may contain extra layers | Assumed not; `disc_120mm_cut_only.dxf` exists for this. |

Reference: https://sendcutsend.com/cnc-guidelines

## File validation

| # | Item |
|---|---|
| 19 | The DXFs are hand-written R12 ASCII and have never been opened in CAD. Load with `ezdxf`, check units and entity counts (disc cut-only: 3 circles). |
| 20 | `$INSUNITS` is set to 4 (mm) in an R12 header, where it is not formally defined. Confirm the upload preview reports 120 mm, not 120 in. |
| 21 | The cap solid is checked by `uv run src/cap.py --check` (single valid solid, no interference with the mast or disc, screw paths clear). The STL and STEP files have not been opened in a slicer or CAD tool. |

## Not yet produced

| # | Item |
|---|---|
| 22 | Dimensioned PDF drawing of the disc and cap |
| 23 | Any RF verification. The stainless screw heads stand about 9 above the plane at r = 47.5; expected negligible at these wavelengths, not measured or simulated. |

## Known limits of the source data

- Antenna dimensions come from the owner's screenshot of Figure 1 and a text extraction of
  the datasheet. The datasheet PDF is now in `third_party/` but has not been re-read
  against these numbers.
- No torque figure is given by u-blox for the M4 mount.
