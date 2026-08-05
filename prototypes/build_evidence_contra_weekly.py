#!/usr/bin/env python3
"""Build Feishu-native weekly report systems for two personalized templates."""

import json
from html import escape
from pathlib import Path

from build_aesthetics_weekly import TRENDS, VARIABLES, SHIFTS, circle, line, multi, rect, svg, text


ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "feishu-weekly-2026-07-21-to-07-27-evidence-atlas"
CONTRA = ROOT / "feishu-weekly-2026-07-21-to-07-27-contra-judgment-lab"
MATISSE = ROOT / "feishu-weekly-2026-07-21-to-07-27-matisse-red-studio"
CONTRA_HTMLBOX = ROOT / "feishu-weekly-2026-07-21-to-07-27-contra-editorial-htmlbox"

E = {
    "paper": "#F4EFE4",
    "card": "#FFF9EE",
    "ink": "#111318",
    "muted": "#6E665B",
    "line": "#D8CDBC",
    "capability": "#D64028",
    "cost": "#D6A435",
    "distribution": "#2459D6",
    "supply": "#13865E",
    "governance": "#765AD8",
    "adoption": "#0F8AA3",
}

C = {
    "paper": "#FBFAF6",
    "ink": "#070707",
    "soft": "#F0EEE7",
    "muted": "#63615A",
    "lime": "#D7FF3F",
    "orange": "#FF6B2C",
    "blue": "#2F54FF",
    "pink": "#FF8BCB",
    "mint": "#18D68A",
    "violet": "#B69CFF",
}

M = {
    "paper": "#F2E7E2",
    "card": "#F1DCD9",
    "soft": "#CD7E6B",
    "font": "DM Sans, system-ui, sans-serif",
    "capability": "#852254",
    "surface": "#B84030",
    "on_surface": "#F2E7E2",
    "ink": "#23110F",
    "primary": "#86281A",
    "primary_container": "#F1DCD9",
    "secondary": "#338247",
    "secondary_container": "#DDEDE1",
    "tertiary": "#855E26",
    "tertiary_container": "#EFE7DB",
    "hot_pink": "#852254",
    "hot_pink_container": "#F0DAE5",
    "plate_blue": "#385081",
    "plate_blue_container": "#DEE3EC",
    "outline": "#984030",
    "line": "#E8C0B0",
    "panel": "#CD7E6B",
    "muted": "#6B342B",
}

E_VAR_COLORS = [E["capability"], E["cost"], E["distribution"], E["supply"], E["governance"], E["adoption"]]
C_VAR_COLORS = [C["orange"], C["lime"], C["blue"], C["mint"], C["violet"], C["pink"]]
M_VAR_COLORS = [M["hot_pink"], M["tertiary"], M["plate_blue"], M["secondary"], M["primary"], "#D868A0"]


def chip_row(x, y, labels, fill, ink, max_width=620, border=None):
    out = []
    cursor_x, cursor_y = x, y
    for label in labels:
        width = max(100, int(len(label) * 9.2 + 34))
        if cursor_x != x and cursor_x + width > x + max_width:
            cursor_x, cursor_y = x, cursor_y + 38
        out.append(rect(cursor_x, cursor_y, width, 30, fill, border or fill, 1, 8))
        out.append(text(cursor_x + 16, cursor_y + 20, label, ink, 15, 700))
        cursor_x += width + 10
    return "".join(out)


def score_bar(x, y, score, color, width=260, height=16):
    return rect(x, y, max(24, int(width * score / 100)), height, color, None, 0, 2)


def evidence_cover():
    body = [
        text(80, 80, "AI WEEKLY", E["ink"], 18, 800),
        text(1520, 80, "EVIDENCE / JUDGMENT", E["muted"], 16, 800, "end"),
        text(80, 190, "新闻退潮，", E["ink"], 86, 900),
        text(80, 292, "证据留下。", E["ink"], 86, 900),
        multi(84, 430, "本周六条变化，最后都落在能力、成本、分发、供给、监管和采用。", E["muted"], 27, 520, 35),
        line(80, 620, 930, 620, E["ink"], 3),
        text(80, 690, "CAPABILITY", E["ink"], 18, 800),
        text(270, 690, "RUNTIME", E["ink"], 18, 800),
        text(430, 690, "ARTIFACT", E["ink"], 18, 800),
        line(80, 720, 790, 720, E["ink"], 2),
        rect(1000, 126, 500, 446, E["card"], E["ink"], 2),
        rect(1028, 160, 40, 40, E["capability"], None, 0, 4),
        rect(1098, 160, 52, 52, E["cost"], None, 0, 4),
        rect(1178, 160, 44, 44, E["distribution"], None, 0, 4),
        rect(1250, 160, 40, 40, E["supply"], None, 0, 4),
        rect(1320, 160, 52, 52, E["governance"], None, 0, 4),
        rect(1400, 160, 44, 44, E["adoption"], None, 0, 4),
        text(1028, 280, "six variables", E["muted"], 20, 800),
        text(1028, 322, "one judgment layer", E["ink"], 30, 900),
        rect(1028, 388, 444, 132, E["paper"], E["ink"], 2),
        text(1058, 440, "agent_value", E["ink"], 25, 800),
        text(1058, 480, "task x success x verification", E["muted"], 18, 600),
    ]
    return svg(1600, 840, E["paper"], "".join(body), "AI weekly evidence cover")


def evidence_variables():
    body = [
        text(80, 80, "01 / VARIABLE SCOREBOARD", E["ink"], 18, 800),
        text(80, 170, "六个变量，决定新闻的重量。", E["ink"], 56, 900),
        multi(84, 258, "先看哪个约束变了，再看哪一家发布了什么。", E["muted"], 22, 520, 36),
    ]
    for idx, (label, score, thesis) in enumerate(VARIABLES):
        col, row = idx % 3, idx // 3
        x, y = 80 + col * 500, 330 + row * 330
        color = E_VAR_COLORS[idx]
        body.extend([
            rect(x, y, 450, 280, E["card"], E["ink"], 2),
            rect(x, y, 450, 12, color),
            text(x + 28, y + 54, f"0{idx + 1}", E["muted"], 17, 800),
            text(x + 28, y + 96, label, E["ink"], 28, 800),
            text(x + 420, y + 96, str(score), color, 48, 900, "end"),
            multi(x + 28, y + 150, thesis, E["muted"], 18, 520, 31),
            text(x + 28, y + 236, "SIGNAL", E["muted"], 14, 800),
            score_bar(x + 28, y + 252, score, color, 300, 14),
        ])
    return svg(1600, 1020, E["paper"], "".join(body), "AI weekly evidence variables")


def evidence_trends():
    body = [
        text(70, 80, "02 / EVIDENCE CARDS", E["ink"], 18, 800),
        text(70, 170, "六条趋势，不做复述，只保留约束变化。", E["ink"], 52, 900),
        multi(74, 248, "每张卡：一条判断、三条证据、一个可复盘信号。", E["muted"], 21, 520, 40),
    ]
    for idx, trend in enumerate(TRENDS):
        col, row = idx % 2, idx // 2
        x, y = 70 + col * 760, 300 + row * 400
        color = E_VAR_COLORS[idx]
        body.extend([
            rect(x, y, 700, 350, E["card"], E["ink"], 2),
            rect(x, y, 12, 350, color),
            text(x + 38, y + 44, f"TREND {trend['no']} / {trend['label']}", E["muted"], 15, 800),
            text(x + 662, y + 48, str(trend["score"]), color, 40, 900, "end"),
            multi(x + 38, y + 100, trend["title"], E["ink"], 25, 850, 29),
            multi(x + 38, y + 187, trend["thesis"], E["muted"], 18, 520, 35),
            text(x + 38, y + 276, "EVIDENCE", E["muted"], 13, 800),
            chip_row(x + 38, y + 295, trend["evidence"][:3], color, E["ink"], 620, color),
        ])
    return svg(1600, 1530, E["paper"], "".join(body), "AI weekly evidence cards")


def evidence_matrix():
    body = [
        text(60, 82, "03 / MIGRATION MATRIX", E["ink"], 18, 800),
        text(60, 168, "行业迁移：从对象升级，到验证升级。", E["ink"], 50, 900),
        text(64, 232, "新闻真正改变的，是系统采购与交付的单位。", E["muted"], 21, 520),
    ]
    x0, y0 = 60, 300
    cols = [70, 230, 260, 500, 200, 220]
    headers = ["NO", "FROM", "TO", "WHY IT MATTERS", "VARIABLES", "PROOF"]
    cursor = x0
    for width, header in zip(cols, headers):
        body.extend([rect(cursor, y0, width, 60, E["ink"], E["ink"], 1), text(cursor + 14, y0 + 38, header, E["paper"], 15, 800)])
        cursor += width
    for idx, (source, target, why, variables, proof) in enumerate(SHIFTS):
        y = y0 + 60 + idx * 116
        fill = E["card"] if idx % 2 == 0 else "#EEE5D6"
        color = E_VAR_COLORS[idx]
        cursor = x0
        vals = [f"0{idx + 1}", source, target, why, variables, proof]
        for col_idx, (width, value) in enumerate(zip(cols, vals)):
            body.append(rect(cursor, y, width, 116, fill, E["line"], 1))
            if col_idx == 0:
                body.append(circle(cursor + 35, y + 58, 21, color))
                body.append(text(cursor + 35, y + 64, value, E["ink"], 15, 900, "middle"))
            else:
                limit = {1: 20, 2: 22, 3: 39, 4: 15, 5: 17}[col_idx]
                body.append(multi(cursor + 14, y + 40, value, E["ink"] if col_idx < 3 else E["muted"], 16, 700 if col_idx < 3 else 520, limit))
            cursor += width
    return svg(1600, 1080, E["paper"], "".join(body), "AI weekly evidence migration matrix")


def evidence_header():
    body = [
        text(78, 78, "AI WEEKLY", E["ink"], 18, 800),
        text(78, 190, "把 AI 当成熟员工管理。", E["ink"], 64, 900),
        multi(84, 430, "Opus 5 删掉提示词噪音之后，行业开始重估 prompt、skills、harness、sandbox、review 和 memory。", E["muted"], 26, 520, 46),
        line(84, 650, 890, 650, E["ink"], 3),
        text(84, 720, "CONTEXT", E["ink"], 17, 800),
        text(280, 720, "RUNTIME", E["ink"], 17, 800),
        text(460, 720, "ARTIFACT", E["ink"], 17, 800),
        rect(1000, 96, 458, 386, E["card"], E["ink"], 2),
    ]
    for idx, color in enumerate(E_VAR_COLORS):
        body.append(rect(1028 + (idx % 3) * 120, 136 + (idx // 3) * 100, 52, 52, color, None, 0, 4))
    return svg(1600, 840, E["paper"], "".join(body), "AI weekly evidence header")


def contra_cover():
    body = [
        text(80, 80, "AI WEEKLY", C["ink"], 18, 900),
        text(1520, 80, "JUDGMENT IS SCARCE", C["muted"], 15, 900, "end"),
        text(80, 190, "判断比执行", C["ink"], 92, 900),
        text(80, 300, "更稀缺。", C["ink"], 92, 900),
        multi(84, 430, "本周六条变化：模型更强之后，真正需要被设计的是判断、边界、交付物和复盘。", C["muted"], 26, 520, 36),
        line(80, 620, 930, 620, C["ink"], 3),
        text(80, 690, "PROMPT", C["ink"], 17, 900),
        text(260, 690, "HARNESS", C["ink"], 17, 900),
        text(445, 690, "TASTE", C["ink"], 17, 900),
        rect(1010, 120, 470, 440, C["soft"], C["ink"], 2),
        rect(1050, 160, 90, 90, C["lime"], C["ink"], 2),
        rect(1170, 160, 90, 90, C["orange"], C["ink"], 2),
        rect(1290, 160, 90, 90, C["blue"], C["ink"], 2),
        rect(1050, 290, 90, 90, C["mint"], C["ink"], 2),
        rect(1170, 290, 90, 90, C["pink"], C["ink"], 2),
        rect(1290, 290, 90, 90, C["violet"], C["ink"], 2),
        rect(1050, 440, 330, 66, C["ink"], C["ink"], 2, 30),
        text(1215, 482, "TASK / SUCCESS / PROOF", C["paper"], 17, 900, "middle"),
    ]
    return svg(1600, 840, C["paper"], "".join(body), "AI weekly judgment cover")


def contra_variables():
    body = [
        text(80, 80, "01 / WHAT MOVED?", C["ink"], 18, 900),
        text(80, 170, "先打分，再相信。", C["ink"], 62, 900),
        text(84, 258, "六个变量，是本周判断的工作台。", C["muted"], 22, 520),
    ]
    for idx, (label, score, thesis) in enumerate(VARIABLES):
        col, row = idx % 3, idx // 3
        x, y = 80 + col * 500, 330 + row * 330
        color = C_VAR_COLORS[idx]
        body.extend([
            rect(x, y, 450, 280, C["soft"] if idx % 2 else C["paper"], C["ink"], 2),
            rect(x + 26, y + 24, 58, 58, color, C["ink"], 2),
            rect(x + 102, y + 33, 132, 38, C["ink"], C["ink"], 2, 18),
            text(x + 168, y + 59, label, C["paper"], 15, 900, "middle"),
            text(x + 420, y + 66, str(score), C["ink"], 50, 900, "end"),
            multi(x + 28, y + 142, thesis, C["muted"], 19, 550, 30),
            text(x + 28, y + 232, "SIGNAL", C["muted"], 14, 900),
            score_bar(x + 28, y + 250, score, color, 300, 16),
        ])
    return svg(1600, 1020, C["paper"], "".join(body), "AI weekly judgment variables")


def contra_trends():
    body = [
        text(70, 80, "02 / SCORECARDS", C["ink"], 18, 900),
        text(70, 170, "新闻只是材料，判断才是产物。", C["ink"], 52, 900),
        text(74, 248, "每张卡都保留：立场、证据、反问。", C["muted"], 21, 550),
    ]
    for idx, trend in enumerate(TRENDS):
        col, row = idx % 2, idx // 2
        x, y = 70 + col * 760, 300 + row * 400
        color = C_VAR_COLORS[idx]
        fill = C["soft"] if idx % 2 else C["paper"]
        body.extend([
            rect(x, y, 700, 350, fill, C["ink"], 2),
            rect(x + 34, y + 28, 52, 52, color, C["ink"], 2),
            rect(x + 102, y + 35, 148, 38, C["ink"], C["ink"], 2, 18),
            text(x + 176, y + 61, f"{trend['no']} / {trend['label']}", C["paper"], 14, 900, "middle"),
            text(x + 660, y + 64, str(trend["score"]), C["ink"], 48, 900, "end"),
            multi(x + 34, y + 122, trend["title"], C["ink"], 25, 900, 29),
            multi(x + 34, y + 202, trend["thesis"], C["muted"], 18, 550, 35),
            text(x + 34, y + 280, "COUNTERCHECK", C["muted"], 13, 900),
            chip_row(x + 34, y + 298, trend["evidence"][:3], color, C["ink"], 620, C["ink"]),
        ])
    return svg(1600, 1530, C["paper"], "".join(body), "AI weekly judgment scorecards")


def contra_matrix():
    body = [
        text(60, 82, "03 / THE SHIFT", C["ink"], 18, 900),
        text(60, 168, "从“更强”到“更会判断”。", C["ink"], 50, 900),
        text(64, 232, "反方问题：如果这是真的，采购、产品和组织会怎么变？", C["muted"], 21, 550),
    ]
    x0, y0 = 60, 300
    cols = [70, 230, 260, 500, 200, 220]
    headers = ["NO", "OLD UNIT", "NEW UNIT", "JUDGMENT", "TASTE", "TEST"]
    cursor = x0
    for width, header in zip(cols, headers):
        body.extend([rect(cursor, y0, width, 60, C["ink"], C["ink"], 1), text(cursor + 14, y0 + 38, header, C["paper"], 15, 900)])
        cursor += width
    for idx, (source, target, why, variables, proof) in enumerate(SHIFTS):
        y = y0 + 60 + idx * 116
        fill = C["paper"] if idx % 2 == 0 else C["soft"]
        color = C_VAR_COLORS[idx]
        cursor = x0
        vals = [f"0{idx + 1}", source, target, why, variables, proof]
        for col_idx, (width, value) in enumerate(zip(cols, vals)):
            body.append(rect(cursor, y, width, 116, fill, C["ink"], 1))
            if col_idx == 0:
                body.append(circle(cursor + 35, y + 58, 21, color, C["ink"], 2))
                body.append(text(cursor + 35, y + 64, value, C["ink"], 15, 900, "middle"))
            else:
                limit = {1: 20, 2: 22, 3: 39, 4: 15, 5: 17}[col_idx]
                body.append(multi(cursor + 14, y + 40, value, C["ink"] if col_idx < 3 else C["muted"], 16, 750 if col_idx < 3 else 550, limit))
            cursor += width
    return svg(1600, 1080, C["paper"], "".join(body), "AI weekly judgment shift matrix")


def contra_header():
    body = [
        text(78, 78, "AI WEEKLY", C["ink"], 18, 900),
        text(78, 190, "不再问谁最强，", C["ink"], 62, 900),
        text(78, 276, "而要问谁更会判断。", C["ink"], 62, 900),
        multi(84, 430, "模型、harness、交付物和复盘，决定一个 Agent 能不能进入真实工作。", C["muted"], 25, 550, 42),
        line(84, 650, 890, 650, C["ink"], 3),
        text(84, 720, "PROMPT", C["ink"], 17, 900),
        text(280, 720, "HARNESS", C["ink"], 17, 900),
        text(460, 720, "TASTE", C["ink"], 17, 900),
        rect(1000, 96, 458, 386, C["soft"], C["ink"], 2),
    ]
    for idx, color in enumerate(C_VAR_COLORS):
        body.append(rect(1028 + (idx % 3) * 120, 136 + (idx // 3) * 100, 52, 52, color, C["ink"], 2))
    return svg(1600, 840, C["paper"], "".join(body), "AI weekly judgment header")


def matisse_cover():
    body = [
        rect(0, 0, 1600, 840, M["surface"]),
        rect(0, 0, 1600, 24, M["primary"]),
        rect(80, 76, 430, 38, M["plate_blue"], None, 0, 3),
        text(98, 101, "AI WEEKLY / MATISSE RED STUDIO", M["on_surface"], 14, 700),
        text(80, 214, "AI 周报", M["on_surface"], 82, 700),
        text(80, 316, "把新闻变成一间判断工作室。", M["on_surface"], 54, 700),
        multi(84, 430, "六条趋势，六个变量，一张迁移图。不是把新闻装饰得更漂亮，而是让每个判断留下颜色、边界和下一次验证。", M["on_surface"], 25, 540, 30),
        line(84, 650, 920, 650, M["on_surface"], 2),
        text(84, 706, "CAPABILITY", M["on_surface"], 15, 700),
        text(278, 706, "RUNTIME", M["on_surface"], 15, 700),
        text(456, 706, "ARTIFACT", M["on_surface"], 15, 700),
        rect(1040, 94, 420, 500, M["primary"], M["on_surface"], 2, 4),
        rect(1080, 138, 108, 108, M["hot_pink"], M["on_surface"], 2, 2),
        rect(1218, 138, 108, 108, M["secondary"], M["on_surface"], 2, 2),
        rect(1356, 138, 64, 108, M["tertiary"], M["on_surface"], 2, 2),
        rect(1080, 278, 64, 108, M["plate_blue"], M["on_surface"], 2, 2),
        rect(1174, 278, 246, 108, M["on_surface"], M["ink"], 2, 2),
        text(1200, 334, "six variables", M["ink"], 23, 700),
        text(1200, 366, "one judgment layer", M["ink"], 17, 500),
        rect(1080, 420, 340, 100, M["tertiary"], M["on_surface"], 2, 2),
        text(1250, 464, "TASK × SUCCESS × PROOF", M["on_surface"], 18, 700, "middle"),
    ]
    return svg(1600, 840, M["surface"], "".join(body), "Matisse red studio AI weekly cover")


def matisse_variables():
    body = [
        rect(0, 0, 1600, 1020, M["on_surface"]),
        rect(0, 0, 1600, 22, M["surface"]),
        text(80, 82, "01 / VARIABLE STUDIO", M["primary"], 18, 700),
        text(80, 170, "六个变量，六种颜色。", M["ink"], 56, 700),
        multi(84, 258, "颜色不是装饰：它标出本周最需要复核的约束。", M["muted"], 22, 520, 36),
    ]
    fills = [M["surface"], M["primary"], M["secondary"], M["plate_blue"], M["hot_pink"], M["tertiary"]]
    for idx, (label, score, thesis) in enumerate(VARIABLES):
        col, row = idx % 3, idx // 3
        x, y = 80 + col * 500, 330 + row * 330
        color = M_VAR_COLORS[idx]
        fill = fills[idx]
        body.extend([
            rect(x, y, 450, 280, fill, M["ink"], 2, 4),
            rect(x, y, 450, 12, color),
            text(x + 28, y + 54, f"0{idx + 1}", M["on_surface"], 17, 700),
            text(x + 28, y + 98, label, M["on_surface"], 28, 700),
            text(x + 420, y + 98, str(score), M["on_surface"], 48, 700, "end"),
            multi(x + 28, y + 150, thesis, M["on_surface"], 18, 520, 31),
            text(x + 28, y + 236, "SIGNAL", M["on_surface"], 14, 700),
            score_bar(x + 28, y + 252, score, M["on_surface"], 300, 14),
        ])
    return svg(1600, 1020, M["on_surface"], "".join(body), "Matisse red studio variable studio")


def matisse_trends():
    fills = [M["primary_container"], M["secondary_container"], M["plate_blue_container"], M["hot_pink_container"], M["tertiary_container"], M["on_surface"]]
    body = [
        rect(0, 0, 1600, 1530, M["surface"]),
        rect(0, 0, 1600, 22, M["primary"]),
        text(70, 80, "02 / TREND WORKSHOP", M["on_surface"], 18, 700),
        text(70, 170, "六条趋势，六次复盘。", M["on_surface"], 52, 700),
        text(74, 248, "每张卡都保留：立场、证据、反问。", M["on_surface"], 21, 500),
    ]
    for idx, trend in enumerate(TRENDS):
        col, row = idx % 2, idx // 2
        x, y = 70 + col * 760, 300 + row * 400
        color = M_VAR_COLORS[idx]
        fill = fills[idx]
        body.extend([
            rect(x, y, 700, 350, fill, M["ink"], 2, 4),
            rect(x, y, 12, 350, color),
            text(x + 38, y + 44, f"TREND {trend['no']} / {trend['label']}", M["ink"], 15, 700),
            text(x + 662, y + 48, str(trend["score"]), M["ink"], 40, 700, "end"),
            multi(x + 38, y + 100, trend["title"], M["ink"], 25, 850, 29),
            multi(x + 38, y + 187, trend["thesis"], M["muted"], 18, 520, 35),
            text(x + 38, y + 276, "COUNTERCHECK", M["muted"], 13, 700),
            chip_row(x + 38, y + 295, trend["evidence"][:3], color, M["on_surface"], 620, M["ink"]),
        ])
    return svg(1600, 1530, M["surface"], "".join(body), "Matisse red studio trend workshop")


def matisse_matrix():
    body = [
        rect(0, 0, 1600, 1080, M["on_surface"]),
        rect(0, 0, 1600, 22, M["surface"]),
        text(60, 82, "03 / MIGRATION STUDIO", M["primary"], 18, 700),
        text(60, 168, "从对象升级，到判断升级。", M["ink"], 50, 700),
        text(64, 232, "颜色标记变量，表格留下验证问题。", M["muted"], 21, 500),
    ]
    x0, y0 = 60, 300
    cols = [70, 230, 260, 500, 200, 220]
    headers = ["NO", "OLD UNIT", "NEW UNIT", "JUDGMENT", "VARIABLES", "TEST"]
    cursor = x0
    for width, header in zip(cols, headers):
        body.extend([rect(cursor, y0, width, 60, M["primary"], M["primary"], 1, 2), text(cursor + 14, y0 + 38, header, M["on_surface"], 15, 700)])
        cursor += width
    row_fills = [M["primary_container"], M["secondary_container"], M["plate_blue_container"], M["hot_pink_container"], M["tertiary_container"], M["on_surface"]]
    for idx, (source, target, why, variables, proof) in enumerate(SHIFTS):
        y = y0 + 60 + idx * 116
        fill = row_fills[idx]
        color = M_VAR_COLORS[idx]
        cursor = x0
        vals = [f"0{idx + 1}", source, target, why, variables, proof]
        for col_idx, (width, value) in enumerate(zip(cols, vals)):
            body.append(rect(cursor, y, width, 116, fill, M["outline"], 1, 2))
            if col_idx == 0:
                body.append(rect(cursor + 17, y + 39, 36, 36, color, M["ink"], 1, 2))
                body.append(text(cursor + 35, y + 63, value, M["on_surface"], 13, 700, "middle"))
            else:
                limit = {1: 20, 2: 22, 3: 39, 4: 15, 5: 17}[col_idx]
                body.append(multi(cursor + 14, y + 40, value, M["ink"] if col_idx < 3 else M["muted"], 16, 700 if col_idx < 3 else 520, limit))
            cursor += width
    return svg(1600, 1080, M["on_surface"], "".join(body), "Matisse red studio migration matrix")


def matisse_header():
    body = [
        rect(0, 0, 1600, 840, M["surface"]),
        rect(0, 0, 1600, 24, M["primary"]),
        text(78, 78, "AI WEEKLY / MATISSE RED STUDIO", M["on_surface"], 17, 700),
        text(78, 190, "把 AI 当成熟员工管理。", M["on_surface"], 64, 700),
        multi(84, 430, "模型、harness、交付物和复盘，决定一个 Agent 能不能进入真实工作。", M["on_surface"], 25, 550, 30),
        line(84, 650, 890, 650, M["on_surface"], 2),
        text(84, 720, "PROMPT", M["on_surface"], 17, 700),
        text(280, 720, "HARNESS", M["on_surface"], 17, 700),
        text(460, 720, "ARTIFACT", M["on_surface"], 17, 700),
        rect(1000, 96, 458, 386, M["primary"], M["on_surface"], 2, 4),
        rect(1028, 136, 52, 52, M["hot_pink"], M["on_surface"], 2, 2),
        rect(1148, 136, 52, 52, M["secondary"], M["on_surface"], 2, 2),
        rect(1268, 136, 52, 52, M["plate_blue"], M["on_surface"], 2, 2),
        rect(1388, 136, 52, 52, M["tertiary"], M["on_surface"], 2, 2),
    ]
    return svg(1600, 840, M["surface"], "".join(body), "Matisse red studio WeChat header")


def matisse_migration_chart_html():
    rows = []
    for idx, (source, target, why, variables, proof) in enumerate(SHIFTS):
        rows.append({
            "id": idx + 1,
            "source": source,
            "target": target,
            "why": why,
            "variables": variables,
            "proof": proof,
            "score": TRENDS[idx]["score"],
            "color": M_VAR_COLORS[idx],
        })
    payload = json.dumps(rows, ensure_ascii=False)
    return r'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="use-iframe" content="true">
  <meta name="html-box-height-mode" content="auto">
  <meta name="description" content="Matisse Red Studio 风格的 AI 周报迁移矩阵动态可视化。">
  <title>迁移矩阵 / Matisse Red Studio</title>
  <style>
    :root { --surface:#B84030; --on-surface:#F2E7E2; --ink:#23110F; --primary:#86281A; --primary-container:#F1DCD9; --green:#338247; --green-container:#DDEDE1; --gold:#855E26; --gold-container:#EFE7DB; --pink:#852254; --pink-container:#F0DAE5; --blue:#385081; --blue-container:#DEE3EC; --plate:#4A6AAA; --line:#E8C0B0; --panel:#CD7E6B; --muted:#6B342B; --brand:"Space Grotesk", "Avenir Next", system-ui, sans-serif; --plain:"DM Sans", system-ui, sans-serif; }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--surface); color:var(--on-surface); font-family:var(--plain); font-size:15px; line-height:1.55; }
    .wrap { width:100%; max-width:980px; margin:0 auto; padding:26px 28px 38px; }
    .topline { display:flex; justify-content:space-between; gap:24px; align-items:flex-start; border-bottom:2px solid var(--line); padding-bottom:20px; }
    .kicker { display:block; color:var(--on-surface); font:700 11px var(--plain); letter-spacing:.18em; }
    h1 { margin:18px 0 10px; max-width:760px; font:400 clamp(34px,5vw,62px)/1.08 var(--brand); letter-spacing:0; }
    .lede { margin:0; color:var(--on-surface); opacity:.9; font-size:16px; line-height:1.6; max-width:760px; }
    .score { border:2px solid var(--on-surface); background:var(--primary); padding:12px 15px; min-width:112px; text-align:right; }
    .score b { display:block; color:var(--on-surface); font:400 32px/1 var(--brand); }
    .score span { display:block; margin-top:7px; color:var(--line); font:700 11px var(--plain); }
    .filters { display:flex; flex-wrap:wrap; gap:8px; padding:17px 0 14px; border-bottom:1px solid var(--line); }
    .filters button { border:1.5px solid var(--on-surface); background:var(--surface); color:var(--on-surface); border-radius:4px; padding:8px 12px; font:500 12px var(--plain); cursor:pointer; transition:background-color .18s ease,color .18s ease; }
    .filters button.active, .filters button:hover { background:var(--hot); border-color:var(--hot); color:#FFFFFF; }
    #chart { width:100%; height:580px; border:2px solid var(--primary); background:var(--panel); }
    .detail { display:grid; grid-template-columns:64px minmax(0,1fr) 260px; gap:18px; align-items:start; margin-top:20px; border-top:2px solid var(--line); padding:18px 0 0; }
    .detail-no { color:var(--line); font:700 28px/1 var(--brand); }
    .detail h2 { margin:0 0 7px; color:var(--on-surface); font:400 23px/1.3 var(--brand); }
    .detail p { margin:0; color:var(--on-surface); opacity:.9; font-size:15px; line-height:1.6; }
    .detail-side { border-left:2px solid var(--line); padding-left:16px; }
    .detail-side b { display:block; color:var(--line); font:700 11px var(--plain); letter-spacing:.08em; }
    .detail-side span { display:block; color:var(--on-surface); font-size:14px; margin-top:7px; line-height:1.55; }
    #fallback { display:none; border:2px solid var(--primary); background:var(--panel); padding:4px 12px; }
    .fallback-lane { display:grid; grid-template-columns:minmax(0,1fr) 36px minmax(0,1fr) 54px; gap:8px; align-items:center; padding:13px 0; border-bottom:1px solid var(--line); }
    .fallback-lane:last-child { border-bottom:0; }
    .node { border:2px solid var(--on-surface); border-radius:3px; padding:10px 12px; font:500 13px var(--plain); }
    .node.old { background:var(--ink); color:var(--on-surface); }
    .node.new { color:var(--ink); background:var(--primary-container); }
    .arrow { color:var(--line); font-size:22px; font-weight:700; text-align:center; }
    .weight { color:var(--on-surface); font:700 16px var(--brand); text-align:right; }
    @media (max-width:700px) { .topline { display:block; } .score { margin-top:16px; text-align:left; } .detail { grid-template-columns:56px minmax(0,1fr); } .detail-side { grid-column:2; border-left:0; border-top:2px solid var(--line); padding:10px 0 0; } #chart { height:520px; } }
  </style>
</head>
<body>
  <main class="wrap">
    <div class="topline">
      <div><span class="kicker">MIGRATION / MATISSE RED STUDIO</span><h1>从“更强”到“更会判断”。</h1><p class="lede">旧单位 → 新单位：每条线不是替换关系，而是 AI 产品、采购和组织的判断单位正在迁移。</p></div>
      <div class="score"><b>6</b><span>迁移路径</span></div>
    </div>
    <nav class="filters" aria-label="过滤变量"><button class="active" data-filter="all">ALL</button><button data-filter="能力">能力</button><button data-filter="成本">成本</button><button data-filter="分发">分发</button><button data-filter="供给">供给</button><button data-filter="监管">监管</button><button data-filter="采用">采用</button></nav>
    <div id="chart" aria-label="AI 周报迁移矩阵图表"></div>
    <div id="fallback"></div>
    <section class="detail" aria-live="polite"><div class="detail-no" id="detail-no">01</div><div><h2 id="detail-title">Prompt scaffolding → Mature agent management</h2><p id="detail-why">给成熟模型目标、边界、参考物和复盘机制</p></div><div class="detail-side"><b>TEST / 反问</b><span id="detail-proof">常驻上下文是否变短</span></div></section>
  </main>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js" onerror="window.__echartsFailed=true"></script>
  <script>
    const DATA = __PAYLOAD__;
    const chartEl = document.getElementById('chart');
    const fallbackEl = document.getElementById('fallback');
    const detail = { no:document.getElementById('detail-no'), title:document.getElementById('detail-title'), why:document.getElementById('detail-why'), proof:document.getElementById('detail-proof') };
    let activeFilter = 'all';
    let chartInstance = null;
    function setDetail(item) { detail.no.textContent = String(item.id).padStart(2,'0'); detail.title.textContent = item.source + ' → ' + item.target; detail.why.textContent = item.why; detail.proof.textContent = item.proof + ' / ' + item.variables; }
    function renderFallback() {
      chartEl.style.display = 'none'; fallbackEl.style.display = 'block';
      fallbackEl.innerHTML = DATA.filter(item => activeFilter === 'all' || item.variables.includes(activeFilter)).map(item => '<div class="fallback-lane"><div class="node old">'+item.source+'</div><div class="arrow">→</div><div class="node new" style="border-color:'+item.color+'">'+item.target+'</div><div class="weight">'+item.score+'</div></div>').join('');
    }
    function renderChart() {
      if (typeof echarts === 'undefined' || window.__echartsFailed) { renderFallback(); return; }
      chartEl.style.display = 'block'; fallbackEl.style.display = 'none';
      const selected = DATA.filter(item => activeFilter === 'all' || item.variables.includes(activeFilter));
      const nodes = [];
      const links = [];
      const chartWidth = Math.max(320, chartEl.clientWidth || 820);
      const narrow = chartWidth < 640;
      const oldWidth = narrow ? 144 : 244;
      const newWidth = narrow ? 154 : 264;
      const labelSize = narrow ? 11 : 14;
      const leftX = narrow ? oldWidth / 2 + 8 : chartWidth * 0.24;
      const rightX = narrow ? chartWidth * 0.56 : chartWidth * 0.76;
      const rowStep = narrow ? 104 : (selected.length > 4 ? 78 : 100);
      const startY = narrow ? 54 : (selected.length > 4 ? 58 : 72);
      chartEl.style.height = narrow ? Math.max(500, startY + selected.length * rowStep + 26) + 'px' : '580px';
      const labelFormatter = ({ name }) => {
        if (!narrow || !name.includes(' ')) return name;
        const words = name.split(' ');
        const pivot = Math.ceil(words.length / 2);
        return words.slice(0, pivot).join(' ') + '\n' + words.slice(pivot).join(' ');
      };
      selected.forEach((item, index) => {
        const y = startY + index * rowStep;
        nodes.push({ id:'old-'+item.id, name:item.source, x:leftX, y, item, symbol:'rect', symbolSize:[oldWidth, narrow ? 52 : 54], itemStyle:{ color:'#23110F', borderColor:'#F2E7E2', borderWidth:1 }, label:{ formatter:labelFormatter, color:'#F2E7E2', fontFamily:'Space Grotesk, Arial, sans-serif', fontSize:labelSize, fontWeight:500 } });
        nodes.push({ id:'new-'+item.id, name:item.target, x:rightX, y, item, symbol:'rect', symbolSize:[newWidth, narrow ? 52 : 54], itemStyle:{ color:'#F1DCD9', borderColor:item.color, borderWidth:3 }, label:{ formatter:labelFormatter, color:'#23110F', fontFamily:'Space Grotesk, Arial, sans-serif', fontSize:labelSize, fontWeight:500 } });
        links.push({ source:'old-'+item.id, target:'new-'+item.id, value:item.score, lineStyle:{ color:item.color, width:2 + item.score / 34, curveness:0.13, opacity:0.95 } });
      });
      chartInstance = echarts.getInstanceByDom(chartEl) || echarts.init(chartEl, null, { renderer:'svg' });
      chartInstance.setOption({ animationDuration:650, animationEasing:'cubicOut', tooltip:{ trigger:'item', backgroundColor:'#86281A', borderColor:'#E8C0B0', textStyle:{ color:'#F2E7E2', fontFamily:'DM Sans, system-ui, sans-serif' }, formatter:params => { const item=params.data && params.data.item; return item ? '<b>'+item.source+' → '+item.target+'</b><br/>score '+item.score+'<br/>'+item.why : ''; } }, series:[{ type:'graph', layout:'none', roam:false, data:nodes, links, coordinateSystem:null, edgeSymbol:['none','arrow'], edgeSymbolSize:8, emphasis:{ focus:'adjacency', lineStyle:{ width:7 } }, label:{ show:true, position:'inside' }, lineStyle:{ opacity:0.95 } }] }, true);
      chartInstance.off('click'); chartInstance.on('click', params => { if (params.data && params.data.item) setDetail(params.data.item); });
      if (selected.length) setDetail(selected[0]);
    }
    window.addEventListener('resize', () => { if (chartInstance) chartInstance.resize(); });
    document.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click', () => { document.querySelectorAll('[data-filter]').forEach(node => node.classList.remove('active')); button.classList.add('active'); activeFilter=button.dataset.filter; renderChart(); }));
    let attempts = 0; (function boot(){ if (typeof echarts !== 'undefined' || window.__echartsFailed || attempts++ > 30) renderChart(); else setTimeout(boot,150); })();
  </script>
</body>
</html>'''.replace('__PAYLOAD__', payload)


HTMLBOX_FRAME_CSS = r'''
  :root { --paper:#FBFAF6; --ink:#070707; --soft:#F0EEE7; --muted:#63615A; --line:#D8D2C7; --orange:#FF6B2C; --lime:#D7FF3F; --blue:#2F54FF; --pink:#FF8BCB; --mint:#18D68A; --violet:#B69CFF; --sans:system-ui,-apple-system,"Noto Sans SC",sans-serif; --serif:"et-book", "Songti SC", "Noto Serif CJK SC", Georgia, serif; --mono:Menlo,Consolas,"SF Mono",monospace; }
  * { box-sizing:border-box; }
  html, body { margin:0; min-height:100%; }
  body { background:var(--paper); color:var(--ink); font-family:var(--serif); }
  .frame { position:relative; width:100%; aspect-ratio:16 / 9; overflow:hidden; background:var(--paper); border:1px solid var(--ink); padding:24px 28px; display:flex; flex-direction:column; }
  .frame-meta { color:var(--blue); font:700 11px var(--mono); letter-spacing:0; }
  .frame h1 { margin:14px 0 8px; font:700 clamp(28px,4.5vw,64px)/1.06 var(--serif); letter-spacing:0; }
  .frame h2 { margin:0; font:700 clamp(15px,2vw,25px)/1.2 var(--serif); }
  .lede { margin:0; max-width:720px; color:var(--muted); font-size:clamp(12px,1.35vw,18px); line-height:1.55; }
  .rule { height:1px; margin:14px 0; background:var(--line); flex:0 0 auto; }
  .tag { display:inline-flex; align-items:center; padding:5px 8px; border:1px solid var(--ink); border-radius:4px; font:700 10px var(--mono); }
  .chip { display:inline-flex; align-items:center; min-height:24px; padding:4px 8px; border:1px solid currentColor; border-radius:4px; font:700 10px var(--sans); white-space:nowrap; }
  .cover-grid { display:grid; grid-template-columns:minmax(0,1.25fr) minmax(220px,.75fr); gap:28px; align-items:center; flex:1; min-height:0; }
  .cover-copy { min-width:0; }
  .cover-copy h1 { max-width:720px; }
  .cover-copy .lede { max-width:620px; }
  .cover-chips { display:flex; flex-wrap:wrap; gap:8px; margin-top:20px; }
  .cover-mark { height:100%; max-height:330px; min-height:190px; border:2px solid var(--ink); background:var(--soft); padding:18px; display:grid; grid-template-columns:1fr 1fr; gap:10px; align-content:center; }
  .cover-mark .mark-title { grid-column:1 / -1; font:700 clamp(20px,3vw,42px)/1 var(--sans); }
  .swatches { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
  .swatches i { display:block; aspect-ratio:1; background:var(--c); border:1px solid var(--ink); }
  .formula { align-self:end; padding:12px; border:1px solid var(--ink); background:var(--ink); color:var(--paper); font:700 clamp(10px,1.2vw,15px) var(--mono); }
  .frame-foot { display:flex; justify-content:space-between; gap:16px; color:var(--muted); font:10px var(--mono); }
  .section-head { flex:0 0 auto; }
  .section-head h1 { font-size:clamp(24px,3.4vw,48px); margin-top:10px; }
  .section-head .lede { max-width:720px; }
  .variable-grid, .trend-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; flex:1; min-height:0; margin-top:16px; }
  .variable-card { min-width:0; border:1px solid var(--ink); border-top:5px solid var(--accent); background:var(--card); padding:14px; display:flex; flex-direction:column; justify-content:space-between; }
  .variable-card .card-top { display:flex; justify-content:space-between; gap:8px; align-items:flex-start; }
  .variable-card .num { color:var(--muted); font:700 10px var(--mono); }
  .variable-card .score { color:var(--accent); font:700 clamp(24px,3vw,46px)/1 var(--sans); }
  .variable-card h2 { margin-top:8px; font-size:clamp(16px,2vw,27px); }
  .variable-card p { margin:8px 0 0; color:var(--muted); font-size:clamp(11px,1.15vw,15px); line-height:1.45; }
  .meter { height:7px; margin-top:12px; background:var(--line); }
  .meter i { display:block; height:100%; width:var(--score); background:var(--accent); }
  .trends-frame { background:var(--soft); }
  .trend-grid { grid-template-columns:repeat(2,minmax(0,1fr)); grid-template-rows:repeat(3,minmax(0,1fr)); }
  .trend-card { min-width:0; border:1px solid var(--ink); border-left:7px solid var(--accent); background:var(--card); padding:12px 14px; display:grid; grid-template-rows:auto auto 1fr auto; gap:5px; }
  .trend-card .card-top { display:flex; justify-content:space-between; gap:8px; color:var(--muted); font:700 10px var(--mono); }
  .trend-card .score { color:var(--ink); font:700 24px/1 var(--sans); }
  .trend-card h2 { font-size:clamp(13px,1.45vw,19px); }
  .trend-card p { margin:0; color:var(--muted); font-size:clamp(10px,1.05vw,14px); line-height:1.4; }
  .evidence { display:flex; flex-wrap:wrap; gap:6px; }
  .matrix-frame { padding-bottom:18px; }
  .matrix-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); grid-template-rows:repeat(2,minmax(0,1fr)); gap:12px; flex:1; min-height:0; margin-top:16px; }
  .matrix-card { min-width:0; border:1px solid var(--ink); border-top:6px solid var(--accent); padding:13px; display:grid; grid-template-columns:44px minmax(0,1fr); gap:10px; background:var(--card); }
  .matrix-card .num { color:var(--accent); font:700 25px/1 var(--mono); }
  .matrix-card .from, .matrix-card .to { font:700 clamp(12px,1.35vw,17px)/1.2 var(--sans); }
  .matrix-card .to { color:var(--accent); }
  .matrix-card p { grid-column:2; margin:3px 0 0; color:var(--muted); font-size:clamp(10px,1vw,13px); line-height:1.35; }
  .matrix-card small { grid-column:2; color:var(--ink); font:700 9px var(--mono); }
  .header-frame { background:var(--ink); color:var(--paper); }
  .header-frame .frame-meta, .header-frame .lede { color:var(--paper); }
  .header-frame h1 { max-width:780px; }
  .header-mark { height:100%; max-height:300px; border:1px solid var(--paper); background:var(--soft); padding:16px; display:grid; grid-template-columns:repeat(4,1fr); gap:10px; align-content:center; }
  .header-mark i { display:block; aspect-ratio:1; background:var(--c); border:1px solid var(--ink); }
  @media (max-width:720px) { .frame { padding:14px 16px; } .cover-grid { grid-template-columns:minmax(0,1fr) minmax(120px,.6fr); gap:12px; } .cover-mark { padding:10px; gap:6px; } .cover-mark .mark-title { font-size:18px; } .variable-grid { gap:6px; margin-top:8px; } .variable-card { padding:8px; border-top-width:3px; } .variable-card p { font-size:9px; } .trend-grid { gap:6px; margin-top:8px; } .trend-card { padding:7px 8px; border-left-width:4px; } .trend-card h2 { font-size:11px; } .trend-card p { font-size:8px; } .chip { min-height:18px; padding:2px 5px; font-size:8px; } .matrix-grid { gap:6px; margin-top:8px; } .matrix-card { padding:7px; grid-template-columns:22px minmax(0,1fr); gap:5px; border-top-width:3px; } .matrix-card .num { font-size:14px; } .matrix-card .from, .matrix-card .to { font-size:9px; } .matrix-card p { font-size:7px; } .matrix-card small { font-size:6px; } .frame-foot { font-size:7px; } }
'''


def htmlbox_asset(title, kicker, body, extra_css=""):
    return ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            '<meta name="use-iframe" content="true"><meta name="html-box-height-mode" content="auto">'
            f'<title>{escape(title)}</title><style>{HTMLBOX_FRAME_CSS}{extra_css}</style></head><body>{body}</body></html>')


def contra_htmlbox_cover():
    swatches = "".join(f'<i style="--c:{color}"></i>' for color in C_VAR_COLORS)
    body = f'''<main class="frame"><div class="frame-meta">{escape("AI WEEKLY / 2026.07.21 — 07.27")}</div><div class="cover-grid"><div class="cover-copy"><span class="tag">JUDGMENT LAB / EDITORIAL SYSTEM</span><h1>判断比执行更稀缺。</h1><p class="lede">本周六条变化：模型更强之后，真正需要被设计的是判断、边界、交付物和复盘。</p><div class="cover-chips"><span class="chip" style="color:var(--orange)">PROMPT</span><span class="chip" style="color:var(--blue)">HARNESS</span><span class="chip" style="color:var(--mint)">ARTIFACT</span><span class="chip" style="color:var(--violet)">TASTE</span></div></div><aside class="cover-mark"><div class="mark-title">THE<br>JUDGMENT<br>UNIT</div><div class="swatches">{swatches}</div><div class="formula">TASK × SUCCESS × PROOF</div></aside></div><div class="rule"></div><div class="frame-foot"><span>CONTRA JUDGMENT LAB</span><span>NEWS → SIGNAL → DECISION</span></div></main>'''
    return htmlbox_asset("AI 周报 / Contra Editorial HTMLBox", "AI WEEKLY", body)


def contra_htmlbox_variables():
    cards = []
    for idx, (label, score, thesis) in enumerate(VARIABLES):
        cards.append(f'''<article class="variable-card" style="--accent:{C_VAR_COLORS[idx]};--card:{C["soft"] if idx % 2 else C["paper"]};--score:{score}%"><div class="card-top"><span class="num">0{idx + 1} / VARIABLE</span><span class="score">{score}</span></div><h2>{escape(label)}</h2><p>{escape(thesis)}</p><div class="meter"><i></i></div></article>''')
    body = f'''<main class="frame"><div class="section-head"><div class="frame-meta">01 / VARIABLE SCOREBOARD</div><h1>六个变量，决定新闻的重量。</h1><p class="lede">先看哪个约束变了，再看哪一家发布了什么。</p></div><div class="variable-grid">{"".join(cards)}</div><div class="rule"></div><div class="frame-foot"><span>CONSTRAINTS FIRST</span><span>SCORE / 100</span></div></main>'''
    return htmlbox_asset("AI 周报 / 六变量", "VARIABLE SCOREBOARD", body)


def contra_htmlbox_trends():
    cards = []
    for idx, trend in enumerate(TRENDS):
        evidence = "".join(f'<span class="chip" style="color:{C_VAR_COLORS[idx]}">{escape(item)}</span>' for item in trend["evidence"][:3])
        cards.append(f'''<article class="trend-card" style="--accent:{C_VAR_COLORS[idx]};--card:{C["paper"] if idx % 2 == 0 else C["soft"]}"><div class="card-top"><span>TREND {trend["no"]} / {escape(trend["label"])}</span><span class="score">{trend["score"]}</span></div><h2>{escape(trend["title"])}</h2><p>{escape(trend["thesis"])}</p><div class="evidence">{evidence}</div></article>''')
    body = f'''<main class="frame trends-frame"><div class="section-head"><div class="frame-meta">02 / SCORECARDS</div><h1>新闻只是材料，判断才是产物。</h1><p class="lede">每张卡都保留：立场、证据、反问。</p></div><div class="trend-grid">{"".join(cards)}</div></main>'''
    return htmlbox_asset("AI 周报 / 六条趋势", "SCORECARDS", body)


def contra_htmlbox_matrix():
    cards = []
    for idx, (source, target, why, variables, proof) in enumerate(SHIFTS):
        cards.append(f'''<article class="matrix-card" style="--accent:{C_VAR_COLORS[idx]};--card:{C["paper"] if idx % 2 == 0 else C["soft"]}"><div class="num">0{idx + 1}</div><div><div class="from">{escape(source)}</div><div class="to">→ {escape(target)}</div></div><p>{escape(why)}</p><small>{escape(variables)} · TEST {escape(proof)}</small></article>''')
    body = f'''<main class="frame matrix-frame"><div class="section-head"><div class="frame-meta">03 / MIGRATION MATRIX</div><h1>从“更强”到“更会判断”。</h1><p class="lede">每条迁移都问一个问题：采购、产品和组织的判断单位，究竟变了什么？</p></div><div class="matrix-grid">{"".join(cards)}</div></main>'''
    return htmlbox_asset("AI 周报 / 迁移矩阵", "MIGRATION MATRIX", body)


def contra_htmlbox_header():
    swatches = "".join(f'<i style="--c:{color}"></i>' for color in [C["orange"], C["lime"], C["blue"], C["mint"], C["violet"], C["pink"]])
    body = f'''<main class="frame header-frame"><div class="frame-meta">AI WEEKLY / WECHAT HEADER</div><div class="cover-grid"><div class="cover-copy"><h1>不再问谁最强，<br>而要问谁更会判断。</h1><p class="lede">模型、harness、交付物和复盘，决定一个 Agent 能不能进入真实工作。</p><div class="cover-chips"><span class="chip" style="color:var(--orange)">CONTEXT</span><span class="chip" style="color:var(--blue)">RUNTIME</span><span class="chip" style="color:var(--pink)">ARTIFACT</span></div></div><aside class="header-mark">{swatches}</aside></div><div class="rule"></div><div class="frame-foot"><span>AI WEEKLY / 2026.07.21 — 07.27</span><span>JUDGMENT OVER HYPE</span></div></main>'''
    return htmlbox_asset("AI 周报 / 公众号头图", "WECHAT HEADER", body)


def contra_editorial_migration_htmlbox():
    rows = []
    for idx, (source, target, why, variables, proof) in enumerate(SHIFTS):
        rows.append({"id":idx + 1, "source":source, "target":target, "why":why, "variables":variables, "proof":proof, "score":TRENDS[idx]["score"], "color":C_VAR_COLORS[idx]})
    payload = json.dumps(rows, ensure_ascii=False)
    return r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="use-iframe" content="true"><meta name="html-box-height-mode" content="auto"><title>AI 周报 / 迁移矩阵</title><style>''' + HTMLBOX_FRAME_CSS + r'''
    .migration-frame { padding-bottom:18px; }
    .migration-tools { display:flex; flex-wrap:wrap; gap:6px; margin-top:10px; flex:0 0 auto; }
    .migration-tools button { border:1px solid var(--ink); background:var(--paper); color:var(--ink); border-radius:4px; padding:5px 9px; font:700 10px var(--mono); cursor:pointer; }
    .migration-tools button.active, .migration-tools button:hover { background:var(--ink); color:var(--paper); }
    #chart { width:100%; min-height:0; flex:1 1 auto; margin-top:8px; border-top:1px solid var(--line); border-bottom:1px solid var(--line); }
    .detail { display:grid; grid-template-columns:50px minmax(0,1fr) 230px; gap:12px; align-items:start; padding-top:9px; flex:0 0 auto; }
    .detail-no { color:var(--blue); font:700 22px/1 var(--mono); }
    .detail h2 { margin:0; font:700 clamp(12px,1.5vw,18px)/1.25 var(--serif); }
    .detail p { margin:3px 0 0; color:var(--muted); font-size:clamp(9px,1vw,12px); line-height:1.35; }
    .detail-side { border-left:1px solid var(--ink); padding-left:10px; }
    .detail-side b { display:block; color:var(--blue); font:700 9px var(--mono); }
    .detail-side span { display:block; color:var(--muted); font-size:clamp(8px,1vw,11px); line-height:1.3; margin-top:3px; }
    @media (max-width:720px) { .migration-tools button { padding:4px 6px; font-size:8px; } .detail { grid-template-columns:28px minmax(0,1fr) 92px; gap:6px; } .detail-no { font-size:14px; } .detail h2 { font-size:9px; } .detail p, .detail-side span { font-size:7px; } .detail-side { padding-left:5px; } .detail-side b { font-size:7px; } }
  </style></head><body><main class="frame migration-frame"><div class="section-head"><div class="frame-meta">04 / MIGRATION MATRIX / HTMLBOX ONLY</div><h1>从“更强”到“更会判断”。</h1><p class="lede">每条线不是替换关系，而是 AI 产品、采购和组织的判断单位正在迁移。</p></div><nav class="migration-tools" aria-label="过滤变量"><button class="active" data-filter="all">ALL</button><button data-filter="能力">能力</button><button data-filter="成本">成本</button><button data-filter="分发">分发</button><button data-filter="供给">供给</button><button data-filter="监管">监管</button><button data-filter="采用">采用</button></nav><div id="chart" aria-label="AI 周报迁移矩阵动态关系图"></div><section class="detail" aria-live="polite"><div class="detail-no" id="detail-no">01</div><div><h2 id="detail-title">Prompt scaffolding → Mature agent management</h2><p id="detail-why">给成熟模型目标、边界、参考物和复盘机制</p></div><div class="detail-side"><b>TEST / 反问</b><span id="detail-proof">常驻上下文是否变短</span></div></section></main><script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js" onerror="window.__echartsFailed=true"></script><script>
      const DATA = __PAYLOAD__;
      const chartEl = document.getElementById('chart');
      const detail = { no:document.getElementById('detail-no'), title:document.getElementById('detail-title'), why:document.getElementById('detail-why'), proof:document.getElementById('detail-proof') };
      let activeFilter = 'all';
      let chartInstance = null;
      function setDetail(item) { detail.no.textContent=String(item.id).padStart(2,'0'); detail.title.textContent=item.source+' → '+item.target; detail.why.textContent=item.why; detail.proof.textContent=item.proof+' / '+item.variables; }
      function renderChart() {
        if (typeof echarts === 'undefined' || window.__echartsFailed) return;
        const selected = DATA.filter(item => activeFilter === 'all' || item.variables.includes(activeFilter));
        const width = Math.max(320, chartEl.clientWidth || 800);
        const height = Math.max(60, chartEl.clientHeight || 300);
        const narrow = width < 640;
        const oldWidth = narrow ? 92 : 180;
        const newWidth = narrow ? 104 : 210;
        const leftX = narrow ? oldWidth / 2 + 10 : width * .23;
        const rightX = narrow ? width * .56 : width * .77;
        const startY = Math.max(18, height / (selected.length + 1) / 2);
        const rowStep = Math.max(narrow ? 22 : 30, (height - startY * 1.4) / Math.max(1, selected.length));
        const labelSize = narrow ? 8 : 12;
        const labelFormatter = ({ name }) => { if (!narrow || !name.includes(' ')) return name; const words=name.split(' '); const pivot=Math.ceil(words.length/2); return words.slice(0,pivot).join(' ')+'\n'+words.slice(pivot).join(' '); };
        const nodes=[]; const links=[];
        selected.forEach((item,index)=>{ const y=startY+index*rowStep; nodes.push({id:'old-'+item.id,name:item.source,x:leftX,y,item,symbol:'rect',symbolSize:[oldWidth,narrow?20:34],itemStyle:{color:'#070707',borderColor:'#070707',borderWidth:1},label:{formatter:labelFormatter,color:'#FBFAF6',fontFamily:'Georgia, Songti SC, serif',fontSize:labelSize,fontWeight:700}}); nodes.push({id:'new-'+item.id,name:item.target,x:rightX,y,item,symbol:'rect',symbolSize:[newWidth,narrow?20:34],itemStyle:{color:'#F0EEE7',borderColor:item.color,borderWidth:2},label:{formatter:labelFormatter,color:'#070707',fontFamily:'Georgia, Songti SC, serif',fontSize:labelSize,fontWeight:700}}); links.push({source:'old-'+item.id,target:'new-'+item.id,value:item.score,lineStyle:{color:item.color,width:narrow?1.2:1.5+item.score/48,curveness:.16,opacity:.92}}); });
        chartInstance=echarts.getInstanceByDom(chartEl)||echarts.init(chartEl,null,{renderer:'svg'});
        chartInstance.setOption({animationDuration:500,tooltip:{trigger:'item',formatter:p=>{const item=p.data&&p.data.item;return item?'<b>'+item.source+' → '+item.target+'</b><br/>score '+item.score+'<br/>'+item.why:''}},series:[{type:'graph',layout:'none',roam:false,data:nodes,links,coordinateSystem:null,edgeSymbol:['none','arrow'],edgeSymbolSize:7,emphasis:{focus:'adjacency',lineStyle:{width:5}},label:{show:true,position:'inside'},lineStyle:{opacity:.92}}]},true);
        chartInstance.off('click'); chartInstance.on('click',p=>{if(p.data&&p.data.item)setDetail(p.data.item);}); if(selected.length)setDetail(selected[0]);
      }
      window.addEventListener('resize',()=>{if(chartInstance)chartInstance.resize();});
      document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('[data-filter]').forEach(node=>node.classList.remove('active'));button.classList.add('active');activeFilter=button.dataset.filter;renderChart();}));
      let attempts=0;(function boot(){if(typeof echarts!=='undefined'||window.__echartsFailed||attempts++>30)renderChart();else setTimeout(boot,150);})();
  </script></body></html>'''.replace('__PAYLOAD__', payload)


def write_contra_editorial_htmlbox(out):
    out.mkdir(parents=True, exist_ok=True)
    assets = {
        "01-cover.html": contra_htmlbox_cover(),
        "02-variable-map.html": contra_htmlbox_variables(),
        "03-trend-cards.html": contra_htmlbox_trends(),
        "04-migration-matrix.html": contra_editorial_migration_htmlbox(),
        "05-wechat-header.html": contra_htmlbox_header(),
    }
    for name, content in assets.items():
        (out / name).write_text(content, encoding="utf-8")
    labels = {"01-cover.html":"01 / 封面", "02-variable-map.html":"02 / 六变量", "03-trend-cards.html":"03 / 六趋势", "04-migration-matrix.html":"04 / 迁移矩阵", "05-wechat-header.html":"05 / 公众号头图"}
    sections = "".join(f'<section><h2>{labels[name]}</h2><iframe src="{name}" title="{labels[name]}"></iframe></section>' for name in assets)
    index = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Contra Editorial HTMLBox · AI 周报</title><style>:root{{--paper:{C["paper"]};--ink:{C["ink"]};--soft:{C["soft"]};--muted:{C["muted"]};--line:#D8D2C7}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:Georgia,"Songti SC",serif}}header,section{{max-width:1280px;margin:0 auto;padding:30px 5vw;border-bottom:1px solid var(--line)}}header h1{{font-size:clamp(34px,6vw,76px);line-height:1.04;margin:0 0 12px}}header p{{color:var(--muted);max-width:850px;line-height:1.6}}section h2{{font-size:20px;margin:0 0 14px}}iframe{{display:block;width:100%;aspect-ratio:16/9;border:0;background:transparent}}@media(max-width:720px){{header,section{{padding:22px 16px}}}}</style></head><body><header><h1>Contra Judgment Lab / Editorial HTMLBox</h1><p>参考 Kimi 的研究型阅读节奏，使用 Contra Judgment Lab 配色；每个 section 都是独立 16:9 HTMLBox，不依赖飞书白板。</p></header>{sections}</body></html>'''
    (out / "index.html").write_text(index, encoding="utf-8")
    doc = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Contra Editorial HTMLBox · 飞书文档版</title><style>body{{margin:0;background:{C["paper"]};color:{C["ink"]};font-family:Georgia,"Songti SC",serif}}.doc{{max-width:1180px;margin:0 auto;padding:36px 24px 72px}}.eyebrow{{color:{C["blue"]};font:700 11px Menlo,monospace}}h1{{font-size:clamp(42px,7vw,86px);line-height:1.05;margin:26px 0 16px}}.lead{{color:{C["muted"]};font-size:20px;line-height:1.55;margin:0 0 32px}}.section{{border-top:1px solid #D8D2C7;padding-top:24px;margin-top:46px}}.section h2{{font-size:26px;margin:0 0 14px}}iframe{{display:block;width:100%;aspect-ratio:16/9;border:0;background:transparent}}@media(max-width:720px){{.doc{{padding:24px 16px 48px}}.lead{{font-size:18px}}}}</style></head><body><main class="doc"><div class="eyebrow">AI WEEKLY / 2026.07.21 — 07.27</div><h1>判断比执行更稀缺。</h1><p class="lead">参考 Kimi 的研究型阅读节奏，使用 Contra Judgment Lab 配色；每个 section 都是独立 16:9 HTMLBox。</p><section class="section"><h2>01 / 封面</h2><iframe src="01-cover.html" title="AI 周报封面"></iframe></section><section class="section"><h2>02 / 六变量</h2><iframe src="02-variable-map.html" title="六变量"></iframe></section><section class="section"><h2>03 / 六趋势</h2><iframe src="03-trend-cards.html" title="六条趋势"></iframe></section><section class="section"><h2>04 / 迁移矩阵</h2><iframe src="04-migration-matrix.html" title="迁移矩阵"></iframe></section><section class="section"><h2>05 / 公众号头图</h2><iframe src="05-wechat-header.html" title="公众号头图"></iframe></section></main></body></html>'''
    (out / "feishu-doc.html").write_text(doc, encoding="utf-8")
    markdown = '''# AI 周报｜判断比执行更稀缺\n\n> Contra Judgment Lab 配色 + Kimi 研究型阅读节奏；每个 section 独立为 16:9 HTMLBox。\n\n- `01-cover.html`：封面 HTMLBox\n- `02-variable-map.html`：六变量 HTMLBox\n- `03-trend-cards.html`：六趋势 HTMLBox\n- `04-migration-matrix.html`：迁移矩阵 HTMLBox\n- `05-wechat-header.html`：公众号头图 HTMLBox\n'''
    (out / "feishu-doc.md").write_text(markdown, encoding="utf-8")
    prefix = f"@prototypes/{out.name}"
    xml = f'''<title>AI 周报｜2026.07.21—07.27｜Contra Editorial HTMLBox</title><h1>判断比执行更稀缺。</h1><p>参考 Kimi 的研究型阅读节奏，使用 Contra Judgment Lab 配色；每个 section 都是独立 16:9 HTMLBox。</p><h2>01 / 封面</h2><html5-block path="{prefix}/01-cover.html"></html5-block><h2>02 / 六变量</h2><html5-block path="{prefix}/02-variable-map.html"></html5-block><h2>03 / 六趋势</h2><html5-block path="{prefix}/03-trend-cards.html"></html5-block><h2>04 / 迁移矩阵</h2><html5-block path="{prefix}/04-migration-matrix.html"></html5-block><h2>05 / 公众号头图</h2><html5-block path="{prefix}/05-wechat-header.html"></html5-block>'''
    (out / "feishu-doc.xml").write_text(xml, encoding="utf-8")
    readme = '''# Contra Editorial HTMLBox · AI 周报可视化\n\n参考 Kimi 的研究型阅读节奏，使用 Contra Judgment Lab 配色，并将所有 section 独立输出为 16:9 HTMLBox。此版本不依赖飞书白板。\n\n- `01-cover.html`：封面 HTMLBox\n- `02-variable-map.html`：六变量 HTMLBox\n- `03-trend-cards.html`：六趋势 HTMLBox\n- `04-migration-matrix.html`：交互式迁移矩阵 HTMLBox\n- `05-wechat-header.html`：公众号头图 HTMLBox\n- `index.html`：16:9 HTMLBox 画廊\n- `feishu-doc.html`：飞书文档阅读版\n- `feishu-doc.xml`：只包含 html5-block 的 lark-cli XML 载荷\n'''
    (out / "README.md").write_text(readme, encoding="utf-8")


def migration_chart_html():
    rows = []
    for idx, (source, target, why, variables, proof) in enumerate(SHIFTS):
        rows.append({
            "id": idx + 1,
            "source": source,
            "target": target,
            "why": why,
            "variables": variables,
            "proof": proof,
            "score": TRENDS[idx]["score"],
            "color": C_VAR_COLORS[idx],
        })
    payload = json.dumps(rows, ensure_ascii=False)
    return r'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="use-iframe" content="true">
  <meta name="html-box-height-mode" content="auto">
  <meta name="description" content="Contra Judgment Lab 风格的 AI 周报迁移矩阵动态可视化：筛选变量并点击迁移节点查看判断依据。">
  <title>迁移矩阵 / Judgment Map</title>
  <style>
    :root { --paper:#FFFFFF; --paper-hi:#F7F9FC; --ink:#051C2C; --ink-md:#42566A; --ink-lo:#8595A6; --line:#DBE2EA; --line-lo:#EEF1F6; --blue:#2251FF; --blue-hi:#1233B8; --blue-lo:#7D9BFF; --serif:"et-book", "Songti SC", "Noto Serif CJK SC", "Source Han Serif SC", "STSong", Georgia, serif; --mono:Menlo, Consolas, "SF Mono", "PingFang SC", monospace; }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--paper); color:var(--ink); font-family:var(--serif); font-size:17px; line-height:1.68; -webkit-font-smoothing:antialiased; }
    .wrap { width:100%; max-width:924px; margin:0 auto; padding:24px 24px 40px; }
    .topline { display:flex; justify-content:space-between; gap:24px; align-items:flex-start; border-bottom:1px solid var(--line); padding-bottom:20px; }
    .kicker { display:block; color:var(--blue); font:11px var(--mono); letter-spacing:.26em; }
    h1 { margin:20px 0 10px; max-width:760px; font-family:var(--serif); font-size:clamp(34px,5vw,64px); font-weight:700; line-height:1.08; letter-spacing:0; }
    .lede { margin:0; color:var(--ink-md); font-size:17px; line-height:1.68; max-width:760px; }
    .score { border:1px solid var(--line); background:var(--paper-hi); padding:12px 15px; min-width:112px; text-align:right; }
    .score b { display:block; color:var(--blue); font:700 32px/1 var(--mono); }
    .score span { display:block; margin-top:7px; font:11px var(--mono); color:var(--ink-lo); }
    .filters { display:flex; flex-wrap:wrap; gap:8px; padding:17px 0 14px; border-bottom:1px solid var(--line-lo); }
    .filters button { border:1.5px solid var(--ink); background:var(--paper); color:var(--ink); border-radius:6px; padding:8px 11px; font:700 11.5px var(--serif); cursor:pointer; transition:background-color .18s ease,color .18s ease,border-color .18s ease; }
    .filters button.active, .filters button:hover { background:var(--blue); border-color:var(--blue); color:var(--paper); }
    #chart { width:100%; height:560px; border-top:1px solid var(--line); border-bottom:1px solid var(--line-lo); background:var(--paper); }
    .detail { display:grid; grid-template-columns:64px minmax(0,1fr) 260px; gap:18px; align-items:start; margin-top:22px; border-top:1px solid var(--line); padding-top:18px; }
    .detail-no { color:var(--blue); font:700 28px/1 var(--mono); }
    .detail h2 { margin:0 0 7px; font:700 23px/1.3 var(--serif); }
    .detail p { margin:0; color:var(--ink-md); font-size:15px; line-height:1.6; }
    .detail-side { border-left:1px solid var(--line); padding-left:16px; }
    .detail-side b { display:block; color:var(--blue); font:11px var(--mono); letter-spacing:.08em; }
    .detail-side span { display:block; color:var(--ink-md); font-size:14px; margin-top:7px; line-height:1.55; }
    #fallback { display:none; border-top:1px solid var(--line); border-bottom:1px solid var(--line-lo); background:var(--paper); padding:4px 0; }
    .fallback-lane { display:grid; grid-template-columns:minmax(0,1fr) 36px minmax(0,1fr) 54px; gap:8px; align-items:center; padding:13px 0; border-bottom:1px solid var(--line-lo); }
    .fallback-lane:last-child { border-bottom:0; }
    .node { border:1.5px solid var(--blue); padding:10px 12px; font-size:14px; font-weight:700; }
    .node.old { background:var(--ink); color:var(--paper); border-color:var(--ink); }
    .node.new { color:var(--ink); background:var(--paper-hi); }
    .arrow { color:var(--blue); font-size:22px; font-weight:700; text-align:center; }
    .weight { color:var(--blue); font:700 16px var(--mono); text-align:right; }
    @media (max-width:700px) { .topline { display:block; } .score { margin-top:16px; text-align:left; } .detail { grid-template-columns:56px minmax(0,1fr); } .detail-side { grid-column:2; border-left:0; border-top:1px solid var(--line); padding:10px 0 0; } #chart { height:520px; } }
  </style>
</head>
<body>
  <main class="wrap">
    <div class="topline">
      <div><span class="kicker">MIGRATION / CONTRA CHECK</span><h1>从“更强”到“更会判断”。</h1><p class="lede">旧单位 → 新单位：每条线不是替换关系，而是 AI 产品、采购和组织的判断单位正在迁移。</p></div>
      <div class="score"><b>6</b><span>迁移路径</span></div>
    </div>
    <nav class="filters" aria-label="过滤变量"><button class="active" data-filter="all">ALL</button><button data-filter="能力">能力</button><button data-filter="成本">成本</button><button data-filter="分发">分发</button><button data-filter="供给">供给</button><button data-filter="监管">监管</button><button data-filter="采用">采用</button></nav>
    <div id="chart" aria-label="AI 周报迁移矩阵图表"></div>
    <div id="fallback"></div>
    <section class="detail" aria-live="polite"><div class="detail-no" id="detail-no">01</div><div><h2 id="detail-title">Prompt scaffolding → Mature agent management</h2><p id="detail-why">给成熟模型目标、边界、参考物和复盘机制</p></div><div class="detail-side"><b>TEST / 反问</b><span id="detail-proof">常驻上下文是否变短</span></div></section>
  </main>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js" onerror="window.__echartsFailed=true"></script>
  <script>
    const DATA = __PAYLOAD__;
    const chartEl = document.getElementById('chart');
    const fallbackEl = document.getElementById('fallback');
    const detail = { no:document.getElementById('detail-no'), title:document.getElementById('detail-title'), why:document.getElementById('detail-why'), proof:document.getElementById('detail-proof') };
    let activeFilter = 'all';
    let chartInstance = null;
    function setDetail(item) { detail.no.textContent = String(item.id).padStart(2,'0'); detail.title.textContent = item.source + ' → ' + item.target; detail.why.textContent = item.why; detail.proof.textContent = item.proof + ' / ' + item.variables; }
    function renderFallback() {
      chartEl.style.display = 'none'; fallbackEl.style.display = 'block';
      fallbackEl.innerHTML = DATA.filter(item => activeFilter === 'all' || item.variables.includes(activeFilter)).map(item => '<div class="fallback-lane"><div class="node old">'+item.source+'</div><div class="arrow">→</div><div class="node new" style="background:'+item.color+'">'+item.target+'</div><div class="weight">'+item.score+'</div></div>').join('');
    }
    function renderChart() {
      if (typeof echarts === 'undefined' || window.__echartsFailed) { renderFallback(); return; }
      chartEl.style.display = 'block'; fallbackEl.style.display = 'none';
      const selected = DATA.filter(item => activeFilter === 'all' || item.variables.includes(activeFilter));
      const nodes = [];
      const links = [];
      const chartWidth = Math.max(320, chartEl.clientWidth || 820);
      const narrow = chartWidth < 640;
      const oldWidth = narrow ? 144 : 244;
      const newWidth = narrow ? 154 : 264;
      const labelSize = narrow ? 11 : 14;
      const leftX = narrow ? oldWidth / 2 + 8 : chartWidth * 0.24;
      const rightX = narrow ? chartWidth * 0.56 : chartWidth * 0.76;
      const rowStep = narrow ? 104 : (selected.length > 4 ? 76 : 98);
      const startY = narrow ? 54 : (selected.length > 4 ? 56 : 72);
      chartEl.style.height = narrow ? Math.max(500, startY + selected.length * rowStep + 26) + 'px' : '560px';
      const labelFormatter = ({ name }) => {
        if (!narrow || !name.includes(' ')) return name;
        const words = name.split(' ');
        const pivot = Math.ceil(words.length / 2);
        return words.slice(0, pivot).join(' ') + '\n' + words.slice(pivot).join(' ');
      };
      selected.forEach((item, index) => {
        const y = startY + index * rowStep;
        nodes.push({ id:'old-'+item.id, name:item.source, x:leftX, y, kind:'old', item, symbol:'roundRect', symbolSize:[oldWidth, narrow ? 52 : 52], itemStyle:{ color:'#051C2C', borderColor:'#051C2C', borderWidth:1 }, label:{ formatter:labelFormatter, color:'#FFFFFF', fontFamily:'Songti SC, Georgia, serif', fontSize:labelSize, fontWeight:700 } });
        nodes.push({ id:'new-'+item.id, name:item.target, x:rightX, y, kind:'new', item, symbol:'roundRect', symbolSize:[newWidth, narrow ? 52 : 52], itemStyle:{ color:'#F7F9FC', borderColor:item.color, borderWidth:2 }, label:{ formatter:labelFormatter, color:'#051C2C', fontFamily:'Songti SC, Georgia, serif', fontSize:labelSize, fontWeight:700 } });
        links.push({ source:'old-'+item.id, target:'new-'+item.id, value:item.score, lineStyle:{ color:item.color, width:1.5 + item.score / 36, curveness:0.14, opacity:0.84 } });
      });
      chartInstance = echarts.getInstanceByDom(chartEl) || echarts.init(chartEl, null, { renderer:'svg' });
      chartInstance.setOption({ animationDuration:650, animationEasing:'cubicOut', tooltip:{ trigger:'item', formatter:params => { const item=params.data && params.data.item; return item ? '<b>'+item.source+' → '+item.target+'</b><br/>score '+item.score+'<br/>'+item.why : ''; } }, series:[{ type:'graph', layout:'none', roam:false, data:nodes, links, coordinateSystem:null, edgeSymbol:['none','arrow'], edgeSymbolSize:7, emphasis:{ focus:'adjacency', lineStyle:{ width:6 } }, label:{ show:true, position:'inside' }, lineStyle:{ opacity:0.84 } }] }, true);
      chartInstance.off('click'); chartInstance.on('click', params => { if (params.data && params.data.item) setDetail(params.data.item); });
      if (selected.length) setDetail(selected[0]);
    }
    window.addEventListener('resize', () => { if (chartInstance) chartInstance.resize(); });
    document.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click', () => { document.querySelectorAll('[data-filter]').forEach(node => node.classList.remove('active')); button.classList.add('active'); activeFilter=button.dataset.filter; renderChart(); }));
    let attempts = 0; (function boot(){ if (typeof echarts !== 'undefined' || window.__echartsFailed || attempts++ > 30) renderChart(); else setTimeout(boot,150); })();
  </script>
</body>
</html>'''.replace('__PAYLOAD__', payload)


def write_artifacts(out, style, description, headline, lead, palette):
    out.mkdir(parents=True, exist_ok=True)
    if style == "AI Evidence Atlas":
        art_functions = {
            "01-cover.svg": evidence_cover,
            "02-variable-map.svg": evidence_variables,
            "03-trend-cards.svg": evidence_trends,
            "04-migration-matrix.svg": evidence_matrix,
            "05-wechat-header.svg": evidence_header,
        }
    elif style == "Contra Judgment Lab":
        art_functions = {
            "01-cover.svg": contra_cover,
            "02-variable-map.svg": contra_variables,
            "03-trend-cards.svg": contra_trends,
            "04-migration-matrix.svg": contra_matrix,
            "05-wechat-header.svg": contra_header,
        }
    else:
        art_functions = {
            "01-cover.svg": matisse_cover,
            "02-variable-map.svg": matisse_variables,
            "03-trend-cards.svg": matisse_trends,
            "04-migration-matrix.svg": matisse_matrix,
            "05-wechat-header.svg": matisse_header,
        }
    files = {
        name: fn() for name, fn in art_functions.items()
    }
    for name, content in files.items():
        (out / name).write_text(content, encoding="utf-8")
    if style == "Contra Judgment Lab":
        (out / "04-migration-chart.html").write_text(migration_chart_html(), encoding="utf-8")
    elif style == "Matisse Red Studio":
        (out / "04-migration-chart.html").write_text(matisse_migration_chart_html(), encoding="utf-8")
    bg, ink, muted = palette["paper"], palette["ink"], palette["muted"]
    labels = {"01-cover.svg": "01 / 封面", "02-variable-map.svg": "02 / 六变量", "03-trend-cards.svg": "03 / 六趋势", "04-migration-matrix.svg": "04 / 行业迁移", "05-wechat-header.svg": "05 / 公众号头图"}
    rows = "".join(f'<section><h2>{labels[name]}</h2><img src="{name}" alt="{labels[name]}"></section>' for name in files)
    if style in {"Contra Judgment Lab", "Matisse Red Studio"}:
        rows += '<section><h2>04 / 迁移图表</h2><iframe src="04-migration-chart.html" title="迁移矩阵动态可视化" style="width:100%;height:850px;border:0"></iframe></section>'
    index_font = palette.get("font", "system-ui, sans-serif")
    index = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(style)} · AI 周报</title><style>body{{margin:0;background:{bg};color:{ink};font-family:{index_font}}}header,section{{padding:28px 5vw;border-bottom:1px solid {muted}}}h1{{font-size:clamp(34px,6vw,72px);line-height:1;margin:0 0 14px}}h2{{font-size:24px}}p{{max-width:900px;line-height:1.6;color:{muted}}}img{{display:block;width:100%;height:auto;border:1px solid {muted}}}</style></head><body><header><h1>{escape(style)} / AI Weekly</h1><p>{escape(description)}</p></header>{rows}</body></html>'''
    (out / "index.html").write_text(index, encoding="utf-8")
    migration_section = '<section class="section"><h2>04 / 迁移矩阵</h2><iframe src="04-migration-chart.html" title="迁移矩阵动态可视化" style="width:100%;height:850px;border:0"></iframe></section>' if style in {"Contra Judgment Lab", "Matisse Red Studio"} else '<section class="section"><h2>04 / 迁移矩阵</h2><img class="visual" src="04-migration-matrix.svg" alt="迁移矩阵"></section>'
    doc_font = palette.get("font", "system-ui,-apple-system,\"Noto Sans SC\",sans-serif")
    doc = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(style)} · 飞书文档版 AI 周报</title><style>:root{{--paper:{bg};--ink:{ink};--muted:{muted};--line:{palette.get("line", "#BDB8AD")};--panel:{palette.get("card", palette.get("soft", "#F0EEE7"))};}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:{doc_font};line-height:1.6}}.doc{{max-width:1180px;margin:0 auto;padding:38px 28px 80px}}.eyebrow{{font-size:13px;font-weight:800;letter-spacing:.08em;color:var(--muted)}}h1{{font-size:clamp(42px,7vw,86px);line-height:1.08;max-width:980px;margin:28px 0 20px}}.lead{{font-size:22px;color:var(--muted);max-width:840px;margin:0 0 34px}}.visual{{display:block;width:100%;height:auto;border:1px solid var(--line)}}.section{{border-top:1px solid var(--line);padding-top:30px;margin-top:52px}}.section h2{{font-size:28px;margin:0 0 12px}}.section p{{color:var(--muted);max-width:900px}}.quote{{border-left:5px solid {palette.get("capability", palette.get("orange", "#FF6B2C"))};padding:12px 0 12px 20px;font-size:24px;font-weight:700;max-width:920px}}@media(max-width:720px){{.doc{{padding:24px 16px 54px}}.lead{{font-size:19px}}}}</style></head><body><main class="doc"><div class="eyebrow">AI WEEKLY / 2026.07.21 — 07.27</div><h1>{escape(headline)}</h1><p class="lead">{escape(lead)}</p><img class="visual" src="01-cover.svg" alt="AI 周报封面"><section class="section"><h2>01 / 判断入口</h2><p>{escape(description)}</p><div class="quote">Agent 价值 = 任务复杂度 × 成功率 × 可验证性 ÷ 全栈成本。</div></section><section class="section"><h2>02 / 六变量</h2><img class="visual" src="02-variable-map.svg" alt="六变量"></section><section class="section"><h2>03 / 六条趋势</h2><img class="visual" src="03-trend-cards.svg" alt="六条趋势"></section>{migration_section}<section class="section"><h2>05 / 结论</h2><p>把 AI 当成熟员工管理：目标、资源、边界、验证器和复盘机制，比更多噪音更重要。</p><img class="visual" src="05-wechat-header.svg" alt="公众号头图"></section></main></body></html>'''
    (out / "feishu-doc.html").write_text(doc, encoding="utf-8")
    markdown = f'''# AI 周报｜{headline}\n\n> {lead}\n\n![AI 周报封面](01-cover.svg)\n\n## 01 / 判断入口\n\n{description}\n\n> Agent 价值 = 任务复杂度 × 成功率 × 可验证性 ÷ 全栈成本。\n\n## 02 / 六变量\n\n![六变量](02-variable-map.svg)\n\n## 03 / 六条趋势\n\n![六条趋势](03-trend-cards.svg)\n\n## 04 / 迁移矩阵\n\n![迁移矩阵](04-migration-matrix.svg)\n\n## 05 / 结论\n\n把 AI 当成熟员工管理：目标、资源、边界、验证器和复盘机制，比更多噪音更重要。\n\n![公众号头图](05-wechat-header.svg)\n'''
    (out / "feishu-doc.md").write_text(markdown, encoding="utf-8")
    path_prefix = f"@prototypes/{out.name}"
    migration_block = f'<html5-block path="{path_prefix}/04-migration-chart.html"></html5-block>' if style in {"Contra Judgment Lab", "Matisse Red Studio"} else f'<whiteboard type="svg" path="{path_prefix}/04-migration-matrix.svg"></whiteboard>'
    xml = f'''<title>AI 周报｜2026.07.21—07.27｜{escape(style)}</title><h1>{escape(headline)}</h1><p>{escape(lead)}</p><whiteboard type="svg" path="{path_prefix}/01-cover.svg"></whiteboard><h2>01 / 判断入口</h2><p>{escape(description)}</p><callout emoji="💡" background-color="light-yellow" border-color="yellow"><p>Agent 价值 = 任务复杂度 × 成功率 × 可验证性 ÷ 全栈成本。</p></callout><h2>02 / 六变量</h2><whiteboard type="svg" path="{path_prefix}/02-variable-map.svg"></whiteboard><h2>03 / 六条趋势</h2><whiteboard type="svg" path="{path_prefix}/03-trend-cards.svg"></whiteboard><h2>04 / 迁移矩阵</h2>{migration_block}<h2>05 / 结论</h2><p>把 AI 当成熟员工管理：目标、资源、边界、验证器和复盘机制，比更多噪音更重要。</p><whiteboard type="svg" path="{path_prefix}/05-wechat-header.svg"></whiteboard>'''
    (out / "feishu-doc.xml").write_text(xml, encoding="utf-8")
    chart_note = "- `04-migration-chart.html`：Contra 风格 HTMLBox 动态迁移图\n" if style == "Contra Judgment Lab" else ("- `04-migration-chart.html`：Matisse Red Studio 风格 HTMLBox 动态迁移图\n" if style == "Matisse Red Studio" else "")
    readme = f'''# {style} · AI 周报可视化\n\n本周周报按 `{style}` 的个性化规则重新编排。\n\n- `01-cover.svg`：封面主图\n- `02-variable-map.svg`：六变量评分台\n- `03-trend-cards.svg`：六趋势证据卡 / 判断卡\n- `04-migration-matrix.svg`：行业迁移矩阵静态版\n{chart_note}- `05-wechat-header.svg`：公众号头图\n- `index.html`：素材画廊\n- `feishu-doc.html`：飞书文档阅读版\n- `feishu-doc.md`：结构化文档稿\n- `feishu-doc.xml`：可用 lark-cli 创建飞书文档的 XML 载荷\n'''
    (out / "README.md").write_text(readme, encoding="utf-8")


def main():
    write_artifacts(EVIDENCE, "AI Evidence Atlas", "把噪声新闻压缩成证据地图：变量先行，判断居中，证据落地。", "新闻退潮，证据留下。", "本周六条变化，最后都落在能力、成本、分发、供给、监管和采用。", E)
    write_artifacts(CONTRA, "Contra Judgment Lab", "把 AI 新闻放进判断实验室：执行越来越便宜，真正稀缺的是选择、反问和验收。", "判断比执行更稀缺。", "本周六条变化：模型更强之后，真正需要被设计的是判断、边界、交付物和复盘。", C)
    write_artifacts(MATISSE, "Matisse Red Studio", "用 Matisse《红色画室》的威尼斯红、绿色、金色和深蓝，把本周 AI 新闻变成一间可复盘的判断工作室。", "把新闻变成一间判断工作室。", "六条趋势，六个变量，一张迁移图：每个判断留下颜色、边界和下一次验证。", M)
    write_contra_editorial_htmlbox(CONTRA_HTMLBOX)
    print(EVIDENCE)
    print(CONTRA)
    print(MATISSE)
    print(CONTRA_HTMLBOX)


if __name__ == "__main__":
    main()
