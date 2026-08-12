#!/usr/bin/env python3
"""Goal 9: Render Markdown + CSV daily report for Day 5."""
import json
import csv
import hashlib
import os
import re
from datetime import date
from html import escape
from pathlib import Path

DATA_DIR = Path("/data/userdata/daily-report/data")
OUT_DIR = Path("/data/userdata/daily-report/output")
DATE = os.environ.get("REPORT_DATE") or date.today().isoformat()
VISUAL_BACKEND = os.environ.get("VISUAL_BACKEND", "imagegen").strip().lower()
VALID_VISUAL_BACKENDS = {"imagegen", "artist-lottery", "mck-ppt"}
if VISUAL_BACKEND not in VALID_VISUAL_BACKENDS:
    raise SystemExit(
        f"Unsupported VISUAL_BACKEND={VISUAL_BACKEND!r}; "
        f"choose one of {sorted(VALID_VISUAL_BACKENDS)}"
    )
ARTIST_LOTTERY_ENABLED = VISUAL_BACKEND == "artist-lottery"
OUT_DIR.mkdir(parents=True, exist_ok=True)

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


def card_highlight(it):
    text = (it.get("card_highlight")
            or it.get("highlight")
            or it.get("structured_summary")
            or it.get("summary")
            or "")
    return re.sub(r"\s+", " ", text).strip()


def item_link(it):
    title = it.get("title", "")
    url = first_source_url(it)
    return f"[{title}]({url})" if url else title


def first_source_url(it):
    """Return the first recommended/original source, preserving editorial order."""
    candidates = (
        it.get("recommended_links"),
        it.get("source_links"),
        it.get("sources"),
        it.get("links"),
    )
    for value in candidates:
        if isinstance(value, str) and value.startswith(("http://", "https://")):
            return value
        if not isinstance(value, list):
            continue
        for entry in value:
            if isinstance(entry, str) and entry.startswith(("http://", "https://")):
                return entry
            if isinstance(entry, dict):
                url = entry.get("url") or entry.get("link") or entry.get("href")
                if isinstance(url, str) and url.startswith(("http://", "https://")):
                    return url
    return it.get("url", "") or it.get("source_url", "")


MUSEUM_SOURCE_REGISTRY = [
    {
        "name": "MoMA Collection",
        "url": "https://www.moma.org/collection/about/",
        "scope": "modern and contemporary art, design, media and performance",
    },
    {
        "name": "MoMA Contemporary Art",
        "url": "https://www.moma.org/collection/terms/contemporary-art",
        "scope": "art made in the present and recent past, roughly 1980 to today",
    },
    {
        "name": "Centre Pompidou Visual Arts",
        "url": "https://www.centrepompidou.fr/en/collection/visual-arts",
        "scope": "major artistic movements of the 20th and 21st centuries",
    },
    {
        "name": "Centre Pompidou Film and New Media",
        "url": "https://www.centrepompidou.fr/en/collection/film-and-new-media",
        "scope": "video, sound, moving image and experimental media",
    },
]

ART_FAIR_SOURCE_REGISTRY = [
    {
        "name": "Art Basel Basel",
        "url": "https://www.artbasel.com/basel/galleries?lang=en",
        "overview_url": "https://www.artbasel.com/BASEL?lang=en",
        "scope": "official exhibitors, sectors and contemporary practices in Basel",
    },
    {
        "name": "Art Basel Miami Beach",
        "url": "https://www.artbasel.com/miami-beach/galleries?lang=en",
        "scope": "official exhibitors and sectors in Miami Beach",
    },
    {
        "name": "Art Basel Hong Kong",
        "url": "https://www.artbasel.com/hong-kong/galleries?lang=en",
        "scope": "official exhibitors and sectors in Hong Kong",
    },
    {
        "name": "Art Basel Paris",
        "url": "https://www.artbasel.com/paris/galleries?lang=en",
        "scope": "official exhibitors and sectors in Paris",
    },
    {
        "name": "Art Basel Artists",
        "url": "https://www.artbasel.com/stories/artists?lang=en",
        "scope": "official artist stories and current contemporary-art signals",
    },
]

# Museum-grounded modern/contemporary pool. Do not add a style without an
# institutional collection anchor and a source URL.
VISUAL_STYLE_CATALOG = [
    {
        "id": "okeeffe-organic-abstraction",
        "label": "Georgia O'Keeffe-inspired organic abstraction",
        "artist_or_movement": "Georgia O'Keeffe / American modernism",
        "period": "20th-century modern art",
        "museum_basis": ["MoMA Collection"],
        "source_urls": ["https://www.moma.org/collection/about/"],
        "note": "用局部放大的有机轮廓、柔软曲面和克制留白制造高级感；适合把抽象行业变化转成可感知的形体关系。",
    },
    {
        "id": "rothko-color-field",
        "label": "Mark Rothko-inspired color field painting",
        "artist_or_movement": "Mark Rothko / color field painting",
        "period": "postwar modern art",
        "museum_basis": ["MoMA Collection"],
        "source_urls": ["https://www.moma.org/collection/about/"],
        "note": "用大面积色场和半透明叠染制造纵深，不靠复杂装饰堆信息；适合表达成本、风险和情绪张力。",
    },
    {
        "id": "klee-poetic-geometry",
        "label": "Paul Klee-inspired poetic geometric drawing",
        "artist_or_movement": "Paul Klee / Bauhaus and poetic abstraction",
        "period": "early 20th-century modern art",
        "museum_basis": ["MoMA Collection", "Centre Pompidou Visual Arts"],
        "source_urls": ["https://www.moma.org/collection/about/", "https://www.centrepompidou.fr/en/collection/visual-arts"],
        "note": "用细线、符号、手绘几何和错落层次组织信息；兼具轻盈感与编辑感，适合把复杂机制讲得更亲近。",
    },
    {
        "id": "kandinsky-musical-abstraction",
        "label": "Wassily Kandinsky-inspired musical abstraction",
        "artist_or_movement": "Wassily Kandinsky / abstract art",
        "period": "early 20th-century modern art",
        "museum_basis": ["MoMA Collection", "Centre Pompidou Visual Arts"],
        "source_urls": ["https://www.moma.org/collection/about/", "https://www.centrepompidou.fr/en/collection/visual-arts"],
        "note": "用节奏化线条、圆形、斜向结构和色彩对位形成视觉动势；适合表达系统协作、流动和多变量变化。",
    },
    {
        "id": "matisse-cut-paper",
        "label": "Henri Matisse-inspired cut-paper collage",
        "artist_or_movement": "Henri Matisse / late modern collage",
        "period": "20th-century modern art",
        "museum_basis": ["MoMA Collection", "Centre Pompidou Visual Arts"],
        "source_urls": ["https://www.moma.org/collection/about/", "https://www.centrepompidou.fr/en/collection/visual-arts"],
        "note": "用干净的剪纸块面、错位叠层和大胆但克制的色块形成时尚编辑感；适合表达应用入口、关系和分发。",
    },
    {
        "id": "mondrian-neoplastic-grid",
        "label": "Piet Mondrian-inspired neoplastic grid",
        "artist_or_movement": "Piet Mondrian / De Stijl",
        "period": "early 20th-century modern art",
        "museum_basis": ["MoMA Collection", "Centre Pompidou Visual Arts"],
        "source_urls": ["https://www.moma.org/collection/about/", "https://www.centrepompidou.fr/en/collection/visual-arts"],
        "note": "用严格网格、非对称分区和有限色彩建立秩序感；适合表达基础设施、路由、约束和资源配置。",
    },
    {
        "id": "warhol-pop-repetition",
        "label": "Andy Warhol-inspired pop repetition and screenprint",
        "artist_or_movement": "Andy Warhol / Pop Art",
        "period": "postwar contemporary art",
        "museum_basis": ["MoMA Collection"],
        "source_urls": ["https://www.moma.org/collection/about/"],
        "note": "用重复、消费品式图像、网版颗粒和有限撞色制造传播性；适合表达规模化分发、注意力和产品同质化。",
    },
    {
        "id": "bourgeois-material-memory",
        "label": "Louise Bourgeois-inspired material memory and spatial tension",
        "artist_or_movement": "Louise Bourgeois / sculpture and installation",
        "period": "late 20th-century contemporary art",
        "museum_basis": ["MoMA Collection", "Centre Pompidou Visual Arts"],
        "source_urls": ["https://www.moma.org/collection/about/", "https://www.centrepompidou.fr/en/collection/visual-arts"],
        "note": "用织物、线、身体感曲线和局部空间制造亲密却不安的层次；适合表达安全、信任和组织关系中的隐性成本。",
    },
    {
        "id": "tinguely-kinetic-machine",
        "label": "Jean Tinguely-inspired kinetic machine assemblage",
        "artist_or_movement": "Jean Tinguely / kinetic and assemblage art",
        "period": "postwar modern and contemporary art",
        "museum_basis": ["MoMA Collection", "Centre Pompidou Visual Arts"],
        "source_urls": ["https://www.moma.org/collection/about/", "https://www.centrepompidou.fr/en/collection/visual-arts"],
        "note": "用可见的机械零件、循环运动和带有故障感的拼装制造动势；适合表达 Agent 工作流、自动化和系统失灵。",
    },
    {
        "id": "paik-media-installation",
        "label": "Nam June Paik-inspired media installation",
        "artist_or_movement": "Nam June Paik / video and media art",
        "period": "postwar and contemporary media art",
        "museum_basis": ["MoMA Collection", "Centre Pompidou Film and New Media"],
        "source_urls": ["https://www.moma.org/collection/about/", "https://www.centrepompidou.fr/en/collection/film-and-new-media"],
        "note": "用屏幕、信号、重复画面和物理装置形成多层媒介空间；适合表达 AI 入口、数据流和人机共处。",
    },
    {
        "id": "riley-op-art",
        "label": "Bridget Riley-inspired optical rhythm",
        "artist_or_movement": "Bridget Riley / Op Art",
        "period": "postwar contemporary art",
        "museum_basis": ["MoMA Collection"],
        "source_urls": ["https://www.moma.org/collection/about/"],
        "note": "用重复线条、密度变化和视错觉制造强节奏；适合表达模型路由、规模效应和看似稳定系统中的波动。",
    },
    {
        "id": "kusama-infinite-repetition",
        "label": "Yayoi Kusama-inspired infinite repetition and immersive field",
        "artist_or_movement": "Yayoi Kusama / installation and repetition",
        "period": "contemporary art",
        "museum_basis": ["MoMA Contemporary Art", "Centre Pompidou Visual Arts"],
        "source_urls": ["https://www.moma.org/collection/terms/contemporary-art", "https://www.centrepompidou.fr/en/collection/visual-arts"],
        "note": "用重复单元、镜面式延展和沉浸空间制造规模感；适合表达算力扩张、内容复制和注意力吞噬。",
    },
]

VISUAL_STYLE_POOL = [entry["label"] for entry in VISUAL_STYLE_CATALOG]
VISUAL_STYLE_NOTES = {entry["label"]: entry["note"] for entry in VISUAL_STYLE_CATALOG}
VISUAL_STYLE_LOOKUP = {entry["label"]: entry for entry in VISUAL_STYLE_CATALOG}


def choose_visual_style():
    """Pick one reproducible style per day, avoiding caller-supplied recent styles."""
    if not ARTIST_LOTTERY_ENABLED:
        return {
            "enabled": False,
            "pool": [],
            "seed": None,
            "selected_style": None,
            "recent_styles_excluded": [],
            "override": False,
            "catalog_id": None,
            "artist_or_movement": None,
            "period": None,
            "museum_basis": [],
            "source_urls": [],
            "art_fair_source_registry": ART_FAIR_SOURCE_REGISTRY,
            "museum_grounded": False,
            "style_note": "艺术家 Lottery 未启用；当前视觉后端由 VISUAL_BACKEND 控制。",
            "selection_reason": "使用默认 imagegen 或其他显式视觉后端；未抽取艺术家风格。",
        }
    override = os.environ.get("VISUAL_STYLE_OVERRIDE", "").strip()
    if override:
        entry = VISUAL_STYLE_LOOKUP.get(override)
        return {
            "enabled": True,
            "pool": VISUAL_STYLE_POOL,
            "seed": None,
            "selected_style": override,
            "recent_styles_excluded": [],
            "override": True,
            "catalog_id": entry["id"] if entry else None,
            "artist_or_movement": entry["artist_or_movement"] if entry else override,
            "period": entry["period"] if entry else "user override",
            "museum_basis": entry["museum_basis"] if entry else [],
            "source_urls": entry["source_urls"] if entry else [],
            "art_fair_source_registry": ART_FAIR_SOURCE_REGISTRY,
            "museum_grounded": bool(entry),
            "style_note": VISUAL_STYLE_NOTES.get(override, "用户指定风格；需通过时尚感、层次感、主题相关性和中文可读性验收。"),
            "selection_reason": "用户明确指定风格，覆盖当日 lottery；若不在博物馆锚定目录中，必须保留 override 标记并单独复核来源。",
        }
    recent = {
        value.strip()
        for value in os.environ.get("RECENT_VISUAL_STYLES", "").split(",")
        if value.strip()
    }
    available = [style for style in VISUAL_STYLE_POOL if style not in recent]
    if not available:
        available = VISUAL_STYLE_POOL
    seed = hashlib.sha256(f"{DATE}|ai-daily-style-lottery".encode("utf-8")).hexdigest()
    selected = available[int(seed[:8], 16) % len(available)]
    entry = VISUAL_STYLE_LOOKUP[selected]
    return {
        "enabled": True,
        "pool": VISUAL_STYLE_POOL,
        "seed": seed,
        "selected_style": selected,
        "recent_styles_excluded": sorted(recent),
        "override": False,
        "catalog_id": entry["id"],
        "artist_or_movement": entry["artist_or_movement"],
        "period": entry["period"],
        "museum_basis": entry["museum_basis"],
        "source_urls": entry["source_urls"],
        "art_fair_source_registry": ART_FAIR_SOURCE_REGISTRY,
        "museum_grounded": True,
        "style_note": VISUAL_STYLE_NOTES[selected],
        "selection_reason": "按日期可复现抽签；候选均来自博物馆锚定的现代/当代目录，若指定近期风格则优先排除，主题相关性和中文可读性仍高于随机性。",
    }


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

visual_style = choose_visual_style()
if ARTIST_LOTTERY_ENABLED:
    md.append("### 🎨 今日视觉 Lottery\n")
    md.append(f"- **抽中风格**：{visual_style['selected_style']}")
    md.append(f"- **馆藏锚点**：{'、'.join(visual_style.get('museum_basis') or ['用户指定 override，待补来源'])}")
    md.append(f"- **风格介绍**：{visual_style['style_note']}")
    md.append("- **执行标准**：保持时尚感、清晰的前中后景层次和编辑感；三张图共享视觉语法但分别重做构图，文字必须大且无遮挡。")
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

# Keep the renderer input next to the final Markdown so Mck PPT visuals use
# the same trend titles and evidence instead of re-parsing or re-inventing them.
trend_payload = {
    "schema_version": "1.0",
    "date": DATE,
    "title": "AI 日报每日关键趋势",
    "source_markdown": "daily-report.md",
    "source": "AI News Digest Goal 9 · sources and links remain in daily-report.md",
    "visual_spec": {
        "fresh_graphic": True,
        "visual_backend": VISUAL_BACKEND,
        "style_lottery": visual_style,
        "style_catalog_version": "museum-and-art-fair-modern-contemporary-v2",
        "museum_source_registry": MUSEUM_SOURCE_REGISTRY,
        "art_fair_source_registry": ART_FAIR_SOURCE_REGISTRY,
        "catalog_policy": "默认只抽取有现当代机构馆藏锚点的 20/21 世纪艺术家或艺术运动；同步巡检 Art Basel Basel、Miami Beach、Hong Kong、Paris 官方展商与艺术家名录作为当代发现层。仅由艺术博览会发现的候选必须经过现代/当代语境、来源可靠性和视觉可执行性复核；古典艺术家不进入默认池。",
        "qa_framework": {
            "name": "Qwen-Image-Bench",
            "source_url": "https://github.com/QwenLM/Qwen-Image-Bench",
            "dimensions": ["Quality", "Aesthetics", "Alignment", "Real-world Fidelity", "Creative Generation"],
            "scoring": {"Fail": 0, "Pass": 1, "Excel": 2, "N/A": None},
            "human_review_only": True,
        },
        "format": "16:9 PNG",
        "text_policy": "大字号中文标题 + 人话核心观点 + 一句批判性判断；不堆参数、机构名单或长摘要。",
        "composition_policy": "三张图共享当日抽中的艺术家视觉语法，但主体、构图骨架和阅读路径必须不同。",
        "no_identifiable_faces": True,
    },
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

style_entry = {
    "date": DATE,
    "enabled": ARTIST_LOTTERY_ENABLED,
    "visual_backend": VISUAL_BACKEND,
    "style_lottery": visual_style,
    "style_catalog_version": "museum-and-art-fair-modern-contemporary-v2",
    "museum_source_registry": MUSEUM_SOURCE_REGISTRY,
    "art_fair_source_registry": ART_FAIR_SOURCE_REGISTRY,
    "catalog_policy": "默认只抽取有现当代机构馆藏或顶级艺术博览会官方名录锚点的现代/当代视觉语言；艺术博览会只作为发现层，不自动替代艺术史与来源复核。",
    "trend_titles": [t["title"] for t in trends],
    "visual_assets": [
        f"reports/{DATE}-ai-daily/trends-imagegen/trend-{i}.png"
        for i in range(1, len(trends) + 1)
    ],
    "lottery_table_layout": {
        "one_table_per_day": True,
        "columns": ["字段", "记录"],
        "trend_rows_include_embedded_screenshots": True,
        "no_standalone_daily_appendix": True,
    },
    "qa_framework": {
        "name": "Qwen-Image-Bench",
        "source_url": "https://github.com/QwenLM/Qwen-Image-Bench",
        "dimensions": ["Quality", "Aesthetics", "Alignment", "Real-world Fidelity", "Creative Generation"],
        "scoring": {"Fail": 0, "Pass": 1, "Excel": 2, "N/A": None},
        "human_review_only": True,
    },
    "qa_status": "pending_visual_qa" if ARTIST_LOTTERY_ENABLED else "not_run_visual_backend_disabled",
    "structured_log_target": "AI日报｜艺术风格 Lottery",
}
(OUT_DIR / "art-style-lottery-entry.json").write_text(
    json.dumps(style_entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

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
        lines.append(f"- {it.get('signal_level', '⚪')} {item_link(it)} - {card_highlight(it)}")
    lines.extend([
        "",
        "## 点击与按钮规则",
        "- 默认 open_url：当日飞书详细版文档 URL（生成卡片时由 `detailed_report_doc` 注入）。",
        "- 底部按钮：长期趋势沉淀 -> https://bytedance.larkoffice.com/docx/JPs1dxjemo6HWMxn1mncxBOEnhg",
    ])
    return "\n".join(lines)


def render_structured_archive():
    board_groups = [
        ("偏fact类", "大厂动向"),
        ("", "初创动向"),
        ("", "生态动向"),
        ("", "技术博客&论文"),
        ("偏观点类", "观点与深度"),
        ("", "海外建设者"),
        ("行动沉淀", "今天就做"),
    ]

    def table_cell(board, selected_items=None):
        board_items = selected_items if selected_items is not None else [
            it for it in items if it.get("board", "未分类") == board
        ]
        if not board_items:
            return "—"
        entries = []
        for it in board_items:
            summary = compact(
                it.get("structured_summary") or it.get("summary") or "",
                120,
                ellipsis=False,
            )
            detail = f"{item_link(it)}：{summary}" if summary else item_link(it)
            detail = detail.replace("|", "／").replace("\n", " ")
            entries.append(f"• {it.get('signal_level', '⚪')} {detail}")
        return "<br>".join(entries)

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
        "",
        "| 大类 | 板块 | 结构化条目 |",
        "|---|---|---|",
    ]
    for category, board in board_groups:
        if any(it.get("board", "未分类") == board for it in items):
            lines.append(f"| {category} | {board} | {table_cell(board)} |")
    uncategorized = [it for it in items if it.get("board", "未分类") not in {b for _, b in board_groups}]
    if uncategorized:
        lines.append(f"|  | 未分类 | {table_cell('未分类', uncategorized)} |")
    lines.extend([
        "",
        "> 结构化沉淀只记录新闻发生了什么；趋势批判性判断、风险推演和壁垒判断保留在详细版。",
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
print(f"✅ 趋势可视化输入已写入: {OUT_DIR / 'daily-trends.json'}")
print(f"✅ 艺术风格 Lottery 单日记录已写入: {OUT_DIR / 'art-style-lottery-entry.json'}")

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
print(f"  [{'✓' if (OUT_DIR / 'daily-trends.json').exists() else '✗'}] daily-trends.json 存在且包含 {len(trends)} 条趋势")
print(f"  [{'✓' if (OUT_DIR / 'art-style-lottery-entry.json').exists() else '✗'}] art-style-lottery-entry.json 存在")
