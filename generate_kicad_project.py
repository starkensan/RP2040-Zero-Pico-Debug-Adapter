#!/usr/bin/env python3
"""Generate the RP2040-Zero Pico debug adapter KiCad PCB.

The schematic is intentionally simple and documented separately; this script
builds the placed/routed board from KiCad 9 stock footprints.
"""

from pathlib import Path
import pcbnew


PROJECT = "RP2040-Zero-Pico-Debug-Adapter"
OUT = Path(__file__).resolve().parent


def mm(value):
    return pcbnew.FromMM(value)


def vec(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def load_fp(lib, name, ref, value, x, y, rot=0):
    fp = pcbnew.FootprintLoad(f"/usr/share/kicad/footprints/{lib}.pretty", name)
    if fp is None:
        raise RuntimeError(f"Unable to load footprint {lib}:{name}")
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(vec(x, y))
    fp.SetOrientationDegrees(rot)
    return fp


def add_net(board, name):
    net = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net)
    return net


def pad(fp, number):
    p = fp.FindPadByNumber(str(number))
    if p is None:
        raise RuntimeError(f"{fp.GetReference()} has no pad {number}")
    return p


def set_pad_net(fp, number, net):
    pad(fp, number).SetNet(net)


def add_track(board, start, end, net, width=0.35, layer=pcbnew.F_Cu):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(vec(*start))
    t.SetEnd(vec(*end))
    t.SetWidth(mm(width))
    t.SetLayer(layer)
    t.SetNet(net)
    board.Add(t)


def add_via(board, x, y, net, diameter=0.8, drill=0.4):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(vec(x, y))
    v.SetWidth(mm(diameter))
    v.SetDrill(mm(drill))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(net)
    board.Add(v)


def route(board, points, net, width=0.35, layer=pcbnew.F_Cu):
    for a, b in zip(points, points[1:]):
        add_track(board, a, b, net, width, layer)


def add_line(board, start, end, layer, width=0.15):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(vec(*start))
    s.SetEnd(vec(*end))
    s.SetLayer(layer)
    s.SetWidth(mm(width))
    board.Add(s)


def add_rect(board, x1, y1, x2, y2, layer, width=0.15):
    add_line(board, (x1, y1), (x2, y1), layer, width)
    add_line(board, (x2, y1), (x2, y2), layer, width)
    add_line(board, (x2, y2), (x1, y2), layer, width)
    add_line(board, (x1, y2), (x1, y1), layer, width)


def add_text(board, text, x, y, size=1.2, layer=pcbnew.F_SilkS, rot=0, thickness=0.16):
    txt = pcbnew.PCB_TEXT(board)
    txt.SetText(text)
    txt.SetPosition(vec(x, y))
    txt.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    txt.SetTextThickness(mm(thickness))
    txt.SetLayer(layer)
    txt.SetTextAngle(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
    board.Add(txt)


def main():
    board = pcbnew.BOARD()
    board.SetBoardUse(0)

    nets = {
        "GND": add_net(board, "GND"),
        "GP10_SWCLK": add_net(board, "GP10_SWCLK"),
        "SWCLK": add_net(board, "SWCLK"),
        "GP11_SWDIO": add_net(board, "GP11_SWDIO"),
        "SWDIO": add_net(board, "SWDIO"),
        "GP4_UART_TX": add_net(board, "GP4_UART_TX"),
        "UART_TX": add_net(board, "UART_TX"),
        "GP5_UART_RX": add_net(board, "GP5_UART_RX"),
        "UART_RX": add_net(board, "UART_RX"),
        "GP12_RESET": add_net(board, "GP12_RESET"),
        "RUN_RESET": add_net(board, "RUN_RESET"),
    }

    # 58 mm x 50 mm compact rectangle with clearance for four M2 holes.
    add_rect(board, 0, 0, 58, 50, pcbnew.Edge_Cuts, 0.1)

    # RP2040-Zero module headers. Pin naming follows the Waveshare side pinout;
    # only the requested debug-probe pins are electrically used.
    j1 = load_fp(
        "Connector_PinHeader_2.54mm",
        "PinHeader_1x15_P2.54mm_Vertical",
        "J1",
        "RP2040-Zero left header",
        13,
        4.2,
    )
    j2 = load_fp(
        "Connector_PinHeader_2.54mm",
        "PinHeader_1x15_P2.54mm_Vertical",
        "J2",
        "RP2040-Zero right header",
        30,
        4.2,
    )
    board.Add(j1)
    board.Add(j2)
    set_pad_net(j1, 2, nets["GND"])
    set_pad_net(j1, 11, nets["GP12_RESET"])
    set_pad_net(j1, 12, nets["GP11_SWDIO"])
    set_pad_net(j1, 13, nets["GP10_SWCLK"])
    set_pad_net(j2, 5, nets["GP4_UART_TX"])
    set_pad_net(j2, 6, nets["GP5_UART_RX"])

    resistors = [
        ("R1", "47R", 39.0, 35.0, "GP10_SWCLK", "SWCLK"),
        ("R2", "47R", 39.0, 38.0, "GP11_SWDIO", "SWDIO"),
        ("R3", "47R", 39.0, 21.0, "GP4_UART_TX", "UART_TX"),
        ("R4", "47R", 39.0, 24.0, "GP5_UART_RX", "UART_RX"),
        ("R5", "47R", 39.0, 30.0, "GP12_RESET", "RUN_RESET"),
    ]
    fps = {"J1": j1, "J2": j2}
    for ref, value, x, y, n1, n2 in resistors:
        r = load_fp(
            "Resistor_THT",
            "R_Axial_DIN0204_L3.6mm_D1.6mm_P7.62mm_Horizontal",
            ref,
            value,
            x,
            y,
        )
        board.Add(r)
        set_pad_net(r, 1, nets[n1])
        set_pad_net(r, 2, nets[n2])
        fps[ref] = r

    swd = load_fp(
        "Connector_JST",
        "JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal",
        "J3",
        "Pico SWD JST-SH",
        54,
        38,
    )
    uart = load_fp(
        "Connector_JST",
        "JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal",
        "J4",
        "UART JST-SH",
        54,
        24,
    )
    reset = load_fp(
        "Connector_PinHeader_2.54mm",
        "PinHeader_1x02_P2.54mm_Vertical",
        "J5",
        "RUN/RESET optional",
        54,
        8,
    )
    for fp in (swd, uart, reset):
        board.Add(fp)
    set_pad_net(swd, 1, nets["SWCLK"])
    set_pad_net(swd, 2, nets["GND"])
    set_pad_net(swd, 3, nets["SWDIO"])
    set_pad_net(uart, 1, nets["UART_TX"])
    set_pad_net(uart, 2, nets["GND"])
    set_pad_net(uart, 3, nets["UART_RX"])
    set_pad_net(reset, 1, nets["RUN_RESET"])
    set_pad_net(reset, 2, nets["GND"])
    fps.update({"J3": swd, "J4": uart, "J5": reset})

    for ref, x, y in (("H1", 4, 4), ("H2", 45, 4), ("H3", 4, 46), ("H4", 54, 46)):
        h = load_fp("MountingHole", "MountingHole_2.2mm_M2", ref, "M2", x, y)
        board.Add(h)

    tp = load_fp("TestPoint", "TestPoint_THTPad_D1.5mm_Drill0.7mm", "TP1", "RUN", 48, 8)
    board.Add(tp)
    set_pad_net(tp, 1, nets["RUN_RESET"])
    fps["TP1"] = tp

    # Routing: 0.35 mm signal tracks, 0.6 mm ground.
    route(board, [(13, 34.68), (20.0, 34.68), (20.0, 33.41), (37.0, 33.41), (37.0, 35.0), (39.0, 35.0)], nets["GP10_SWCLK"])
    route(board, [(46.62, 35.0), (53.0, 35.0), (53.0, 36.0)], nets["SWCLK"])
    route(board, [(13, 32.14), (22.0, 32.14), (22.0, 30.87), (35.8, 30.87), (35.8, 38.0), (39.0, 38.0)], nets["GP11_SWDIO"], layer=pcbnew.B_Cu)
    route(board, [(46.62, 38.0), (55.0, 38.0), (55.0, 36.0)], nets["SWDIO"])
    route(board, [(30, 14.36), (34.0, 14.36), (34.0, 21.0), (39.0, 21.0)], nets["GP4_UART_TX"])
    route(board, [(46.62, 21.0), (53.0, 21.0), (53.0, 22.0)], nets["UART_TX"])
    route(board, [(30, 16.9), (35.5, 16.9), (35.5, 24.0), (39.0, 24.0)], nets["GP5_UART_RX"], layer=pcbnew.B_Cu)
    route(board, [(46.62, 24.0), (55.0, 24.0), (55.0, 22.0)], nets["UART_RX"])
    route(board, [(13, 29.6), (23.0, 29.6), (23.0, 28.33), (37.0, 28.33), (37.0, 30.0), (39.0, 30.0)], nets["GP12_RESET"])
    route(board, [(46.62, 30.0), (50.0, 30.0), (50.0, 8.0), (54.0, 8.0)], nets["RUN_RESET"], layer=pcbnew.B_Cu)
    route(board, [(50.0, 8.0), (48.0, 8.0)], nets["RUN_RESET"], layer=pcbnew.B_Cu)

    g = nets["GND"]
    add_via(board, 54.0, 34.5, g)
    add_via(board, 54.0, 20.5, g)
    route(board, [(13, 6.74), (7.0, 6.74), (7.0, 48.0), (56.0, 48.0), (56.0, 34.5), (54.0, 34.5)], g, 0.6, pcbnew.B_Cu)
    route(board, [(56.0, 34.5), (56.0, 20.5), (54.0, 20.5)], g, 0.6, pcbnew.B_Cu)
    route(board, [(56.0, 20.5), (56.0, 10.54), (54.0, 10.54)], g, 0.6, pcbnew.B_Cu)
    route(board, [(54.0, 34.5), (54.0, 36.0)], g, 0.25, pcbnew.F_Cu)
    route(board, [(54.0, 20.5), (54.0, 22.0)], g, 0.25, pcbnew.F_Cu)

    # Silkscreen module keepout/placement guide and connector labels.
    add_rect(board, 9.0, 1.9, 34.0, 42.0, pcbnew.F_SilkS, 0.15)
    add_text(board, "Waveshare RP2040-Zero", 10.2, 2.8, 1.0)
    add_text(board, "USB-C end", 10.2, 5.0, 0.9)
    add_text(board, "PICO SWD", 47.0, 31.7, 1.25)
    add_text(board, "1 SWCLK  2 GND  3 SWDIO", 38.5, 33.2, 0.75)
    add_text(board, "UART", 49.6, 17.8, 1.25)
    add_text(board, "1 TX  2 GND  3 RX", 42.0, 19.4, 0.75)
    add_text(board, "RUN", 49.4, 5.8, 1.0)
    add_text(board, "NO 3V3 TO TARGET", 14.5, 41.0, 1.0)
    add_text(board, "GP10", 14.4, 35.0, 0.8)
    add_text(board, "GP11", 14.4, 32.5, 0.8)
    add_text(board, "GP12", 14.4, 30.0, 0.8)
    add_text(board, "GP4", 31.4, 14.6, 0.8)
    add_text(board, "GP5", 31.4, 17.1, 0.8)
    add_text(board, PROJECT, 4.0, 49.0, 0.85)

    # Small pin-1 marks by the target JST connectors.
    add_text(board, "1", 50.0, 35.4, 0.8)
    add_text(board, "1", 50.0, 21.4, 0.8)

    pcbnew.SaveBoard(str(OUT / f"{PROJECT}.kicad_pcb"), board)


if __name__ == "__main__":
    main()
