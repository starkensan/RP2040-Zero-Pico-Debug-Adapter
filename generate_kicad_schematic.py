#!/usr/bin/env python3
"""Generate the KiCad schematic for the RP2040-Zero debug adapter."""

from pathlib import Path
from uuid import uuid4


PROJECT = "RP2040-Zero-Pico-Debug-Adapter"
ROOT = Path(__file__).resolve().parent
OUT = ROOT / f"{PROJECT}.kicad_sch"
SYMLIB = ROOT / "Adapter.kicad_sym"
SYMTABLE = ROOT / "sym-lib-table"


def u():
    return str(uuid4())


def effects(size=1.27, hide=False, justify=None):
    hide_s = "\n\t\t\t\t(hide yes)" if hide else ""
    justify_s = f"\n\t\t\t\t(justify {justify})" if justify else ""
    return (
        "\n\t\t\t(effects"
        f"\n\t\t\t\t(font\n\t\t\t\t\t(size {size} {size})\n\t\t\t\t)"
        f"{hide_s}{justify_s}\n\t\t\t)"
    )


def prop(name, value, x, y, rot=0, hide=False):
    return f'\n\t\t(property "{name}" "{value}"\n\t\t\t(at {x} {y} {rot}){effects(hide=hide)}\n\t\t)'


def pin(number, name, x, y, rot, length=3.81, ptype="passive"):
    return f'''
\t\t\t(pin {ptype} line
\t\t\t\t(at {x} {y} {rot})
\t\t\t\t(length {length})
\t\t\t\t(name "{name}"{effects()}\n\t\t\t\t)
\t\t\t\t(number "{number}"{effects()}\n\t\t\t\t)
\t\t\t)'''


def lib_symbol(name, ref_prefix, value, footprint="", pins="", box=(-5.08, -5.08, 5.08, 5.08), in_bom="yes"):
    x1, y1, x2, y2 = box
    return f'''
\t(symbol "{name}"
\t\t(pin_names
\t\t\t(offset 1.016)
\t\t)
\t\t(exclude_from_sim no)
\t\t(in_bom {in_bom})
\t\t(on_board yes)
{prop("Reference", ref_prefix, 0, y1 - 2.54)}
{prop("Value", value, 0, y2 + 2.54)}
{prop("Footprint", footprint, 0, 0, hide=True)}
{prop("Datasheet", "~", 0, 0, hide=True)}
{prop("Description", value, 0, 0, hide=True)}
\t\t(symbol "{name.split(':')[-1]}_1_1"
\t\t\t(rectangle
\t\t\t\t(start {x1} {y1})
\t\t\t\t(end {x2} {y2})
\t\t\t\t(stroke
\t\t\t\t\t(width 0.254)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type background)
\t\t\t\t)
\t\t\t)
{pins}
\t\t)
\t\t(embedded_fonts no)
\t)'''


def resistor_symbol():
    pins = pin("1", "~", -5.08, 0, 0) + pin("2", "~", 5.08, 0, 180)
    return lib_symbol(
        "Adapter:R_Series",
        "R",
        "47R",
        "Internet_Footprints:R_Axial_DIN0204_L3.6mm_D1.6mm_P7.62mm_Horizontal",
        pins,
        (-1.27, -2.54, 1.27, 2.54),
    )


def connector3_symbol():
    pins = (
        pin("1", "Pin_1", -5.08, 2.54, 0)
        + pin("2", "Pin_2", -5.08, 0, 0)
        + pin("3", "Pin_3", -5.08, -2.54, 0)
    )
    return lib_symbol(
        "Adapter:Conn_01x03",
        "J",
        "Conn_01x03",
        "Internet_Footprints:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal",
        pins,
        (-1.27, -3.81, 1.27, 3.81),
    )


def connector2_symbol():
    pins = pin("1", "Pin_1", -5.08, 1.27, 0) + pin("2", "Pin_2", -5.08, -1.27, 0)
    return lib_symbol(
        "Adapter:Conn_01x02",
        "J",
        "Conn_01x02",
        "Internet_Footprints:PinHeader_1x02_P2.54mm_Vertical",
        pins,
        (-1.27, -2.54, 1.27, 2.54),
    )


def testpoint_symbol():
    return lib_symbol(
        "Adapter:TestPoint",
        "TP",
        "TestPoint",
        "Internet_Footprints:TestPoint_THTPad_D1.5mm_Drill0.7mm",
        pin("1", "1", -5.08, 0, 0),
        (-1.27, -1.27, 1.27, 1.27),
    )


def module_left_symbol():
    pins = (
        pin("13", "GP10 / SWCLK", 10.16, 7.62, 180, ptype="bidirectional")
        + pin("12", "GP11 / SWDIO", 10.16, 0, 180, ptype="bidirectional")
        + pin("11", "GP12 / RUN", 10.16, -7.62, 180, ptype="bidirectional")
        + pin("2", "GND", 10.16, -15.24, 180)
    )
    return lib_symbol(
        "Adapter:RP2040_Zero_Left_DebugPins",
        "J",
        "RP2040-Zero left header",
        "Internet_Footprints:PinHeader_1x15_P2.54mm_Vertical",
        pins,
        (-8.89, -11.43, 6.35, 19.05),
    )


def module_right_symbol():
    pins = (
        pin("5", "GP4 / UART TX", 10.16, 2.54, 180, ptype="output")
        + pin("6", "GP5 / UART RX", 10.16, -2.54, 180, ptype="input")
    )
    return lib_symbol(
        "Adapter:RP2040_Zero_Right_DebugPins",
        "J",
        "RP2040-Zero right header",
        "Internet_Footprints:PinHeader_1x15_P2.54mm_Vertical",
        pins,
        (-8.89, -6.35, 6.35, 6.35),
    )


def schematic_symbol(lib_id, ref, value, x, y, footprint, fields=None):
    fields = fields or {}
    props = (
        prop("Reference", ref, x, y - 7.62)
        + prop("Value", value, x, y + 7.62)
        + prop("Footprint", footprint, x, y, hide=True)
        + prop("Datasheet", "~", x, y, hide=True)
        + prop("Description", fields.get("Description", value), x, y, hide=True)
    )
    return f'''
\t(symbol
\t\t(lib_id "{lib_id}")
\t\t(at {x} {y} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{u()}")
{props}
\t\t(instances
\t\t\t(project "{PROJECT}"
\t\t\t\t(path "/"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)'''


def wire(x1, y1, x2, y2):
    return f'''
\t(wire
\t\t(pts
\t\t\t(xy {x1} {y1}) (xy {x2} {y2})
\t\t)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{u()}")
\t)'''


def label(text, x, y, rot=0):
    return f'''
\t(label "{text}"
\t\t(at {x} {y} {rot})
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify left bottom)
\t\t)
\t\t(uuid "{u()}")
\t)'''


def text_note(text, x, y, size=1.27):
    return f'''
\t(text "{text}"
\t\t(exclude_from_sim no)
\t\t(at {x} {y} 0)
\t\t(effects
\t\t\t(font
\t\t\t\t(size {size} {size})
\t\t\t)
\t\t\t(justify left bottom)
\t\t)
\t\t(uuid "{u()}")
\t)'''


def main():
    lib_symbols = "\n".join(
        [
            resistor_symbol(),
            connector3_symbol(),
            connector2_symbol(),
            testpoint_symbol(),
            module_left_symbol(),
            module_right_symbol(),
        ]
    )
    SYMLIB.write_text(
        f'''(kicad_symbol_lib
\t(version 20241209)
\t(generator "kicad_symbol_editor")
\t(generator_version "9.0")
{lib_symbols}
)
'''
    )
    SYMTABLE.write_text(
        '''(sym_lib_table
  (lib (name "Adapter")(type "KiCad")(uri "${KIPRJMOD}/Adapter.kicad_sym")(options "")(descr "RP2040-Zero debug adapter local schematic symbols"))
)
'''
    )

    parts = []
    parts.append(
        schematic_symbol(
            "Adapter:RP2040_Zero_Left_DebugPins",
            "J1",
            "RP2040-Zero left header",
            30.48,
            55.88,
            "Internet_Footprints:PinHeader_1x15_P2.54mm_Vertical",
        )
    )
    parts.append(
        schematic_symbol(
            "Adapter:RP2040_Zero_Right_DebugPins",
            "J2",
            "RP2040-Zero right header",
            30.48,
            96.52,
            "Internet_Footprints:PinHeader_1x15_P2.54mm_Vertical",
        )
    )
    for ref, x, y in [
        ("R1", 81.28, 48.26),
        ("R2", 81.28, 55.88),
        ("R5", 81.28, 63.5),
        ("R3", 81.28, 93.98),
        ("R4", 81.28, 99.06),
    ]:
        parts.append(schematic_symbol("Adapter:R_Series", ref, "47R", x, y, "Internet_Footprints:R_Axial_DIN0204_L3.6mm_D1.6mm_P7.62mm_Horizontal"))
    parts.append(schematic_symbol("Adapter:Conn_01x03", "J3", "Pico SWD JST-SH", 139.7, 50.8, "Internet_Footprints:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal"))
    parts.append(schematic_symbol("Adapter:Conn_01x03", "J4", "UART JST-SH", 139.7, 96.52, "Internet_Footprints:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal"))
    parts.append(schematic_symbol("Adapter:Conn_01x02", "J5", "RUN/RESET optional", 139.7, 121.92, "Internet_Footprints:PinHeader_1x02_P2.54mm_Vertical"))
    parts.append(schematic_symbol("Adapter:TestPoint", "TP1", "RUN", 111.76, 127, "Internet_Footprints:TestPoint_THTPad_D1.5mm_Drill0.7mm"))

    wires = []
    # J1 GP10/GP11/GP12 to series resistors.
    wires += [wire(40.64, 48.26, 76.2, 48.26), wire(86.36, 48.26, 134.62, 48.26)]
    wires += [wire(40.64, 55.88, 76.2, 55.88), wire(86.36, 55.88, 106.68, 55.88), wire(106.68, 55.88, 106.68, 53.34), wire(106.68, 53.34, 134.62, 53.34)]
    wires += [wire(40.64, 63.5, 76.2, 63.5), wire(86.36, 63.5, 101.6, 63.5), wire(101.6, 63.5, 101.6, 120.65), wire(101.6, 120.65, 134.62, 120.65)]
    wires += [wire(101.6, 127, 106.68, 127), wire(101.6, 120.65, 101.6, 127)]
    # J2 UART through series resistors.
    wires += [wire(40.64, 93.98, 76.2, 93.98), wire(86.36, 93.98, 134.62, 93.98)]
    wires += [wire(40.64, 99.06, 76.2, 99.06), wire(86.36, 99.06, 134.62, 99.06)]
    # GND labels/wires.
    wires += [wire(40.64, 71.12, 48.26, 71.12), wire(134.62, 50.8, 127, 50.8), wire(134.62, 96.52, 127, 96.52), wire(134.62, 123.19, 127, 123.19)]

    labels = [
        label("GP10_SWCLK", 52.07, 48.26),
        label("SWCLK", 111.76, 48.26),
        label("GP11_SWDIO", 52.07, 55.88),
        label("SWDIO", 111.76, 53.34),
        label("GP12_RESET", 52.07, 63.5),
        label("RUN_RESET", 106.68, 120.65),
        label("GP4_UART_TX", 52.07, 93.98),
        label("UART_TX", 111.76, 93.98),
        label("GP5_UART_RX", 52.07, 99.06),
        label("UART_RX", 111.76, 99.06),
        label("GND", 48.26, 71.12),
        label("GND", 127, 50.8),
        label("GND", 127, 96.52),
        label("GND", 127, 123.19),
    ]
    notes = [
        text_note("J3 Pico SWD pinout: 1 SWCLK, 2 GND, 3 SWDIO", 122, 38),
        text_note("J4 UART pinout: 1 TX from probe, 2 GND, 3 RX to probe", 115, 83),
        text_note("Do not connect RP2040-Zero 3V3 to the target by default.", 25, 135),
        text_note("RP2040-Zero runs debugprobe-zero firmware.", 25, 141),
    ]

    content = f'''(kicad_sch
\t(version 20250114)
\t(generator "eeschema")
\t(generator_version "9.0")
\t(uuid "{u()}")
\t(paper "A4")
\t(title_block
\t\t(title "{PROJECT}")
\t\t(company "Generated by Codex")
\t\t(comment 1 "Waveshare RP2040-Zero debugprobe-zero adapter for Raspberry Pi Pico targets")
\t\t(comment 2 "Target 3V3 is intentionally not connected")
\t)
\t(lib_symbols
{lib_symbols}
\t)
{"".join(parts)}
{"".join(wires)}
{"".join(labels)}
{"".join(notes)}
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
\t(embedded_fonts no)
)
'''
    OUT.write_text(content)


if __name__ == "__main__":
    main()
