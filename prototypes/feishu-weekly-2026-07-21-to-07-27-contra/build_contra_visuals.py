#!/usr/bin/env python3
"""Build Contra Labs inspired Feishu-ready SVG visuals for the AI weekly."""

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent

P = {
    "paper": "#FBFAF6",
    "ink": "#070707",
    "soft": "#F0EEE7",
    "muted": "#63615A",
    "line": "#111111",
    "lime": "#D7FF3F",
    "orange": "#FF6B2C",
    "blue": "#2F54FF",
    "pink": "#FF8BCB",
    "mint": "#18D68A",
    "violet": "#B69CFF",
}

TRENDS = [
    {
        "no": "01",
        "label": "CONTEXT",
        "title": "上下文工程从写更多规则，变成授权成熟模型",
        "thesis": "贵的不是上下文长度，而是团队偏好、验证流程和真实参考物。",
        "score": 92,
        "signal": "80% prompt cut",
        "accent": "orange",
        "vars": [("能力", 92), ("成本", 72), ("采用", 86)],
    },
    {
        "no": "02",
        "label": "RUNTIME",
        "title": "Agent 安全从发布前评测，变成运行时边界",
        "thesis": "治理单位不再只是模型，而是身份、权限、网络、日志和回滚。",
        "score": 94,
        "signal": "runtime boundary",
        "accent": "violet",
        "vars": [("监管", 94), ("采用", 76), ("成本", 64)],
    },
    {
        "no": "03",
        "label": "SYSTEM",
        "title": "竞争单位变成模型、Harness、验证器和轨迹",
        "thesis": "可复盘的工作流水线，才会改写团队规模和代码产出关系。",
        "score": 90,
        "signal": "model-system pair",
        "accent": "mint",
        "vars": [("能力", 84), ("采用", 90), ("成本", 68)],
    },
    {
        "no": "04",
        "label": "SURFACE",
        "title": "入口从聊天框转向 Office、画布和设计台",
        "thesis": "谁离最终交付物最近，谁就更容易拿到上下文、反馈和付费。",
        "score": 92,
        "signal": "artifact surface",
        "accent": "blue",
        "vars": [("分发", 92), ("采用", 80), ("能力", 70)],
    },
    {
        "no": "05",
        "label": "DATA",
        "title": "下一轮训练数据红利来自真实工作轨迹",
        "thesis": "网页文本告诉模型世界有什么，轨迹数据告诉模型工作怎么做完。",
        "score": 88,
        "signal": "workflow data",
        "accent": "pink",
        "vars": [("供给", 78), ("采用", 84), ("监管", 58)],
    },
    {
        "no": "06",
        "label": "INFRA",
        "title": "成本竞争从 token 单价扩展到工业账本",
        "thesis": "AI 越来越像工业系统，胜负取决于全栈单位任务成本。",
        "score": 96,
        "signal": "3.2GW + chips",
        "accent": "lime",
        "vars": [("成本", 94), ("供给", 96), ("监管", 70)],
    },
]

VARIABLES = [
    ("能力", 86, "orange", "模型成熟后，prompt 噪音开始被削掉。"),
    ("成本", 82, "lime", "成本从 token 扩展到电力、吞吐、债务。"),
    ("分发", 78, "blue", "Office、画布、设计台成为交付表面。"),
    ("供给", 88, "mint", "芯片、电力、园区协议决定 AI 速度。"),
    ("监管", 91, "violet", "安全与版权边界进入运行时。"),
    ("组织采用", 84, "pink", "Agent 需要任务、权限、检查点和复盘。"),
]

SHIFTS = [
    ("Prompt scaffolding", "Mature agent management", "给成熟模型目标、边界、参考物和复盘机制", "能力/成本/采用", "常驻上下文是否变短"),
    ("Pre-release eval", "Runtime boundary", "把安全治理搬到身份、权限、日志、审批和回滚", "监管/采用", "是否记录工具调用轨迹"),
    ("Model ranking", "Model-system pair", "比较模型和 harness、验证器、memory 的组合能力", "能力/采用/成本", "采购对象是否变成系统包"),
    ("Chat interface", "Artifact surface", "让 AI 进入 Excel、Outlook、画布、图片和设计台", "分发/采用", "交付物是否成为入口"),
    ("Web corpus", "Workflow trajectory", "从内容学习转向过程学习和验收轨迹", "供给/采用", "是否沉淀可验证任务轨迹"),
    ("Token price", "Industrial ledger", "从 API 价格表迁移到电力、租赁和债务结构", "成本/供给", "单位任务成本是否全栈计量"),
]


def wrap(text, limit):
    lines, line, width = [], "", 0.0
    for ch in text:
        unit = 0.55 if ord(ch) < 128 else 1.0
        if width + unit > limit and line:
            lines.append(line)
            line, width = ch, unit
        else:
            line += ch
            width += unit
    if line:
        lines.append(line)
    return lines


def text(x, y, value, size=24, fill=None, weight=700, anchor="start", family="Inter, Arial, sans-serif"):
    fill = fill or P["ink"]
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}" letter-spacing="0">{escape(value)}</text>'
    )


def block(x, y, value, size=28, limit=20, leading=1.18, fill=None, weight=700):
    return "\n".join(
        text(x, y + i * size * leading, line, size, fill, weight)
        for i, line in enumerate(wrap(value, limit))
    )


def pill(x, y, value, fill=None, stroke=None, fg=None, size=14, pad=18):
    fill = fill or P["paper"]
    stroke = stroke or P["line"]
    fg = fg or P["ink"]
    w = max(76, len(value) * 8.2 + pad * 2)
    return (
        f'<rect x="{x}" y="{y}" width="{w:.1f}" height="34" rx="17" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        + text(x + w / 2, y + 22, value, size, fg, 820, "middle")
    )


def svg(width, height, body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">
  <rect width="{width}" height="{height}" fill="{P["paper"]}"/>
  <g opacity=".06">
    <path d="M0 120 H{width} M0 240 H{width} M0 360 H{width} M0 480 H{width} M0 600 H{width} M0 720 H{width} M0 840 H{width} M0 960 H{width} M0 1080 H{width}" stroke="{P["line"]}"/>
    <path d="M160 0 V{height} M320 0 V{height} M480 0 V{height} M640 0 V{height} M800 0 V{height} M960 0 V{height} M1120 0 V{height} M1280 0 V{height} M1440 0 V{height}" stroke="{P["line"]}"/>
  </g>
  {body}
</svg>
'''


def lab_tiles(x, y):
    colors = ["orange", "blue", "mint", "pink", "lime", "violet", "paper", "orange", "blue", "mint", "paper", "pink"]
    parts = [f'<rect x="{x}" y="{y}" width="530" height="430" fill="{P["ink"]}"/>']
    idx = 0
    for row in range(3):
        for col in range(4):
            xx, yy = x + 22 + col * 122, y + 22 + row * 122
            fill = P[colors[idx]]
            parts.append(f'<rect x="{xx}" y="{yy}" width="104" height="104" fill="{fill}" stroke="{P["paper"]}" stroke-width="1"/>')
            if idx % 3 == 0:
                parts.append(f'<circle cx="{xx+52}" cy="{yy+52}" r="30" fill="none" stroke="{P["ink"]}" stroke-width="8"/>')
            elif idx % 3 == 1:
                parts.append(f'<path d="M{xx+18} {yy+70} L{xx+42} {yy+38} L{xx+66} {yy+58} L{xx+88} {yy+25}" fill="none" stroke="{P["ink"]}" stroke-width="8"/>')
            else:
                parts.append(text(xx + 52, yy + 62, f"{idx+1:02d}", 30, P["ink"], 900, "middle"))
            idx += 1
    return "\n".join(parts)


def make_cover():
    w, h = 1600, 820
    body = [
        pill(72, 62, "AI WEEKLY"),
        pill(198, 62, "2026.07.21-07.27"),
        pill(396, 62, "HUMAN TASTE LAB"),
        block(72, 185, "Execution is free. Judgment is everything.", 92, 12, .96, P["ink"], 920),
        block(76, 478, "本周主线：当模型更成熟，AI 日报不该堆更多新闻，而要判断哪些约束真的改变了。", 30, 31, 1.34, P["muted"], 560),
        f'<line x1="72" y1="654" x2="908" y2="654" stroke="{P["line"]}" stroke-width="2"/>',
        text(72, 720, "FIRST PRINCIPLES", 18, P["ink"], 900),
        text(330, 720, "agent_value = task_complexity x success_rate x verifiability / total_system_cost", 22, P["ink"], 720, family="Menlo, Monaco, monospace"),
        lab_tiles(996, 74),
        f'<rect x="996" y="548" width="530" height="184" fill="{P["soft"]}" stroke="{P["line"]}" stroke-width="2"/>',
        text(1028, 610, "WEEKLY SIGNAL", 16, P["muted"], 850),
        block(1028, 666, "把 Agent 当成熟员工管理", 42, 11, 1.0, P["ink"], 900),
    ]
    return svg(w, h, "\n".join(body), "Contra style AI weekly cover")


def make_variable_map():
    w, h = 1600, 1020
    body = [
        pill(72, 64, "01 / SCOREBOARD"),
        block(72, 150, "Six variables. One editorial judgment layer.", 64, 16, 1.0, P["ink"], 920),
        text(76, 272, "柱高代表本周约束变化强度，不是精确统计。先看变量，再读新闻。", 24, P["muted"], 560),
        f'<rect x="72" y="350" width="1456" height="548" fill="{P["paper"]}" stroke="{P["line"]}" stroke-width="2.5"/>',
    ]
    col_w = 1456 / 6
    for i, (name, score, accent, desc) in enumerate(VARIABLES):
        x = 72 + i * col_w
        bar = 298 * score / 100
        body.append(f'<line x1="{x}" y1="350" x2="{x}" y2="898" stroke="{P["line"]}" stroke-width="1.5"/>' if i else "")
        body.append(f'<rect x="{x+24}" y="{812-bar:.1f}" width="{col_w-48:.1f}" height="{bar:.1f}" fill="{P[accent]}"/>')
        body.append(text(x + 24, 414, f"{i+1:02d}", 22, P["muted"], 800))
        body.append(text(x + 24, 468, name, 30, P["ink"], 900))
        body.append(text(x + 24, 792 - bar, str(score), 58, P["ink"], 920))
        body.append(block(x + 24, 852, desc, 16, 12, 1.35, P["muted"], 560))
    body.append(f'<line x1="72" y1="812" x2="1528" y2="812" stroke="{P["line"]}" stroke-width="2"/>')
    return svg(w, h, "\n".join(body), "Contra style variable scoreboard")


def tiny_bars(x, y, vars_):
    parts = []
    for i, (name, score) in enumerate(vars_):
        yy = y + i * 31
        parts.append(text(x, yy + 17, name, 14, P["muted"], 800))
        parts.append(f'<rect x="{x+58}" y="{yy+7}" width="178" height="8" fill="{P["soft"]}" stroke="{P["line"]}" stroke-width=".8"/>')
        parts.append(f'<rect x="{x+58}" y="{yy+7}" width="{178*score/100:.1f}" height="8" fill="{P["ink"]}"/>')
        parts.append(text(x + 252, yy + 17, str(score), 13, P["ink"], 820))
    return "\n".join(parts)


def make_trend_cards():
    w, h = 1600, 1980
    body = [
        pill(72, 64, "02 / CREATIVE EVAL CARDS"),
        block(72, 150, "六条趋势，像评审作品一样被打分。", 64, 16, 1.0, P["ink"], 920),
        text(76, 272, "每张卡只保留 thesis、变量条和一个高信号证据，避免新闻堆积。", 24, P["muted"], 560),
    ]
    card_w, card_h = 458, 510
    for idx, tr in enumerate(TRENDS):
        row, col = divmod(idx, 3)
        x = 72 + col * 500
        y = 366 + row * 570
        accent = P[tr["accent"]]
        body.append(f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" fill="{P["paper"]}" stroke="{P["line"]}" stroke-width="2.5"/>')
        body.append(f'<rect x="{x}" y="{y}" width="{card_w}" height="88" fill="{accent}" stroke="{P["line"]}" stroke-width="2.5"/>')
        body.append(text(x + 24, y + 58, tr["no"], 42, P["ink"], 920))
        body.append(text(x + 115, y + 54, tr["label"], 18, P["ink"], 900))
        body.append(text(x + card_w - 28, y + 58, str(tr["score"]), 42, P["ink"], 920, "end"))
        body.append(block(x + 24, y + 142, tr["title"], 26, 15, 1.22, P["ink"], 900))
        body.append(block(x + 24, y + 268, tr["thesis"], 18, 22, 1.45, P["muted"], 560))
        body.append(tiny_bars(x + 24, y + 376, tr["vars"]))
        body.append(pill(x + 24, y + 454, tr["signal"], fill=P["soft"], stroke=P["line"], fg=P["ink"], size=13))
    return svg(w, h, "\n".join(body), "Contra style trend cards")


def make_shift_matrix():
    w, h = 1600, 1030
    col_w = [72, 246, 272, 456, 202, 294]
    headers = ["#", "旧问题", "新判断", "迁移含义", "变量", "下周观察"]
    x0, y0 = 60, 320
    body = [
        pill(72, 64, "03 / MIGRATION MATRIX"),
        block(72, 150, "From news intake to judgment infrastructure.", 62, 17, 1.0, P["ink"], 920),
        text(76, 268, "用更高密度的矩阵替代行业迁移大图，飞书里扫读更快，也更像研究台账。", 24, P["muted"], 560),
        f'<rect x="{x0}" y="{y0}" width="{sum(col_w)}" height="598" fill="{P["paper"]}" stroke="{P["line"]}" stroke-width="2.5"/>',
    ]
    cx = x0
    for htxt, cw in zip(headers, col_w):
        body.append(f'<rect x="{cx}" y="{y0}" width="{cw}" height="64" fill="{P["ink"]}" stroke="{P["ink"]}" stroke-width="1"/>')
        body.append(text(cx + 14, y0 + 40, htxt, 15, P["paper"], 850))
        cx += cw
    row_h = 89
    accents = ["orange", "violet", "mint", "blue", "pink", "lime"]
    for i, row in enumerate(SHIFTS):
        y = y0 + 64 + i * row_h
        fill = P["soft"] if i % 2 else P["paper"]
        body.append(f'<rect x="{x0}" y="{y}" width="{sum(col_w)}" height="{row_h}" fill="{fill}" stroke="{P["line"]}" stroke-width="1"/>')
        cx = x0
        values = [f"{i+1:02d}", *row]
        limits = [3, 18, 20, 33, 12, 20]
        for j, (value, cw, limit) in enumerate(zip(values, col_w, limits)):
            if j:
                body.append(f'<line x1="{cx}" y1="{y}" x2="{cx}" y2="{y+row_h}" stroke="{P["line"]}" stroke-width="1"/>')
            if j == 0:
                body.append(f'<circle cx="{cx+36}" cy="{y+44}" r="22" fill="{P[accents[i]]}" stroke="{P["line"]}" stroke-width="1.5"/>')
                body.append(text(cx + 36, y + 51, value, 18, P["ink"], 900, "middle"))
            elif j in (1, 2):
                body.append(block(cx + 14, y + 34, value, 15, limit, 1.2, P["ink"], 800))
            else:
                body.append(block(cx + 14, y + 31, value, 14, limit, 1.25, P["muted"], 560))
            cx += cw
    return svg(w, h, "\n".join(body), "Contra style migration matrix")


def make_wechat_header():
    w, h = 1600, 840
    body = [
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="{P["ink"]}"/>',
        lab_tiles(994, 72),
        pill(82, 76, "AI WEEKLY / HUMAN TASTE LAB", fill=P["ink"], stroke=P["paper"], fg=P["paper"]),
        block(82, 190, "Execution is free. Judgment is everything.", 86, 12, .96, P["paper"], 920),
        block(86, 524, "当模型更成熟，日报的价值不再是追热点，而是判断哪些约束真的改变了。", 30, 31, 1.35, "#CFCBC0", 560),
        f'<rect x="82" y="704" width="658" height="2" fill="{P["paper"]}"/>',
        text(82, 762, "2026.07.21-07.27 / 公众号头图复用版", 22, "#CFCBC0", 850),
    ]
    return svg(w, h, "\n".join(body), "Contra style WeChat header")


def write_preview():
    assets = [
        ("01-cover.svg", "飞书文档封面主图"),
        ("02-variable-map.svg", "六变量 Scoreboard"),
        ("03-trend-cards.svg", "六趋势 Creative Eval Cards"),
        ("04-migration-matrix.svg", "行业迁移矩阵"),
        ("05-wechat-header.svg", "公众号头图复用版"),
    ]
    rows = "\n".join(
        f'<section><h2>{escape(title)}</h2><img src="{name}" alt="{escape(title)}"></section>'
        for name, title in assets
    )
    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Contra Lab Style · AI Weekly Visuals</title>
  <style>
    body {{ margin: 0; font-family: Inter, Arial, sans-serif; background: {P["paper"]}; color: {P["ink"]}; }}
    header, section {{ padding: 36px; border-bottom: 2px solid {P["ink"]}; }}
    h1 {{ margin: 0 0 12px; max-width: 900px; font-size: clamp(48px, 8vw, 116px); line-height: .92; letter-spacing: 0; }}
    h2 {{ margin: 0 0 18px; font-size: 26px; }}
    p {{ color: {P["muted"]}; line-height: 1.6; max-width: 880px; font-size: 18px; }}
    img {{ display: block; width: 100%; height: auto; border: 2px solid {P["ink"]}; background: {P["paper"]}; }}
    .pill {{ display:inline-block; border:2px solid {P["ink"]}; border-radius:999px; padding:8px 16px; font-weight:800; margin-bottom:24px; }}
  </style>
</head>
<body>
  <header>
    <div class="pill">CONTRA LAB STYLE DRAFT</div>
    <h1>Judgment Layer for AI Weekly</h1>
    <p>白底、黑线、大标题、创意评测卡和高密度矩阵。用于确认风格方向，暂不覆盖已有飞书文档。</p>
  </header>
  {rows}
</body>
</html>
'''
    (OUT / "index.html").write_text(html, encoding="utf-8")


def write_readme():
    md = """# Contra Lab Style Draft

这是一版参考 Contra Labs 气质的 AI 周报飞书视觉资产：白底、黑线、巨大标题、pill 标签、创意评测卡、scoreboard 和高密度 migration matrix。

## 文件

- `01-cover.svg`：飞书文档封面主图。
- `02-variable-map.svg`：六变量 scoreboard。
- `03-trend-cards.svg`：六趋势 creative eval cards。
- `04-migration-matrix.svg`：行业迁移矩阵。
- `05-wechat-header.svg`：公众号头图复用版。
- `index.html`：本地预览。

本版用于风格确认，暂不覆盖已有飞书文档。
"""
    (OUT / "README.md").write_text(md, encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "01-cover.svg": make_cover(),
        "02-variable-map.svg": make_variable_map(),
        "03-trend-cards.svg": make_trend_cards(),
        "04-migration-matrix.svg": make_shift_matrix(),
        "05-wechat-header.svg": make_wechat_header(),
    }
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    write_preview()
    write_readme()
    for name in [*files.keys(), "index.html", "README.md"]:
        print(OUT / name)


if __name__ == "__main__":
    main()
