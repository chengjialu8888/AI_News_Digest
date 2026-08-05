#!/usr/bin/env python3
"""Build two Feishu-safe visual versions of the 2026-07-21 to 2026-07-27 AI weekly."""

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GENERATIVE = ROOT / "feishu-weekly-2026-07-21-to-07-27-generative-art"
SPACE = ROOT / "feishu-weekly-2026-07-21-to-07-27-outer-space"


TRENDS = [
    {
        "no": "01",
        "label": "上下文",
        "title": "上下文工程从写更多规则，变成授权成熟模型",
        "thesis": "该删的不是上下文，而是模型能自己推断的废上下文。真正贵的是团队偏好、验证流程和真实参考物。",
        "score": 92,
        "evidence": ["Opus 5", "80% prompt cut", "thick context"],
        "vars": [("能力", 92), ("成本", 72), ("采用", 86)],
    },
    {
        "no": "02",
        "label": "运行时",
        "title": "Agent 安全从发布前评测变成运行时边界",
        "thesis": "治理单位不再只是模型，而是身份、权限、网络、日志、审批和回滚。",
        "score": 94,
        "evidence": ["HF incident", "AISI cheating", "Agent Harness"],
        "vars": [("监管", 94), ("采用", 76), ("成本", 64)],
    },
    {
        "no": "03",
        "label": "系统",
        "title": "竞争单位变成模型、Harness、验证器和轨迹",
        "thesis": "最强模型不是单点答案。可复盘的工作流水线，才会改写团队规模和代码产出关系。",
        "score": 90,
        "evidence": ["Hyra", "Cursor Swarm", "Tunix", "MagenticLite"],
        "vars": [("能力", 84), ("采用", 90), ("成本", 68)],
    },
    {
        "no": "04",
        "label": "交付物",
        "title": "入口从聊天框转向 Office、画布和设计台",
        "thesis": "谁离最终交付物最近，谁就更容易拿到上下文、反馈和付费。聊天框只是入口之一。",
        "score": 92,
        "evidence": ["Qwen-Image", "Grok Excel", "Copilot Canvas", "Miora"],
        "vars": [("分发", 92), ("采用", 80), ("能力", 70)],
    },
    {
        "no": "05",
        "label": "数据",
        "title": "下一轮训练数据红利来自真实工作轨迹",
        "thesis": "网页文本告诉模型世界有什么；轨迹数据告诉模型工作怎么做完。",
        "score": 88,
        "evidence": ["workflow data", "Economic Index", "Unslop", "BigMac"],
        "vars": [("供给", 78), ("采用", 84), ("监管", 58)],
    },
    {
        "no": "06",
        "label": "基础设施",
        "title": "成本竞争从 token 单价扩展到工业账本",
        "thesis": "AI 越来越像工业系统，胜负取决于全栈单位任务成本。",
        "score": 96,
        "evidence": ["Gemini Flash", "3.2GW", "AMD + Anthropic", "Nikkei debt"],
        "vars": [("成本", 94), ("供给", 96), ("监管", 70)],
    },
]

VARIABLES = [
    ("能力", 86, "模型成熟后，prompt 噪音开始被削掉。"),
    ("成本", 82, "成本从 token 扩展到吞吐、电力、债务。"),
    ("分发", 78, "Office、画布、设计台成为交付表面。"),
    ("供给", 88, "芯片、电力、园区协议决定 AI 速度。"),
    ("监管", 91, "安全与版权边界进入运行时。"),
    ("组织采用", 84, "Agent 需要任务、权限、检查点和复盘。"),
]

SHIFTS = [
    ("Prompt scaffolding", "Mature agent management", "给成熟模型目标、边界、参考物和复盘机制", "能力 / 成本 / 采用", "常驻上下文是否变短"),
    ("Pre-release eval", "Runtime boundary", "把安全治理搬到身份、权限、日志、审批和回滚", "监管 / 采用", "是否记录工具调用轨迹"),
    ("Model ranking", "Model-system pair", "比较模型和 harness、验证器、memory 的组合能力", "能力 / 采用 / 成本", "采购对象是否变成系统包"),
    ("Chat interface", "Artifact surface", "让 AI 进入 Excel、Outlook、画布、图片和设计台", "分发 / 采用", "交付物是否成为入口"),
    ("Web corpus", "Workflow trajectory", "从内容学习转向过程学习和验收轨迹", "供给 / 采用", "是否沉淀可验证任务轨迹"),
    ("Token price", "Industrial ledger", "从 API 价格表迁移到电力、租赁和债务结构", "成本 / 供给", "单位任务成本是否全栈计量"),
]

G = {
    "paper": "#F0ECE1",
    "ink": "#22241F",
    "muted": "#6A6D60",
    "green": "#4BAA71",
    "orange": "#E78543",
    "violet": "#8A6FCC",
    "blue": "#5E8FD4",
    "gold": "#D6B956",
    "soft": "#E1DCCC",
}

S = {
    "paper": "#0C1528",
    "ink": "#F5F4EF",
    "muted": "#AEB8CC",
    "cobalt": "#3F68D9",
    "violet": "#7C63D5",
    "pink": "#D476B1",
    "gold": "#E9C35F",
    "line": "#344463",
    "panel": "#14213A",
}


def rect(x, y, w, h, fill, stroke=None, sw=0, rx=0):
    attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"', f'fill="{fill}"']
    if stroke:
        attrs += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
    if rx:
        attrs.append(f'rx="{rx}"')
    return "<rect " + " ".join(attrs) + "/>"


def circle(cx, cy, r, fill, stroke=None, sw=0):
    attrs = [f'cx="{cx}"', f'cy="{cy}"', f'r="{r}"', f'fill="{fill}"']
    if stroke:
        attrs += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
    return "<circle " + " ".join(attrs) + "/>"


def ellipse(cx, cy, rx, ry, fill, stroke=None, sw=0):
    attrs = [f'cx="{cx}"', f'cy="{cy}"', f'rx="{rx}"', f'ry="{ry}"', f'fill="{fill}"']
    if stroke:
        attrs += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
    return "<ellipse " + " ".join(attrs) + "/>"


def line(x1, y1, x2, y2, stroke, sw=2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"/>'


def text(x, y, value, fill, size=20, weight=500, anchor="start"):
    return f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'


def wrap(value, limit):
    lines, current, width = [], "", 0.0
    for char in value:
        unit = 0.56 if ord(char) < 128 else 1.0
        if current and width + unit > limit:
            lines.append(current)
            current, width = char, unit
        else:
            current += char
            width += unit
    if current:
        lines.append(current)
    return lines


def multi(x, y, value, fill, size=20, weight=500, limit=28, leading=1.25):
    lines = wrap(value, limit)
    out = [f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}">']
    for idx, item in enumerate(lines):
        dy = 0 if idx == 0 else int(size * leading)
        out.append(f'<tspan x="{x}" dy="{dy}">{escape(item)}</tspan>')
    out.append('</text>')
    return "".join(out)


def svg(w, h, background, body, label):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-label="{escape(label)}">{rect(0, 0, w, h, background)}{body}</svg>\n'


def grid_pattern(x, y, cols, rows, cell, gap, palette, offset=0, frame=True):
    out = []
    if frame:
        out.append(rect(x - 24, y - 24, cols * (cell + gap) - gap + 48, rows * (cell + gap) - gap + 48, G["paper"], G["ink"], 2))
    for row in range(rows):
        for col in range(cols):
            idx = (row * 3 + col * 2 + offset + row * col) % len(palette)
            size = cell - ((row + col + offset) % 3) * 8
            xx = x + col * (cell + gap)
            yy = y + row * (cell + gap)
            out.append(rect(xx, yy, size, size, palette[idx], None, 0, 4))
    return "".join(out)


def space_stars(x, y, w, h):
    coords = [(32, 44, 4), (118, 88, 6), (244, 30, 3), (354, 122, 5), (476, 52, 4), (590, 148, 3), (720, 38, 5), (842, 100, 4), (958, 48, 3)]
    return "".join(circle(x + dx, y + dy, r, S["ink"]) for dx, dy, r in coords if dx < w and dy < h)


def generative_cover():
    body = [
        text(80, 80, "AI WEEKLY", G["ink"], 18, 800),
        text(1520, 80, "SIX CONSTRAINTS", G["muted"], 18, 800, "end"),
        text(80, 190, "当模型更成熟，", G["ink"], 72, 900),
        text(80, 270, "约束开始重排。", G["ink"], 72, 900),
        multi(84, 420, "本周六条趋势：上下文、运行时、系统、交付物、轨迹、工业成本。", G["muted"], 27, 520, 32, 1.35),
        line(80, 620, 930, 620, G["ink"], 3),
        text(80, 690, "RULES", G["ink"], 18, 800),
        text(240, 690, "VARIATION", G["ink"], 18, 800),
        text(460, 690, "FORM", G["ink"], 18, 800),
        line(80, 720, 790, 720, G["ink"], 2),
        grid_pattern(1010, 150, 7, 6, 48, 20, [G["green"], G["orange"], G["violet"], G["blue"], G["gold"]], 2),
        rect(1010, 600, 460, 120, G["soft"], G["ink"], 2),
        text(1040, 650, "agent_value", G["ink"], 24, 800),
        text(1040, 690, "task x success x verification", G["muted"], 18, 600),
    ]
    return svg(1600, 840, G["paper"], "".join(body), "AI weekly cover")


def generative_variables():
    body = [
        text(80, 80, "01 / VARIABLE FIELD", G["ink"], 18, 800),
        multi(80, 170, "六个底层变量，正在一起改变。", G["ink"], 56, 900, 18, 1.05),
        multi(84, 280, "柱高代表本周编辑判断强度。先看哪一个约束变了，再看新闻本身。", G["muted"], 22, 520, 42, 1.35),
        rect(80, 370, 1440, 540, G["paper"], G["ink"], 2),
    ]
    colors = [G["orange"], G["gold"], G["blue"], G["green"], G["violet"], G["green"]]
    col_w = 240
    for idx, ((name, score, desc), color) in enumerate(zip(VARIABLES, colors)):
        x = 80 + idx * col_w
        bar_h = 300 * score / 100
        body += [
            line(x, 370, x, 910, G["soft"], 2) if idx else "",
            rect(x + 34, 820 - bar_h, 170, bar_h, color),
            text(x + 34, 432, f"{idx + 1:02d}", G["muted"], 18, 800),
            text(x + 34, 474, name, G["ink"], 26, 800),
            text(x + 34, 790 - bar_h, str(score), G["ink"], 50, 900),
            multi(x + 34, 860, desc, G["muted"], 15, 520, 13, 1.35),
        ]
    body.append(line(80, 820, 1520, 820, G["ink"], 2))
    return svg(1600, 1020, G["paper"], "".join(body), "AI weekly variable field")


def generative_trends():
    body = [
        text(70, 80, "02 / TREND CELLS", G["ink"], 18, 800),
        multi(70, 170, "六条趋势，不做新闻复述，做约束变化。", G["ink"], 54, 900, 19, 1.05),
        text(74, 286, "每张卡先给规则，再给变异，最后给一个可判断的形态。", G["muted"], 22, 520),
    ]
    card_w, card_h = 468, 530
    colors = [G["orange"], G["violet"], G["green"], G["blue"], G["gold"], G["green"]]
    for idx, (trend, accent) in enumerate(zip(TRENDS, colors)):
        row, col = divmod(idx, 3)
        x = 70 + col * 500
        y = 360 + row * 570
        body += [
            rect(x, y, card_w, card_h, G["paper"], G["ink"], 2),
            grid_pattern(x + 34, y + 34, 3, 2, 28, 12, [accent, G["green"], G["violet"], G["gold"]], idx, frame=False),
            text(x + 210, y + 58, f"TREND {trend['no']}", G["muted"], 14, 800),
            text(x + 210, y + 96, trend["label"], G["ink"], 24, 800),
            multi(x + 24, y + 204, trend["title"], G["ink"], 23, 850, 17, 1.2),
            multi(x + 24, y + 332, trend["thesis"], G["muted"], 16, 520, 25, 1.4),
            text(x + 24, y + 456, "SIGNAL", G["muted"], 14, 800),
        ]
        for j, (name, score) in enumerate(trend["vars"]):
            yy = y + 472 + j * 16
            body += [rect(x + 94, yy, 150 * score / 100, 8, accent), text(x + 24, yy + 8, name, G["muted"], 12, 700)]
        body.append(text(x + 274, y + 492, trend["evidence"][0], G["ink"], 11, 700))
    return svg(1600, 1530, G["paper"], "".join(body), "AI weekly trend cells")


def generative_matrix():
    body = [
        text(70, 80, "03 / MIGRATION MATRIX", G["ink"], 18, 800),
        multi(70, 170, "从旧问题到新判断，行业正在换一套坐标系。", G["ink"], 52, 900, 20, 1.05),
        text(74, 288, "六条迁移压成一张可扫读的高密度台账。", G["muted"], 22, 520),
    ]
    x0, y0 = 70, 350
    widths = [68, 236, 256, 470, 210, 280]
    headers = ["#", "旧问题", "新判断", "迁移含义", "变量", "下周观察"]
    total = sum(widths)
    row_h = 94
    cx = x0
    for header, width in zip(headers, widths):
        body += [rect(cx, y0, width, 70, G["ink"]), text(cx + 14, y0 + 44, header, G["paper"], 15, 800)]
        cx += width
    accents = [G["orange"], G["violet"], G["green"], G["blue"], G["gold"], G["green"]]
    for idx, row in enumerate(SHIFTS):
        y = y0 + 70 + idx * row_h
        cx = x0
        values = [f"{idx + 1:02d}", row[0], "→ " + row[1], row[2], row[3], row[4]]
        limits = [3, 17, 19, 31, 14, 19]
        for col, (value, width, limit) in enumerate(zip(values, widths, limits)):
            body.append(rect(cx, y, width, row_h, G["soft"] if idx % 2 else G["paper"], G["ink"], 1))
            if col == 0:
                body += [circle(cx + 34, y + 46, 22, accents[idx]), text(cx + 34, y + 52, value, G["ink"], 16, 900, "middle")]
            else:
                body.append(multi(cx + 14, y + 32, value, G["ink"] if col in (1, 2) else G["muted"], 15 if col != 0 else 16, 750 if col in (1, 2) else 520, limit, 1.2))
            cx += width
    return svg(1600, 1080, G["paper"], "".join(body), "AI weekly migration matrix")


def generative_header():
    body = [
        text(78, 78, "AI WEEKLY", G["ink"], 18, 800),
        multi(78, 190, "把 Agent 当成熟员工管理。", G["ink"], 64, 900, 15, 1.05),
        multi(84, 430, "Opus 5 删掉提示词噪音之后，行业开始重估 prompt、skills、harness、sandbox、review 和 memory 哪些是真基础设施。", G["muted"], 26, 520, 35, 1.35),
        line(84, 650, 890, 650, G["ink"], 3),
        text(84, 720, "CONTEXT", G["ink"], 17, 800),
        text(280, 720, "RUNTIME", G["ink"], 17, 800),
        text(460, 720, "ARTIFACT", G["ink"], 17, 800),
        grid_pattern(1010, 120, 6, 5, 50, 22, [G["green"], G["orange"], G["violet"], G["blue"], G["gold"]], 5),
    ]
    return svg(1600, 840, G["paper"], "".join(body), "AI weekly WeChat header")


def space_cover():
    body = [
        text(80, 80, "AI WEEKLY", S["ink"], 18, 800),
        text(1520, 80, "THE NEXT FRONTIER", S["muted"], 18, 800, "end"),
        multi(80, 190, "前沿，不再只是模型。", S["ink"], 72, 900, 13, 1.05),
        multi(84, 420, "本周六条航线：上下文、运行时、系统、交付物、轨迹、工业成本。", S["muted"], 27, 520, 32, 1.35),
        line(80, 620, 890, 620, S["ink"], 3),
        text(80, 690, "MISSION", S["ink"], 18, 800),
        text(260, 690, "EVIDENCE", S["ink"], 18, 800),
        text(470, 690, "MILESTONE", S["ink"], 18, 800),
        rect(1010, 120, 440, 600, S["panel"], S["line"], 2),
        space_stars(1030, 140, 400, 150),
        line(1040, 370, 1410, 370, S["line"], 2),
        line(1040, 500, 1410, 500, S["line"], 2),
        line(1040, 630, 1410, 630, S["line"], 2),
        circle(1120, 370, 42, S["cobalt"]),
        circle(1270, 500, 58, S["violet"]),
        circle(1370, 630, 30, S["gold"]),
        text(1040, 340, "01", S["muted"], 15, 800),
        text(1040, 470, "02", S["muted"], 15, 800),
        text(1040, 600, "03", S["muted"], 15, 800),
    ]
    return svg(1600, 840, S["paper"], "".join(body), "AI weekly outer space cover")


def space_variables():
    body = [
        text(80, 80, "01 / MISSION MAP", S["ink"], 18, 800),
        multi(80, 170, "六个变量，组成一条前沿航线。", S["ink"], 56, 900, 18, 1.05),
        multi(84, 280, "圆点大小代表本周约束变化强度。它们不是独立星体，而是一组彼此牵引的任务坐标。", S["muted"], 22, 520, 40, 1.35),
        rect(80, 370, 1440, 540, S["panel"], S["line"], 2),
        line(130, 640, 1470, 640, S["line"], 2),
    ]
    colors = [S["cobalt"], S["gold"], S["pink"], S["violet"], S["gold"], S["cobalt"]]
    positions = [150, 385, 610, 835, 1060, 1280]
    for idx, ((name, score, desc), color, x) in enumerate(zip(VARIABLES, colors, positions)):
        r = 24 + score * 0.42
        body += [
            circle(x, 640, r, color),
            text(x, 640 + 6, str(score), S["paper"], 22, 900, "middle"),
            text(x - 62, 520, f"{idx + 1:02d}", S["muted"], 16, 800),
            text(x - 62, 555, name, S["ink"], 24, 800),
            multi(x - 62, 740, desc, S["muted"], 14, 520, 13, 1.35),
        ]
    return svg(1600, 1020, S["paper"], "".join(body), "AI weekly mission map")


def space_trends():
    body = [
        text(70, 80, "02 / MISSION LOG", S["ink"], 18, 800),
        multi(70, 170, "六条趋势，六个正在移动的坐标。", S["ink"], 54, 900, 19, 1.05),
        text(74, 286, "每张卡保留一个信号、一个判断、一个下一站。", S["muted"], 22, 520),
    ]
    card_w, card_h = 468, 530
    colors = [S["cobalt"], S["violet"], S["gold"], S["pink"], S["cobalt"], S["gold"]]
    for idx, (trend, accent) in enumerate(zip(TRENDS, colors)):
        row, col = divmod(idx, 3)
        x = 70 + col * 500
        y = 360 + row * 570
        body += [
            rect(x, y, card_w, card_h, S["panel"], S["line"], 2),
            line(x + 28, y + 102, x + card_w - 28, y + 102, S["line"], 2),
            circle(x + 68, y + 54, 30, accent),
            text(x + 68, y + 61, trend["no"], S["paper"], 16, 900, "middle"),
            text(x + 120, y + 60, trend["label"], S["ink"], 22, 800),
            text(x + card_w - 28, y + 60, str(trend["score"]), S["muted"], 26, 900, "end"),
            multi(x + 28, y + 164, trend["title"], S["ink"], 23, 850, 17, 1.2),
            multi(x + 28, y + 300, trend["thesis"], S["muted"], 16, 520, 25, 1.4),
            line(x + 28, y + 424, x + card_w - 28, y + 424, S["line"], 2),
            text(x + 28, y + 464, "NEXT CHECKPOINT", S["muted"], 13, 800),
            text(x + 28, y + 500, trend["evidence"][0], S["ink"], 16, 700),
        ]
    return svg(1600, 1530, S["paper"], "".join(body), "AI weekly mission log")


def space_matrix():
    body = [
        text(70, 80, "03 / TRAJECTORY MATRIX", S["ink"], 18, 800),
        multi(70, 170, "旧坐标正在失效，新航线需要被记录。", S["ink"], 52, 900, 20, 1.05),
        text(74, 288, "把六条迁移压成任务日志：从哪里出发，驶向哪里，下一站看什么。", S["muted"], 22, 520),
    ]
    x0, y0 = 70, 350
    widths = [68, 236, 256, 470, 210, 280]
    headers = ["#", "旧坐标", "新航线", "为什么移动", "变量", "下一站"]
    total = sum(widths)
    row_h = 94
    cx = x0
    for header, width in zip(headers, widths):
        body += [rect(cx, y0, width, 70, S["panel"]), text(cx + 14, y0 + 44, header, S["ink"], 15, 800)]
        cx += width
    accents = [S["cobalt"], S["violet"], S["gold"], S["pink"], S["cobalt"], S["gold"]]
    for idx, row in enumerate(SHIFTS):
        y = y0 + 70 + idx * row_h
        cx = x0
        values = [f"{idx + 1:02d}", row[0], row[1], row[2], row[3], row[4]]
        limits = [3, 17, 19, 31, 14, 19]
        for col, (value, width, limit) in enumerate(zip(values, widths, limits)):
            body.append(rect(cx, y, width, row_h, S["panel"] if idx % 2 else S["paper"], S["line"], 1))
            if col == 0:
                body += [circle(cx + 34, y + 46, 22, accents[idx]), text(cx + 34, y + 52, value, S["paper"], 16, 900, "middle")]
            else:
                body.append(multi(cx + 14, y + 32, value, S["ink"] if col in (1, 2) else S["muted"], 15, 750 if col in (1, 2) else 520, limit, 1.2))
            cx += width
    return svg(1600, 1080, S["paper"], "".join(body), "AI weekly trajectory matrix")


def space_header():
    body = [
        text(78, 78, "AI WEEKLY", S["ink"], 18, 800),
        multi(78, 190, "前沿，不再只是模型。", S["ink"], 64, 900, 15, 1.05),
        multi(84, 430, "当模型更成熟，竞争开始沿着上下文、运行时、交付物、轨迹和工业成本向外扩张。", S["muted"], 26, 520, 35, 1.35),
        line(84, 650, 890, 650, S["ink"], 3),
        text(84, 720, "MISSION", S["ink"], 17, 800),
        text(280, 720, "RUNTIME", S["ink"], 17, 800),
        text(460, 720, "FRONTIER", S["ink"], 17, 800),
        rect(1010, 120, 440, 600, S["panel"], S["line"], 2),
        space_stars(1030, 140, 400, 120),
        line(1040, 360, 1410, 360, S["line"], 2),
        line(1040, 500, 1410, 500, S["line"], 2),
        line(1040, 640, 1410, 640, S["line"], 2),
        circle(1120, 360, 42, S["cobalt"]),
        circle(1270, 500, 58, S["violet"]),
        circle(1370, 640, 30, S["gold"]),
        text(1040, 330, "01", S["muted"], 15, 800),
        text(1040, 470, "02", S["muted"], 15, 800),
        text(1040, 610, "03", S["muted"], 15, 800),
    ]
    return svg(1600, 840, S["paper"], "".join(body), "AI weekly outer space header")


def write_bundle(out, style, files, description):
    out.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (out / name).write_text(content, encoding="utf-8")
    labels = {
        "01-cover.svg": "01 / 封面",
        "02-variable-map.svg": "02 / 底层变量",
        "03-trend-cards.svg": "03 / 六条趋势",
        "04-migration-matrix.svg": "04 / 行业迁移",
        "05-wechat-header.svg": "05 / 公众号头图",
    }
    html_rows = "\n".join(
        f'<section><h2>{escape(labels.get(name, name))}</h2><img src="{escape(name)}" alt="{escape(labels.get(name, name))}"></section>'
        for name in files
    )
    html = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(style)} · AI 周报</title><style>body{{margin:0;background:{G["paper"] if style == "Generative Art" else S["paper"]};color:{G["ink"] if style == "Generative Art" else S["ink"]};font-family:system-ui,sans-serif}}header,section{{padding:28px 5vw;border-bottom:1px solid #687080}}h1{{font-size:clamp(34px,6vw,72px);line-height:1;margin:0 0 14px}}h2{{font-size:24px}}p{{max-width:900px;line-height:1.6;color:{G["muted"] if style == "Generative Art" else S["muted"]}}}img{{display:block;width:100%;height:auto;border:1px solid #687080}}</style></head><body><header><h1>{escape(style)} / AI Weekly</h1><p>{escape(description)}</p></header>{html_rows}</body></html>'''
    (out / "index.html").write_text(html, encoding="utf-8")
    write_document_artifacts(out, style, description)
    readme = f'''# {style} · AI 周报可视化\n\n来源：`/Users/bytedance/Documents/New project/ai-weekly-2026-07-21-to-07-27.md`\n\n本目录用 `{style}` 模板完成本周 AI 周报的同一组信息可视化：\n\n- `01-cover.svg`：飞书文档封面主图\n- `02-variable-map.svg`：六个底层变量\n- `03-trend-cards.svg`：六条趋势卡\n- `04-migration-matrix.svg`：六条行业迁移\n- `05-wechat-header.svg`：公众号头图复用版\n- `index.html`：本地预览\n'''
    readme += "- `feishu-doc.html`：按飞书文档阅读顺序编排的视觉版\n- `feishu-doc.md`：可导入/改写的结构化文档稿\n"
    readme += "- `feishu-doc.xml`：可用 lark-cli 创建飞书文档的 XML 载荷（内嵌 5 个可编辑画板）\n"
    (out / "README.md").write_text(readme, encoding="utf-8")


def write_document_artifacts(out, style, description):
    is_space = style == "Outer Space"
    paper = S["paper"] if is_space else G["paper"]
    ink = S["ink"] if is_space else G["ink"]
    muted = S["muted"] if is_space else G["muted"]
    accent = S["cobalt"] if is_space else G["orange"]
    panel = S["panel"] if is_space else G["soft"]
    headline = "前沿，不再只是模型。" if is_space else "当模型更成熟，约束开始重排。"
    lead = "本周六条航线：上下文、运行时、系统、交付物、轨迹、工业成本。" if is_space else "本周六条趋势：上下文、运行时、系统、交付物、轨迹、工业成本。"
    trend_rows = []
    md_rows = []
    for trend in TRENDS:
        evidence = " · ".join(trend["evidence"][:3])
        trend_rows.append(
            f'<article class="trend"><div class="trend-no">{escape(trend["no"])} / {escape(trend["label"])}</div>'
            f'<h3>{escape(trend["title"])}</h3><p>{escape(trend["thesis"])}</p>'
            f'<div class="evidence">{escape(evidence)}</div></article>'
        )
        md_rows.append(f'### {trend["no"]} / {trend["label"]}\n\n**{trend["title"]}**\n\n{trend["thesis"]}\n\n证据：{evidence}\n')
    trends_html = "".join(trend_rows)
    doc_html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(style)} · 飞书文档版 AI 周报</title>
<style>
:root{{--paper:{paper};--ink:{ink};--muted:{muted};--accent:{accent};--panel:{panel};--line:{S["line"] if is_space else "#B8B3A6"};}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font-family:system-ui,-apple-system,"Noto Sans SC",sans-serif;line-height:1.6}}
.doc{{max-width:1180px;margin:0 auto;padding:38px 28px 80px}} .eyebrow{{font-size:13px;font-weight:800;letter-spacing:.08em;color:var(--muted)}}
h1{{font-size:clamp(42px,7vw,86px);line-height:1.08;max-width:980px;margin:28px 0 20px;letter-spacing:0}}
.lead{{font-size:22px;color:var(--muted);max-width:820px;margin:0 0 34px}} .hero,.visual{{display:block;width:100%;height:auto;border:1px solid var(--line);background:var(--paper)}}
.section{{border-top:1px solid var(--line);padding-top:30px;margin-top:52px}} .section h2{{font-size:28px;margin:0 0 12px}} .section-intro{{color:var(--muted);max-width:820px}}
.quote{{border-left:5px solid var(--accent);padding:12px 0 12px 20px;font-size:24px;font-weight:700;max-width:900px}}
.trend-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:22px}} .trend{{border:1px solid var(--line);padding:22px;background:var(--panel)}}
.trend-no,.evidence{{font-size:12px;font-weight:800;letter-spacing:.06em;color:var(--muted)}} .trend h3{{font-size:22px;line-height:1.25;margin:18px 0 12px}} .trend p{{color:var(--muted);margin:0 0 18px}} .evidence{{border-top:1px solid var(--line);padding-top:12px}}
.closing{{font-size:25px;max-width:930px}} @media(max-width:720px){{.doc{{padding:24px 16px 54px}}.trend-grid{{grid-template-columns:1fr}}.lead{{font-size:19px}}}}
</style></head><body><main class="doc">
<div class="eyebrow">AI WEEKLY / 2026.07.21 — 07.27</div><h1>{escape(headline)}</h1><p class="lead">{escape(lead)}</p>
<img class="hero" src="01-cover.svg" alt="AI 周报封面">
<section class="section"><h2>01 / 本周判断</h2><p class="section-intro">{escape(description)}</p>
<div class="quote">Agent 价值 = 可完成任务的复杂度 × 成功率 × 可验证性 ÷ 上下文、推理、治理与集成成本。</div></section>
<section class="section"><h2>02 / 六个底层变量</h2><p class="section-intro">新闻表面在变，底层变量集中在能力、成本、分发、供给、监管和组织采用。</p><img class="visual" src="02-variable-map.svg" alt="六个底层变量"></section>
<section class="section"><h2>03 / 六条趋势</h2><p class="section-intro">每条趋势先给出约束变化，再给出证据和可复盘的判断。</p><div class="trend-grid">{trends_html}</div><img class="visual" src="03-trend-cards.svg" alt="六条趋势卡" style="margin-top:24px"></section>
<section class="section"><h2>04 / 行业迁移</h2><p class="section-intro">竞争从单个模型向模型系统、交付物表面、真实工作轨迹和工业账本迁移。</p><img class="visual" src="04-migration-matrix.svg" alt="行业迁移矩阵"></section>
<section class="section"><h2>05 / 结论</h2><p class="closing">把 AI 当成熟员工管理：少一点噪音，多一点结构；给目标、资源、边界、验证器和复盘机制。</p><img class="visual" src="05-wechat-header.svg" alt="公众号头图"></section>
</main></body></html>'''
    (out / "feishu-doc.html").write_text(doc_html, encoding="utf-8")
    markdown = f'''# AI 周报｜{headline}

> {lead}

![AI 周报封面](01-cover.svg)

## 01 / 本周判断

{description}

> Agent 价值 = 可完成任务的复杂度 × 成功率 × 可验证性 ÷ 上下文、推理、治理与集成成本。

## 02 / 六个底层变量

新闻表面在变，底层变量集中在能力、成本、分发、供给、监管和组织采用。

![六个底层变量](02-variable-map.svg)

## 03 / 六条趋势

{chr(10).join(md_rows)}
![六条趋势卡](03-trend-cards.svg)

## 04 / 行业迁移

竞争从单个模型向模型系统、交付物表面、真实工作轨迹和工业账本迁移。

![行业迁移矩阵](04-migration-matrix.svg)

## 05 / 结论

把 AI 当成熟员工管理：少一点噪音，多一点结构；给目标、资源、边界、验证器和复盘机制。

![公众号头图](05-wechat-header.svg)
'''
    (out / "feishu-doc.md").write_text(markdown, encoding="utf-8")
    path_prefix = f"@prototypes/{out.name}"
    xml = f'''<title>AI 周报｜2026.07.21—07.27｜{escape(style)}</title>
<h1>{escape(headline)}</h1>
<p>{escape(lead)}</p>
<whiteboard type="svg" path="{path_prefix}/01-cover.svg"></whiteboard>
<h2>01 / 本周判断</h2>
<p>{escape(description)}</p>
<callout emoji="💡" background-color="light-yellow" border-color="yellow"><p>Agent 价值 = 可完成任务的复杂度 × 成功率 × 可验证性 ÷ 上下文、推理、治理与集成成本。</p></callout>
<h2>02 / 六个底层变量</h2>
<p>新闻表面在变，底层变量集中在能力、成本、分发、供给、监管和组织采用。</p>
<whiteboard type="svg" path="{path_prefix}/02-variable-map.svg"></whiteboard>
<h2>03 / 六条趋势</h2>
<p>每条趋势先给出约束变化，再给出证据和可复盘的判断。</p>
<whiteboard type="svg" path="{path_prefix}/03-trend-cards.svg"></whiteboard>
<h2>04 / 行业迁移</h2>
<p>竞争从单个模型向模型系统、交付物表面、真实工作轨迹和工业账本迁移。</p>
<whiteboard type="svg" path="{path_prefix}/04-migration-matrix.svg"></whiteboard>
<h2>05 / 结论</h2>
<p>把 AI 当成熟员工管理：少一点噪音，多一点结构；给目标、资源、边界、验证器和复盘机制。</p>
<whiteboard type="svg" path="{path_prefix}/05-wechat-header.svg"></whiteboard>
'''
    (out / "feishu-doc.xml").write_text(xml, encoding="utf-8")


def main():
    write_bundle(GENERATIVE, "Generative Art", {
        "01-cover.svg": generative_cover(),
        "02-variable-map.svg": generative_variables(),
        "03-trend-cards.svg": generative_trends(),
        "04-migration-matrix.svg": generative_matrix(),
        "05-wechat-header.svg": generative_header(),
    }, "规则先行、变异可见、形态最后：把本周新闻压成一套可复盘的约束系统。")
    write_bundle(SPACE, "Outer Space", {
        "01-cover.svg": space_cover(),
        "02-variable-map.svg": space_variables(),
        "03-trend-cards.svg": space_trends(),
        "04-migration-matrix.svg": space_matrix(),
        "05-wechat-header.svg": space_header(),
    }, "用航线、任务坐标和下一站，把本周 AI 变化读成一场系统级前沿迁移。")
    print(GENERATIVE)
    print(SPACE)


if __name__ == "__main__":
    main()
