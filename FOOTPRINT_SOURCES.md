# Footprint and Source Notes

## Sources Checked

- SnapMagic/SnapEDA RP2040-ZERO page provided by the user.
  - https://www.snapeda.com/parts/RP2040-ZERO/Waveshare%20Electronics/view-part/
  - The page advertises CAD Models for Symbol, Footprint, and 3D Model, and lists KiCad as an available format.
  - Direct automated download from SnapEDA was blocked by Cloudflare/API 403 in this environment, so the SnapEDA model was not copied into the repository.
- Waveshare RP2040-Zero wiki: official product page with pinout and dimensions sections.
  - https://www.waveshare.com/wiki/RP2040-Zero
- Waveshare RP2040-Zero official schematic PDF.
  - https://files.waveshare.com/upload/4/4c/RP2040_Zero.pdf
- KiCad official footprint library entry for the JST-SH connector used by this project.
  - https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_JST.pretty/JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal.kicad_mod

## Downloaded Online Footprints

These footprints were downloaded from the KiCad official online footprint repository and registered through `fp-lib-table` as `Internet_Footprints`:

- `Internet_Footprints:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal`
- `Internet_Footprints:R_Axial_DIN0204_L3.6mm_D1.6mm_P7.62mm_Horizontal`
- `Internet_Footprints:PinHeader_1x02_P2.54mm_Vertical`
- `Internet_Footprints:PinHeader_1x15_P2.54mm_Vertical`
- `Internet_Footprints:TestPoint_THTPad_D1.5mm_Drill0.7mm`
- `Internet_Footprints:MountingHole_2.2mm_M2`

The RP2040-Zero module is mounted using two downloaded KiCad 1x15 through-hole pin-header footprints in the PCB layout, matching the original board requirement for through-hole headers.

The downloaded KiCad `master` footprint files were normalized for KiCad 9.0 compatibility by removing newer footprint attributes that KiCad 9's `pcbnew.FootprintLoad` cannot parse and changing the 3D model environment variable from `${KICAD10_3DMODEL_DIR}` to `${KICAD9_3DMODEL_DIR}`. Geometry, pads, and footprint names remain from the downloaded online KiCad footprint files.

## Netlist

The KiCad netlist is generated from `RP2040-Zero-Pico-Debug-Adapter.kicad_sch`:

```sh
kicad-cli sch export netlist --format kicadsexpr \
  --output RP2040-Zero-Pico-Debug-Adapter.net \
  RP2040-Zero-Pico-Debug-Adapter.kicad_sch
```

No matching public netlist for this exact adapter project was found online. Netlists are design-specific, so the repository keeps the KiCad-exported netlist generated from the project schematic.
