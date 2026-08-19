"""Shared contracts for the museum-grounded artist Lottery.

The daily renderer selects a provenance entry, but this module owns the
translation and review contract so the standard and Kleisli paths cannot
quietly drift apart.
"""

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path


STYLE_CONTRACT_VERSION = "1.0"
CASE_MEMORY_VERSION = "1.0"
RETURN_STAGES = ("catalog", "mechanism_extract", "trend_translation", "prompt", "craft")


FAMILY_BY_STYLE_ID = {
    "okeeffe-organic-abstraction": "organic",
    "rothko-color-field": "color_field",
    "klee-poetic-geometry": "poetic_geometry",
    "kandinsky-musical-abstraction": "musical_abstraction",
    "matisse-cut-paper": "cut_paper",
    "mondrian-neoplastic-grid": "grid",
    "warhol-pop-repetition": "repetition",
    "bourgeois-material-memory": "material_memory",
    "tinguely-kinetic-machine": "kinetic",
    "paik-media-installation": "media_installation",
    "riley-op-art": "optical_rhythm",
    "kusama-infinite-repetition": "immersive_repetition",
    "met-ancient-egyptian-register": "frontal_register",
    "met-hokusai-ukiyo-e": "ukiyo_e",
    "met-islamic-geometric-manuscript": "geometric_manuscript",
    "british-assyrian-narrative-relief": "continuous_relief",
    "british-medieval-manuscript-illumination": "marginal_manuscript",
    "louvre-caravaggio-tenebrism": "tenebrism",
    "louvre-david-neoclassical-civic-order": "civic_order",
    "athens-cycladic-minimal-form": "ritual_minimalism",
    "athens-attic-vase-narrative": "banded_narrative",
    "berlin-mesopotamian-brick-relief": "modular_procession",
    "berlin-hellenistic-frieze-motion": "compressed_motion",
    "mexico-maya-glyphic-narrative": "calendrical_glyphs",
    "mexico-teotihuacan-mural-symbolism": "ceremonial_geometry",
    "colombia-muisca-gold-votive": "emblematic_material",
    "colombia-colonial-devotional-workshop": "archival_frontality",
}


FAMILY_CONTRACTS = {
    "organic": {
        "visual_intent": "把趋势转译为可接近的有机形体，让局部结构承载整体变化。",
        "mechanisms": [
            {"id": "cropped_form", "category": "space", "rule": "用局部放大的曲面和裁切制造近距离观看。"},
            {"id": "soft_transition", "category": "material", "rule": "用连续的色阶与柔性边界表达渐进变化。"},
            {"id": "quiet_field", "category": "viewing", "rule": "保留大块安静区域，让一个结构性变量成为焦点。"},
        ],
        "fit_signals": ["产品入口变化", "用户体验迁移", "组织采用"],
    },
    "color_field": {
        "visual_intent": "把竞争、成本或风险压缩为相互作用的色场，而不是装饰性背景。",
        "mechanisms": [
            {"id": "layered_field", "category": "space", "rule": "用相邻而不完全封闭的色场表达变量之间的张力。"},
            {"id": "edge_tension", "category": "material", "rule": "让边缘有轻微渗透，表示边界正在被重新定价。"},
            {"id": "single_anchor", "category": "rhythm", "rule": "每张图只设置一个主锚点，避免把多条新闻做成噪声墙。"},
        ],
        "fit_signals": ["价格变化", "资本重估", "能力与成本的张力"],
    },
    "poetic_geometry": {
        "visual_intent": "用轻量符号和几何关系把复杂机制变成可读的编辑叙事。",
        "mechanisms": [
            {"id": "symbolic_geometry", "category": "information", "rule": "把抽象变量编码为少量可重复但不装饰化的符号。"},
            {"id": "hand_drawn_offset", "category": "material", "rule": "保留轻微错位和手工痕迹，拒绝过度自动化的完美网格。"},
            {"id": "layered_reading", "category": "viewing", "rule": "建立主标题、关系线和注释的三层阅读顺序。"},
        ],
        "fit_signals": ["复杂产品机制", "工作流变化", "证据链"],
    },
    "musical_abstraction": {
        "visual_intent": "把多变量协作与流动关系组织成有节奏的视觉动势。",
        "mechanisms": [
            {"id": "directional_rhythm", "category": "rhythm", "rule": "用斜向线、圆形和间隔变化表达力量方向，而不是画箭头流程图。"},
            {"id": "color_counterpoint", "category": "material", "rule": "让有限色彩形成对位，区分互补、竞争和反馈。"},
            {"id": "distributed_focus", "category": "space", "rule": "保留多个次级节点，但只让一个节点承担判断。"},
        ],
        "fit_signals": ["生态协作", "多模型路由", "分发网络"],
    },
    "cut_paper": {
        "visual_intent": "用可移动的块面和错位关系表现产品入口、组合与再分发。",
        "mechanisms": [
            {"id": "cut_block", "category": "space", "rule": "用明确的平面块面切分主体、证据和背景。"},
            {"id": "overlap", "category": "material", "rule": "让层与层发生真实遮挡，表达组合关系而非贴纸装饰。"},
            {"id": "editorial_crop", "category": "viewing", "rule": "使用大胆裁切把读者带到一个具体变化，而不是平均展示全部信息。"},
        ],
        "fit_signals": ["应用集成", "产品分发", "平台入口"],
    },
    "grid": {
        "visual_intent": "把基础设施、约束和资源配置表现为有偏好的秩序。",
        "mechanisms": [
            {"id": "asymmetric_grid", "category": "space", "rule": "以非对称网格分配注意力，最大单元必须承载最重要判断。"},
            {"id": "limited_palette", "category": "material", "rule": "用少量高对比色标记状态，不用渐变制造虚假的层级。"},
            {"id": "hard_boundary", "category": "information", "rule": "让边界表达权限、成本或路由约束。"},
        ],
        "fit_signals": ["基础设施", "API 路由", "资源分配"],
    },
    "repetition": {
        "visual_intent": "把规模化分发和同质化的双刃剑显形为重复单元。",
        "mechanisms": [
            {"id": "serial_unit", "category": "rhythm", "rule": "重复同一单元并保留可测的偏差，区分规模与复制。"},
            {"id": "screenprint_texture", "category": "material", "rule": "使用颗粒和套色错位表达分发摩擦，不用品牌 logo 充当证据。"},
            {"id": "attention_interrupt", "category": "viewing", "rule": "设置一个打断重复的异常点，让判断落在结构变化上。"},
        ],
        "fit_signals": ["规模增长", "内容同质化", "注意力竞争"],
    },
    "material_memory": {
        "visual_intent": "把安全、信任和组织摩擦表现为带有触感的空间记忆。",
        "mechanisms": [
            {"id": "stitched_relation", "category": "material", "rule": "用缝合、纤维或柔性连接表示依赖关系与修复成本。"},
            {"id": "intimate_scale", "category": "viewing", "rule": "让关键证据靠近观看者，拒绝把风险做成宏大口号。"},
            {"id": "uneasy_void", "category": "space", "rule": "保留不安的空隙，显示系统尚未被完全自动化。"},
        ],
        "fit_signals": ["安全事件", "信任成本", "组织协作"],
    },
    "kinetic": {
        "visual_intent": "把 Agent 工作流表现为会运行、会卡顿、会返工的机械系统。",
        "mechanisms": [
            {"id": "visible_parts", "category": "information", "rule": "露出工具、状态和中间件，让流程可被审计。"},
            {"id": "loop_and_fault", "category": "rhythm", "rule": "建立循环，并加入一个可解释的卡点或回滚。"},
            {"id": "assembled_depth", "category": "space", "rule": "用前后层叠表达依赖顺序，不把所有步骤压成一条箭头。"},
        ],
        "fit_signals": ["Agent 工程化", "自动化失败", "可恢复工作流"],
    },
    "media_installation": {
        "visual_intent": "让数据流、屏幕和物理入口同时存在，强调媒介不是透明管道。",
        "mechanisms": [
            {"id": "screen_stack", "category": "space", "rule": "用不同尺度的屏幕/窗口形成并置，而不是一个万能 dashboard。"},
            {"id": "signal_noise", "category": "material", "rule": "让信号、扫描和干扰共存，提示路由与来源的不确定性。"},
            {"id": "human_scale", "category": "viewing", "rule": "保留一个人的观看位置，说明系统最终仍通过使用者被验证。"},
        ],
        "fit_signals": ["模型入口", "数据流", "人机共处"],
    },
    "optical_rhythm": {
        "visual_intent": "把路由、规模和系统波动转译为可感知的频率变化。",
        "mechanisms": [
            {"id": "density_wave", "category": "rhythm", "rule": "通过线条密度变化制造加速和拥塞，而不是使用速度图标。"},
            {"id": "perceptual_shift", "category": "viewing", "rule": "让远看与近看产生不同层级，但标题必须在两种距离都可读。"},
            {"id": "controlled_instability", "category": "space", "rule": "保留受控的抖动，表达稳定表象下的概率波动。"},
        ],
        "fit_signals": ["模型路由", "吞吐规模", "波动风险"],
    },
    "immersive_repetition": {
        "visual_intent": "把扩张、复制和注意力吞噬做成一个可进入的场，而非单个图标。",
        "mechanisms": [
            {"id": "repeating_field", "category": "space", "rule": "让重复单元延伸到边界，形成不可一眼穷尽的规模感。"},
            {"id": "reflective_depth", "category": "viewing", "rule": "用反射或回声制造第二层空间，提示增长的反馈。"},
            {"id": "one_disruption", "category": "information", "rule": "放入一个异常单元，避免无限重复变成纯装饰。"},
        ],
        "fit_signals": ["算力扩张", "内容复制", "注意力消耗"],
    },
    "frontal_register": {
        "visual_intent": "用稳定的正面秩序和分层记录，把长期趋势变成可回看的档案。",
        "mechanisms": [
            {"id": "frontal_order", "category": "viewing", "rule": "保持正面、清晰、可重复的观看秩序，避免透视戏剧化。"},
            {"id": "stacked_register", "category": "information", "rule": "按层级和时间分格，把事实、判断和观察分开。"},
            {"id": "symbolic_recurrence", "category": "rhythm", "rule": "使用有限重复符号标记状态，不挪用具体神祇或祭祀图像。"},
        ],
        "fit_signals": ["长期趋势", "制度变化", "证据档案"],
    },
    "ukiyo_e": {
        "visual_intent": "以非对称裁切和平面叙事捕捉一个正在发生的行业转向。",
        "mechanisms": [
            {"id": "asymmetric_crop", "category": "space", "rule": "用强裁切制造方向和压力，不复刻具体名作构图。"},
            {"id": "flat_plane", "category": "material", "rule": "用平面色块与清晰轮廓压缩复杂关系。"},
            {"id": "wave_rhythm", "category": "rhythm", "rule": "用连续波形或折线连接变化，但不替代实际因果证据。"},
        ],
        "fit_signals": ["产品冲击", "平台迁移", "快速变化"],
    },
    "geometric_manuscript": {
        "visual_intent": "将复杂系统编码为可扩展的几何秩序，同时保留边界与阅读方向。",
        "mechanisms": [
            {"id": "recursive_geometry", "category": "space", "rule": "用中心、边界和递归尺度表达系统嵌套。"},
            {"id": "interlaced_relation", "category": "information", "rule": "让关系交错但可追踪，不能只铺纹样。"},
            {"id": "protected_margin", "category": "viewing", "rule": "保留边界和呼吸区，避免信息填满神圣/仪式性空间。"},
        ],
        "fit_signals": ["系统嵌套", "权限边界", "平台规则"],
    },
    "continuous_relief": {
        "visual_intent": "将多条佐证组织成连续事件带，强调动作如何推进而非谁最醒目。",
        "mechanisms": [
            {"id": "event_band", "category": "information", "rule": "用横向连续带连接证据、动作和结果。"},
            {"id": "repeated_action", "category": "rhythm", "rule": "重复动作姿态以显示流程与规模，而不制作英雄叙事。"},
            {"id": "relief_layers", "category": "space", "rule": "用浅层叠压表达前景、背景和因果层级。"},
        ],
        "fit_signals": ["事件链", "竞争推进", "多源验证"],
    },
    "marginal_manuscript": {
        "visual_intent": "把正文判断与边缘证据并置，给读者一条可回查的阅读路径。",
        "mechanisms": [
            {"id": "main_margin", "category": "space", "rule": "用主栏承载判断、边栏承载证据和异议。"},
            {"id": "initial_anchor", "category": "information", "rule": "设置一个醒目的导航锚点，帮助读者回到本页命题。"},
            {"id": "fine_detail", "category": "material", "rule": "把细节放在可选阅读层，不用密度掩盖主结论。"},
        ],
        "fit_signals": ["证据注释", "反例", "事实核验"],
    },
    "tenebrism": {
        "visual_intent": "用有限光源揭示一个决定性变量，让判断从背景噪声中浮出。",
        "mechanisms": [
            {"id": "staged_revelation", "category": "viewing", "rule": "只照亮真正改变结构的变量，其余事实退到暗部。"},
            {"id": "deep_context", "category": "space", "rule": "保留深暗背景作为未知、风险或尚未验证部分。"},
            {"id": "directional_light", "category": "material", "rule": "让光线有方向且服务于因果，不用泛光制造热闹。"},
        ],
        "fit_signals": ["单一关键变量", "风险暴露", "发布与事实的差距"],
    },
    "civic_order": {
        "visual_intent": "把行业变化呈现为制度与公共叙事的重排，而非个人英雄故事。",
        "mechanisms": [
            {"id": "civic_axis", "category": "space", "rule": "用明确轴线组织主体与证据，显示谁在承担制度性作用。"},
            {"id": "group_judgement", "category": "information", "rule": "用群像关系表达公共判断，不把一个公司做成唯一主角。"},
            {"id": "ethical_contrast", "category": "rhythm", "rule": "设置选择或代价的对照，而不是纯庆祝式高光。"},
        ],
        "fit_signals": ["监管", "公共基础设施", "行业规则"],
    },
    "ritual_minimalism": {
        "visual_intent": "以克制、静默和少数结构形体表达趋势的最小骨架。",
        "mechanisms": [
            {"id": "reduced_contour", "category": "space", "rule": "把趋势压缩为少数轮廓，删除不影响判断的装饰。"},
            {"id": "material_silence", "category": "material", "rule": "让材料的重量和空白承担情绪，不用纹理补足空洞。"},
            {"id": "front_view", "category": "viewing", "rule": "使用稳定正面观看，使结论像一个需要停留的对象。"},
        ],
        "fit_signals": ["基础变量", "能力边界", "长期转向"],
    },
    "banded_narrative": {
        "visual_intent": "把复杂事件压成有边界、可扫描的连续序列。",
        "mechanisms": [
            {"id": "bounded_band", "category": "space", "rule": "以带状容器约束信息，让每段动作都有开始和结果。"},
            {"id": "contour_story", "category": "information", "rule": "用轮廓和动作顺序讲因果，不靠长段说明。"},
            {"id": "repeat_scale", "category": "rhythm", "rule": "保持叙事节奏稳定，只有结构转折处改变比例。"},
        ],
        "fit_signals": ["流程", "事件序列", "多步任务"],
    },
    "modular_procession": {
        "visual_intent": "用模块、路径和重复单元表达基础设施的规模与依赖。",
        "mechanisms": [
            {"id": "modular_unit", "category": "space", "rule": "使用可复用模块形成大结构，但保留依赖方向。"},
            {"id": "processional_path", "category": "viewing", "rule": "让阅读沿着一条有节奏的路径前进，而不是四散卡片。"},
            {"id": "scale_repeat", "category": "rhythm", "rule": "用重复单元显示规模，不能把具体文化符号当 UI 图标。"},
        ],
        "fit_signals": ["基础设施", "训练管线", "供应链"],
    },
    "compressed_motion": {
        "visual_intent": "在一个压缩瞬间里表现博弈、冲突和转折。",
        "mechanisms": [
            {"id": "twist", "category": "space", "rule": "通过扭转和前后景压缩多个力量方向。"},
            {"id": "collision", "category": "rhythm", "rule": "让对立动作在一个节点相遇，呈现代价而非装饰性动势。"},
            {"id": "frozen_change", "category": "viewing", "rule": "把关键转折冻结成可核验的瞬间。"},
        ],
        "fit_signals": ["竞争", "战略转折", "能力边界冲突"],
    },
    "calendrical_glyphs": {
        "visual_intent": "把长期趋势、周期与反馈做成可回看的时间语法。",
        "mechanisms": [
            {"id": "symbol_block", "category": "information", "rule": "用有限符号块区分阶段、反馈和状态，不随意挪用神圣符号。"},
            {"id": "cyclic_time", "category": "rhythm", "rule": "让循环包含积累或偏移，避免把趋势画成无意义圆环。"},
            {"id": "layered_scale", "category": "space", "rule": "同时显示日级信号和更长周期的结构背景。"},
        ],
        "fit_signals": ["周期性", "反馈", "长期知识沉淀"],
    },
    "ceremonial_geometry": {
        "visual_intent": "用平面分区、轴线和重复秩序表达组织结构与集体动作。",
        "mechanisms": [
            {"id": "planar_zone", "category": "space", "rule": "用平面分区让入口、执行和结果各有位置。"},
            {"id": "architectural_axis", "category": "information", "rule": "让轴线表达组织方向，而不是绘制真实建筑。"},
            {"id": "ceremonial_repeat", "category": "rhythm", "rule": "用有节奏的重复显示制度化动作，不复制具体神祇或遗址。"},
        ],
        "fit_signals": ["组织流程", "平台治理", "集体采用"],
    },
    "emblematic_material": {
        "visual_intent": "用材料价值、微型重复和交换关系表现信任与资源的可见化。",
        "mechanisms": [
            {"id": "metal_reflection", "category": "material", "rule": "用受控反光标记价值变化，不把金色当作成功滤镜。"},
            {"id": "micro_repeat", "category": "rhythm", "rule": "用小尺度重复表达网络和交换，不堆叠无意义图标。"},
            {"id": "social_object", "category": "viewing", "rule": "让物件处于关系中，提示价值由使用与信任共同生成。"},
        ],
        "fit_signals": ["价值重估", "信任", "交换与分发"],
    },
    "archival_frontality": {
        "visual_intent": "把制度记忆、来源和证据链放在可回查的正面档案结构中。",
        "mechanisms": [
            {"id": "archive_frame", "category": "space", "rule": "用边界和留档结构区分原始事实、解释与推断。"},
            {"id": "symbolic_placement", "category": "information", "rule": "让每个象征物有层级和理由，不把宗教图像当通用装饰。"},
            {"id": "viewing_distance", "category": "viewing", "rule": "设置可读的观看距离，让读者先看档案主张再看细节。"},
        ],
        "fit_signals": ["事实核验", "制度记忆", "来源追溯"],
    },
}


def _fallback_contract(entry):
    label = (entry or {}).get("label") or "user override"
    return {
        "visual_intent": f"将 {label} 仅作为可验证的视觉机制来源，不把姓名或表面符号当作风格本体。",
        "mechanisms": [
            {"id": "spatial_relation", "category": "space", "rule": "明确主体、背景和阅读路径之间的关系。"},
            {"id": "material_action", "category": "material", "rule": "明确材料或动作如何承载当天的结构变量。"},
            {"id": "viewing_condition", "category": "viewing", "rule": "明确读者从哪里看、先看什么、如何回查证据。"},
        ],
        "fit_signals": ["能力", "成本", "分发", "组织采用"],
    }


def build_style_contract(entry):
    """Turn a catalog item into an executable, reviewer-facing style contract."""
    family = FAMILY_BY_STYLE_ID.get((entry or {}).get("id"))
    base = deepcopy(FAMILY_CONTRACTS.get(family, _fallback_contract(entry)))
    source_urls = list((entry or {}).get("source_urls") or [])
    label = (entry or {}).get("label") or "user override"
    anti_patterns = [
        f"不要把 {label} 的姓名、代表作或标志性图案直接当作 prompt。",
        "不要复制具体作品、神圣符号、文物图像、logo 或可识别人物。",
        "不要只换颜色、纹理或边框；三张趋势图必须有不同主体和构图骨架。",
    ]
    return {
        "contract_version": STYLE_CONTRACT_VERSION,
        "family": family or "catalog_generic",
        "visual_intent": base["visual_intent"],
        "mechanisms": [
            {
                **mechanism,
                "evidence_basis": "design_inference_from_catalog_note",
                "source_urls": source_urls,
            }
            for mechanism in base["mechanisms"]
        ],
        "translation_rules": [
            "先写当天趋势改变的结构变量，再选择两个以上机制承载它。",
            "保持机制不变、主体和构图重做；艺术家姓名只保留为 provenance。",
            "把事实、解释、推断分开记录，图像只做判断入口，详细证据回到日报正文。",
        ],
        "anti_patterns": anti_patterns,
        "fit_signals": base["fit_signals"],
        "prompt_components": [
            "mechanism_fact",
            "trend_proposition",
            "subject_and_spatial_relation",
            "material_and_light",
            "type_and_information_hierarchy",
            "exclusions_and_cultural_safety",
        ],
        "evaluator_subchecks": [
            {
                "id": "mechanism_count",
                "stage": "mechanism_extract",
                "question": "是否至少保留两个可解释的工作机制？",
                "pass_condition": "2+ mechanisms are named and connected to the source note",
                "return_to": "mechanism_extract",
            },
            {
                "id": "trend_specificity",
                "stage": "trend_translation",
                "question": "视觉关系是否服务于今天的趋势，而不是泛化审美？",
                "pass_condition": "each trend has a distinct subject, relation and structural variable",
                "return_to": "trend_translation",
            },
            {
                "id": "anti_slop",
                "stage": "prompt",
                "question": "是否依赖艺术家名字、调色板或符号捷径？",
                "pass_condition": "prompt is executable without the artist name",
                "return_to": "prompt",
            },
            {
                "id": "craft_and_legibility",
                "stage": "craft",
                "question": "截图是否无重叠、无折叠、标题可读且信息层级稳定？",
                "pass_condition": "surface, typography, layout and Chinese legibility pass visual QA",
                "return_to": "craft",
            },
        ],
        "reference_works": {
            "catalog_query": (entry or {}).get("catalog_query"),
            "museum_basis": (entry or {}).get("museum_basis") or [],
            "source_urls": source_urls,
        },
    }


def default_case_path(data_dir):
    return Path(os.environ.get("STYLE_CASES_PATH", str(Path(data_dir) / "art-style-cases.json")))


def load_style_cases(path):
    path = Path(path)
    if not path.exists():
        return {"schema_version": CASE_MEMORY_VERSION, "cases": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema_version": CASE_MEMORY_VERSION, "cases": [], "load_warning": "unreadable_case_store"}
    if isinstance(payload, list):
        return {"schema_version": CASE_MEMORY_VERSION, "cases": payload}
    cases = payload.get("cases") if isinstance(payload, dict) else []
    return {
        "schema_version": payload.get("schema_version", CASE_MEMORY_VERSION) if isinstance(payload, dict) else CASE_MEMORY_VERSION,
        "cases": cases if isinstance(cases, list) else [],
    }


def recent_style_labels(path, limit=3):
    """Return labels from reviewed recent cases for anti-repetition lottery input."""
    cases = load_style_cases(path).get("cases", [])
    labels = []
    for case in reversed(cases):
        if case.get("status") not in {"accepted", "rejected", "rework_requested"}:
            continue
        label = case.get("selected_style") or case.get("style_label")
        if label and label not in labels:
            labels.append(label)
        if len(labels) >= limit:
            break
    return set(labels)


def build_evaluation_contract(style_contract):
    return {
        "contract_version": STYLE_CONTRACT_VERSION,
        "evaluator_isolation": "评估器只接收最终截图、趋势输入和结构化契约，不接收生成器私有推理或自评结论。",
        "check_order": list(RETURN_STAGES),
        "checks": style_contract.get("evaluator_subchecks", []) if style_contract else [],
        "routing_policy": "每个失败必须返回一个具体阶段、一个可观察问题和一个修复动作；禁止只写 optimize / make it better。",
        "status": "pending",
    }


def build_case_id(report_date, catalog_id, seed):
    raw = f"{report_date}|{catalog_id or 'override'}|{seed or 'override'}"
    return f"lottery-{report_date}-{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:12]}"


def build_case_memory(selection, report_date, data_dir):
    if not selection.get("enabled"):
        return {"enabled": False, "schema_version": CASE_MEMORY_VERSION, "store": None, "prior_cases_considered": 0}
    path = default_case_path(data_dir)
    store = load_style_cases(path)
    cases = store.get("cases", [])
    case_id = build_case_id(report_date, selection.get("catalog_id"), selection.get("seed"))
    seen = [case for case in cases if case.get("case_id") == case_id]
    return {
        "enabled": True,
        "schema_version": CASE_MEMORY_VERSION,
        "store": "data/art-style-cases.json",
        "store_path_config": str(path),
        "prior_cases_considered": len(cases),
        "selected_style_seen_before": any(
            case.get("selected_style") == selection.get("selected_style") for case in cases
        ),
        "current_case": {
            "case_id": case_id,
            "status": seen[-1].get("status") if seen else "pending_review",
            "review_command": "python visualization/artist-lottery/record_case_review.py --entry output/art-style-lottery-entry.json --status accepted",
        },
    }


def enrich_style_selection(selection, style_lookup, report_date, data_dir):
    """Attach the contract and memory metadata without changing lottery choice."""
    if not selection.get("enabled"):
        selection.update({
            "contract_version": STYLE_CONTRACT_VERSION,
            "style_contract": None,
            "evaluation_contract": None,
            "mechanism_extract": [],
            "surface_fidelity": "not_run_visual_backend_disabled",
            "mechanism_fidelity": "not_run_visual_backend_disabled",
            "fidelity_verdict": "not_run_visual_backend_disabled",
            "rejection_reason": None,
            "case_memory": build_case_memory(selection, report_date, data_dir),
        })
        return selection
    entry = style_lookup.get(selection.get("selected_style"))
    selection["contract_version"] = STYLE_CONTRACT_VERSION
    selection["style_contract"] = build_style_contract(entry)
    selection["mechanism_extract"] = selection["style_contract"]["mechanisms"]
    selection["evaluation_contract"] = build_evaluation_contract(selection["style_contract"])
    selection["surface_fidelity"] = "pending_visual_qa"
    selection["mechanism_fidelity"] = "pending_visual_qa"
    selection["fidelity_verdict"] = "pending_visual_qa"
    selection["rejection_reason"] = None
    selection["case_memory"] = build_case_memory(selection, report_date, data_dir)
    selection["case_id"] = selection["case_memory"]["current_case"]["case_id"]
    return selection


def _compact(text, limit=180):
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def build_trend_translation(style_contract, trends):
    if not style_contract:
        return []
    mechanisms = style_contract.get("mechanisms", [])
    translations = []
    for index, trend in enumerate(trends, 1):
        selected = [mechanisms[(index - 1) % len(mechanisms)], mechanisms[index % len(mechanisms)]] if mechanisms else []
        translations.append({
            "trend_index": index,
            "trend_title": trend.get("title"),
            "structural_variable": trend.get("variable") or "待从趋势正文确认",
            "mechanism_ids": [item["id"] for item in selected],
            "mechanism_rules": [item["rule"] for item in selected],
            "visual_thesis": f"用 {' + '.join(item['id'] for item in selected)} 把“{_compact(trend.get('title'), 72)}”的结构变化变成可观看的关系，而不是插图化新闻摘要。",
            "composition_job": "主体、阅读路径和空间骨架必须与其他趋势不同；共享材料语法，不共享构图模板。",
            "evidence_boundary": "图像只承载判断入口；数字、来源与反例回到详细日报正文。",
        })
    return translations


def build_prompt_trace(style_contract, trends, trend_translation):
    if not style_contract:
        return []
    traces = []
    for translation, trend in zip(trend_translation, trends):
        traces.append({
            "trend_index": translation["trend_index"],
            "trend_title": trend.get("title"),
            "artist_name_as_prompt_shortcut": False,
            "components": {
                "mechanism_fact": translation["mechanism_rules"],
                "trend_proposition": _compact(trend.get("desc"), 280),
                "subject_and_spatial_relation": translation["visual_thesis"],
                "material_and_light": "沿用当日契约的材料动作与观看条件；不追加无法解释的科技质感。",
                "type_and_information_hierarchy": "大字号中文标题、单一主判断、证据回查入口，文字不压过主体。",
                "exclusions_and_cultural_safety": style_contract["anti_patterns"],
            },
        })
    return traces


def return_route(stage, finding, fix):
    if stage not in RETURN_STAGES:
        stage = "craft"
    return {"return_to": stage, "finding": finding, "fix": fix}
