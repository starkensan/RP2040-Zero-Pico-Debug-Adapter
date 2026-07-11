# Footprint and Source Notes

## Sources Checked

- Waveshare RP2040-Zero wiki: official product page with pinout and dimensions sections.
  - https://www.waveshare.com/wiki/RP2040-Zero
- Waveshare RP2040-Zero official schematic PDF.
  - https://files.waveshare.com/upload/4/4c/RP2040_Zero.pdf
- Waveshare RP2040-Zero official STEP model.
  - https://files.waveshare.com/upload/f/f7/RP2040_Zero_stp.zip
  - Stored as `3dmodels/Waveshare_RP2040-Zero.step` and referenced directly by the local footprint.
- dj505 RP2040-Zero KiCad symbol and footprint library, downloaded at commit `b22a0c1afb350dda50ebb7cf2d9c5f3dd3e419ce`.
  - https://github.com/dj505/RP2040-Zero-KiCAD
  - License: CERN Open Hardware Licence Version 2 - Permissive; local copy in `LICENSES/RP2040-Zero-KiCAD-CERN-OHL-P-2.0.txt`.
- KiCad official footprint library entry for the JST-SH connector used by this project.
  - https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_JST.pretty/JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal.kicad_mod

## Local Footprints

- `Adapter.pretty/Waveshare_RP2040-Zero.kicad_mod`
  - Downloaded from dj505's public KiCad library and checked against Waveshare's official 18.00 mm x 23.50 mm dimensions and 23-pin pinout.
  - Supports the castellated SMD pads and optional 0.8 mm through holes.
  - The source footprint's internal `Edge.Cuts` cutout was removed because this carrier board does not require a module-area cutout.
  - Applied to `U1`; used nets are `GP10` (pin 22), `GP11` (21), `GP12` (20), `GP4` (14), `GP5` (15), and `GND` (2).

## Local Symbol

- `RP2040-Zero.kicad_sym`
  - Downloaded from the same dj505 library.
  - Default footprint and official Waveshare datasheet fields were added locally; the module GND pin was changed from `power_in` to `passive` to match this unpowered adapter's ERC semantics.
  - Registered as `RP2040_Zero:RP2040-Zero` and applied to `U1`.

## Stock KiCad Footprints Used

The remaining footprints are stock KiCad 9 footprints, with the JST-SH connector cross-checked against the KiCad official online footprint library:

- `Connector_JST:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal`
- `Resistor_SMD:R_0603_1608Metric`
- `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical`
- `TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm`

## Netlist

The KiCad netlist is generated from `RP2040-Zero-Pico-Debug-Adapter.kicad_sch`:

```sh
kicad-cli sch export netlist --format kicadsexpr \
  --output RP2040-Zero-Pico-Debug-Adapter.net \
  RP2040-Zero-Pico-Debug-Adapter.kicad_sch
```
