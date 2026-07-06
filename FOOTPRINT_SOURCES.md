# Footprint and Source Notes

## Sources Checked

- Waveshare RP2040-Zero wiki: official product page with pinout and dimensions sections.
  - https://www.waveshare.com/wiki/RP2040-Zero
- Waveshare RP2040-Zero official schematic PDF.
  - https://files.waveshare.com/upload/4/4c/RP2040_Zero.pdf
- KiCad official footprint library entry for the JST-SH connector used by this project.
  - https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_JST.pretty/JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal.kicad_mod

## Local Footprints

- `Adapter.pretty/Waveshare_RP2040-Zero_DebugHeaders.kicad_mod`
  - Based on the Waveshare official 18.00 mm x 23.50 mm module dimensions.
  - Uses 2.54 mm header pitch from the official dimension drawing.
  - Includes only the debugprobe-zero pins used by this adapter: `GP10`, `GP11`, `GP12`, `GP4`, `GP5`, and `GND`.
  - Intended for through-hole header mounting, not direct castellated soldering.

## Stock KiCad Footprints Used

The remaining footprints are stock KiCad 9 footprints, with the JST-SH connector cross-checked against the KiCad official online footprint library:

- `Connector_JST:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal`
- `Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P7.62mm_Horizontal`
- `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical`
- `TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm`
- `MountingHole:MountingHole_2.2mm_M2`

## Netlist

The KiCad netlist is generated from `RP2040-Zero-Pico-Debug-Adapter.kicad_sch`:

```sh
kicad-cli sch export netlist --format kicadsexpr \
  --output RP2040-Zero-Pico-Debug-Adapter.net \
  RP2040-Zero-Pico-Debug-Adapter.kicad_sch
```
