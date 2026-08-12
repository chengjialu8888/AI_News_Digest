<p align="center">
  <img src="assets/github-header.svg" alt="AI News Digest - From scattered AI signals to a trusted daily brief" width="100%">
</p>

<div align="center">

# AI News Digest

**把分散的 AI 动态，压缩成一份可验证、可追溯、可复用的行业日报。**<br>
**Turn scattered AI signals into a verified daily brief with source links and structured outputs.**

[![Mira Skill](https://img.shields.io/badge/Mira_Skill-Ready-blue?style=flat-square)](https://github.com/chengjialu8888/AI_News_Digest)
[![Sources](https://img.shields.io/badge/Sources-60%2B-orange?style=flat-square)](#source-system)
[![QA Gates](https://img.shields.io/badge/QA_Gates-5-green?style=flat-square)](#trust-layer)
[![Outputs](https://img.shields.io/badge/Outputs-Feishu_%2B_MD_%2B_Archive_%2B_CSV_%2B_HTML-purple?style=flat-square)](#outputs)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](#license)

[中文](#中文) · [English](#english) · [快速开始](#快速开始) · [Quick Start](#quick-start) · [Source System](#source-system)

</div>

---

## 中文

AI News Digest 是一个面向 **AI 从业者、投资研究者、产品经理、内容创作者和开发者** 的日报生成引擎。它不是再做一个“AI 总结器”，而是把散落在中英文媒体、官方博客、GitHub、Hacker News、Hugging Face、X Builder 动态和 RSS Feed 里的信号，整理成一份可以直接阅读、追踪和二次加工的行业情报。

你可以用它每天生成：

- 一份 **3 分钟可读完** 的 AI 行业日报
- 每条新闻都带 **原始链接** 的可追溯摘要
- 微信公众号文章可抓取 **全文 Markdown 归档**，不只依赖搜索片段
- 带信号等级的内容筛选：重磅 / 值得关注 / 常规
- 可沉淀到表格、看板或知识库的 **12 列 CSV**
- 飞书 **Newsrun 卡片**、**详细版文档**、**结构化沉淀文档**、CSV 和 HTML 五类产物
- 详细版默认配套由 imagegen 直接生成“图 + 字”的三张 16:9 趋势 PNG；需要艺术化输出时，可选开启艺术家 Lottery：从 MoMA、Centre Pompidou 等现当代机构馆藏锚定的现代/当代艺术风格池抽取当日视觉语法，同时巡检 Art Basel Basel、Miami Beach、Hong Kong、Paris 官方名录捕捉当代视觉信号；艺术博览会只作为发现层，仍需经过语境、来源和视觉执行复核。开启后每日风格会追加到统一的「AI日报｜艺术风格 Lottery」飞书文档；HTML 仍是独立日报阅读产物，不是趋势图默认中间格式
- `初创动向` 每日优先扫描 AI 产品上游供给层与下游产品层的 AI-native startup，关注现金流/经营信号和成长线索；普通垂类公司不纳入，不把融资额当作商业成功
- 适合团队同步、选题会、投研记录和公众号素材库的结构化输出
- 面向长程运行的 **Codex Goal × Ralph Loop × Kleisli Gate** 工作流
- 首次使用前先询问你的产物偏好，避免把个人速读、团队同步、投研和内容运营混成同一种交付

## 它解决什么问题？

| 读者痛点 | 常见做法 | AI News Digest 的做法 |
| --- | --- | --- |
| 每天刷太多源，仍然怕漏掉大事 | 手动打开 10+ 网站、公众号和社群 | 60+ 信源分层巡检，一次生成日报 |
| 中文信息慢半拍，海外一手动态跟不上 | 等转译、等二次报道 | 英文官方源 + GitHub/HN/HF + Builder Feed 直接进入流程 |
| AI 生成新闻容易编链接、混事实 | 让通用模型直接总结 | 5 道 QA Gate：去重、交叉验证、事实核验、信号分级 |
| 微信公众号只有标题片段，正文难回溯 | 凭搜索摘要判断内容 | wechat-article-fetch 抓取 mp.weixin.qq.com 全文，保存 Markdown 和图片资源 |
| 有摘要但不能复盘来源 | 只保存最终文章 | 每条内容保留原文 URL，方便团队回溯和验证 |
| 日报只能阅读，不能运营 | 复制粘贴再整理 | 飞书卡片 + 详细版文档 + 结构化沉淀 + CSV + HTML，方便进入表格、知识库和内容流水线 |
| 产物一开始就不适配自己的工作方式 | 先生成，再人工删改 | 首次使用前确认场景、语言、语气、产物组合、推送位置和沉淀规则 |
| 全量日报跑到一半上下文爆炸 | 单个 prompt 硬塞采集、分析、出稿 | Codex Goal 分阶段运行，每个阶段独立上下文，只把结构化结果落盘 |
| 中途失败只能从头再来 | 人工重跑，容易漏步骤 | Ralph Loop 用 `.progress` / `.done` 断点续跑，失败后回到最近有效阶段 |
| 多阶段处理后出现跨日重复、版本冲突 | 最后人工检查，证据散落 | Kleisli Gate 逐步传递 Report 状态、证据和告警，可短路失败并写入 QA trace |

## 长程运行架构

AI News Digest 现在不只是一个“日报提示词”，而是一个可以持续跑完复杂信息工作的分阶段系统。

| 架构模块 | 长程运行里的问题 | 解决方式 |
| --- | --- | --- |
| **Codex Goal** | 60+ 信源、邮件、MCP、HN 评论和 QA 全塞进一个窗口，容易在后半程失控 | 把采集、合并、质检、渲染拆成独立 Goal；每个 Goal 只读本阶段需要的上下文 |
| **Ralph Loop** | 工作跨多个阶段后，任何一次失败都会破坏连续性 | 用文件系统做记忆，通过 `.progress` / `.done` 标记阶段状态，支持持续运行和断点续跑 |
| **Kleisli Arrow / Report Monad** | 多个质量 gate 串联时，错误、证据、告警很难稳定传递 | 每个 gate 返回 `Report[value, status, evidence]`；状态自动升级，失败可短路，证据进入最终报告 |
| **文件存储层** | Agent 记忆不可靠，长搜索记录会撑爆上下文 | 只在阶段之间传递 `data/*.json`、trace 和 output 文件，原始信息在本地沉淀 |
| **QA Trace** | 读者看不到哪些条目被剔除、为什么被降级 | 跨日去重、版本一致性、URL 策略等结果写入 trace，并在日报中显式提示 |

## 适合谁？

| 角色 | 可以怎么用 |
| --- | --- |
| AI 产品 / 运营 | 每天快速判断产品、模型、政策和竞品变化 |
| 投资 / 研究 | 收集融资、公司动态、技术趋势和早期项目信号 |
| 开发者 / Builder | 跟踪新工具、开源项目、论文、模型和 Agent 生态 |
| 内容创作者 | 建立稳定选题池，减少低质量转载和信息重复 |
| 团队负责人 | 把日报作为晨会、周会和行业同步材料 |

## 一眼看懂：工作流与产品架构

### 工作流

```mermaid
flowchart LR
    A["60+ 中英文信源"] --> B["抓取与反爬降级"]
    B --> C["去重与交叉验证"]
    C --> D["信号分级"]
    D --> E["事实核验"]
    E --> F["Markdown 日报"]
    E --> G["12 列 CSV"]
    F --> H["询问用户补充"]
    G --> H
    H --> I["最终版 Markdown 三大趋势"]
    I --> J["ImageGen 三张 16:9 图 + QA"]
    J --> K["飞书详细版 + 结构化沉淀"]
    K --> L["Newsrun 卡片推送"]
```

### 产品架构

<p align="center">
  <img src="assets/product-architecture.svg" alt="AI News Digest product architecture" width="100%">
</p>

## Trust Layer

AI News Digest 的核心价值不是“写得更像日报”，而是让日报更可信。

质量检测环节的设计灵感来自 [Signex](https://github.com/zhiyuzi/Signex)：把分散信号先沉淀为可检查的数据，再通过 source health、去重、分析视角和反馈记忆，让日报不只是“聚合”，而是逐步变成一个可校准的情报工作流。

```text
Gate 1: 数据源健康检查  -> 信源是否正常返回、内容是否足够新
Gate 2: 去重与交叉验证  -> 合并同一事件，优先保留一手来源
Gate 3: 信号分级        -> 标记重磅、值得关注、常规信息
Gate 4: 事实核验        -> 检查公司名、时间线、数字、引用和链接
Gate 5: 完整性自检      -> 确认日报板块覆盖完整，无明显遗漏
```

## Source System

AI News Digest 使用 9 层信源系统，把“覆盖面”和“可靠性”拆开处理。

| Tier | 信源类型 | 价值 |
| --- | --- | --- |
| Tier 1-2 | 新智元、量子位、机器之心、36Kr、华尔街见闻、极客公园、IT之家等中文核心源 | 中文语境下的行业动态与本土化解读 |
| Tier 3 | TechCrunch、The Verge、Reuters、Bloomberg、Hugging Face、TLDR、GitHub 等英文源 | 海外一手发布与国际视角 |
| Tier 4 | aicpb.com、AIwatch.ai、Toolify.ai 等数据型来源 | 产品榜单、流量、热度和市场侧参考 |
| Tier 5 | [follow-builders](https://github.com/zarazhangrui/follow-builders)：25 位 AI Builder 的 X 动态、6 个 AI 播客、Anthropic/Claude 官方博客 | 捕捉社区里比媒体更早出现的 Builder 原创观点和弱信号 |
| Tier 6 | news-aggregator、smart-web-fetch、content-trend-researcher | 批量抓取、反爬降级、跨平台趋势验证 |
| Tier 7 | wechat-article-fetch、Sensight social_search、大厂公众号、行业深度公众号 | 微信生态首发内容 + 可回溯原文全文 |
| Tier 8 | [agents-radar MCP](https://github.com/duanyytop/agents-radar) | GitHub、ArXiv、HN、HF、Product Hunt、Dev.to、Lobste.rs 等结构化 AI 生态数据 |
| Tier 9 | [AI HOT Feed](https://aihot.virxact.com/feed.xml) | 中文预处理的 AI 热点、官方发布与 KOL 观点 |

## Outputs

第一次运行前，工作流会先询问产物偏好：使用场景、产物组合、语言语气、推送位置和沉淀规则。确认后写入 `data/output-preferences.json`，后续运行默认复用；这让同一套日报可以稳定服务个人速读、团队晨会、投研记录、内容运营和知识库沉淀。

各类产物各自承担不同工作：

| 产物 | 用途 | 长期价值 |
| --- | --- | --- |
| 飞书 Newsrun 卡片 | 每日高信号速览和团队推送 | 降低分发摩擦，让运营动作每天稳定发生 |
| Markdown / 飞书详细版文档 | 完整日报、趋势判断、QA 说明 | 保留可阅读叙事，方便周报和复盘引用 |
| ImageGen 趋势图 | 默认后端；三大趋势各一张 16:9 图，图中文字直接生成，只保留批判性判断 | 让趋势先被看懂，再回到详细正文核验 |
| 艺术家 Lottery 趋势图 | 可选后端；博物馆锚定的艺术家/艺术运动语法 + 三张 16:9 ImageGen 图 + 独立 Lottery 表格日志 | 给日报增加可复盘的视觉语法，风格服务于当日趋势而不是固定模板 |
| Mck PPT 趋势图 | 三页咨询式 16:9 PPT + PNG，行动标题、关键佐证、结构判断、下周观察 | 把每日趋势变成可演示、可插图、可复盘的决策资产 |
| 结构化沉淀文档 | 按截图式分组表格记录板块、新闻、信号等级和首个原始链接 | 构建长期知识库、选题池和趋势命中率样本 |
| 12 列 CSV | 表格、Base、Dashboard、检索和二次分析 | 让新闻从文章变成可查询、可聚合的数据资产 |
| HTML | 浏览器预览、静态归档、跨团队分享 | 低成本发布和历史日报回看 |

### 可选艺术家 Lottery 视觉后端

默认视觉后端是 imagegen；需要使用艺术家/艺术运动作为当日视觉语法时，显式开启：

```bash
VISUAL_BACKEND=artist-lottery \
  python ralph-daily-loop/stage9.py
```

Lottery 链路会按日期可复现地从现代/当代目录抽签，优先使用 MoMA、Centre Pompidou 等机构的馆藏锚点，并把 Art Basel 各地官方名录作为发现层。它会把 `style_lottery`、博物馆/艺术博览会来源、三条趋势适配、三张 16:9 PNG、表格布局和 QA 结果写入 `output/daily-trends.json` 与 `output/art-style-lottery-entry.json`；只有开启此后端时，才追加统一的「AI日报｜艺术风格 Lottery」飞书文档。可用 `VISUAL_STYLE_OVERRIDE` 指定目录内风格，`RECENT_VISUAL_STYLES` 排除近期风格。

QA 采用 Qwen-Image-Bench 的五个一级维度：Quality、Aesthetics、Alignment、Real-world Fidelity、Creative Generation；日报工作流只做人工参考评审，不声称运行 Q-Judger。[维度与评分参考](https://github.com/QwenLM/Qwen-Image-Bench)

### Mck PPT Design 趋势可视化

仓库已接入 [likaku/Mck-ppt-design-skill](https://github.com/likaku/Mck-ppt-design-skill)（当前远端版本：`e190e083`）。它作为用户明确指定时使用的咨询式视觉后端，不替换默认的 imagegen 图像生成：同一份 `daily-trends.json` 可以按场景输出飞书插图或三页 PPT；趋势可视化 HTML 不默认生成。

Goal 9 会在 `output/daily-trends.json` 中保存最终三条趋势和佐证。确认最终 Markdown 后运行：

```bash
python visualization/mck-ppt-design/render_daily_trends.py \
  --trends-json output/daily-trends.json \
  --out-dir output/mck-ppt-design
```

渲染器遵循 Mck 的 S3/S4 机器门禁，产出 `content.json`、`gate_s3.json`、`gate_result.json`、三页 `.pptx` 和 `trend-1-mck.png` 至 `trend-3-mck.png`。PNG 固定为 16:9，可直接插入飞书详细版；如需公众号 HTML，必须由用户明确指定。完整来源仍留在日报正文，视觉层只承载判断入口。

### Markdown / 飞书详细版文档

```markdown
# AI 日报 2026-04-07

## 一句话总结
> 今天的主线：模型能力、Agent 工具链和 AI 基础设施继续加速。

## 偏 fact 类新闻

### 大厂动向
1. [重磅] OpenAI 发布新产品更新 -- 摘要... [[Source]](https://example.com)

### 初创 / 融资
### 生态 / 政策

## 偏观点类
## 海外建设者动态
## 质量审核报告
```

### CSV 结构化数据

| 日期 | 编号 | 板块 | 标题 | 信号等级 | 事实核验 | 关联公司 | 关联赛道 | 来源 | 原文URL | 摘要 | 是否推送 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

### 本地输出路径

```text
output/feishu-card.md
output/daily-report.md
output/structured-archive.md
output/daily-report.csv
output/daily-report.html
```

## 快速开始

### Claude Code

```bash
git clone https://github.com/chengjialu8888/AI_News_Digest.git ~/.claude/skills/ai-news-digest
```

### Codex

```bash
git clone https://github.com/chengjialu8888/AI_News_Digest.git ~/.codex/skills/ai-news-digest
```

### OpenClaw

```bash
git clone https://github.com/chengjialu8888/AI_News_Digest.git ~/skills/ai-news-digest
```

### Mira

```bash
cp -r ai-daily-report /opt/tiger/mira_nas/plugins/prod/<your_id>/skills/
```

### 其他个人助手

```bash
curl -L https://raw.githubusercontent.com/chengjialu8888/AI_News_Digest/main/ai-daily-report/SKILL.md -o ai-news-digest.system.md
```

安装后对你的助手说：“跑一下今天的 AI 日报”或“出一期适合团队晨会的 AI 行业日报”。首次运行时，它会先问你产物偏好；通用个人助手可把 `ai-news-digest.system.md` 作为 System Prompt 使用。

## 项目结构

```text
AI_News_Digest/
├── ai-daily-report/
│   ├── SKILL.md
│   ├── evals/
│   └── examples/
├── news-aggregator-skill/
├── smart-web-fetch/
├── content-trend-researcher/
├── wechat-article-fetch/
├── visualization/
│   └── artist-lottery/
├── assets/
│   └── github-header.svg
├── ai-daily-report.skill
└── README.md
```

## Evaluation

| Test Case | Score | Grade |
| --- | ---: | --- |
| Standard Daily Report | 92 | A |
| Specific Company Focus | 90 | A |
| Multi-day Comparison | 88 | A- |
| **Mean** | **90.0** | **A** |

---

## English

AI News Digest is a daily intelligence engine for **AI operators, researchers, investors, builders, and content teams**. It turns scattered signals from Chinese and English media, official blogs, GitHub, Hacker News, Hugging Face, X builder feeds, and RSS sources into a verified daily brief.

It helps you produce:

- A readable AI industry brief in about 3 minutes
- Source-linked summaries for every news item
- Full Markdown archives for WeChat articles, not just search snippets
- Signal grading for what is important, interesting, or routine
- A 12-column CSV for databases, spreadsheets, dashboards, and knowledge bases
- Five outputs: Feishu Newsrun cards, detailed docs, structured archive docs, CSV, and HTML
- A reusable workflow for team syncs, research notes, editorial planning, and market tracking
- A long-running **Codex Goal × Ralph Loop × Kleisli Gate** workflow for complex daily intelligence
- A first-run preference check so personal scanning, team distribution, research, and content operations do not get forced into the same output shape

## Why Star This Repo?

Star this repo if you want a practical starting point for building a reliable AI news workflow:

- It focuses on **source-backed intelligence**, not generic summaries.
- It combines **Chinese context + international first-hand sources**.
- It can fetch `mp.weixin.qq.com` articles into local Markdown archives for traceable Chinese-source verification.
- It ships with a reusable **Mira Skill / system prompt**.
- It outputs **Feishu cards**, **detailed docs**, **structured archives**, **CSV**, and **HTML**.
- It is designed to keep running as new AI sources, MCP servers, feeds, newsletters, and QA gates appear.
- It treats long-context failure as a product problem: stages, checkpoints, files, and traces are part of the design.
- It turns daily news into an operating system for memory: each issue becomes a readable brief, a pushable card, and a queryable dataset for future trend reviews.

Tier 5 builder signals come from [follow-builders](https://github.com/zarazhangrui/follow-builders), which tracks 25 curated AI builders on X, 6 AI podcasts, and official Anthropic/Claude blog updates.

The QA workflow is inspired by [Signex](https://github.com/zhiyuzi/Signex): source health checks, signal convergence, analysis lenses, and feedback memory are adapted here for daily AI news production.

## Long-Run Architecture

AI News Digest is no longer just a prompt for a daily brief. It is a staged system for finishing a large, failure-prone intelligence job without blowing up the context window.

| Component | Long-run failure mode | How it helps |
| --- | --- | --- |
| **Codex Goal** | One giant prompt tries to collect, analyze, verify, and render everything in a single context window | Splits the workflow into independent goals; each stage gets a clean context and writes structured output |
| **Ralph Loop** | A mid-run failure forces the whole report to start over | Uses `.progress` / `.done` checkpoint files so the run can resume from the last valid stage |
| **Kleisli Arrow / Report Monad** | QA gates lose evidence, warnings, or failure state as data moves across stages | Each gate returns `Report[value, status, evidence]`; status propagates, failures can short-circuit, and evidence becomes a trace |
| **File-backed memory** | Agent memory is unreliable and raw research quickly bloats the context | Only `data/*.json`, traces, and final outputs move between stages; raw collection stays persisted outside the prompt |
| **QA Trace** | Readers cannot see why an item was removed, downgraded, or flagged | Cross-day dedupe, version consistency, URL policy, and other checks write machine-readable traces and visible report notes |

## Quick Start

### Claude Code

```bash
git clone https://github.com/chengjialu8888/AI_News_Digest.git ~/.claude/skills/ai-news-digest
```

### Codex

```bash
git clone https://github.com/chengjialu8888/AI_News_Digest.git ~/.codex/skills/ai-news-digest
```

### OpenClaw

```bash
git clone https://github.com/chengjialu8888/AI_News_Digest.git ~/skills/ai-news-digest
```

### Mira

```bash
cp -r ai-daily-report /opt/tiger/mira_nas/plugins/prod/<your_id>/skills/
```

### Other Personal Assistants

```bash
curl -L https://raw.githubusercontent.com/chengjialu8888/AI_News_Digest/main/ai-daily-report/SKILL.md -o ai-news-digest.system.md
```

After installation, ask your assistant: "Generate today's AI daily report" or "Create an AI industry brief for my team sync." On the first run, it will ask for output preferences before producing or pushing artifacts. For generic assistants, use `ai-news-digest.system.md` as the system prompt.

## Output Workflow

The workflow produces a set of operational artifacts and asks for preferences before the first run:

| Output | Purpose | Operational value |
| --- | --- | --- |
| Feishu Newsrun card | Fast daily signal distribution | Keeps the daily push lightweight and repeatable |
| Markdown / Feishu detailed doc | Full brief, trend judgement, and QA notes | Preserves the narrative record for weekly reviews |
| Structured archive doc | Board/company/track/signal-level archive | Builds a long-term knowledge base and topic pool |
| 12-column CSV | Spreadsheet, Base, dashboard, and search workflows | Turns news into queryable operational data |
| HTML | Browser preview, static archive, internal sharing | Makes historical reports easy to browse and circulate |

### Mck PPT Design trend visuals

The repository now includes [likaku/Mck-ppt-design-skill](https://github.com/likaku/Mck-ppt-design-skill) (remote revision `e190e083`) as an optional consultant-style visual backend. The default visual backend is imagegen; the museum-grounded artist Lottery backend is also opt-in. Trend HTML is not generated unless the user explicitly requests it.

Goal 9 writes the final three trends and their evidence to `output/daily-trends.json`. After the Markdown is confirmed, run:

```bash
python visualization/mck-ppt-design/render_daily_trends.py \
  --trends-json output/daily-trends.json \
  --out-dir output/mck-ppt-design
```

The renderer follows Mck's machine-readable S3/S4 gates and produces `content.json`, `gate_s3.json`, `gate_result.json`, a three-slide `.pptx`, and `trend-1-mck.png` through `trend-3-mck.png`. The PNGs are fixed at 16:9 for Feishu; WeChat HTML requires an explicit user request. Full source evidence remains in the detailed report while the visual layer provides the decision entry point.

## How It Compares

| Dimension | AI News Digest | RSS Reader | Generic AI Summary | Manual Curation |
| --- | --- | --- | --- | --- |
| Source coverage | 60+ layered sources | Depends on subscriptions | Limited by model/tool access | Usually 5-10 sources |
| Freshness | Same-day source checks | Real-time but unfiltered | Often stale or incomplete | Same-day but slow |
| Fact verification | 5 QA gates | None | Risk of hallucinated claims | Manual and inconsistent |
| Source links | Required per item | Available but scattered | Often missing or fabricated | Partial |
| WeChat article depth | Full article fetch + Markdown archive | Title/snippet only | Usually unavailable | Manual copy/paste |
| Output | Feishu card + detailed doc + structured archive + CSV + HTML | Raw feeds | Plain text | Varies by editor |
| Best for | Repeatable intelligence workflow | Reading feeds | Quick brainstorming | High-touch editorial work |

## License

MIT

---

<div align="center">

**If this saves you from one hour of AI news digging, give it a star and make tomorrow's brief easier to produce.**

</div>

> Note: The example report title, date, and `https://example.com` link above are placeholders used to show the output format. Replace them with real daily report data before publishing generated examples.
