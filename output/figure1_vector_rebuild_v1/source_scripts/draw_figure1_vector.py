"""Generate an editable Inkscape SVG reconstruction of Figure 1.

Panels A, B, E, and F are deterministic vector schematics. Panels C and D
retain only their panel headings and are intentionally blank for later data
plots. The SVG uses owner-first semantic groups and Inkscape layers following
the BayesianBrain illustrator-scientific-figures skill.
"""

from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape


WIDTH = 1800
HEIGHT = 1000
OUT_DIR = Path(__file__).resolve().parents[1]
OUT_SVG = OUT_DIR / "Figure1_vector_C_D_blank.svg"

INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"

BLACK = "#171a21"
GRAY = "#6b7280"
LIGHT_GRAY = "#d1d5db"
BLUE = "#2455d6"
SKY = "#3498db"
TEAL = "#11899b"
GREEN = "#2d7d3e"
PALE_GREEN = "#eaf5e6"
ORANGE = "#ff6b00"
PURPLE = "#7433a8"
RED = "#ef3b33"
PALE_RED = "#fbe8e8"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def attrs(**kwargs: object) -> str:
    return " ".join(
        f'{key.replace("_", "-")}="{escape(str(value))}"'
        for key, value in kwargs.items()
        if value is not None
    )


def rect(x: float, y: float, w: float, h: float, *, ident: str, **style: object) -> str:
    return f'<rect id="{ident}" x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" {attrs(**style)}/>'


def circle(cx: float, cy: float, r: float, *, ident: str, **style: object) -> str:
    return f'<circle id="{ident}" cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" {attrs(**style)}/>'


def ellipse(cx: float, cy: float, rx: float, ry: float, *, ident: str, **style: object) -> str:
    return f'<ellipse id="{ident}" cx="{fmt(cx)}" cy="{fmt(cy)}" rx="{fmt(rx)}" ry="{fmt(ry)}" {attrs(**style)}/>'


def line(x1: float, y1: float, x2: float, y2: float, *, ident: str, **style: object) -> str:
    return f'<path id="{ident}" d="M {fmt(x1)} {fmt(y1)} L {fmt(x2)} {fmt(y2)}" {attrs(**style)}/>'


def path(d: str, *, ident: str, **style: object) -> str:
    return f'<path id="{ident}" d="{d}" {attrs(**style)}/>'


def text(
    x: float,
    y: float,
    value: str,
    *,
    ident: str,
    size: float = 16,
    fill: str = BLACK,
    weight: str = "normal",
    anchor: str = "start",
    style: str | None = None,
) -> str:
    extra = f' style="{escape(style)}"' if style else ""
    return (
        f'<text id="{ident}" x="{fmt(x)}" y="{fmt(y)}" '
        f'font-family="Arial,Helvetica,sans-serif" font-size="{fmt(size)}" '
        f'font-weight="{weight}" text-anchor="{anchor}" fill="{fill}"{extra}>'
        f'{escape(value)}</text>'
    )


def formula_text(
    x: float,
    y: float,
    base: str,
    sub: str,
    *,
    ident: str,
    size: float = 18,
    fill: str = BLACK,
    anchor: str = "middle",
) -> str:
    return (
        f'<text id="{ident}" x="{fmt(x)}" y="{fmt(y)}" '
        f'font-family="Arial,Helvetica,sans-serif" font-size="{fmt(size)}" '
        f'font-style="italic" font-weight="600" text-anchor="{anchor}" fill="{fill}">'
        f'{escape(base)}<tspan font-size="{fmt(size * 0.68)}" baseline-shift="sub">{escape(sub)}</tspan></text>'
    )


def group(ident: str, items: list[str], *, label: str | None = None, extra: str = "") -> str:
    label_attr = f' inkscape:label="{escape(label)}"' if label else ""
    return f'<g id="{ident}"{label_attr}{extra}>\n' + "\n".join(items) + "\n</g>"


def arrow_path(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    ident: str,
    color: str = BLACK,
    width: float = 2.4,
    head_len: float = 10,
    head_width: float = 14,
    dash: str | None = None,
) -> str:
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    bx, by = x2 - ux * head_len, y2 - uy * head_len
    lx, ly = bx + px * head_width / 2, by + py * head_width / 2
    rx, ry = bx - px * head_width / 2, by - py * head_width / 2
    d = (
        f'M {fmt(x1)} {fmt(y1)} L {fmt(bx)} {fmt(by)} '
        f'M {fmt(x2)} {fmt(y2)} L {fmt(lx)} {fmt(ly)} L {fmt(rx)} {fmt(ry)} Z'
    )
    return path(
        d,
        ident=ident,
        fill=color,
        stroke=color,
        stroke_width=width,
        stroke_linecap="round",
        stroke_linejoin="round",
        stroke_dasharray=dash,
    )


def curved_arrow(
    x1: float,
    y1: float,
    cx: float,
    cy: float,
    x2: float,
    y2: float,
    *,
    ident: str,
    color: str,
    width: float = 2.4,
) -> str:
    dx, dy = x2 - cx, y2 - cy
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    head_len, head_width = 9, 13
    bx, by = x2 - ux * head_len, y2 - uy * head_len
    lx, ly = bx + px * head_width / 2, by + py * head_width / 2
    rx, ry = bx - px * head_width / 2, by - py * head_width / 2
    d = (
        f'M {fmt(x1)} {fmt(y1)} Q {fmt(cx)} {fmt(cy)} {fmt(bx)} {fmt(by)} '
        f'M {fmt(x2)} {fmt(y2)} L {fmt(lx)} {fmt(ly)} L {fmt(rx)} {fmt(ry)} Z'
    )
    return path(d, ident=ident, fill=color, stroke=color, stroke_width=width, stroke_linecap="round")


class Panel:
    LAYERS = (
        "00_metadata",
        "01_reference_locked",
        "02_layout_guides",
        "10_background_locked",
        "20_components",
        "30_data_plots",
        "40_formulas",
        "50_annotations",
        "60_arrows_connectors",
        "70_labels",
        "90_export_notes",
    )

    def __init__(self, panel_id: str) -> None:
        self.panel_id = panel_id
        self.items: dict[str, list[str]] = {name: [] for name in self.LAYERS}

    def add(self, layer: str, item: str) -> None:
        self.items[layer].append(item)

    def render(self) -> str:
        layers: list[str] = []
        for name in self.LAYERS:
            hidden = ' style="display:none"' if name in {"00_metadata", "01_reference_locked", "02_layout_guides", "90_export_notes"} else ""
            layers.append(
                f'<g id="{self.panel_id}.{name}" inkscape:groupmode="layer" inkscape:label="{name}"{hidden}>\n'
                + "\n".join(self.items[name])
                + "\n</g>"
            )
        return (
            f'<g id="{self.panel_id}" inkscape:groupmode="layer" inkscape:label="{self.panel_id}">\n'
            + "\n".join(layers)
            + "\n</g>"
        )


def add_panel_heading(panel: Panel, letter: str, title_value: str, x: float, y: float) -> None:
    panel.add("70_labels", text(x, y, letter, ident=f"Figure1{letter}.label.panel_letter", size=24, weight="700"))
    if title_value:
        panel.add(
            "70_labels",
            text(x + 38, y, title_value, ident=f"Figure1{letter}.label.panel_title", size=21, weight="700"),
        )


def node_group(
    ident: str,
    cx: float,
    cy: float,
    r: float,
    label_lines: list[str],
    color: str = BLUE,
    owned: list[str] | None = None,
) -> str:
    parts = [circle(cx, cy, r, ident=f"{ident}.frame", fill="#ffffff", stroke=color, stroke_width=2.2)]
    start_y = cy - (len(label_lines) - 1) * 9
    for index, value in enumerate(label_lines):
        parts.append(text(cx, start_y + index * 18, value, ident=f"{ident}.label_{index + 1}", size=14, anchor="middle"))
    parts.extend(owned or [])
    return group(ident, parts)


def fish_group(ident: str, x: float, y: float, scale: float = 1.0, color: str = "#2f6690") -> str:
    parts = [
        ellipse(x, y, 14 * scale, 7 * scale, ident=f"{ident}.body", fill=color, stroke="#244b6b", stroke_width=1),
        path(
            f'M {fmt(x - 13 * scale)} {fmt(y)} L {fmt(x - 24 * scale)} {fmt(y - 8 * scale)} L {fmt(x - 24 * scale)} {fmt(y + 8 * scale)} Z',
            ident=f"{ident}.tail",
            fill=color,
            stroke="#244b6b",
            stroke_width=1,
        ),
        circle(x + 7 * scale, y - 2 * scale, 1.4 * scale, ident=f"{ident}.eye", fill="#ffffff"),
    ]
    return group(ident, parts)


def thermometer_group(ident: str, x: float, y: float, scale: float = 1.0) -> str:
    return group(
        ident,
        [
            rect(x - 6 * scale, y - 35 * scale, 12 * scale, 55 * scale, ident=f"{ident}.tube", rx=6 * scale, fill="#ffffff", stroke=BLACK, stroke_width=1.8),
            rect(x - 2.2 * scale, y - 26 * scale, 4.4 * scale, 39 * scale, ident=f"{ident}.mercury", rx=2 * scale, fill=RED),
            circle(x, y + 20 * scale, 10 * scale, ident=f"{ident}.bulb_outer", fill="#ffffff", stroke=BLACK, stroke_width=1.8),
            circle(x, y + 20 * scale, 6 * scale, ident=f"{ident}.bulb_inner", fill=BLUE),
        ],
    )


def build_panel_a(panel: Panel) -> None:
    add_panel_heading(panel, "A", "Ecological task", 14, 31)
    panel.add("70_labels", text(250, 67, "Possible causal structure", ident="Figure1A.label.causal_structure", size=17, fill=BLUE, weight="700", anchor="middle"))
    panel.add("70_labels", text(680, 67, "Task interface", ident="Figure1A.label.task_interface", size=17, fill=BLUE, weight="700", anchor="middle"))

    panel.add(
        "20_components",
        node_group(
            "Figure1A.node.hidden_depth",
            250,
            125,
            48,
            ["Hidden", "depth"],
            owned=[formula_text(250, 153, "x", "t", ident="Figure1A.node.hidden_depth.formula", size=18)],
        ),
    )
    panel.add(
        "20_components",
        node_group(
            "Figure1A.node.temperature",
            105,
            275,
            53,
            ["Temperature"],
            owned=[
                formula_text(105, 298, "c", "1,t", ident="Figure1A.node.temperature.formula", size=17),
                thermometer_group("Figure1A.node.temperature.icon", 105, 323, 0.55),
            ],
        ),
    )
    panel.add(
        "20_components",
        node_group(
            "Figure1A.node.fish_speed",
            395,
            275,
            53,
            ["Fish-school", "speed"],
            owned=[
                formula_text(395, 303, "c", "2,t", ident="Figure1A.node.fish_speed.formula", size=17),
                fish_group("Figure1A.node.fish_speed.icon_1", 384, 323, 0.4),
                fish_group("Figure1A.node.fish_speed.icon_2", 406, 316, 0.35),
            ],
        ),
    )
    panel.add("60_arrows_connectors", arrow_path(214, 158, 144, 232, ident="Figure1A.connector.depth_to_temperature", width=2.2))
    panel.add("60_arrows_connectors", arrow_path(145, 225, 215, 151, ident="Figure1A.connector.temperature_to_depth", width=2.2))
    panel.add("60_arrows_connectors", arrow_path(286, 158, 356, 232, ident="Figure1A.connector.depth_to_fish", width=2.2))
    panel.add("60_arrows_connectors", arrow_path(355, 225, 285, 151, ident="Figure1A.connector.fish_to_depth", width=2.2))
    panel.add("60_arrows_connectors", arrow_path(160, 275, 337, 275, ident="Figure1A.connector.temperature_to_fish", width=2.2))
    panel.add("60_arrows_connectors", arrow_path(337, 286, 160, 286, ident="Figure1A.connector.fish_to_temperature", width=2.2))

    tank_parts = [
        rect(500, 78, 365, 216, ident="Figure1A.card.task_interface.water", rx=18, fill="url(#waterGradient)"),
        path("M 500 259 Q 575 240 650 261 T 790 255 T 865 260 L 865 294 L 500 294 Z", ident="Figure1A.card.task_interface.sand", fill="#c5a45a"),
        ellipse(535, 270, 28, 17, ident="Figure1A.card.task_interface.rock_1", fill="#7b6a50"),
        ellipse(812, 272, 24, 13, ident="Figure1A.card.task_interface.rock_2", fill="#655a4b"),
        path("M 565 262 Q 557 232 565 206 M 576 263 Q 584 230 579 195 M 588 263 Q 595 236 592 215", ident="Figure1A.card.task_interface.plants_left", fill="none", stroke="#14824b", stroke_width=5, stroke_linecap="round"),
        path("M 750 268 Q 746 237 750 218 M 763 269 Q 772 238 768 205 M 782 270 Q 787 245 784 224", ident="Figure1A.card.task_interface.plants_right", fill="none", stroke="#14824b", stroke_width=5, stroke_linecap="round"),
        fish_group("Figure1A.card.task_interface.fish_1", 680, 132, 0.8),
        fish_group("Figure1A.card.task_interface.fish_2", 730, 157, 0.9),
        fish_group("Figure1A.card.task_interface.fish_3", 660, 190, 0.75),
        fish_group("Figure1A.card.task_interface.fish_4", 755, 205, 0.82),
        thermometer_group("Figure1A.card.task_interface.thermometer", 532, 155, 0.8),
        text(552, 125, "temperature", ident="Figure1A.card.task_interface.temperature_label", size=13, fill=BLUE, weight="700"),
        text(552, 143, "cue", ident="Figure1A.card.task_interface.temperature_cue", size=13, fill=BLUE),
        text(770, 175, "fish-speed", ident="Figure1A.card.task_interface.fish_label", size=13, fill=BLUE, weight="700"),
        text(770, 193, "cue", ident="Figure1A.card.task_interface.fish_cue", size=13, fill=BLUE),
        arrow_path(796, 134, 842, 134, ident="Figure1A.card.task_interface.internal_motion_arrow", color=BLUE, width=2),
        rect(500, 78, 365, 216, ident="Figure1A.card.task_interface.frame", rx=18, fill="none", stroke=BLACK, stroke_width=4),
    ]
    panel.add("20_components", group("Figure1A.card.task_interface", tank_parts))

    slider = [
        text(682, 325, "Report hidden depth", ident="Figure1A.control.depth_slider.label", size=16, fill=BLUE, weight="700", anchor="middle"),
        text(522, 355, "shallower", ident="Figure1A.control.depth_slider.shallower", size=13, anchor="middle"),
        text(846, 355, "deeper", ident="Figure1A.control.depth_slider.deeper", size=13, anchor="middle"),
        line(565, 348, 800, 348, ident="Figure1A.control.depth_slider.baseline", stroke=BLACK, stroke_width=2.5),
    ]
    for i in range(7):
        x = 565 + i * (235 / 6)
        slider.append(line(x, 339, x, 357, ident=f"Figure1A.control.depth_slider.tick_{i + 1}", stroke=BLACK, stroke_width=1.8))
    slider.append(rect(675, 334, 13, 29, ident="Figure1A.control.depth_slider.thumb", rx=6, fill="#2e77d0", stroke=BLACK, stroke_width=1.5))
    panel.add("20_components", group("Figure1A.control.depth_slider", slider))


def matrix_group(ident: str, x: float, y: float, values: list[list[int]]) -> str:
    cell = 21
    items = [text(x + 31.5, y - 12, "Transition matrix", ident=f"{ident}.title", size=10.5, weight="700", anchor="middle")]
    labels = ["x", "c1", "c2"]
    for i, lab in enumerate(labels):
        items.append(text(x + (i + 0.5) * cell, y - 1, lab, ident=f"{ident}.col_{i}", size=9, anchor="middle", style="font-style:italic"))
        items.append(text(x - 6, y + (i + 0.68) * cell, lab, ident=f"{ident}.row_{i}", size=9, anchor="end", style="font-style:italic"))
    for row in range(3):
        for col in range(3):
            value = values[row][col]
            fill = "#6f91cf" if value > 0 else "#d16863" if value < 0 else "#ffffff"
            items.append(rect(x + col * cell, y + row * cell, cell, cell, ident=f"{ident}.cell_{row}_{col}", fill=fill, stroke="#737373", stroke_width=0.9))
    return group(ident, items)


def mini_graph(ident: str, x: float, y: float, mode: str) -> str:
    items = [
        group(
            f"{ident}.node_x",
            [
                circle(x + 43, y, 16, ident=f"{ident}.node_x.frame", fill="#ffffff", stroke=BLUE, stroke_width=1.8),
                text(x + 43, y + 5, "x", ident=f"{ident}.node_x.label", size=13, anchor="middle", style="font-style:italic"),
            ],
        ),
        group(
            f"{ident}.node_c1",
            [
                circle(x + 20, y + 62, 16, ident=f"{ident}.node_c1.frame", fill="#ffffff", stroke=BLUE, stroke_width=1.8),
                text(x + 20, y + 67, "c1", ident=f"{ident}.node_c1.label", size=12, anchor="middle", style="font-style:italic"),
            ],
        ),
        group(
            f"{ident}.node_c2",
            [
                circle(x + 66, y + 62, 16, ident=f"{ident}.node_c2.frame", fill="#ffffff", stroke=BLUE, stroke_width=1.8),
                text(x + 66, y + 67, "c2", ident=f"{ident}.node_c2.label", size=12, anchor="middle", style="font-style:italic"),
            ],
        ),
    ]
    if mode in {"common", "rot_c1", "rot_both"}:
        items.append(arrow_path(x + 38, y + 17, x + 25, y + 45, ident=f"{ident}.connector.x_to_c1", color=BLUE, width=1.8, head_len=7, head_width=10))
    if mode in {"common", "rot_both"}:
        items.append(arrow_path(x + 48, y + 17, x + 61, y + 45, ident=f"{ident}.connector.x_to_c2", color=BLUE, width=1.8, head_len=7, head_width=10))
    if mode == "serial":
        items.append(arrow_path(x + 38, y + 17, x + 25, y + 45, ident=f"{ident}.connector.x_to_c1", color=RED, width=1.8, head_len=7, head_width=10))
        items.append(arrow_path(x + 37, y + 62, x + 49, y + 62, ident=f"{ident}.connector.c1_to_c2", color=RED, width=1.8, head_len=7, head_width=10))
    if mode in {"rot_c1", "rot_both"}:
        items.append(curved_arrow(x + 33, y + 54, x + 43, y + 37, x + 55, y + 54, ident=f"{ident}.connector.c1_to_c2", color=BLUE, width=1.7))
        items.append(curved_arrow(x + 54, y + 70, x + 43, y + 85, x + 31, y + 70, ident=f"{ident}.connector.c2_to_c1", color=RED, width=1.7))
    return group(ident, items)


def build_panel_b(panel: Panel) -> None:
    add_panel_heading(panel, "B", "task models", 14, 408)
    specs = [
        ("common", "Common cause", BLUE, [[1, 0, 0], [1, 1, 0], [1, 0, 1]]),
        ("serial", "Serial mediation", RED, [[1, 0, 0], [1, 1, 0], [0, 1, 1]]),
        ("rot_c1", "Rotational: x -> c1", BLUE, [[1, 0, 0], [1, 1, -1], [0, 1, 1]]),
        ("rot_both", "Rotational: x -> both", BLUE, [[1, 0, 0], [1, 1, -1], [1, 1, 1]]),
    ]
    for i, (mode, title_value, color, values) in enumerate(specs):
        x = 8 + i * 238
        entry = [
            text(x + 116, 432, title_value, ident=f"Figure1B.model.{mode}.title", size=13, fill=color, weight="700", anchor="middle"),
            mini_graph(f"Figure1B.model.{mode}.graph", x + 5, 470, mode),
            matrix_group(f"Figure1B.model.{mode}.matrix", x + 122, 471, values),
        ]
        panel.add("20_components", group(f"Figure1B.model.{mode}", entry))
    panel.add("50_annotations", text(944, 571, "blue = positive; red = negative", ident="Figure1B.annotation.color_key", size=9, fill=GRAY, anchor="end"))


def build_blank_panel(panel: Panel, letter: str, title_value: str, x: float, y: float) -> None:
    add_panel_heading(panel, letter, title_value, x, y)
    panel.add("90_export_notes", text(x + 40, y + 40, "Intentionally blank for future data artwork", ident=f"Figure1{letter}.note.blank_panel", size=12, fill=GRAY))


def build_panel_e(panel: Panel) -> None:
    add_panel_heading(panel, "E", "Bayesian Brain's generative model", 978, 31)
    row_specs = [
        ("task", "Task\ndynamics", 1110, "#9cbde2", BLUE),
        ("belief", "Belief\ndynamics", 1230, "#bddcae", GREEN),
        ("behavior", "Behavior", 1330, "#ff922e", ORANGE),
        ("neural", "Neural\nactivity", 1430, "#7f43a5", PURPLE),
    ]
    y_by = {"task": 100, "belief": 220, "behavior": 320, "neural": 420}
    label_x = 990
    for role, label_value, _, fill, color in row_specs:
        lines = label_value.split("\n")
        for j, value in enumerate(lines):
            panel.add("70_labels", text(label_x, y_by[role] - 4 + j * 18, value, ident=f"Figure1E.label.{role}_{j}", size=15, fill=color, weight="700"))
    cols = [1110, 1220, 1330]
    for role, _, _, fill, color in row_specs:
        y = y_by[role]
        for i, x in enumerate(cols):
            panel.add("20_components", group(f"Figure1E.node.{role}_{i + 1}", [circle(x, y, 21, ident=f"Figure1E.node.{role}_{i + 1}.frame", fill=fill, stroke=BLACK, stroke_width=2.2)]))
        panel.add("70_labels", text(1376, y + 6, "...", ident=f"Figure1E.label.{role}_ellipsis", size=22, weight="700"))
    for i in range(2):
        panel.add("60_arrows_connectors", arrow_path(cols[i] + 23, 100, cols[i + 1] - 23, 100, ident=f"Figure1E.connector.task_time_{i + 1}", width=2.1))
        panel.add("60_arrows_connectors", arrow_path(cols[i] + 23, 220, cols[i + 1] - 23, 220, ident=f"Figure1E.connector.belief_time_{i + 1}", width=2.1))
    for i, x in enumerate(cols):
        panel.add("60_arrows_connectors", arrow_path(x, 123, x, 196, ident=f"Figure1E.connector.sensory_{i + 1}", color=TEAL, width=1.9, dash="7,5"))
        panel.add("60_arrows_connectors", arrow_path(x, 243, x, 296, ident=f"Figure1E.connector.belief_to_behavior_{i + 1}", width=2.1))
        panel.add("60_arrows_connectors", arrow_path(x, 343, x, 396, ident=f"Figure1E.connector.behavior_to_neural_{i + 1}", width=2.1))
    panel.add("50_annotations", text(1220, 176, "sensory evidence", ident="Figure1E.annotation.sensory_evidence", size=14, fill=TEAL, weight="700", anchor="middle"))

    panel.add("70_labels", text(1624, 78, "Experienced world", ident="Figure1E.label.experienced_world", size=18, fill=BLUE, weight="700", anchor="middle"))
    matrix_x, matrix_y, cw, ch = 1510, 145, 128, 108
    panel.add("70_labels", text(matrix_x + cw / 2, 126, "Common cause", ident="Figure1E.label.world_col_common", size=13, anchor="middle"))
    panel.add("70_labels", text(matrix_x + 1.5 * cw, 126, "Serial mediation", ident="Figure1E.label.world_col_serial", size=13, anchor="middle"))
    panel.add("70_labels", text(1498, matrix_y + 48, "Common", ident="Figure1E.label.world_row_common_1", size=13, anchor="end"))
    panel.add("70_labels", text(1498, matrix_y + 66, "cause", ident="Figure1E.label.world_row_common_2", size=13, anchor="end"))
    panel.add("70_labels", text(1498, matrix_y + ch + 48, "Serial", ident="Figure1E.label.world_row_serial_1", size=13, anchor="end"))
    panel.add("70_labels", text(1498, matrix_y + ch + 66, "mediation", ident="Figure1E.label.world_row_serial_2", size=13, anchor="end"))
    values = [[("matched", PALE_GREEN), ("mismatched", PALE_RED)], [("mismatched", PALE_RED), ("matched", PALE_GREEN)]]
    cards = []
    for row in range(2):
        for col in range(2):
            value, fill = values[row][col]
            ident = f"Figure1E.matrix.world_model.cell_{row}_{col}"
            cards.append(
                group(
                    ident,
                    [
                        rect(matrix_x + col * cw, matrix_y + row * ch, cw, ch, ident=f"{ident}.frame", rx=8, fill=fill, stroke="#555555", stroke_width=1.6),
                        text(matrix_x + (col + 0.5) * cw, matrix_y + (row + 0.56) * ch, value, ident=f"{ident}.label", size=14, fill=GREEN if value == "matched" else BLACK, weight="700", anchor="middle"),
                    ],
                )
            )
    panel.add("20_components", group("Figure1E.matrix.world_model", cards))
    panel.add("50_annotations", arrow_path(1432, 370, 1432, 155, ident="Figure1E.annotation.internal_model_axis", color=GREEN, width=2.2))
    panel.add(
        "50_annotations",
        '<text id="Figure1E.annotation.internal_model_label" x="1417" y="270" '
        'font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" '
        'text-anchor="middle" fill="#2d7d3e" transform="rotate(-90 1417 270)">Internal model</text>',
    )
    panel.add("50_annotations", text(1635, 455, "Task model and internal model need not agree.", ident="Figure1E.annotation.model_note", size=14, anchor="middle"))


def signal_path(x: float, y: float, w: float, amp: float, phase: float, cycles: float = 2.5) -> str:
    points = []
    for i in range(61):
        px = x + w * i / 60
        py = y + amp * math.sin(phase + cycles * 2 * math.pi * i / 60) * (0.72 + 0.28 * math.cos(i / 7))
        points.append((px, py))
    return "M " + " L ".join(f"{fmt(px)} {fmt(py)}" for px, py in points)


def model_icon(ident: str, x: float, y: float, serial: bool) -> str:
    color = RED if serial else BLUE
    parts = [
        group(
            f"{ident}.node_x",
            [
                circle(x + 68, y + 45, 18, ident=f"{ident}.node_x.frame", fill="#ffffff", stroke=color, stroke_width=1.8),
                text(x + 68, y + 50, "x", ident=f"{ident}.node_x.label", size=13, anchor="middle", style="font-style:italic"),
            ],
        ),
        group(
            f"{ident}.node_c1",
            [
                circle(x + 42, y + 112, 18, ident=f"{ident}.node_c1.frame", fill="#ffffff", stroke=color, stroke_width=1.8),
                text(x + 42, y + 117, "c1", ident=f"{ident}.node_c1.label", size=12, anchor="middle", style="font-style:italic"),
            ],
        ),
        group(
            f"{ident}.node_c2",
            [
                circle(x + 96, y + 112, 18, ident=f"{ident}.node_c2.frame", fill="#ffffff", stroke=color, stroke_width=1.8),
                text(x + 96, y + 117, "c2", ident=f"{ident}.node_c2.label", size=12, anchor="middle", style="font-style:italic"),
            ],
        ),
    ]
    if serial:
        parts.append(arrow_path(x + 63, y + 64, x + 47, y + 92, ident=f"{ident}.connector.x_to_c1", color=RED, width=1.8, head_len=7, head_width=10))
        parts.append(arrow_path(x + 62, y + 112, x + 76, y + 112, ident=f"{ident}.connector.c1_to_c2", color=RED, width=1.8, head_len=7, head_width=10))
    else:
        parts.append(arrow_path(x + 62, y + 64, x + 47, y + 92, ident=f"{ident}.connector.x_to_c1", color=BLUE, width=1.8, head_len=7, head_width=10))
        parts.append(arrow_path(x + 74, y + 64, x + 91, y + 92, ident=f"{ident}.connector.x_to_c2", color=BLUE, width=1.8, head_len=7, head_width=10))
    return group(ident, parts)


def build_panel_f(panel: Panel) -> None:
    add_panel_heading(panel, "F", "System identification", 978, 531)
    card_specs = [
        ("observations", 600, SKY, "observations"),
        ("neural", 700, PURPLE, "neural activity"),
        ("behavior", 800, ORANGE, "behavior"),
    ]
    for role, y, color, label_value in card_specs:
        items = [
            rect(995, y, 185, 70, ident=f"Figure1F.card.{role}.frame", rx=8, fill="#ffffff", stroke=color, stroke_width=2.2),
            text(1008, y + 25, label_value, ident=f"Figure1F.card.{role}.label", size=14, fill=color, weight="700"),
        ]
        if role == "observations":
            items.append(path(signal_path(1070, y + 48, 75, 5, 0.3, 4), ident=f"Figure1F.card.{role}.wave", fill="none", stroke=BLUE, stroke_width=2))
            items.append(thermometer_group(f"Figure1F.card.{role}.thermometer", 1150, y + 33, 0.38))
        elif role == "neural":
            pts = [(1070 + i * 2.2, y + 46 + 14 * math.sin(i * 1.9) * (0.3 + (i % 5) / 6)) for i in range(36)]
            d = "M " + " L ".join(f"{fmt(px)} {fmt(py)}" for px, py in pts)
            items.append(path(d, ident=f"Figure1F.card.{role}.trace", fill="none", stroke=PURPLE, stroke_width=2))
        else:
            items.append(line(1070, y + 53, 1160, y + 53, ident=f"Figure1F.card.{role}.baseline", stroke=BLACK, stroke_width=1.5))
            for i, height in enumerate([18, 28, 12, 34, 22, 30, 15]):
                items.append(line(1080 + i * 12, y + 53, 1080 + i * 12, y + 53 - height, ident=f"Figure1F.card.{role}.spike_{i + 1}", stroke=ORANGE, stroke_width=2.2))
        panel.add("20_components", group(f"Figure1F.card.{role}", items))
        panel.add("60_arrows_connectors", arrow_path(1185, y + 35, 1225, y + 35, ident=f"Figure1F.connector.{role}_to_latent", width=2.2))

    latent_items = [
        rect(1230, 590, 335, 285, ident="Figure1F.card.latent_dynamics.frame", rx=12, fill="#ffffff", stroke=GREEN, stroke_width=2.5),
        text(1397, 625, "schematic belief dynamics", ident="Figure1F.card.latent_dynamics.title", size=16, fill=GREEN, weight="700", anchor="middle"),
        path(signal_path(1250, 680, 290, 22, 0.2, 2.4), ident="Figure1F.card.latent_dynamics.trace_observations", fill="none", stroke=BLUE, stroke_width=2.3),
        path(signal_path(1250, 750, 290, 24, 0.9, 2.7), ident="Figure1F.card.latent_dynamics.trace_neural", fill="none", stroke=GREEN, stroke_width=2.3),
        path(signal_path(1250, 820, 290, 18, -0.4, 2.1), ident="Figure1F.card.latent_dynamics.trace_behavior", fill="none", stroke=ORANGE, stroke_width=2.3),
    ]
    panel.add("20_components", group("Figure1F.card.latent_dynamics", latent_items))
    panel.add("50_annotations", text(1628, 570, "test candidate", ident="Figure1F.annotation.test_candidate_1", size=14, fill=GREEN, weight="700", anchor="middle"))
    panel.add("50_annotations", text(1628, 588, "internal models", ident="Figure1F.annotation.test_candidate_2", size=14, fill=GREEN, weight="700", anchor="middle"))

    candidates = [
        ("common", 610, BLUE, "Common cause", False),
        ("serial", 785, RED, "Serial mediation", True),
    ]
    for role, y, color, title_value, serial in candidates:
        items = [
            rect(1610, y, 170, 155, ident=f"Figure1F.model.{role}.frame", rx=10, fill="#ffffff", stroke=color, stroke_width=2.3),
            text(1695, y + 26, title_value, ident=f"Figure1F.model.{role}.title", size=15, fill=color, weight="700", anchor="middle"),
            model_icon(f"Figure1F.model.{role}.graph", 1626, y + 17, serial),
        ]
        panel.add("20_components", group(f"Figure1F.model.{role}", items))
        panel.add("60_arrows_connectors", arrow_path(1570, 690 if role == "common" else 800, 1600, y + 78, ident=f"Figure1F.connector.latent_to_{role}", width=2.2))
    panel.add("70_labels", text(1385, 930, "Which internal world model is the brain using?", ident="Figure1F.label.question", size=18, weight="700", anchor="middle"))


def build_svg() -> str:
    panels = {letter: Panel(f"Figure1{letter}") for letter in "ABCDEF"}
    build_panel_a(panels["A"])
    build_panel_b(panels["B"])
    build_blank_panel(panels["C"], "C", "cue dynamics", 14, 608)
    build_blank_panel(panels["D"], "D", "", 14, 798)
    build_panel_e(panels["E"])
    build_panel_f(panels["F"])

    defs = """
    <defs>
      <linearGradient id="waterGradient" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#8cd8f5"/>
        <stop offset="0.55" stop-color="#45a8d1"/>
        <stop offset="1" stop-color="#236e9a"/>
      </linearGradient>
    </defs>
    """
    backing = (
        '<g id="Figure1.05_export_background_locked" inkscape:groupmode="layer" inkscape:label="05_export_background_locked">'
        + rect(0, 0, WIDTH, HEIGHT, ident="Figure1.background.export_white", fill="#ffffff")
        + "</g>"
    )
    separators = group(
        "Figure1.annotations.panel_separators",
        [
            line(960, 0, 960, 1000, ident="Figure1.separator.main_vertical", stroke="#777777", stroke_width=1.2),
            line(0, 380, 960, 380, ident="Figure1.separator.left_A_B", stroke="#8b8b8b", stroke_width=1.1),
            line(0, 580, 960, 580, ident="Figure1.separator.left_B_C", stroke="#8b8b8b", stroke_width=1.1),
            line(0, 770, 960, 770, ident="Figure1.separator.left_C_D", stroke="#8b8b8b", stroke_width=1.1),
            line(960, 500, 1800, 500, ident="Figure1.separator.right_E_F", stroke="#8b8b8b", stroke_width=1.1),
        ],
    )
    root_annotations = f'<g id="Figure1.global_annotations" inkscape:groupmode="layer" inkscape:label="global_annotations">{separators}</g>'
    rendered_panels = "\n".join(panels[letter].render() for letter in "ABCDEF")
    metadata = (
        '<metadata id="Figure1.metadata">'
        '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
        '<rdf:Description rdf:about="" backend="inkscape_svg" variant="vector_C_D_blank_v1"/>'
        "</rdf:RDF></metadata>"
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="{INKSCAPE_NS}"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     width="1800" height="1000" viewBox="0 0 1800 1000">
  <title>Figure 1 vector reconstruction with panels C and D blank</title>
  <desc>Editable vector reconstruction generated for Inkscape. No embedded raster artwork.</desc>
  {metadata}
  {defs}
  {backing}
  {rendered_panels}
  {root_annotations}
</svg>
'''


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_SVG.write_text(build_svg(), encoding="utf-8")
    print(OUT_SVG)


if __name__ == "__main__":
    main()
