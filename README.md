# RP2040-Zero-Pico-Debug-Adapter

KiCad 9 project for a small 2-layer adapter PCB that mounts a Waveshare RP2040-Zero module and exposes the debugprobe-zero SWD/UART signals for Raspberry Pi Pico targets.

## Signal Mapping

| RP2040-Zero signal | Adapter part | Target connector pin |
| --- | --- | --- |
| GP10 | R1 47 ohm series | J3 pin 1 SWCLK |
| GND | direct | J3 pin 2 GND |
| GP11 | R2 47 ohm series | J3 pin 3 SWDIO |
| GP4 | R3 47 ohm series | J4 pin 1 TX from probe |
| GND | direct | J4 pin 2 GND |
| GP5 | R4 47 ohm series | J4 pin 3 RX to probe |
| GP12 | R5 47 ohm series | J5 pin 1 RUN/RESET and TP1 |
| GND | direct | J5 pin 2 GND |

The RP2040-Zero 3V3 pin is not routed to the target connectors by default.

## Connectors

- `J3` Pico SWD JST-SH, 1.00 mm pitch:
  - Pin 1: `SWCLK`
  - Pin 2: `GND`
  - Pin 3: `SWDIO`
- `J4` UART JST-SH, 1.00 mm pitch:
  - Pin 1: `TX` from probe
  - Pin 2: `GND`
  - Pin 3: `RX` to probe
- `J5` optional 2-pin RUN/RESET header:
  - Pin 1: `RUN_RESET`
  - Pin 2: `GND`

## Build Notes

- Board size: 58 mm x 50 mm.
- Copper layers: 2.
- Signal tracks: 0.35 mm nominal.
- Ground routes: 0.6 mm nominal on the back layer.
- Series resistors are through-hole 7.62 mm axial footprints and can be populated as 47 ohm resistors or shorted with wire jumpers.
- The RP2040-Zero module area is marked on silkscreen. Verify the module pinout and USB-C orientation before soldering headers.

## Files

- `RP2040-Zero-Pico-Debug-Adapter.kicad_pro`: KiCad project.
- `RP2040-Zero-Pico-Debug-Adapter.kicad_sch`: schematic note/net-map sheet.
- `RP2040-Zero-Pico-Debug-Adapter.kicad_pcb`: placed and routed PCB layout.
- `RP2040-Zero-Pico-Debug-Adapter.net`: KiCad netlist exported from the schematic.
- `RP2040-Zero-Pico-Debug-Adapter_bom.csv`: bill of materials.
- `generate_kicad_project.py`: reproducible PCB generator using KiCad 9 `pcbnew`.
- `generate_kicad_schematic.py`: reproducible schematic/local symbol generator.
- `Internet_Footprints.pretty/`: footprints downloaded from online KiCad library references.
- `SnapEDA/README.md`: source URL and manual import notes for the SnapEDA RP2040-ZERO model.
- `FOOTPRINT_SOURCES.md`: footprint source notes and URLs.
