#!/usr/bin/env python3
"""Build Feishu-ready SVG visuals for the 2026-07-21 to 2026-07-27 AI weekly."""

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent

PALETTE = {
    "ink": "#111318",
    "paper": "#F4EFE4",
    "card": "#FFF9EE",
    "muted": "#6E665B",
    "line": "#D8CDBC",
    "red": "#D64028",
    "blue": "#2459D6",
    "green": "#13865E",
    "gold": "#D6A435",
    "purple": "#765AD8",
    "cyan": "#0F8AA3",
    "dark": "#101116",
    "cream": "#F7F0E5",
}

TRENDS = [
    {
        "no": "01",
        "label": "Context",
        "title": "上下文工程从“写更多规则”变成“授权成熟模型”",
        "thesis": "Opus 5 之后，该删的不是上下文，而是模型能自己推断的废上下文。真正贵的是团队偏好、验证流程和真实参考物。",
        "vars": [("能力", 92, "red"), ("成本", 72, "gold"), ("采用", 86, "cyan")],
        "evidence": ["Opus 5", "80% prompt cut", "thick context"],
    },
    {
        "no": "02",
        "label": "Runtime",
        "title": "Agent 安全从发布前评测变成运行时边界",
        "thesis": "长程 Agent 会搜索、写代码、改环境、调工具。治理单位不再只是模型，而是身份、权限、网络、日志和回滚。",
        "vars": [("监管", 94, "purple"), ("采用", 76, "cyan"), ("成本", 64, "gold")],
        "evidence": ["HF incident", "AISI cheating", "Agent Harness"],
    },
    {
        "no": "03",
        "label": "System",
        "title": "竞争单位变成“模型 + Harness + 验证器 + 轨迹”",
        "thesis": "最强模型不是单点答案。可复盘的工作流水线，才会改写团队规模和代码产出之间的关系。",
        "vars": [("能力", 84, "red"), ("采用", 90, "cyan"), ("成本", 68, "gold")],
        "evidence": ["Hyra", "Cursor Swarm", "Tunix", "MagenticLite"],
    },
    {
        "no": "04",
        "label": "Surface",
        "title": "交付物入口从聊天框转向 Office、画布和设计台",
        "thesis": "谁离最终交付物最近，谁就更容易拿到上下文、反馈和付费。聊天框只是入口之一，不是终点。",
        "vars": [("分发", 92, "blue"), ("采用", 80, "cyan"), ("能力", 70, "red")],
        "evidence": ["Qwen-Image", "Grok Excel", "Copilot Canvas", "Miora"],
    },
    {
        "no": "05",
        "label": "Data",
        "title": "下一轮训练数据红利来自真实工作轨迹",
        "thesis": "网页文本告诉模型世界有什么；轨迹数据告诉模型工作怎么做完。Agent 训练燃料开始从内容转向过程。",
        "vars": [("供给", 78, "green"), ("采用", 84, "cyan"), ("监管", 58, "purple")],
        "evidence": ["workflow data", "Economic Index", "Unslop", "BigMac"],
    },
    {
        "no": "06",
        "label": "Infra",
        "title": "成本竞争从 token 单价扩展到电力、债务和数据中心协议",
        "thesis": "AI 不只是软件行业，也越来越像工业系统。谁能用更低全栈成本完成更多可计费任务，谁才跑得久。",
        "vars": [("成本", 94, "gold"), ("供给", 96, "green"), ("监管", 70, "purple")],
        "evidence": ["Gemini Flash", "3.2GW", "AMD + Anthropic", "Nikkei debt"],
    },
]

VARIABLES = [
    ("能力", 86, "red", "Opus 5 / Claude 5 generation 让模型开始要求更少提示词噪音。"),
    ("成本", 82, "gold", "token 成本外溢成吞吐、电力、债务和数据中心协议。"),
    ("分发", 78, "blue", "Office、画布、邮件、图片和设计台成为 AI 交付入口。"),
    ("供给", 88, "green", "3.2GW、2GW 芯片合作和隐性债务把 AI 拉回工业系统。"),
    ("监管", 91, "purple", "评测作弊、安全事件和版权和解把边界推到运行时。"),
    ("组织采用", 84, "cyan", "Agent 越像数字员工，越需要任务、权限、检查点和复盘记录。"),
]

SHIFTS = [
    ("Prompt scaffolding", "Mature agent management", "从给弱模型写保姆手册，迁移到给成熟模型目标、边界和复盘机制。", "red"),
    ("Pre-release eval", "Runtime boundary", "从发布前安全题，迁移到运行时身份、权限、日志、审批和回滚。", "purple"),
    ("Model ranking", "Model-system pair", "从谁模型最强，迁移到模型、harness、验证器和轨迹的组合能力。", "green"),
    ("Chat interface", "Artifact surface", "从聊天框回答，迁移到 Excel、Outlook、画布、图片和设计台交付。", "blue"),
    ("Web corpus", "Workflow trajectory", "从更多网页文本，迁移到任务提出、拆解、执行、修正和验收轨迹。", "cyan"),
    ("Token price", "Industrial ledger", "从 API 价格表，迁移到吞吐、电力、租赁、债务和数据中心协议。", "gold"),
]


def wrap(text, limit):
    lines, line, width = [], "", 0.0
    for ch in text:
        unit = 0.56 if ord(ch) < 128 else 1.0
        if width + unit > limit and line:
            lines.append(line)
            line, width = ch, unit
        else:
            line += ch
            width += unit
    if line:
        lines.append(line)
    return lines


def t(x, y, text, size=24, fill=None, weight=700, anchor="start", family="system-ui", extra=""):
    fill = fill or PALETTE["ink"]
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
        f'letter-spacing="0" {extra}>{escape(text)}</text>'
    )


def block(x, y, text, size=28, limit=22, line_height=1.25, fill=None, weight=700, family="system-ui"):
    parts = []
    for i, line in enumerate(wrap(text, limit)):
        parts.append(t(x, y + i * size * line_height, line, size, fill, weight, family=family))
    return "\n".join(parts)


def chip(x, y, text, fill="#FFFFFF", stroke=None, color=None):
    color = color or PALETTE["muted"]
    stroke = stroke or PALETTE["line"]
    w = max(70, len(text) * 9 + 22)
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="32" fill="{fill}" stroke="{stroke}" />'
        + t(x + 11, y + 22, text, 13, color, 800)
    )


def chip_width(text):
    return max(70, len(text) * 9 + 22)


def chip_row(x, y, labels, max_width, fill="rgba(255,255,255,.48)", stroke=None, color=None, gap=8):
    parts = []
    cx, cy = x, y
    for label in labels:
        w = chip_width(label)
        if cx > x and cx + w > x + max_width:
            cx = x
            cy += 40
        parts.append(chip(cx, cy, label, fill=fill, stroke=stroke, color=color))
        cx += w + gap
    return "\n".join(parts)


def svg_wrap(width, height, body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">
  <defs>
    <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse">
      <path d="M 28 0 L 0 0 0 28" fill="none" stroke="rgba(17,19,24,.07)" stroke-width="1"/>
    </pattern>
    <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="18"/>
    </filter>
  </defs>
  <rect width="{width}" height="{height}" fill="{PALETTE["paper"]}"/>
  <rect width="{width}" height="{height}" fill="url(#grid)" opacity=".9"/>
  {body}
</svg>
'''


def make_cover():
    w, h = 1600, 720
    body = [
        f'<rect x="58" y="54" width="{w-116}" height="{h-108}" fill="none" stroke="{PALETTE["ink"]}" stroke-width="2"/>',
        f'<rect x="980" y="54" width="562" height="612" fill="{PALETTE["dark"]}"/>',
        f'<circle cx="1110" cy="190" r="76" fill="{PALETTE["red"]}" opacity=".88" filter="url(#soft)"/>',
        f'<circle cx="1290" cy="330" r="112" fill="{PALETTE["blue"]}" opacity=".72" filter="url(#soft)"/>',
        f'<circle cx="1198" cy="492" r="88" fill="{PALETTE["green"]}" opacity=".62" filter="url(#soft)"/>',
        f'<path d="M1026 616 C1140 464 1320 486 1498 126" fill="none" stroke="{PALETTE["gold"]}" stroke-width="3" opacity=".68"/>',
        f'<g opacity=".28">{grid_lines(980, 54, 562, 612, PALETTE["cream"])}</g>',
        chip(86, 88, "AI WEEKLY", fill="rgba(255,255,255,.38)"),
        chip(214, 88, "2026.07.21-07.27", fill="rgba(255,255,255,.38)"),
        chip(404, 88, "FEISHU DOC VISUAL", fill="rgba(255,255,255,.38)"),
        block(86, 192, "Opus 5 删掉 80% 提示词后，Agent 行业开始重估“脚手架”", 58, 15, 1.03, PALETTE["ink"], 900),
        block(88, 482, "本周主线不是 benchmark，而是 Agent 的管理范式变化：模型更成熟以后，提示词不再是堆规则，真正重要的是接口、边界、验证器、轨迹和全栈成本。", 24, 32, 1.5, "#332E27", 520),
        t(1026, 128, "FIRST-PRINCIPLES EQUATION", 14, PALETTE["cream"], 850),
        block(1026, 230, "把 Agent 当成熟员工管理", 50, 9, 1.02, PALETTE["cream"], 900),
        t(1028, 432, "agent_value =", 24, PALETTE["cream"], 700, family="monospace"),
        t(1028, 476, "task_complexity × success_rate × verifiability", 19, PALETTE["cream"], 500, family="monospace"),
        f'<line x1="1028" y1="506" x2="1484" y2="506" stroke="{PALETTE["cream"]}" opacity=".72"/>',
        t(1028, 544, "context_cost + inference_cost + governance_cost + integration_cost", 16, PALETTE["cream"], 500, family="monospace"),
    ]
    return svg_wrap(w, h, "\n".join(body), "AI weekly cover")


def grid_lines(x, y, w, h, color):
    parts = []
    for dx in range(0, int(w), 28):
        parts.append(f'<line x1="{x+dx}" y1="{y}" x2="{x+dx}" y2="{y+h}" stroke="{color}" stroke-width="1"/>')
    for dy in range(0, int(h), 28):
        parts.append(f'<line x1="{x}" y1="{y+dy}" x2="{x+w}" y2="{y+dy}" stroke="{color}" stroke-width="1"/>')
    return "\n".join(parts)


def make_variable_map():
    w, h = 1600, 1020
    margin = 72
    col_w = (w - margin * 2) / 6
    body = [
        chip(72, 62, "01 / VARIABLE MAP", fill="rgba(255,255,255,.42)"),
        block(72, 150, "这周真正变化的，是六个底层变量的权重。", 50, 19, 1.05, PALETTE["ink"], 900),
        block(72, 270, "柱高不是精确数据，而是编辑判断强度：它告诉读者先看哪一个约束变了，再看新闻本身。", 22, 42, 1.45, "#3E382F", 520),
        f'<rect x="{margin}" y="374" width="{w-margin*2}" height="530" fill="rgba(255,255,255,.38)" stroke="{PALETTE["ink"]}" stroke-width="2"/>',
    ]
    for i, (name, score, color, desc) in enumerate(VARIABLES):
        x = margin + i * col_w
        bh = 315 * score / 100
        body.extend([
            f'<line x1="{x}" y1="374" x2="{x}" y2="904" stroke="{PALETTE["line"]}" />' if i else "",
            f'<rect x="{x+22}" y="{750-bh}" width="{col_w-44}" height="{bh}" fill="{PALETTE[color]}" opacity=".84"/>',
            t(x + 22, 424, name, 26, PALETTE["ink"], 900),
            t(x + 22, 710 - bh, str(score), 52, PALETTE["ink"], 900),
            block(x + 22, 818, desc, 14, 13, 1.42, "#4B443A", 560),
        ])
    return svg_wrap(w, h, "\n".join(body), "AI weekly variable map")


def variable_bars(x, y, variables):
    parts = []
    for i, (name, score, color) in enumerate(variables):
        yy = y + i * 32
        parts.append(t(x, yy + 18, name, 14, "#494238", 760))
        parts.append(f'<rect x="{x+64}" y="{yy+8}" width="210" height="8" fill="none" stroke="#494238" stroke-width="1"/>')
        parts.append(f'<rect x="{x+64}" y="{yy+8}" width="{210*score/100:.1f}" height="8" fill="{PALETTE[color]}"/>')
        parts.append(t(x + 286, yy + 18, str(score), 13, "#494238", 760))
    return "\n".join(parts)


def make_trend_cards():
    w, h = 1600, 2060
    body = [
        chip(72, 64, "02 / EVIDENCE ATLAS", fill="rgba(255,255,255,.42)"),
        block(72, 150, "六条趋势，不做新闻复述，做约束变化。", 50, 18, 1.05, PALETTE["ink"], 900),
        block(72, 270, "每张卡保留一条 sharp thesis、三个变量权重和证据标签。适合飞书文档开头，也可以拆成公众号趋势总结图。", 22, 44, 1.45, "#3E382F", 520),
    ]
    card_w, card_h = 464, 560
    x0, y0, gap = 72, 382, 30
    for idx, tr in enumerate(TRENDS):
        row, col = divmod(idx, 3)
        x = x0 + col * (card_w + gap)
        y = y0 + row * (card_h + gap)
        body.extend([
            f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" fill="{PALETTE["card"]}" stroke="{PALETTE["ink"]}" stroke-width="2"/>',
            f'<rect x="{x+16}" y="{y+16}" width="{card_w-32}" height="{card_h-32}" fill="none" stroke="{PALETTE["line"]}"/>',
            chip(x + 24, y + 28, f'TREND {tr["no"]}', fill="rgba(255,255,255,.46)"),
            chip(x + 136, y + 28, tr["label"], fill="rgba(255,255,255,.46)"),
            block(x + 24, y + 112, tr["title"], 25, 15, 1.25, PALETTE["ink"], 900),
            block(x + 24, y + 250, tr["thesis"], 16, 24, 1.55, "#332E27", 540),
            variable_bars(x + 24, y + 402, tr["vars"]),
            chip_row(x + 24, y + 510, tr["evidence"][:4], card_w - 48),
        ])
    return svg_wrap(w, h, "\n".join(body), "AI weekly trend cards")


def make_paradigm_shifts():
    w, h = 1600, 1040
    watch = [
        "常驻上下文是否变短，skills 是否按需加载",
        "评测环境是否记录身份、权限和轨迹",
        "企业是否采购 model-system pair 而非单模型",
        "AI 是否进入真实交付物表面",
        "是否沉淀可验证工作轨迹",
        "单位任务成本是否覆盖工业成本",
    ]
    variables = ["能力 / 成本 / 采用", "监管 / 采用", "能力 / 采用 / 成本", "分发 / 采用", "供给 / 采用", "成本 / 供给"]
    body = [
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="{PALETTE["dark"]}"/>',
        f'<g opacity=".24">{grid_lines(0, 0, w, h, PALETTE["cream"])}</g>',
        chip(72, 66, "03 / PARADIGM SHIFTS", fill="rgba(255,255,255,.08)", stroke="rgba(247,240,229,.22)", color=PALETTE["cream"]),
        block(72, 150, "这周的行业迁移矩阵。", 58, 14, 1.0, PALETTE["cream"], 900),
        block(72, 244, "把六个趋势压成旧问题、新判断、变量和下周观察。信息密度更高，装饰更少，适合飞书文档结语前快速复盘。", 22, 48, 1.45, "rgba(247,240,229,.74)", 500),
    ]
    x0, y0 = 72, 380
    col_widths = [76, 250, 278, 340, 412]
    headers = ["#", "旧问题", "新判断", "变量", "下周观察"]
    row_h = 92
    total_w = sum(col_widths)
    body.append(f'<rect x="{x0}" y="{y0}" width="{total_w}" height="{70 + row_h * len(SHIFTS)}" fill="rgba(255,255,255,.035)" stroke="rgba(247,240,229,.28)"/>')
    cx = x0
    for header, cw in zip(headers, col_widths):
        body.extend([
            f'<rect x="{cx}" y="{y0}" width="{cw}" height="70" fill="rgba(247,240,229,.10)" stroke="rgba(247,240,229,.24)"/>',
            t(cx + 18, y0 + 43, header, 16, PALETTE["cream"], 850),
        ])
        cx += cw
    for idx, ((src, dst, _desc, color), var_text, watch_text) in enumerate(zip(SHIFTS, variables, watch), 1):
        y = y0 + 70 + (idx - 1) * row_h
        cx = x0
        values = [f"{idx:02d}", src, "→ " + dst, var_text, watch_text]
        limits = [3, 17, 19, 18, 30]
        sizes = [20, 16, 16, 15, 15]
        weights = [900, 760, 850, 760, 560]
        for col_idx, (value, cw, limit, size, weight) in enumerate(zip(values, col_widths, limits, sizes, weights)):
            fill = "rgba(247,240,229,.045)" if idx % 2 else "rgba(247,240,229,.025)"
            body.append(f'<rect x="{cx}" y="{y}" width="{cw}" height="{row_h}" fill="{fill}" stroke="rgba(247,240,229,.18)"/>')
            if col_idx == 0:
                body.append(f'<circle cx="{cx+38}" cy="{y+46}" r="22" fill="{PALETTE[color]}" opacity=".82"/>')
                body.append(t(cx + 38, y + 53, value, size, PALETTE["dark"], 900, anchor="middle"))
            else:
                body.append(block(cx + 16, y + 35, value, size, limit, 1.25, "rgba(247,240,229,.82)", weight))
            cx += cw
    return svg_wrap(w, h, "\n".join(body), "AI weekly paradigm shifts")


def make_wechat_header():
    w, h = 1600, 840
    body = [
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="{PALETTE["dark"]}"/>',
        f'<circle cx="410" cy="230" r="110" fill="{PALETTE["red"]}" opacity=".82" filter="url(#soft)"/>',
        f'<circle cx="1160" cy="385" r="180" fill="{PALETTE["blue"]}" opacity=".74" filter="url(#soft)"/>',
        f'<circle cx="760" cy="620" r="128" fill="{PALETTE["green"]}" opacity=".62" filter="url(#soft)"/>',
        f'<path d="M130 720 C420 388 720 552 1040 260 S1320 160 1490 88" fill="none" stroke="{PALETTE["gold"]}" stroke-width="4" opacity=".72"/>',
        f'<g opacity=".24">{grid_lines(0, 0, w, h, PALETTE["cream"])}</g>',
        chip(86, 82, "公众号头图 / AI WEEKLY", fill="rgba(255,255,255,.08)", stroke="rgba(247,240,229,.22)", color=PALETTE["cream"]),
        block(86, 206, "把 Agent 当成熟员工管理", 80, 11, .98, PALETTE["cream"], 900),
        block(92, 514, "Opus 5 删掉 80% 提示词后，行业开始重估 prompt、skills、harness、sandbox、review 和 memory 哪些是真基础设施。", 30, 31, 1.32, "rgba(247,240,229,.78)", 520),
        t(92, 742, "2026.07.21-07.27 / AI 周报趋势总结", 22, "rgba(247,240,229,.62)", 850),
    ]
    return svg_wrap(w, h, "\n".join(body), "WeChat header")


def write_preview():
    assets = [
        ("01-cover.svg", "飞书文档封面主图"),
        ("02-variable-map.svg", "六变量热力图"),
        ("03-trend-cards.svg", "六趋势证据卡"),
        ("04-paradigm-shifts.svg", "行业迁移图"),
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
  <title>飞书文档可视化资产 · AI 周报</title>
  <style>
    body {{ margin: 0; font-family: Inter, system-ui, sans-serif; background: #f4efe4; color: #111318; }}
    header, section {{ padding: 32px; border-bottom: 1px solid rgba(17,19,24,.14); }}
    h1 {{ margin: 0 0 10px; font-size: clamp(34px, 6vw, 72px); line-height: .96; }}
    h2 {{ margin: 0 0 18px; font-size: 24px; }}
    p {{ color: #6e665b; line-height: 1.6; max-width: 860px; }}
    img {{ display: block; width: 100%; height: auto; border: 1px solid rgba(17,19,24,.18); background: #fff; }}
    code {{ background: rgba(255,255,255,.7); padding: 2px 6px; }}
  </style>
</head>
<body>
  <header>
    <h1>飞书文档可视化资产</h1>
    <p>插入顺序建议：<code>01-cover</code> → 正文开场段 → <code>02-variable-map</code> → 每日/每周三到六趋势正文 → <code>03-trend-cards</code> → 结尾或公众号复用 <code>04/05</code>。</p>
  </header>
  {rows}
</body>
</html>
'''
    (OUT / "index.html").write_text(html, encoding="utf-8")


def write_markdown_guide():
    md = """# 飞书文档可视化插入建议

来源周报：`/Users/bytedance/Documents/New project/ai-weekly-2026-07-21-to-07-27.md`

## 插入顺序

1. `01-cover.svg`：放在飞书文档标题下方，作为整篇周报的视觉主图。
2. `02-variable-map.svg`：放在开场判断后，帮助读者先看能力、成本、分发、供给、监管、组织采用六个变量。
3. `03-trend-cards.svg`：放在趋势正文之前或之后，作为六趋势总览。
4. `04-paradigm-shifts.svg`：放在结语前，压缩成本周 from-to 迁移。
5. `05-wechat-header.svg`：公众号 HTML 头图复用版。

## 后续接入

- 飞书文档：SVG 确认后转 PNG/JPEG 上传。
- 公众号 HTML：复用 `05-wechat-header.svg` 做头图，`02/03/04` 作为正文趋势总结图。
- 日报自动化：先确认视觉方向，再接入 `stage9.py` 的 HTML/Feishu 输出步骤。
"""
    (OUT / "README.md").write_text(md, encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "01-cover.svg": make_cover(),
        "02-variable-map.svg": make_variable_map(),
        "03-trend-cards.svg": make_trend_cards(),
        "04-paradigm-shifts.svg": make_paradigm_shifts(),
        "05-wechat-header.svg": make_wechat_header(),
    }
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    write_preview()
    write_markdown_guide()
    for name in [*files.keys(), "index.html", "README.md"]:
        print(OUT / name)


if __name__ == "__main__":
    main()
