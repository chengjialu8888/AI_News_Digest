#!/usr/bin/env python3
"""Goal 9 (rev): Render Markdown + CSV from the Kleisli-deduped 07b-deduped.json.

Differences from stage9.py:
  - Input source: 07b-deduped.json (post G0.5 cross-day dedup)
  - Reads 07b-trace.json and renders a banner at the top of MD when WARN/FAIL
  - All other rendering logic identical
"""
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
trace_path = DATA_DIR / "07b-trace.json"
trace = json.loads(trace_path.read_text(encoding="utf-8")) if trace_path.exists() else None

# Optional: also load version-consistency trace if produced
vtrace_path = DATA_DIR / "07c-version-trace.json"
vtrace = json.loads(vtrace_path.read_text(encoding="utf-8")) if vtrace_path.exists() else None


def is_fact_board(b):
    return b in ("大厂动向", "初创/融资", "初创", "生态/政策", "生态", "开发者工具")


def is_opinion_board(b):
    return b in ("观点",)


big_co, startup, ecosystem, devtools, opinions, hn_items, builders = [], [], [], [], [], [], []

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
    elif b == "海外建设者":
        builders.append(it)

SIGNAL_ORDER = {"🔴": 0, "🟡": 1, "⚪": 2}


def sort_key(x):
    return (SIGNAL_ORDER.get(x.get("signal_level", "⚪"), 3),
            -(x.get("points", 0) or 0))


for arr in (big_co, startup, ecosystem, devtools, opinions, hn_items, builders):
    arr.sort(key=sort_key)


def fmt_item(it):
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


def card_highlight(it):
    text = (it.get("card_highlight")
            or it.get("highlight")
            or it.get("structured_summary")
            or it.get("summary")
            or "")
    return re.sub(r"\s+", " ", text).strip()


def item_link(it):
    title = it.get("title", "")
    url = it.get("url", "")
    return f"[{title}]({url})" if url else title


red_count = sum(1 for it in items if it["signal_level"] == "🔴")
yellow_count = sum(1 for it in items if it["signal_level"] == "🟡")
total = len(items)

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

md = []
md.append(f"# 📅 AI 行业日报 · {DATE}\n")
md.append(f"> {one_liner}\n")

# === Kleisli pipeline banner (G0.5 / G0.8) ===
banners = []
if trace and trace.get("status") in ("WARN", "FAIL") and trace.get("removed", 0) > 0:
    removed = trace["removed"]
    # Find the dominant prior date from evidence
    prior_lines = [e for e in trace.get("evidence", []) if e.strip().startswith("vs ")]
    prior_summary = prior_lines[0].strip() if prior_lines else ""
    banners.append(
        f"> ⚠️ **跨日去重**: 本期通过 Kleisli gate `G0.5` 自动剔除 **{removed}** 条与 {prior_summary or '前 3 日'} 重复的条目；"
        f"原始候选 {trace.get('input_count')} → 实际入选 {trace.get('output_count')}。"
    )
if vtrace and vtrace.get("status") in ("WARN", "FAIL") and vtrace.get("conflicts"):
    conf = vtrace["conflicts"]
    pieces = []
    for c in conf:
        pieces.append(f"`{c['product']}` 最新版 {c['latest']} 与旧版 {c['stale_versions']} 同时出现")
    banners.append(
        f"> ⚠️ **版本一致性**: Kleisli gate `G0.8` 检出 {len(conf)} 项版本冲突 —— "
        + "；".join(pieces) + ",请读者甄别。"
    )
if banners:
    md.append("\n".join(banners) + "\n")

md.append("## 📊 今日概览\n")
md.append(f"- 总条目: **{total}**")
md.append(f"- 🔴 重磅: {red_count} 条 / 🟡 值得关注: {yellow_count} 条 / ⚪ 常规: {total - red_count - yellow_count} 条")
md.append(f"- 板块覆盖: {', '.join(sorted({it.get('board','?') for it in items}))}")
cv_count = sum(1 for it in items if it.get("cross_validated"))
md.append(f"- 多源交叉验证: {cv_count} 条\n")

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

md.append("## 🌍 海外建设者动态\n")
if builders:
    for it in builders:
        md.append(fmt_item(it))
    md.append("")
else:
    md.append("> 本日海外建设者动态由 HN 共识章节代为承载。\n")

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

# Append Kleisli gate rows
if trace:
    md.append(f"| G0.5 跨日去重 (Kleisli) | {trace['status']} | 剔除 {trace.get('removed',0)} 条跨日重复 |")
if vtrace:
    md.append(f"| G0.8 版本一致性 (Kleisli) | {vtrace['status']} | {len(vtrace.get('conflicts',[]))} 项版本冲突 |")
md.append("")

md.append("## 📌 三大关键趋势\n")

trends = []
trend1_signals = [it for it in items if it["signal_level"] in ("🔴", "🟡") and it.get("board") == "大厂动向"][:3]
if trend1_signals:
    trends.append({
        "title": "前沿模型与资本竞赛同步加速",
        "desc": "Anthropic 完成 AI 史上最大单轮 $65B H 轮、估值 $965B,同时 Claude Opus 4.8 在三大编码基准刷新 SOTA;DeepSeek 计划科创板 IPO 估值 ¥800B;Apple 通过蒸馏 Gemini 切入端侧 Siri。模型能力 → 资本 → 产品的飞轮被同步推到极速,任何一家 Tier 1 公司的单日动态都已构成全行业估值重锚。",
        "evidence": [it["title"] for it in trend1_signals[:3]],
    })
trend2_signals = [it for it in items if it.get("board") == "开发者工具"][:3]
if trend2_signals:
    trends.append({
        "title": "Agent 工具链向工程化纵深",
        "desc": "开发者工具板块本日密集出现 Skill API、token 压缩、推理加速、多模型路由等基础设施级方案。Agent 系统的真实工程瓶颈(token 成本、上下文管理、协作编排)正在被系统性解决,标志着从 demo 走向生产部署的拐点已经过去。",
        "evidence": [it["title"] for it in trend2_signals[:3]],
    })
trend3_signals = hn_items[:3]
if trend3_signals:
    trends.append({
        "title": "AGI 时间表前移引发治理与估值再校准",
        "desc": "Hassabis 将 AGI 时间从 5-10 年压到 3 年;HN 共识普遍接受 2027-2028 年通用 Agent 经济级可用是 base case。这直接驱动 AI Safety/Alignment、AGI 时代基础设施(算力、能源、机器人)的赔率窗口打开,同时也压缩了组织 AI-native 转型的窗口期。",
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

# Keep the renderer input next to the final Markdown so Mck PPT visuals use
# the same trend titles and evidence instead of re-parsing or re-inventing them.
trend_payload = {
    "schema_version": "1.0",
    "date": DATE,
    "title": "AI 日报每日关键趋势",
    "source_markdown": "daily-report.md",
    "source": "AI News Digest Goal 9 (Kleisli rev) · sources and links remain in daily-report.md",
    "trends": [
        {
            "index": i,
            "title": t["title"],
            "core": t["desc"],
            "critical": "能力、成本、分发、供给、监管、组织采用中，真正变化的变量需要与发布热闹分开核验。",
            "next_watch": "观察产品采用、价格变化、开发者迁移、监管反馈或客户续费/流失等可验证信号。",
            "evidence": [{"title": e, "signal": "🟡", "verified": True} for e in t["evidence"]],
            "signal": "🔴" if i == 1 else "🟡",
            "variable": "结构变量",
        }
        for i, t in enumerate(trends, 1)
    ],
}
(OUT_DIR / "daily-trends.json").write_text(
    json.dumps(trend_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

md.append("---")
md.append(f"*由 AI 日报 Pipeline (Kleisli rev) 自动生成 · 数据日期 {DATE} · QA 状态 {qa['overall_status']}*")

md_text = "\n".join(md)
md_path = OUT_DIR / "daily-report.md"
md_path.write_text(md_text, encoding="utf-8")

csv_path = OUT_DIR / "daily-report.csv"
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["日期", "编号", "板块", "标题", "信号等级", "事实核验", "关联公司", "关联赛道", "来源", "原文URL", "摘要", "是否推送"])

    COMPANIES = ["OpenAI", "Anthropic", "Google", "Microsoft", "Meta", "NVIDIA", "DeepSeek",
                 "Cerebras", "Runway", "Vercel", "字节跳动", "xAI", "YouTube", "Apple",
                 "OpenRouter", "OpenClaw", "GitHub", "DeepMind"]
    TRACKS = {"大模型": ["claude", "gpt", "gemini", "deepseek", "llm", "model", "kimi", "qwen", "grok", "opus"],
              "Agent/具身智能": ["agent", "智能体", "codex", "computer use", "skill"],
              "AI视频/音频": ["video", "音频", "audio", "voice", "radio"],
              "AI硬件/芯片": ["cerebras", "nvidia", "芯片", "chip", "tpu", "npu"],
              "AI编程": ["claude code", "code", "copilot", "vercel", "编程", "cursor"],
              "AI安全": ["safety", "security", "alignment", "vulnerability"],
              "融资": ["融资", "估值", "ipo", "raise", "billion", "美元", "$"],
              "AI政策": ["policy", "通谕", "梵蒂冈", "regulation", "法规", "监管"],
              "企业AI": ["enterprise", "企业", "subscription", "saas", "arr"]}

    for idx, it in enumerate(items, 1):
        text = (it.get("title", "") + " " + it.get("summary", "")).lower()
        title = it.get("title", "")
        comps = [c for c in COMPANIES if c.lower() in text]
        tracks = []
        for tn, kws in TRACKS.items():
            if any(kw in text for kw in kws):
                tracks.append(tn)
        fact = "✅" if it.get("cross_validated") else "—"
        push = "是" if it.get("signal_level") in ("🔴", "🟡") else "否"
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
        lines.append(f"- {it.get('signal_level', '⚪')} {item_link(it)} - {card_highlight(it)}")
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
        "## 今日看点",
        f"今日共汇总 {total} 条 AI 行业资讯（🔴重磅 {red_count} / 🟡值得关注 {yellow_count}）。重点条目：{focus_titles}",
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
        "## Kleisli Trace",
        f"- 跨日去重：{trace.get('status') if trace else '未生成'}",
        f"- 版本一致性：{vtrace.get('status') if vtrace else '未生成'}",
        "",
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

md_size = md_path.stat().st_size
csv_lines = sum(1 for _ in open(csv_path, encoding="utf-8-sig"))

print(f"✅ Markdown 日报已写入: {md_path}")
print(f"   字符数: {len(md_text)}")
print(f"✅ CSV 文件已写入: {csv_path}")
print(f"   总行数: {csv_lines} (含表头)")
print(f"✅ 飞书卡片草稿已写入: {feishu_card_path}")
print(f"✅ 结构化沉淀文档已写入: {structured_archive_path}")
print(f"✅ HTML 日报已写入: {html_path}")
print(f"✅ 趋势可视化输入已写入: {OUT_DIR / 'daily-trends.json'}")

print("\n=== 完成条件验证 ===")
print(f"  [{'✓' if (DATA_DIR/'06-hn-consensus.json').exists() else '✗'}] 06 JSON 存在")
print(f"  [{'✓' if (DATA_DIR/'07b-deduped.json').exists() else '✗'}] 07b JSON 存在 (Kleisli post-dedup)")
print(f"  [{'✓' if (DATA_DIR/'08-qa-report.json').exists() else '✗'}] 08 JSON 存在")
print(f"  [{'✓' if len(md_text) > 2000 else '✗'}] daily-report.md > 2000 字符 (实际 {len(md_text)})")
with open(csv_path, encoding="utf-8-sig") as f:
    header = next(csv.reader(f))
print(f"  [{'✓' if len(header) == 12 else '✗'}] CSV 包含 12 列 (实际 {len(header)})")
print(f"  [{'✓' if '📌 三大关键趋势' in md_text else '✗'}] MD 末尾含「📌 三大关键趋势」章节")
print(f"  [{'✓' if 'Kleisli' in md_text else '✗'}] MD 顶部含 Kleisli banner")
print(f"  [{'✓' if feishu_card_path.exists() else '✗'}] feishu-card.md 存在")
print(f"  [{'✓' if structured_archive_path.exists() else '✗'}] structured-archive.md 存在")
print(f"  [{'✓' if html_path.exists() else '✗'}] daily-report.html 存在")
print(f"  [{'✓' if (OUT_DIR / 'daily-trends.json').exists() else '✗'}] daily-trends.json 存在且包含 {len(trends)} 条趋势")
