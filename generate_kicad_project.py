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


def route(board, points, net, width=0.35, layer=pcbnew.F_Cu, chamfer=0.4):
    # Convert arbitrary diagonals to 45-degree segments, then chamfer 90-degree corners.
    expanded = [points[0]]
    for end in points[1:]:
        start = expanded[-1]
        dx, dy = end[0] - start[0], end[1] - start[1]
        if dx == 0 or dy == 0 or abs(abs(dx) - abs(dy)) < 1e-6:
            expanded.append(end)
            continue
        sx, sy = (1 if dx > 0 else -1), (1 if dy > 0 else -1)
        if abs(dx) > abs(dy):
            expanded.append((end[0] - sx * abs(dy), start[1]))
        else:
            expanded.append((start[0], end[1] - sy * abs(dx)))
        expanded.append(end)

    routed = [expanded[0]]
    for index in range(1, len(expanded) - 1):
        a, b, c = expanded[index - 1], expanded[index], expanded[index + 1]
        incoming = (b[0] - a[0], b[1] - a[1])
        outgoing = (c[0] - b[0], c[1] - b[1])
        u1 = tuple(0 if value == 0 else (1 if value > 0 else -1) for value in incoming)
        u2 = tuple(0 if value == 0 else (1 if value > 0 else -1) for value in outgoing)
        if u1[0] * u2[0] + u1[1] * u2[1] == 0:
            span1 = max(abs(incoming[0]), abs(incoming[1]))
            span2 = max(abs(outgoing[0]), abs(outgoing[1]))
            setback = min(chamfer, span1 / 3, span2 / 3)
            routed.append((b[0] - u1[0] * setback, b[1] - u1[1] * setback))
            routed.append((b[0] + u2[0] * setback, b[1] + u2[1] * setback))
        else:
            routed.append(b)
    routed.append(expanded[-1])

    for a, b in zip(routed, routed[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        if dx != 0 and dy != 0 and abs(abs(dx) - abs(dy)) >= 1e-6:
            raise ValueError(f"Non-45-degree track segment: {a} -> {b}")
    for a, b, c in zip(routed, routed[1:], routed[2:]):
        incoming = (b[0] - a[0], b[1] - a[1])
        outgoing = (c[0] - b[0], c[1] - b[1])
        if incoming[0] * outgoing[0] + incoming[1] * outgoing[1] == 0:
            raise ValueError(f"90-degree track corner remains at {b}")

    for a, b in zip(routed, routed[1:]):
        if a == b:
            continue
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

    # 30 mm x 40 mm portrait layout matching the mechanical concept sketch.
    add_rect(board, 0, 0, 30, 40, pcbnew.Edge_Cuts, 0.1)

    # Downloaded 23-pin RP2040-Zero footprint, centered with USB-C at the top.
    u1 = load_local_fp("Waveshare_RP2040-Zero", "U1", "RP2040-Zero", 4.84, 27.187)
    board.Add(u1)
    set_pad_net(u1, 2, nets["GND"])
    set_pad_net(u1, 14, nets["GP4_UART_TX"])
    set_pad_net(u1, 15, nets["GP5_UART_RX"])
    set_pad_net(u1, 20, nets["RUN_RESET"])
    set_pad_net(u1, 21, nets["GP11_SWDIO"])
    set_pad_net(u1, 22, nets["GP10_SWCLK"])

    resistors = [
        ("R1", "100R", 17.54, 28.8, 270, "GP10_SWCLK", "SWCLK"),
        ("R2", "100R", 15.0, 28.8, 270, "GP11_SWDIO", "SWDIO"),
        ("R3", "100R", 20.08, 28.8, 270, "GP4_UART_TX", "UART_TX"),
        ("R4", "100R", 22.62, 28.8, 270, "GP5_UART_RX", "UART_RX"),
    ]
    fps = {"U1": u1}
    for ref, value, x, y, rot, n1, n2 in resistors:
        r = load_fp(
            "Resistor_SMD",
            "R_0603_1608Metric",
            ref,
            value,
            x,
            y,
            rot,
        )
        board.Add(r)
        set_pad_net(r, 1, nets[n1])
        set_pad_net(r, 2, nets[n2])
        fps[ref] = r
    fps["R1"].Reference().SetPosition(vec(17.54, 31.8))
    fps["R2"].Reference().SetPosition(vec(13.2, 28.8))
    fps["R3"].Reference().SetPosition(vec(20.08, 31.8))
    fps["R4"].Reference().SetPosition(vec(25.0, 28.8))

    swd = load_fp(
        "Connector_JST",
        "JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal",
        "J3",
        "Pico SWD JST-SH",
        23,
        36.5,
    )
    uart = load_fp(
        "Connector_JST",
        "JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal",
        "J4",
        "UART JST-SH",
        7,
        36.5,
    )
    reset = load_fp(
        "Connector_PinHeader_2.54mm",
        "PinHeader_1x02_P2.54mm_Vertical",
        "J5",
        "RUN/RESET optional",
        2.5,
        28.5,
    )
    for fp in (swd, uart, reset):
        board.Add(fp)
    reset.Reference().SetPosition(vec(2.5, 25.5))
    set_pad_net(swd, 1, nets["SWCLK"])
    set_pad_net(swd, 2, nets["GND"])
    set_pad_net(swd, 3, nets["SWDIO"])
    set_pad_net(uart, 1, nets["UART_TX"])
    set_pad_net(uart, 2, nets["GND"])
    set_pad_net(uart, 3, nets["UART_RX"])
    set_pad_net(reset, 1, nets["RUN_RESET"])
    set_pad_net(reset, 2, nets["GND"])
    fps.update({"J3": swd, "J4": uart, "J5": reset})

    tp = load_fp("TestPoint", "TestPoint_THTPad_D1.5mm_Drill0.7mm", "TP1", "RUN", 6, 29.5)
    board.Add(tp)
    tp.Reference().SetPosition(vec(2.0, 23.5))
    set_pad_net(tp, 1, nets["RUN_RESET"])
    fps["TP1"] = tp

    # Routing: exact footprint pad positions, 0.35 mm signals, 0.6 mm ground.
    r1_in, r1_out = pad_xy(fps["R1"], 1), pad_xy(fps["R1"], 2)
    r2_in, r2_out = pad_xy(fps["R2"], 1), pad_xy(fps["R2"], 2)
    r3_in, r3_out = pad_xy(fps["R3"], 1), pad_xy(fps["R3"], 2)
    r4_in, r4_out = pad_xy(fps["R4"], 1), pad_xy(fps["R4"], 2)
    swd1, swd2, swd3 = (pad_xy(swd, number) for number in (1, 2, 3))
    uart1, uart2, uart3 = (pad_xy(uart, number) for number in (1, 2, 3))

    gp4, gp5 = pad_xy(u1, 14), pad_xy(u1, 15)
    run, gp11, gp10 = pad_xy(u1, 20), pad_xy(u1, 21), pad_xy(u1, 22)

    # SWD source termination directly below the RP2040-Zero bottom pads.
    route(board, [gp10, r1_in], nets["GP10_SWCLK"])
    route(board, [r1_out, (17.54, 30.5)], nets["SWCLK"])
    add_via(board, 17.54, 30.5, nets["SWCLK"])
    route(board, [(17.54, 30.5), (21.0, 30.5)], nets["SWCLK"], layer=pcbnew.B_Cu)
    add_via(board, 21.0, 30.5, nets["SWCLK"])
    route(board, [(21.0, 30.5), swd1], nets["SWCLK"])
    route(board, [gp11, r2_in], nets["GP11_SWDIO"])
    route(board, [r2_out, (15.0, 31.5)], nets["SWDIO"])
    add_via(board, 15.0, 31.5, nets["SWDIO"])
    route(board, [(15.0, 31.5), (24.0, 31.5)], nets["SWDIO"], layer=pcbnew.B_Cu)
    add_via(board, 24.0, 31.5, nets["SWDIO"])
    route(board, [(24.0, 31.5), swd3], nets["SWDIO"])

    # UART inputs wrap around the module's right edge into the aligned resistor row.
    route(board, [gp4, (27.0, gp4[1]), (27.0, 18.0)], nets["GP4_UART_TX"])
    add_via(board, 27.0, 18.0, nets["GP4_UART_TX"])
    route(board, [(27.0, 18.0), (27.0, 26.5), (20.275, 26.5), (18.8, 27.975)], nets["GP4_UART_TX"], layer=pcbnew.B_Cu)
    add_via(board, 18.8, 27.975, nets["GP4_UART_TX"])
    route(board, [(18.8, 27.975), r3_in], nets["GP4_UART_TX"])
    route(board, [gp5, (28.0, gp5[1]), (28.0, r4_in[1])], nets["GP5_UART_RX"], layer=pcbnew.B_Cu)
    add_via(board, 28.0, r4_in[1], nets["GP5_UART_RX"])
    route(board, [(28.0, r4_in[1]), r4_in], nets["GP5_UART_RX"])

    # UART outputs use lower B.Cu lanes toward the lower-left connector.
    route(board, [r3_out, (20.08, 32.5)], nets["UART_TX"])
    add_via(board, 20.08, 32.5, nets["UART_TX"])
    route(board, [(20.08, 32.5), (6.0, 32.5)], nets["UART_TX"], layer=pcbnew.B_Cu)
    add_via(board, 6.0, 32.5, nets["UART_TX"])
    route(board, [(6.0, 32.5), uart1], nets["UART_TX"])
    route(board, [r4_out, (26.5, r4_out[1]), (26.5, 33.5)], nets["UART_RX"])
    add_via(board, 26.5, 33.5, nets["UART_RX"])
    route(board, [(26.5, 33.5), (8.0, 33.5)], nets["UART_RX"], layer=pcbnew.B_Cu)
    add_via(board, 8.0, 33.5, nets["UART_RX"])
    route(board, [(8.0, 33.5), uart3], nets["UART_RX"])

    # RUN/RESET header at the left-center position shown in the concept sketch.
    route(board, [run, (run[0], 28.0), (4.5, 28.0), (4.5, pad_xy(reset, 1)[1]), pad_xy(reset, 1)], nets["RUN_RESET"])
    route(board, [pad_xy(reset, 1), pad_xy(tp, 1)], nets["RUN_RESET"])

    g = nets["GND"]
    for x, y in [(1.2, 1.2), (28.8, 1.2), (1.2, 20.0), (1.2, 38.8), (28.8, 38.8)]:
        add_via(board, x, y, g)

    # Connector labels. U1 provides its own module outline and orientation.
    add_text(board, "USB-C", 15.0, 1.2, 0.8)
    add_text(board, "RUN", 6.0, 27.0, 0.8)
    add_text(board, "UART", 10.0, 29.0, 0.8)
    add_text(board, "SWD", 27.5, 26.5, 0.8)
    add_text(board, "3V3 ISOLATED", 15.0, 33.5, 0.8)

    # GND pours on both copper layers, inset from the routed board edge.
    zone_outline = [(0.3, 0.3), (29.7, 0.3), (29.7, 39.7), (0.3, 39.7)]
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
