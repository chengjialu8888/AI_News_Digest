#!/usr/bin/env python3
"""Goal 9: Render Markdown + CSV daily report for Day 5."""
import json
import csv
import re
from html import escape
from pathlib import Path

DATA_DIR = Path("/data/userdata/daily-report/data")
OUT_DIR = Path("/data/userdata/daily-report/output")
OUT_DIR.mkdir(parents=True, exist_ok=True)

DATE = "2026-06-01"

items = json.loads((DATA_DIR / "07b-deduped.json").read_text(encoding="utf-8"))
qa = json.loads((DATA_DIR / "08-qa-report.json").read_text(encoding="utf-8"))

# Classify into render buckets
def is_fact_board(b):
    return b in ("大厂动向", "初创/融资", "初创", "生态/政策", "生态", "开发者工具")

def is_opinion_board(b):
    return b in ("观点",)

big_co = []        # 🏢 大厂动向
startup = []       # 🚀 初创融资
ecosystem = []     # 🌐 生态政策
devtools = []      # 🛠️ 开发者工具
opinions = []      # 💬 观点
hn_items = []      # HN 共识
builders = []      # 🌍 海外建设者(空,因 03 缺失)

for it in items:
    b = it.get("board", "")
    if it.get("consensus"):
        hn_items.append(it)
    elif b == "大厂动向":
        big_co.append(it)
    elif b in ("初创/融资", "初创"):
        startup.append(it)
    elif b in ("生态/政策", "生态"):
        ecosystem.append(it)
    elif b == "开发者工具":
        devtools.append(it)
    elif b == "观点":
        opinions.append(it)

# Sort: 🔴 first, then 🟡, then ⚪
SIGNAL_ORDER = {"🔴": 0, "🟡": 1, "⚪": 2}
def sort_key(x):
    return (SIGNAL_ORDER.get(x.get("signal_level", "⚪"), 3),
            -(x.get("points", 0) or 0))

for arr in (big_co, startup, ecosystem, devtools, opinions, hn_items):
    arr.sort(key=sort_key)


def fmt_item(it, idx=None):
    sig = it.get("signal_level", "⚪")
    title = it.get("title", "")
    url = it.get("url", "")
    src = it.get("source", "") or "未知来源"
    summary = it.get("summary", "") or ""
    cv = " ✅多源" if it.get("cross_validated") else ""
    head = f"- {sig} **{title}**{cv}"
    if summary:
        head += f"\n  {summary}"
    if url:
        head += f" [[{src}]]({url})"
    return head


def compact(text, limit=120, ellipsis=True):
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= limit:
        return text
    if not ellipsis:
        return text[:limit].rstrip()
    return text[: limit - 1].rstrip() + "..."


def item_link(it):
    title = it.get("title", "")
    url = it.get("url", "")
    return f"[{title}]({url})" if url else title


# Top-level summary
red_count = sum(1 for it in items if it["signal_level"] == "🔴")
yellow_count = sum(1 for it in items if it["signal_level"] == "🟡")
total = len(items)

# One-liner: data-driven
top_titles = []
for it in items:
    if it["signal_level"] == "🔴":
        top_titles.append(it["title"])
    if len(top_titles) >= 3:
        break
if not top_titles:
    for it in items:
        if it["signal_level"] == "🟡":
            top_titles.append(it["title"])
        if len(top_titles) >= 3:
            break

focus_titles = " | ".join(t[:26] for t in top_titles[:3])
one_liner = (
    f"今日共汇总 {total} 条 AI 行业资讯（🔴重磅 {red_count} / 🟡值得关注 {yellow_count}）。"
    f"读法：先判断这些信号是否改变能力、成本、分发或组织采用，再看新闻本身：{focus_titles}"
)

# Build Markdown
md = []
md.append(f"# 📅 AI 行业日报 · {DATE}\n")
md.append(f"> {one_liner}\n")

# Summary stats
md.append("## 📊 今日概览\n")
md.append(f"- 总条目: **{total}**")
md.append(f"- 🔴 重磅: {red_count} 条 / 🟡 值得关注: {yellow_count} 条 / ⚪ 常规: {total - red_count - yellow_count} 条")
md.append(f"- 板块覆盖: {', '.join(sorted({it.get('board','?') for it in items}))}")
cv_count = sum(1 for it in items if it.get("cross_validated"))
md.append(f"- 多源交叉验证: {cv_count} 条\n")

# Section 1: 📰 偏 fact 类
md.append("## 📰 偏 Fact 类\n")

if big_co:
    md.append("### 🏢 大厂动向\n")
    for it in big_co:
        md.append(fmt_item(it))
    md.append("")

if startup:
    md.append("### 🚀 初创/融资\n")
    for it in startup:
        md.append(fmt_item(it))
    md.append("")

if ecosystem:
    md.append("### 🌐 生态/政策\n")
    for it in ecosystem:
        md.append(fmt_item(it))
    md.append("")

if devtools:
    md.append("### 🛠️ 开发者工具\n")
    for it in devtools:
        md.append(fmt_item(it))
    md.append("")

# Section 2: 💬 偏观点类（含 HN）
md.append("## 💬 偏观点类\n")
if opinions:
    md.append("### 行业观察\n")
    for it in opinions:
        md.append(fmt_item(it))
    md.append("")

if hn_items:
    md.append("### [HN 共识] 海外社区高热讨论\n")
    for it in hn_items:
        sig = it.get("signal_level", "⚪")
        md.append(f"#### {sig} {it['title']}")
        md.append(f"> 🔥 {it.get('points',0)} pts / 💬 {it.get('comment_count',0)} 评论 · [[Hacker News]]({it['url']})\n")
        md.append("**社区共识:**")
        for c in it.get("consensus", []):
            md.append(f"- {c}")
        md.append("")
        adv = it.get("action_advice", {})
        if adv:
            md.append("**行动建议:**")
            md.append(f"- 🔨 Builder: {adv.get('builder','—')}")
            md.append(f"- 👥 团队: {adv.get('team','—')}")
            md.append(f"- 💰 投资者: {adv.get('investor','—')}")
        md.append("")

# Section 3: 🌍 海外建设者动态
md.append("## 🌍 海外建设者动态\n")
if builders:
    for it in builders:
        md.append(fmt_item(it))
    md.append("")
else:
    md.append("> 本日 03-builder 信源未采集到数据,海外建设者动态由 HN 共识章节代为承载。\n")

# Section 4: 📊 质量审核报告
md.append("## 📊 质量审核报告\n")
md.append(f"**整体状态: {qa['overall_status']}**  ·  通过 Gate: {qa['passed_items']}/5  ·  Flag: {qa['flagged_items']}\n")
md.append("| Gate | 状态 | 关键发现 |")
md.append("|---|---|---|")
gate_label = {
    "gate1_data_health": "数据源健康",
    "gate2_dedup_verify": "去重验证",
    "gate3_signal_review": "信号分级复核",
    "gate4_fact_check": "事实核验",
    "gate5_completeness": "完整性自检",
}
for gname, ginfo in qa["gates"].items():
    label = gate_label.get(gname, gname)
    issues = ginfo.get("issues", [])
    finding = "无问题" if not issues else f"{len(issues)} 项: {issues[0][:40]}{'...' if len(issues[0])>40 else ''}"
    md.append(f"| {label} | {ginfo['status']} | {finding} |")
md.append("")

# Section 5: 📌 三大关键趋势
md.append("## 📌 三大关键趋势\n")

# Auto-derive 3 trends from highest-priority items
trends = []
# Trend 1: based on big enterprise + cross-validated items
trend1_signals = [it for it in items if it["signal_level"] in ("🔴", "🟡") and it.get("board") == "大厂动向"][:3]
if trend1_signals:
    trends.append({
        "title": "巨头加速产品化与垂直整合",
        "desc": "OpenAI/Anthropic/Google 等头部公司本日密集发布产品级能力与生态合作,从模型层向应用层、桌面控制、第三方集成、企业战略合作全面下沉,验证了 HN 共识中 *AI is a technology not a product* 的判断:基础模型公司正在向应用层转型,价值锚正在从 API 调用上移到产品矩阵和分发渠道。",
        "evidence": [it["title"] for it in trend1_signals[:3]],
    })
# Trend 2: developer tools and agent infra
trend2_signals = [it for it in items if it.get("board") == "开发者工具"][:3]
if trend2_signals:
    trends.append({
        "title": "Agent 基础设施进入工程化深水区",
        "desc": "本日开发者工具板块密集出现 Vercel Zero(AI 智能体专用语言)、Headroom(token 压缩)、Lighthouse Attention(17x 加速)、Fin 元智能体管理、OpenRouter 人机协作等基础设施级方案。Agent 系统的工程瓶颈(token 成本、上下文管理、协作编排、推理加速)正在被系统性解决,标志着从 demo 走向生产部署的阶段拐点。",
        "evidence": [it["title"] for it in trend2_signals[:3]],
    })
# Trend 3: AI economic + societal disruption from HN
trend3_signals = hn_items[:3]
if trend3_signals:
    trends.append({
        "title": "AI 经济与社会冲击加速显化",
        "desc": "HN 高热讨论集中在 AI 落地的负面外部性:订阅模式不可持续(Per-seat 失效)、流程提效幻觉(管理层预期与执行落差)、AI 内容污染开源生态(GitHub spam)、AI 主播替代人类 DJ。叠加 Eric Schmidt 毕业典礼演讲被嘘、AI 相关岗位裁员潮等社会信号,2026 年 AI 行业的核心矛盾从 *能不能* 转向 *怎么共处*。",
        "evidence": [it["title"] for it in trend3_signals[:3]],
    })

for i, t in enumerate(trends, 1):
    md.append(f"### 趋势 {i}: {t['title']}\n")
    md.append(f"- 🎯 **核心观点**：{t['desc']}")
    md.append("- 🧭 **批判性判断**：说明能力、成本、分发、供给、监管、组织采用中哪一个变量真的变化；如果只有发布热闹、口径未核验或缺少采用证据，只能作为判断线索，不能写成确定结论。")
    md.append("- 🔎 **下周观察**：看支撑事件是否转化为可验证的产品采用、价格变化、开发者迁移、监管反馈或客户续费/流失信号。\n")
    md.append("**关键佐证:**")
    for e in t["evidence"]:
        md.append(f"- {e}")
    md.append("")

md.append("---")
md.append(f"*由 AI 日报 Pipeline 自动生成 · 数据日期 {DATE} · QA 状态 {qa['overall_status']}*")

md_text = "\n".join(md)
md_path = OUT_DIR / "daily-report.md"
md_path.write_text(md_text, encoding="utf-8")

# CSV: 12 columns
csv_path = OUT_DIR / "daily-report.csv"
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["日期", "编号", "板块", "标题", "信号等级", "事实核验", "关联公司", "关联赛道", "来源", "原文URL", "摘要", "是否推送"])

    COMPANIES = ["OpenAI", "Anthropic", "Google", "Microsoft", "Meta", "NVIDIA", "DeepSeek",
                 "Cerebras", "Runway", "Vercel", "字节跳动", "xAI", "YouTube", "Vatican",
                 "教皇", "OpenRouter", "OpenClaw", "GitHub"]
    TRACKS = {"大模型": ["claude", "gpt", "gemini", "deepseek", "llm", "model", "kimi", "qwen", "grok"],
              "Agent/具身智能": ["agent", "智能体", "codex", "computer use"],
              "AI视频/音频": ["video", "音频", "audio", "weights.gg", "voice", "radio", "广播"],
              "AI硬件/芯片": ["cerebras", "nvidia", "芯片", "chip", "tpu"],
              "AI编程": ["claude code", "code", "copilot", "vercel", "编程", "headroom"],
              "AI安全": ["safety", "security", "deepfake", "mdash", "vulnerability", "spam"],
              "融资": ["融资", "估值", "ipo", "raise", "billion", "美元"],
              "AI政策": ["policy", "通谕", "梵蒂冈", "regulation", "法规"],
              "企业AI": ["enterprise", "企业", "subscription", "saas"]}

    for idx, it in enumerate(items, 1):
        text = (it.get("title", "") + " " + it.get("summary", "")).lower()
        title = it.get("title", "")
        # Companies
        comps = [c for c in COMPANIES if c.lower() in text]
        # Tracks
        tracks = []
        for tn, kws in TRACKS.items():
            if any(kw in text for kw in kws):
                tracks.append(tn)
        # Fact verification: ✅ if cross_validated, otherwise —
        fact = "✅" if it.get("cross_validated") else "—"
        # Push: 是 if 🔴 or 🟡
        push = "是" if it.get("signal_level") in ("🔴", "🟡") else "否"
        # Summary fallback
        summ = it.get("summary", "")
        if not summ and it.get("consensus"):
            summ = "HN 共识: " + " | ".join(it["consensus"][:3])

        w.writerow([
            it.get("date", DATE),
            f"D{idx:03d}",
            it.get("board", ""),
            title,
            it.get("signal_level", ""),
            fact,
            "; ".join(comps) if comps else "—",
            "; ".join(tracks) if tracks else "—",
            it.get("source", ""),
            it.get("url", ""),
            summ,
            push,
        ])

def render_feishu_card():
    push_items = [it for it in items if it.get("signal_level") in ("🔴", "🟡")][:8]
    lines = [
        f"# {DATE.replace('-', '/')} Newsrun",
        "",
        f"> {DATE.replace('-', '/')} Newsrun：{total} 条 AI 新闻，{red_count} 条高影响。",
        "",
        "## 今日主线",
        one_liner,
        "",
        "## 顶部指标",
        f"- 新闻条目：{total}",
        f"- 高影响：{red_count}",
        f"- 今天就做：{sum(1 for it in items if it.get('board') == '今天就做')}",
        "",
        "## 推送卡片正文",
    ]
    for it in push_items:
        lines.append(f"- {it.get('signal_level', '⚪')} {item_link(it)} - {compact(it.get('summary'), 80, ellipsis=False)}")
    lines.extend([
        "",
        "## 点击与按钮规则",
        "- 默认 open_url：当日飞书详细版文档 URL（生成卡片时由 `detailed_report_doc` 注入）。",
        "- 底部按钮：长期趋势沉淀 -> https://bytedance.larkoffice.com/docx/JPs1dxjemo6HWMxn1mncxBOEnhg",
    ])
    return "\n".join(lines)


def render_structured_archive():
    lines = [
        "---",
        f"date: {DATE}",
        "type: ai-newsrun-archive",
        f"items: {total}",
        f"high_signal: {red_count}",
        f"qa_status: {qa.get('overall_status')}",
        "---",
        "",
        f"# AI 日报结构化沉淀 · {DATE}",
        "",
        "## 长期趋势索引",
        one_liner,
        "",
        "## 结构化条目",
    ]
    for board in sorted({it.get("board", "未分类") for it in items}):
        board_items = [it for it in items if it.get("board", "未分类") == board]
        lines.append(f"### {board}")
        for it in board_items:
            lines.append(f"- {it.get('signal_level', '⚪')} {item_link(it)}")
            lines.append(f"  - 摘要：{compact(it.get('summary'), 160)}")
            lines.append(f"  - 来源：{it.get('source', '未知来源')}；事实核验：{'多源验证' if it.get('cross_validated') else '待复核'}")
        lines.append("")
    lines.extend([
        "## 运营字段",
        "- 可进入 CSV / Base / 知识库的字段：日期、板块、标题、信号等级、事实核验、关联公司、关联赛道、来源、URL、摘要、是否推送。",
        "- 长期沉淀目的：复盘趋势命中率、追踪公司/赛道变化、沉淀选题池和团队运营素材。",
    ])
    return "\n".join(lines)


def render_html(markdown_text):
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI 行业日报 · {escape(DATE)}</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #172033; background: #f6f7fb; }}
    main {{ max-width: 920px; margin: 0 auto; padding: 40px 20px 64px; }}
    article {{ background: #fff; border: 1px solid #e5e8f0; border-radius: 8px; padding: 28px; box-shadow: 0 16px 40px rgba(23, 32, 51, .06); }}
    pre {{ white-space: pre-wrap; word-wrap: break-word; line-height: 1.7; font: 15px/1.7 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
  </style>
</head>
<body>
  <main>
    <article>
      <pre>{escape(markdown_text)}</pre>
    </article>
  </main>
</body>
</html>
"""


feishu_card_path = OUT_DIR / "feishu-card.md"
structured_archive_path = OUT_DIR / "structured-archive.md"
html_path = OUT_DIR / "daily-report.html"
feishu_card_path.write_text(render_feishu_card(), encoding="utf-8")
structured_archive_path.write_text(render_structured_archive(), encoding="utf-8")
html_path.write_text(render_html(md_text), encoding="utf-8")

# Stats
md_size = md_path.stat().st_size
csv_lines = sum(1 for _ in open(csv_path, encoding="utf-8-sig"))

print(f"✅ Markdown 日报已写入: {md_path}")
print(f"   字符数: {len(md_text)}")
print(f"✅ CSV 文件已写入: {csv_path}")
print(f"   总行数: {csv_lines} (含表头)")
print(f"✅ 飞书卡片草稿已写入: {feishu_card_path}")
print(f"✅ 结构化沉淀文档已写入: {structured_archive_path}")
print(f"✅ HTML 日报已写入: {html_path}")

# Verify completion conditions
print("\n=== 完成条件验证 ===")
print(f"  [{'✓' if (DATA_DIR/'06-hn-consensus.json').exists() else '✗'}] 06 JSON 存在")
print(f"  [{'✓' if (DATA_DIR/'07-merged.json').exists() else '✗'}] 07 JSON 存在")
print(f"  [{'✓' if (DATA_DIR/'08-qa-report.json').exists() else '✗'}] 08 JSON 存在")
print(f"  [{'✓' if len(md_text) > 2000 else '✗'}] daily-report.md > 2000 字符 (实际 {len(md_text)})")
with open(csv_path, encoding="utf-8-sig") as f:
    header = next(csv.reader(f))
print(f"  [{'✓' if len(header) == 12 else '✗'}] CSV 包含 12 列 (实际 {len(header)})")
print(f"  [{'✓' if '📌 三大关键趋势' in md_text else '✗'}] MD 末尾含「📌 三大关键趋势」章节")
print(f"  [{'✓' if feishu_card_path.exists() else '✗'}] feishu-card.md 存在")
print(f"  [{'✓' if structured_archive_path.exists() else '✗'}] structured-archive.md 存在")
print(f"  [{'✓' if html_path.exists() else '✗'}] daily-report.html 存在")
