# RP2040-Zero-Pico-Debug-Adapter

KiCad 9 project for a small 2-layer adapter PCB that mounts a Waveshare RP2040-Zero module and exposes the debugprobe-zero SWD/UART signals for Raspberry Pi Pico targets.

## Signal Mapping

| RP2040-Zero signal | Adapter part | Target connector pin |
| --- | --- | --- |
| GP10 | R1 100 ohm series | J3 pin 1 SWCLK |
| GND | direct | J3 pin 2 GND |
| GP11 | R2 100 ohm series | J3 pin 3 SWDIO |
| GP4 | R3 100 ohm series | J4 pin 1 TX from probe |
| GND | direct | J4 pin 2 GND |
| GP5 | R4 100 ohm series | J4 pin 3 RX to probe |
| GP12 | direct | J5 pin 1 RUN/RESET and TP1 |
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

- Board size: 30 mm x 40 mm, portrait orientation.
- Copper layers: 2.
- GND copper pours: filled zones on both F.Cu and B.Cu.
- Signal tracks: 0.35 mm nominal.
- Ground routes: 0.6 mm nominal on the back layer.
- SWD and UART use 100 ohm source-termination resistors in 0603 (1608 metric) packages. RUN/RESET is connected directly.
- With the RP2040-Zero USB-C connector at the top, J5 is at the left-center, UART is at the lower-left, and SWD is at the lower-right. Both JST-SH cable openings face outward/downward.
- RP2040-Zero is represented as one 23-pin `U1` symbol and the project-local `Adapter:Waveshare_RP2040-Zero` footprint.
- The footprint supports castellated SMD mounting and optional 0.8 mm through holes. Verify the USB-C orientation before soldering.

## Files

- `RP2040-Zero-Pico-Debug-Adapter.kicad_pro`: KiCad project.
- `RP2040-Zero-Pico-Debug-Adapter.kicad_sch`: schematic note/net-map sheet.
- `RP2040-Zero-Pico-Debug-Adapter.kicad_pcb`: placed and routed PCB layout.
- `RP2040-Zero-Pico-Debug-Adapter.net`: KiCad netlist exported from the schematic.
- `RP2040-Zero-Pico-Debug-Adapter_bom.csv`: bill of materials.
- `generate_kicad_project.py`: reproducible PCB generator using KiCad 9 `pcbnew`.
- `generate_kicad_schematic.py`: reproducible schematic/local symbol generator.
- `RP2040-Zero.kicad_sym`: downloaded RP2040-Zero symbol library.
- `Adapter.pretty/`: project-local footprints, including the downloaded and verified RP2040-Zero footprint.
- `3dmodels/Waveshare_RP2040-Zero.step`: official Waveshare 3D model used by the RP2040-Zero footprint.
- `FOOTPRINT_SOURCES.md`: footprint source notes and URLs.
