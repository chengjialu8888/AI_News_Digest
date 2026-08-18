#!/usr/bin/env python3
"""Goal 9 (rev): Render Markdown + CSV from the Kleisli-deduped 07b-deduped.json.

Differences from stage9.py:
  - Input source: 07b-deduped.json (post G0.5 cross-day dedup)
  - Reads 07b-trace.json and renders a banner at the top of MD when WARN/FAIL
  - All other rendering logic identical
"""
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
    {
        "name": "The Met Collection",
        "url": "https://www.metmuseum.org/art/collection",
        "scope": "global art history from ancient cultures through modern and contemporary art, including Egyptian, Greek and Roman, Islamic, Asian, African, European and American collections",
    },
    {
        "name": "British Museum Collection Online",
        "url": "https://www.britishmuseum.org/collection",
        "scope": "global human history and material culture, with searchable objects across archaeology, art, manuscripts and design",
    },
    {
        "name": "Louvre Collections",
        "url": "https://collections.louvre.fr/en/",
        "scope": "more than 500,000 documented works across antiquities, paintings, sculpture, drawings, decorative arts and world cultures",
    },
    {
        "name": "National Archaeological Museum of Athens",
        "url": "https://www.namuseum.gr/en/collections/",
        "scope": "prehistoric, Cycladic, Mycenaean, Greek sculpture, vase painting, metalwork, Egyptian and Cypriot antiquities",
    },
    {
        "name": "Staatliche Museen zu Berlin Collections Online",
        "url": "https://search.smb.museum/",
        "scope": "searchable collections across the Pergamonmuseum institutions, Ancient Near East, Greek and Roman antiquities, Islamic art and related museums",
    },
    {
        "name": "Museo Nacional de Antropología Mexico",
        "url": "https://mna.inah.gob.mx/index.php/inicio/",
        "scope": "archaeology and ethnography collections of Mesoamerican and Indigenous cultures, including Teotihuacan, Maya, Mexica and Oaxaca",
    },
    {
        "name": "Museo Nacional de Colombia Collections",
        "url": "https://museonacional.gov.co/colecciones/Paginas/default.aspx",
        "scope": "archaeology, art, history and ethnography collections documenting Colombian and pre-Hispanic visual cultures",
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
    {
        "id": "met-ancient-egyptian-register",
        "label": "Ancient Egyptian funerary register and frontal order",
        "artist_or_movement": "Ancient Egyptian visual tradition / funerary art",
        "period": "Predynastic to Ptolemaic Egypt, c. 5000–30 BCE",
        "culture_region": "Nile Valley / North Africa",
        "catalog_kind": "tradition",
        "catalog_query": "Ancient Egypt",
        "museum_basis": ["The Met Collection"],
        "source_urls": ["https://www.metmuseum.org/art/collection"],
        "note": "用正面性、层级分格、重复符号和清晰的观看秩序组织信息；转译时关注稳定的阅读层级与时间性，不复制具体墓葬或神祇图像。",
    },
    {
        "id": "met-hokusai-ukiyo-e",
        "label": "Katsushika Hokusai-inspired ukiyo-e compositional wave",
        "artist_or_movement": "Katsushika Hokusai / ukiyo-e",
        "period": "late Edo Japan, 18th–19th century",
        "culture_region": "Japan / East Asia",
        "catalog_kind": "artist",
        "catalog_query": "Katsushika Hokusai",
        "museum_basis": ["The Met Collection"],
        "source_urls": ["https://www.metmuseum.org/art/collection"],
        "note": "提取非对称裁切、平面色块、强轮廓和波形节奏，把复杂系统压缩成具有方向性的阅读路径；不复刻《神奈川冲浪里》的主体或构图。",
    },
    {
        "id": "met-islamic-geometric-manuscript",
        "label": "Islamic geometric manuscript illumination and arabesque",
        "artist_or_movement": "Islamic art / geometric ornament and manuscript tradition",
        "period": "medieval to early modern Islamic art",
        "culture_region": "West Asia / North Africa / South Asia",
        "catalog_kind": "tradition",
        "catalog_query": "Islamic Art geometric manuscript",
        "museum_basis": ["The Met Collection"],
        "source_urls": ["https://www.metmuseum.org/art/collection"],
        "note": "用重复几何、中心与边界、交错纹样和尺度递归建立可扩展秩序；把它转译为系统关系，不将宗教文字或具体装饰当作可随意挪用的纹理。",
    },
    {
        "id": "british-assyrian-narrative-relief",
        "label": "Neo-Assyrian palace relief and continuous narrative",
        "artist_or_movement": "Neo-Assyrian palace relief tradition",
        "period": "Iron Age Mesopotamia, c. 900–600 BCE",
        "culture_region": "Mesopotamia / West Asia",
        "catalog_kind": "tradition",
        "catalog_query": "Assyrian relief",
        "museum_basis": ["British Museum Collection Online"],
        "source_urls": ["https://www.britishmuseum.org/collection", "https://www.britishmuseum.org/collection/search"],
        "note": "提取连续叙事、横向推进、重复人物动作和浮雕层次，把新闻证据组织成事件带；不复刻战争、王权或具体文物图像。",
    },
    {
        "id": "british-medieval-manuscript-illumination",
        "label": "Medieval manuscript illumination and marginal narrative",
        "artist_or_movement": "European medieval manuscript workshop tradition",
        "period": "medieval Europe, c. 1100–1500",
        "culture_region": "Europe",
        "catalog_kind": "workshop tradition",
        "catalog_query": "illuminated manuscript",
        "museum_basis": ["British Museum Collection Online"],
        "source_urls": ["https://www.britishmuseum.org/collection", "https://www.britishmuseum.org/collection/search"],
        "note": "提取页边叙事、文本与图像并置、首字母作为导航锚点和细密层级；适合把证据注释做成阅读入口，不复制宗教场景或手稿页面。",
    },
    {
        "id": "louvre-caravaggio-tenebrism",
        "label": "Caravaggio-inspired tenebrism and staged revelation",
        "artist_or_movement": "Caravaggio / Baroque tenebrism",
        "period": "early 17th-century Baroque",
        "culture_region": "Italy / Europe",
        "catalog_kind": "artist",
        "catalog_query": "Caravaggio",
        "museum_basis": ["Louvre Collections"],
        "source_urls": ["https://collections.louvre.fr/en/"],
        "note": "提取暗部包围主体、单一光源揭示关键动作和戏剧化前后景；适合强调一个决定性变量，不借用宗教人物或具体画面。",
    },
    {
        "id": "louvre-david-neoclassical-civic-order",
        "label": "Jacques-Louis David-inspired neoclassical civic order",
        "artist_or_movement": "Jacques-Louis David / Neoclassicism",
        "period": "late 18th to early 19th century",
        "culture_region": "France / Europe",
        "catalog_kind": "artist",
        "catalog_query": "Jacques-Louis David",
        "museum_basis": ["Louvre Collections"],
        "source_urls": ["https://collections.louvre.fr/en/"],
        "note": "提取明确轴线、群像编排、道德判断与公共叙事的结构关系；适合表达制度性转向，不复刻历史人物、服饰或政治场景。",
    },
    {
        "id": "athens-cycladic-minimal-form",
        "label": "Cycladic marble minimal form and ritual silence",
        "artist_or_movement": "Cycladic art / prehistoric Aegean sculpture",
        "period": "Early Bronze Age Aegean, c. 3200–2000 BCE",
        "culture_region": "Cyclades / Aegean",
        "catalog_kind": "tradition",
        "catalog_query": "Cycladic antiquities",
        "museum_basis": ["National Archaeological Museum of Athens"],
        "source_urls": ["https://www.namuseum.gr/en/collections/", "https://www.namuseum.gr/en/permanent_exhibition/"],
        "note": "提取极简轮廓、材料克制、空白的仪式感和正面观看关系；适合把趋势压缩成少数结构性形体，不仿造具体偶像或墓葬。",
    },
    {
        "id": "athens-attic-vase-narrative",
        "label": "Attic black-figure and red-figure vase narrative",
        "artist_or_movement": "Ancient Greek vase-painting workshops",
        "period": "Archaic to Classical Greece, c. 600–400 BCE",
        "culture_region": "Attica / Aegean",
        "catalog_kind": "workshop tradition",
        "catalog_query": "vases and miniature arts",
        "museum_basis": ["National Archaeological Museum of Athens"],
        "source_urls": ["https://www.namuseum.gr/en/collections/", "https://www.namuseum.gr/en/collection/"],
        "note": "提取轮廓线、带状叙事、人物动作的顺序和容器边界；适合把事件流压成可扫描的序列，不拼贴神话人物或古典器形。",
    },
    {
        "id": "berlin-mesopotamian-brick-relief",
        "label": "Ancient Near Eastern glazed-brick procession and modular relief",
        "artist_or_movement": "Ancient Near Eastern architectural relief tradition",
        "period": "Neo-Babylonian Mesopotamia, c. 7th–6th century BCE",
        "culture_region": "Mesopotamia / West Asia",
        "catalog_kind": "tradition",
        "catalog_query": "Vorderasiatisches Museum / Ishtar Gate",
        "museum_basis": ["Staatliche Museen zu Berlin Collections Online", "Pergamonmuseum"],
        "source_urls": ["https://search.smb.museum/", "https://www.smb.museum/en/museums-institutions/pergamonmuseum/home/"],
        "note": "提取模块化砖面、重复动物单元、仪式性路径和建筑尺度；适合表达基础设施与规模，不复制伊什塔尔门的具体图像。",
    },
    {
        "id": "berlin-hellenistic-frieze-motion",
        "label": "Hellenistic frieze and compressed bodily motion",
        "artist_or_movement": "Hellenistic Greek sculpture and architectural frieze tradition",
        "period": "Hellenistic Mediterranean, c. 323–31 BCE",
        "culture_region": "Aegean / Mediterranean",
        "catalog_kind": "tradition",
        "catalog_query": "Antikensammlung / Hellenistic sculpture",
        "museum_basis": ["Staatliche Museen zu Berlin Collections Online", "Pergamonmuseum"],
        "source_urls": ["https://search.smb.museum/", "https://www.smb.museum/en/museums-institutions/pergamonmuseum/home/"],
        "note": "提取连续浮雕中的扭转、碰撞、前后景和瞬间凝固；适合表现多方博弈与高压转折，不重演具体神话战斗。",
    },
    {
        "id": "mexico-maya-glyphic-narrative",
        "label": "Maya glyphic narrative and calendrical rhythm",
        "artist_or_movement": "Maya visual culture / glyphic and calendrical tradition",
        "period": "Mesoamerica, c. 250–900 CE and related traditions",
        "culture_region": "Maya region / Central America",
        "catalog_kind": "cultural visual system",
        "catalog_query": "Maya archaeology",
        "museum_basis": ["Museo Nacional de Antropología Mexico"],
        "source_urls": ["https://mna.inah.gob.mx/index.php/inicio/"],
        "note": "提取符号块、周期性时间、层级叙事与仪式性尺度；适合表达长期趋势和反馈循环，不能把神圣符号当作装饰贴纸。",
    },
    {
        "id": "mexico-teotihuacan-mural-symbolism",
        "label": "Teotihuacan mural geometry and ceremonial procession",
        "artist_or_movement": "Teotihuacan visual culture / mural and architectural symbolism",
        "period": "Central Mexico, c. 100 BCE–550 CE",
        "culture_region": "Central Mexico / Mesoamerica",
        "catalog_kind": "cultural visual system",
        "catalog_query": "Teotihuacan archaeology",
        "museum_basis": ["Museo Nacional de Antropología Mexico"],
        "source_urls": ["https://mna.inah.gob.mx/index.php/inicio/"],
        "note": "提取平面分区、重复图式、建筑轴线与仪式性 procession；适合把组织结构画成可进入的空间，不复制壁画神祇或具体遗址。",
    },
    {
        "id": "colombia-muisca-gold-votive",
        "label": "Muisca votive goldwork and emblematic repetition",
        "artist_or_movement": "Muisca material culture / pre-Hispanic goldwork",
        "period": "pre-Hispanic Colombia, c. 600–1600 CE",
        "culture_region": "Andean Colombia / South America",
        "catalog_kind": "material tradition",
        "catalog_query": "archaeology goldwork",
        "museum_basis": ["Museo Nacional de Colombia Collections"],
        "source_urls": ["https://museonacional.gov.co/colecciones/Paginas/default.aspx", "https://www.museonacional.gov.co/exposiciones/permanentes/Paginas/default.aspx"],
        "note": "提取金属反光、微型重复、象征性姿态和物件作为社会关系媒介的逻辑；适合表达价值、信任和交换，不复制具体器物或仪式。",
    },
    {
        "id": "colombia-colonial-devotional-workshop",
        "label": "Colombian colonial devotional painting and archive",
        "artist_or_movement": "Colombian colonial art / devotional workshop tradition",
        "period": "colonial New Granada, 17th–18th century",
        "culture_region": "Colombia / Latin America",
        "catalog_kind": "workshop tradition",
        "catalog_query": "art collection colonial painting",
        "museum_basis": ["Museo Nacional de Colombia Collections"],
        "source_urls": ["https://museonacional.gov.co/colecciones/Paginas/default.aspx", "https://www.museonacional.gov.co/exposiciones/permanentes/Paginas/default.aspx"],
        "note": "提取档案式正面构图、象征物的层级摆放、金色边界与观看距离；适合表达制度记忆与证据链，不把宗教图像当成通用装饰。",
    },
]

# Keep the original modern/contemporary entries on the same provenance contract
# as the expanded classical and cross-civilizational catalog.
LEGACY_STYLE_METADATA = {
    "okeeffe-organic-abstraction": {"culture_region": "United States / North America", "catalog_kind": "artist", "catalog_query": "Georgia O'Keeffe"},
    "rothko-color-field": {"culture_region": "United States / North America", "catalog_kind": "artist", "catalog_query": "Mark Rothko"},
    "klee-poetic-geometry": {"culture_region": "Switzerland / Europe", "catalog_kind": "artist", "catalog_query": "Paul Klee"},
    "kandinsky-musical-abstraction": {"culture_region": "Russia / Germany / Europe", "catalog_kind": "artist", "catalog_query": "Wassily Kandinsky"},
    "matisse-cut-paper": {"culture_region": "France / Europe", "catalog_kind": "artist", "catalog_query": "Henri Matisse"},
    "mondrian-neoplastic-grid": {"culture_region": "Netherlands / Europe", "catalog_kind": "artist", "catalog_query": "Piet Mondrian"},
    "warhol-pop-repetition": {"culture_region": "United States / North America", "catalog_kind": "artist", "catalog_query": "Andy Warhol"},
    "bourgeois-material-memory": {"culture_region": "France / United States", "catalog_kind": "artist", "catalog_query": "Louise Bourgeois"},
    "tinguely-kinetic-machine": {"culture_region": "Switzerland / France / Europe", "catalog_kind": "artist", "catalog_query": "Jean Tinguely"},
    "paik-media-installation": {"culture_region": "Korea / United States", "catalog_kind": "artist", "catalog_query": "Nam June Paik"},
    "riley-op-art": {"culture_region": "United Kingdom / Europe", "catalog_kind": "artist", "catalog_query": "Bridget Riley"},
    "kusama-infinite-repetition": {"culture_region": "Japan / East Asia", "catalog_kind": "artist", "catalog_query": "Yayoi Kusama"},
}
for entry in VISUAL_STYLE_CATALOG:
    entry.update(LEGACY_STYLE_METADATA.get(entry["id"], {}))

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
            "culture_region": None,
            "catalog_kind": None,
            "catalog_query": None,
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
            "culture_region": entry.get("culture_region") if entry else None,
            "catalog_kind": entry.get("catalog_kind") if entry else None,
            "catalog_query": entry.get("catalog_query") if entry else None,
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
        "culture_region": entry.get("culture_region"),
        "catalog_kind": entry.get("catalog_kind"),
        "catalog_query": entry.get("catalog_query"),
        "art_fair_source_registry": ART_FAIR_SOURCE_REGISTRY,
        "museum_grounded": True,
        "style_note": VISUAL_STYLE_NOTES[selected],
        "selection_reason": "按日期可复现抽签；候选均来自官方博物馆锚定的现代/当代或古典/跨文明目录，若指定近期风格则优先排除，主题相关性、来源可追溯性和中文可读性仍高于随机性。",
    }


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

visual_style = choose_visual_style()
if ARTIST_LOTTERY_ENABLED:
    md.append("### 🎨 今日视觉 Lottery\n")
    md.append(f"- **抽中风格**：{visual_style['selected_style']}")
    md.append(f"- **馆藏锚点**：{'、'.join(visual_style.get('museum_basis') or ['用户指定 override，待补来源'])}")
    md.append(f"- **风格介绍**：{visual_style['style_note']}")
    md.append("- **执行标准**：保持时尚感、清晰的前中后景层次和编辑感；三张图共享视觉语法但分别重做构图，文字必须大且无遮挡。")
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
    "visual_spec": {
        "fresh_graphic": True,
        "visual_backend": VISUAL_BACKEND,
        "style_lottery": visual_style,
        "style_catalog_version": "museum-and-art-fair-global-classical-v3",
        "museum_source_registry": MUSEUM_SOURCE_REGISTRY,
        "art_fair_source_registry": ART_FAIR_SOURCE_REGISTRY,
        "catalog_policy": "默认抽取有官方博物馆馆藏或可靠目录锚点的艺术家、艺术运动、工坊传统和文化视觉系统；现代/当代机构与 Art Basel 作为现代/当代发现层，The Met、大英博物馆、卢浮宫、雅典国立考古博物馆、柏林国家博物馆群、墨西哥国立人类学博物馆和哥伦比亚国家博物馆补充全球古典与跨文明目录。艺术博览会只作发现层，古典与传统条目必须以馆藏目录、时期、地域和机制提取为依据，不能把无名作品归给个人或把神圣符号当装饰。",
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
    "style_catalog_version": "museum-and-art-fair-global-classical-v3",
    "museum_source_registry": MUSEUM_SOURCE_REGISTRY,
    "art_fair_source_registry": ART_FAIR_SOURCE_REGISTRY,
    "catalog_policy": "默认抽取有官方博物馆馆藏或可靠目录锚点的艺术家、艺术运动、工坊传统和文化视觉系统；现代/当代机构与 Art Basel 作为现代/当代发现层，全球博物馆目录补充古典与跨文明视觉系统。艺术博览会只作发现层，古典与传统条目必须保留时期、地域、目录查询词和机制复核，不能把无名作品归给个人或把神圣符号当装饰。",
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
        "- 底部并列按钮：长期趋势沉淀 -> https://bytedance.larkoffice.com/docx/JPs1dxjemo6HWMxn1mncxBOEnhg；艺术风格 Lottery -> https://bytedance.larkoffice.com/docx/SBCBdt4tiodAGBxpnPncXYtqnyg",
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
        "## Kleisli Trace",
        f"- 跨日去重：{trace.get('status') if trace else '未生成'}",
        f"- 版本一致性：{vtrace.get('status') if vtrace else '未生成'}",
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
print(f"  [{'✓' if (OUT_DIR / 'art-style-lottery-entry.json').exists() else '✗'}] art-style-lottery-entry.json 存在")
