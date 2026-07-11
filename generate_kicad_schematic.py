#!/usr/bin/env python3
"""Generate the KiCad schematic for the RP2040-Zero debug adapter."""

from pathlib import Path
from uuid import uuid4


PROJECT = "RP2040-Zero-Pico-Debug-Adapter"
ROOT = Path(__file__).resolve().parent
OUT = ROOT / f"{PROJECT}.kicad_sch"
SYMLIB = ROOT / "Adapter.kicad_sym"
SYMTABLE = ROOT / "sym-lib-table"
RP2040_ZERO_SYMLIB = ROOT / "RP2040-Zero.kicad_sym"


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
        "100R",
        "Resistor_SMD:R_0603_1608Metric",
        pins,
        (-2.54, -1.27, 2.54, 1.27),
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
        "Connector_JST:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal",
        pins,
        (-1.27, -3.81, 1.27, 3.81),
    )


def connector2_symbol():
    pins = pin("1", "Pin_1", -5.08, 1.27, 0) + pin("2", "Pin_2", -5.08, -1.27, 0)
    return lib_symbol(
        "Adapter:Conn_01x02",
        "J",
        "Conn_01x02",
        "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
        pins,
        (-1.27, -2.54, 1.27, 2.54),
    )


def testpoint_symbol():
    return lib_symbol(
        "Adapter:TestPoint",
        "TP",
        "TestPoint",
        "TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm",
        pin("1", "1", -5.08, 0, 0),
        (-1.27, -1.27, 1.27, 1.27),
    )


def rp2040_zero_symbol():
    """Embed the downloaded library symbol under its project library ID."""
    text = RP2040_ZERO_SYMLIB.read_text()
    start = text.index('(symbol "RP2040-Zero"')
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                return text[start : index + 1].replace(
                    '(symbol "RP2040-Zero"',
                    '(symbol "RP2040_Zero:RP2040-Zero"',
                    1,
                )
    raise ValueError("Invalid RP2040-Zero symbol library")
def schematic_symbol(lib_id, ref, value, x, y, footprint, fields=None):
    fields = fields or {}
    ref_dy = fields.get("ref_dy", 7.62)
    value_dy = fields.get("value_dy", 7.62)
    props = (
        prop("Reference", ref, x, y - ref_dy)
        + prop("Value", value, x, y + value_dy)
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


def no_connect(x, y):
    return f'''
	(no_connect
		(at {x} {y})
		(uuid "{u()}")
	)'''


def label(text, x, y, rot=0, justify="left bottom"):
    return f'''
\t(label "{text}"
\t\t(at {x} {y} {rot})
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify {justify})
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
        ]
    )
    embedded_symbols = lib_symbols + "\n" + rp2040_zero_symbol()
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
  (lib (name "RP2040_Zero")(type "KiCad")(uri "${KIPRJMOD}/RP2040-Zero.kicad_sym")(options "")(descr "Downloaded Waveshare RP2040-Zero symbol"))
)
'''
    )

    parts = []
    parts.append(
        schematic_symbol(
            "RP2040_Zero:RP2040-Zero",
            "U1",
            "RP2040-Zero",
            45.72,
            76.2,
            "Adapter:Waveshare_RP2040-Zero",
            {"Description": "Waveshare RP2040-Zero module"},
        )
    )
    for ref, x, y in [
        ("R1", 91.44, 48.26),
        ("R2", 91.44, 55.88),
        ("R3", 91.44, 88.9),
        ("R4", 91.44, 96.52),
    ]:
        parts.append(schematic_symbol(
            "Adapter:R_Series", ref, "100R", x, y,
            "Resistor_SMD:R_0603_1608Metric",
            {"ref_dy": 2.54, "value_dy": 2.54},
        ))
    parts.append(schematic_symbol("Adapter:Conn_01x03", "J3", "Pico SWD JST-SH", 139.7, 52.07, "Connector_JST:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal"))
    parts.append(schematic_symbol("Adapter:Conn_01x03", "J4", "UART JST-SH", 139.7, 92.71, "Connector_JST:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal"))
    parts.append(schematic_symbol("Adapter:Conn_01x02", "J5", "RUN/RESET optional", 139.7, 116.84, "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"))
    parts.append(schematic_symbol(
        "Adapter:TestPoint", "TP1", "RUN", 111.76, 116.84,
        "TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm",
        {"ref_dy": 2.54, "value_dy": 2.54},
    ))

    wires = []
    # Short local stubs keep functional blocks readable; labels carry nets.
    wires += [wire(48.26, 100.33, 48.26, 105.41), wire(48.26, 105.41, 55.88, 105.41)]
    wires += [wire(45.72, 100.33, 45.72, 107.95), wire(45.72, 107.95, 55.88, 107.95)]
    wires += [wire(43.18, 100.33, 43.18, 110.49), wire(43.18, 110.49, 55.88, 110.49)]
    wires += [wire(60.96, 81.28, 68.58, 81.28), wire(60.96, 83.82, 68.58, 83.82)]
    wires += [wire(30.48, 73.66, 25.4, 73.66)]
    for y in (48.26, 55.88, 88.9, 96.52):
        wires += [wire(86.36, y, 78.74, y), wire(96.52, y, 104.14, y)]
    wires += [wire(134.62, 49.53, 127, 49.53), wire(134.62, 52.07, 127, 52.07), wire(134.62, 54.61, 127, 54.61)]
    wires += [wire(134.62, 90.17, 127, 90.17), wire(134.62, 92.71, 127, 92.71), wire(134.62, 95.25, 127, 95.25)]
    wires += [wire(134.62, 115.57, 127, 115.57), wire(134.62, 118.11, 127, 118.11)]
    wires += [wire(106.68, 116.84, 101.6, 116.84)]

    labels = [
        label("GP10_SWCLK", 55.88, 105.41), label("GP11_SWDIO", 55.88, 107.95),
        label("RUN_RESET", 55.88, 110.49), label("GP4_UART_TX", 68.58, 81.28),
        label("GP5_UART_RX", 68.58, 83.82), label("GND", 25.4, 73.66, justify="right bottom"),
        label("GP10_SWCLK", 78.74, 48.26, justify="right bottom"), label("SWCLK", 104.14, 48.26),
        label("GP11_SWDIO", 78.74, 55.88, justify="right bottom"), label("SWDIO", 104.14, 55.88),
        label("GP4_UART_TX", 78.74, 88.9, justify="right bottom"), label("UART_TX", 104.14, 88.9),
        label("GP5_UART_RX", 78.74, 96.52, justify="right bottom"), label("UART_RX", 104.14, 96.52),
        label("SWCLK", 127, 49.53, justify="right bottom"), label("GND", 127, 52.07, justify="right bottom"), label("SWDIO", 127, 54.61, justify="right bottom"),
        label("UART_TX", 127, 90.17, justify="right bottom"), label("GND", 127, 92.71, justify="right bottom"), label("UART_RX", 127, 95.25, justify="right bottom"),
        label("RUN_RESET", 127, 115.57, justify="right bottom"), label("GND", 127, 118.11, justify="right bottom"),
        label("RUN_RESET", 101.6, 116.84, justify="right bottom"),
    ]
    notes = [
        text_note("RP2040-ZERO DEBUG PROBE", 25, 35, 2.0),
        text_note("SWD", 121, 39, 1.5),
        text_note("UART", 121, 80, 1.5),
        text_note("RUN / RESET", 121, 106, 1.5),
        text_note("Target 3V3 is intentionally isolated.", 25, 124),
    ]

    unused_pins = [
        (30.48, 71.12), (30.48, 76.2), (30.48, 78.74), (30.48, 81.28),
        (30.48, 83.82), (30.48, 86.36), (30.48, 88.9), (30.48, 91.44),
        (60.96, 71.12), (60.96, 73.66), (60.96, 76.2), (60.96, 78.74),
        (60.96, 86.36), (60.96, 88.9), (60.96, 91.44),
        (40.64, 100.33), (50.8, 100.33),
    ]

    content = f'''(kicad_sch
\t(version 20250114)
\t(generator "eeschema")
\t(generator_version "9.0")
\t(uuid "{u()}")
\t(paper "A5")
\t(title_block
\t\t(title "{PROJECT}")
\t\t(company "Generated by Codex")
\t\t(comment 1 "Waveshare RP2040-Zero debugprobe-zero adapter for Raspberry Pi Pico targets")
\t\t(comment 2 "Target 3V3 is intentionally not connected")
\t)
\t(lib_symbols
{embedded_symbols}
\t)
{"".join(parts)}
{"".join(wires)}
{"".join(labels)}
{"".join(notes)}
{"".join(no_connect(x, y) for x, y in unused_pins)}
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
