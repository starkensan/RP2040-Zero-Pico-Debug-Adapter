#!/usr/bin/env python3
"""Generate the RP2040-Zero Pico debug adapter KiCad PCB.

The schematic is intentionally simple and documented separately; this script
builds the placed/routed board from KiCad 9 stock footprints.
"""

from pathlib import Path
import subprocess
import sys
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


def load_local_fp(name, ref, value, x, y, rot=0):
    fp = pcbnew.FootprintLoad(str(OUT / "Adapter.pretty"), name)
    if fp is None:
        raise RuntimeError(f"Unable to load local footprint Adapter:{name}")
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
    matches = [p for p in fp.Pads() if p.GetNumber() == str(number)]
    if not matches:
        raise RuntimeError(f"{fp.GetReference()} has no pad {number}")
    for item in matches:
        item.SetNet(net)


def pad_xy(fp, number):
    position = pad(fp, number).GetPosition()
    return (pcbnew.ToMM(position.x), pcbnew.ToMM(position.y))


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


def add_zone(board, net, layer, points, clearance=0.25, min_thickness=0.25):
    zone = pcbnew.ZONE(board)
    zone.SetNet(net)
    zone.SetLayer(layer)
    zone.SetLocalClearance(mm(clearance))
    zone.SetMinThickness(mm(min_thickness))
    outline = zone.Outline()
    outline.NewOutline()
    for point in points:
        outline.Append(vec(*point))
    board.Add(zone)
    return zone


def fill_zones(board_path):
    board = pcbnew.LoadBoard(str(board_path))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(board_path), board)


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
        "RUN_RESET": add_net(board, "RUN_RESET"),
    }

    # 48 mm x 30 mm compact layout: module left, target I/O along the bottom.
    add_rect(board, 0, 0, 48, 30, pcbnew.Edge_Cuts, 0.1)

    # Downloaded 23-pin RP2040-Zero footprint, USB-C end toward board top.
    u1 = load_local_fp("Waveshare_RP2040-Zero", "U1", "RP2040-Zero", 3.5, 27.187)
    board.Add(u1)
    set_pad_net(u1, 2, nets["GND"])
    set_pad_net(u1, 14, nets["GP4_UART_TX"])
    set_pad_net(u1, 15, nets["GP5_UART_RX"])
    set_pad_net(u1, 20, nets["RUN_RESET"])
    set_pad_net(u1, 21, nets["GP11_SWDIO"])
    set_pad_net(u1, 22, nets["GP10_SWCLK"])

    resistors = [
        ("R1", "100R", 30.0, 18.0, "GP10_SWCLK", "SWCLK"),
        ("R2", "100R", 34.0, 20.5, "GP11_SWDIO", "SWDIO"),
        ("R3", "100R", 39.0, 14.0, "GP4_UART_TX", "UART_TX"),
        ("R4", "100R", 42.0, 18.0, "GP5_UART_RX", "UART_RX"),
    ]
    fps = {"U1": u1}
    for ref, value, x, y, n1, n2 in resistors:
        r = load_fp(
            "Resistor_SMD",
            "R_0603_1608Metric",
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
        34,
        26.5,
    )
    uart = load_fp(
        "Connector_JST",
        "JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal",
        "J4",
        "UART JST-SH",
        43.5,
        26.5,
    )
    reset = load_fp(
        "Connector_PinHeader_2.54mm",
        "PinHeader_1x02_P2.54mm_Vertical",
        "J5",
        "RUN/RESET optional",
        35,
        3,
    )
    for fp in (swd, uart, reset):
        board.Add(fp)
    reset.Reference().SetPosition(vec(39.0, 7.0))
    set_pad_net(swd, 1, nets["SWCLK"])
    set_pad_net(swd, 2, nets["GND"])
    set_pad_net(swd, 3, nets["SWDIO"])
    set_pad_net(uart, 1, nets["UART_TX"])
    set_pad_net(uart, 2, nets["GND"])
    set_pad_net(uart, 3, nets["UART_RX"])
    set_pad_net(reset, 1, nets["RUN_RESET"])
    set_pad_net(reset, 2, nets["GND"])
    fps.update({"J3": swd, "J4": uart, "J5": reset})

    tp = load_fp("TestPoint", "TestPoint_THTPad_D1.5mm_Drill0.7mm", "TP1", "RUN", 29, 3)
    board.Add(tp)
    set_pad_net(tp, 1, nets["RUN_RESET"])
    fps["TP1"] = tp

    # Routing: exact footprint pad positions, 0.35 mm signals, 0.6 mm ground.
    r1_in, r1_out = pad_xy(fps["R1"], 1), pad_xy(fps["R1"], 2)
    r2_in, r2_out = pad_xy(fps["R2"], 1), pad_xy(fps["R2"], 2)
    r3_in, r3_out = pad_xy(fps["R3"], 1), pad_xy(fps["R3"], 2)
    r4_in, r4_out = pad_xy(fps["R4"], 1), pad_xy(fps["R4"], 2)
    swd1, swd2, swd3 = (pad_xy(swd, number) for number in (1, 2, 3))
    uart1, uart2, uart3 = (pad_xy(uart, number) for number in (1, 2, 3))

    route(board, [(16.2, 24.52), (16.2, 27.5), (23.5, 27.5)], nets["GP10_SWCLK"])
    add_via(board, 23.5, 27.5, nets["GP10_SWCLK"])
    route(board, [(23.5, 27.5), (27.0, 27.5)], nets["GP10_SWCLK"], layer=pcbnew.B_Cu)
    add_via(board, 27.0, 27.5, nets["GP10_SWCLK"])
    route(board, [(27.0, 27.5), (27.0, r1_in[1]), r1_in], nets["GP10_SWCLK"])
    route(board, [r1_out, (32.0, r1_out[1]), (32.0, 23.0), swd1], nets["SWCLK"])
    route(board, [(13.66, 24.52), (13.66, 26.0), (33.175, 26.0), (33.175, 19.3)], nets["GP11_SWDIO"], layer=pcbnew.B_Cu)
    add_via(board, 33.175, 19.3, nets["GP11_SWDIO"])
    route(board, [(33.175, 19.3), r2_in], nets["GP11_SWDIO"])
    route(board, [r2_out, swd3], nets["SWDIO"])
    route(board, [(21.28, 14.36), (23.0, 14.36)], nets["GP4_UART_TX"])
    add_via(board, 23.0, 14.36, nets["GP4_UART_TX"])
    route(board, [(23.0, 14.36), (27.0, 14.36)], nets["GP4_UART_TX"], layer=pcbnew.B_Cu)
    add_via(board, 27.0, 14.36, nets["GP4_UART_TX"])
    route(board, [(27.0, 14.36), (27.0, r3_in[1]), r3_in], nets["GP4_UART_TX"])
    route(board, [r3_out, (40.2, r3_out[1]), (40.2, 22.5), uart1], nets["UART_TX"])
    route(board, [(21.28, 16.9), (41.175, 16.9), (41.175, 19.3)], nets["GP5_UART_RX"], layer=pcbnew.B_Cu)
    add_via(board, 41.175, 19.3, nets["GP5_UART_RX"])
    route(board, [(41.175, 19.3), r4_in], nets["GP5_UART_RX"])
    route(board, [r4_out, (44.5, r4_out[1]), uart3], nets["UART_RX"])
    route(board, [(11.12, 24.52), (11.12, 29.0), (25.0, 29.0)], nets["RUN_RESET"], layer=pcbnew.B_Cu)
    add_via(board, 25.0, 29.0, nets["RUN_RESET"])
    route(board, [(25.0, 29.0), (25.0, 3.0), pad_xy(reset, 1)], nets["RUN_RESET"])
    route(board, [(25.0, 3.0), pad_xy(tp, 1)], nets["RUN_RESET"])

    g = nets["GND"]
    add_via(board, uart2[0], 22.0, g)
    add_via(board, swd2[0], 22.0, g)
    route(board, [(6.04, 6.74), (1.0, 6.74), (1.0, 1.0), (47.0, 1.0), (47.0, 22.0)], g, 0.6, pcbnew.B_Cu)
    route(board, [(47.0, pad_xy(reset, 2)[1]), pad_xy(reset, 2)], g, 0.6, pcbnew.B_Cu)
    route(board, [(47.0, 22.0), (swd2[0], 22.0)], g, 0.6, pcbnew.B_Cu)
    route(board, [(uart2[0], 22.0), uart2], g, 0.3, pcbnew.F_Cu)
    route(board, [(swd2[0], 22.0), swd2], g, 0.3, pcbnew.F_Cu)

    # Connector labels. U1 provides its own module outline and orientation.
    add_text(board, "USB-C", 13.5, 3.5, 0.8)
    add_text(board, "SWD", 34.0, 16.5, 0.8)
    add_text(board, "UART", 43.5, 12.0, 0.8)
    add_text(board, "3V3 ISOLATED", 10.0, 28.0, 0.8)

    # Small pin-1 marks by the target JST connectors.
    add_text(board, "1", 31.6, 23.0, 0.8)
    add_text(board, "1", 41.1, 23.0, 0.8)

    # GND pours on both copper layers, inset from the routed board edge.
    zone_outline = [(0.3, 0.3), (47.7, 0.3), (47.7, 29.7), (0.3, 29.7)]
    add_zone(board, g, pcbnew.F_Cu, zone_outline)
    add_zone(board, g, pcbnew.B_Cu, zone_outline)

    board_path = OUT / f"{PROJECT}.kicad_pcb"
    pcbnew.SaveBoard(str(board_path), board)
    subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--fill-zones", str(board_path)],
        check=True,
    )


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--fill-zones":
        fill_zones(Path(sys.argv[2]))
    else:
        main()
