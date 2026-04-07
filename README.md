<div align="center">

# 🤖 AI News Digest

**AI 行业日报自动化引擎 · Automated AI Industry Daily Report Engine**

[![Mira Skill](https://img.shields.io/badge/Mira_Skill-Installed-blue?style=flat-square)](https://github.com/chengjialu8888/AI_News_Digest)
[![Sources](https://img.shields.io/badge/信源覆盖-45+-orange?style=flat-square)](#信源架构--source-architecture)
[![QA Gates](https://img.shields.io/badge/质量关卡-5_Gates-green?style=flat-square)](#五道质量审核--5-qa-gates)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

> 3 分钟掌握当天 AI 领域最值得关注的动态，每条新闻都有可点击的原始链接。
>
> Get the most important AI industry updates in 3 minutes — every item backed by clickable source links.

[中文](#中文说明) · [English](#english) · [快速开始 Quick Start](#快速开始--quick-start)

</div>

---

# 中文说明

## 为什么需要 AI News Digest？

| 痛点 | 现有方案 | AI News Digest |
|------|---------|---------------|
| 信息分散 | 手动刷 10+ 网站/公众号 | **45+ 信源自动巡检**，一次出稿 |
| 海外盲区 | 中文媒体转译延迟 24-48h | **25 位 Builder 实时 Feed** + 28 信源英文直连 |
| 假新闻/噪声 | 无验证机制 | **5 道 QA Gate**：交叉验证 + 事实核验 + 信号分级 |
| 原文不可达 | 聚合平台只给摘要 | **每条必附一手原文链接** + 5 层反爬降级 |
| 格式杂乱 | 复制粘贴人工整理 | **结构化 Markdown + 12 列 CSV** 双输出 |
| 趋势判断靠感觉 | 编辑主观筛选 | **跨 10+ 平台趋势验证**，数据驱动信号分级 |

## 信源架构 · Source Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI News Digest Engine                      │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│  Tier 1-2   │   Tier 3    │   Tier 5    │     Tier 6        │
│  中文核心    │  英文信源    │ Builder Feed │   虾评增强         │
├─────────────┼─────────────┼─────────────┼───────────────────┤
│ 新智元       │ TechCrunch  │ follow-     │ news-aggregator   │
│ 量子位       │ The Verge   │ builders    │ (28源批量抓取)      │
│ 机器之心     │ Reuters     │ ┌─ X推文     │                   │
│ 36Kr        │ Bloomberg   │ ├─ 播客      │ smart-web-fetch   │
│ 华尔街见闻   │ HuggingFace │ └─ 博客      │ (5层反爬降级)      │
│ 极客公园     │ Product Hunt│             │                   │
│ IT之家      │ TLDR        │ 25位顶级     │ content-trend     │
│ 海外独角兽   │ GitHub      │ AI Builder  │ (趋势验证)         │
├─────────────┴─────────────┴─────────────┴───────────────────┤
│  Tier 4: 数据型 (aicpb.com / AIwatch / Toolify / Trust MRR) │
└─────────────────────────────────────────────────────────────┘
```

### Tier 6 虾评增强层（v0407 新增）

通过 [虾评Skill](https://xiaping.coze.site) 平台集成的 3 个增强技能：

| 技能 | 能力 | 解决的问题 |
|------|------|-----------|
| **全网新闻聚合助手** | 28 信源一键批量抓取（HN / GitHub / HF Papers / AI Newsletters / 华尔街见闻 / 微博 / Product Hunt 等） | 减少逐站巡检耗时，从 30min → 5min |
| **Smart Web Fetch** | 5 层反爬降级（markdown.new → defuddle.md → r.jina.ai → Scrapling → Playwright） | 抓取成功率从 ~70% 提升至 ~95% |
| **内容趋势研究** | 跨 10+ 平台趋势分析（Google Trends / Reddit / X / YouTube） | 用数据而非直觉判断新闻重要性 |

## 五道质量审核 · 5 QA Gates

```
Gate 1: 数据源健康检查    → 信源是否正常返回、时效性校验
Gate 2: 去重与交叉验证    → 同一事件多源交叉确认，消除重复
Gate 3: 信号分级          → 🔴 重磅 / 🟡 值得关注 / ⚪ 常规
Gate 4: 事实核验          → 数据、引用、公司名、时间线准确性
Gate 5: 完整性自检        → 是否覆盖所有板块，是否有遗漏
```

## 输出格式

### Markdown 日报

```
# AI 日报 2026-04-07

## 一句话总结
> OpenAI 发布 GPT-5 Turbo，Google DeepMind 开源 Gemma 3...

## 📰 偏fact类新闻

### 🏢 大厂动向
1. 🔴 **OpenAI 发布 GPT-5 Turbo** — 推理速度提升 3x...[[OpenAI Blog]](https://openai.com/blog/...)

### 🚀 初创 / 融资
### 🌐 生态 / 政策

## 💬 偏观点类
## 🌍 海外建设者动态
## 📊 质量审核报告
```

### CSV 结构化数据（12 列）

| 日期 | 编号 | 板块 | 标题 | 信号等级 | 事实核验 | 关联公司 | 关联赛道 | 来源 | 原文URL | 摘要 | 是否推送 |
|------|------|------|------|---------|---------|---------|---------|------|---------|------|---------|

## 与其他方案的对比

| 维度 | AI News Digest | 传统 RSS 阅读器 | ChatGPT 生成新闻 | 人工编辑日报 |
|------|---------------|----------------|-----------------|-------------|
| 信源数量 | **45+** | 取决于订阅 | 训练数据截止 | 5-10 个 |
| 实时性 | **当日实时** | 实时 | 延迟数月 | 当日但慢 |
| 信号分级 | **🔴🟡⚪ 三级** | 无 | 无 | 人工主观 |
| 事实核验 | **5 道 QA Gate** | 无 | 易幻觉 | 人工有限 |
| 原文链接 | **每条必附** | 有 | 经常编造 | 有但不全 |
| 海外 Builder | **25 人 Feed** | 需自己找 | 无 | 极少覆盖 |
| 反爬能力 | **5 层降级** | N/A | N/A | 手动打开 |
| 趋势验证 | **跨平台数据** | 无 | 无 | 靠经验 |
| 输出格式 | **MD + CSV** | 原文 | 纯文本 | 各异 |
| 成本 | **零成本** | 免费/付费 | $20/月 | 人力 |

## 项目结构

```
AI_News_Digest/
├── ai-daily-report/
│   └── SKILL.md              # 核心技能定义（530 行）
├── evals/
│   └── evals.json            # 3 组评测用例
├── news-aggregator-skill/     # 虾评：28 信源批量抓取
│   ├── SKILL.md
│   └── scripts/fetch_news.py
├── smart-web-fetch/           # 虾评：5 层反爬降级
│   ├── SKILL.md
│   └── scripts/fetch.py
├── content-trend-researcher/  # 虾评：趋势验证
│   └── SKILL.md
└── README.md
```

## 快速开始 · Quick Start

### 作为 Mira Skill 使用

```bash
# 安装到 Mira skills 目录
cp -r ai-daily-report /opt/tiger/mira_nas/plugins/prod/<your_id>/skills/

# 然后在 Mira 中说：
# "跑一下今天的 AI 日报"
# "今天有什么 AI 新闻"
# "出一期日报"
```

### 作为独立提示词使用

将 `ai-daily-report/SKILL.md` 的内容作为 System Prompt 输入任何支持工具调用的 LLM（Claude / GPT-4 / Gemini），即可驱动日报生成。

---

# English

## Why AI News Digest?

AI News Digest is an **automated AI industry daily report engine** that eliminates the gap between scattered news sources and actionable intelligence. Unlike generic AI summarizers that hallucinate links and miss breaking news, this system:

- **Inspects 45+ sources** systematically — from Chinese tech media to HuggingFace Papers to 25 top AI builders' real-time feeds
- **Verifies every claim** through 5 QA gates — cross-validation, fact-checking, and signal grading (🔴/🟡/⚪)
- **Attaches original source links** to every single news item — no fabricated URLs, no dead links
- **Defeats anti-scraping** with 5-layer fallback (markdown.new → defuddle.md → r.jina.ai → Scrapling → Playwright)
- **Validates trends with data** — cross-platform trend analysis across Google Trends, Reddit, X, YouTube

## How It Compares

| Feature | AI News Digest | RSS Readers | ChatGPT News | Manual Curation |
|---------|---------------|-------------|--------------|----------------|
| Source Count | **45+** | Varies | Training cutoff | 5-10 |
| Real-time | **Same day** | Real-time | Months delayed | Same day, slow |
| Fact Verification | **5 QA Gates** | None | Hallucinations | Limited |
| Source Links | **Every item** | Yes | Often fabricated | Partial |
| Builder Tracking | **25 people** | DIY | None | Rare |
| Anti-scraping | **5-layer fallback** | N/A | N/A | Manual |
| Output Format | **MD + CSV** | Raw | Plain text | Varies |
| Cost | **Free** | Free/Paid | $20/mo | Labor |

## Source Architecture

### 6-Tier Source Hierarchy

| Tier | Sources | Purpose |
|------|---------|---------|
| **Tier 1** (Must-check) | 新智元, 量子位, 机器之心, 36Kr, 华尔街见闻, 极客公园 | Chinese core news |
| **Tier 2** | 有新Newin, AIBase, IT之家, 海外独角兽, 赛博禅心 | Cross-validation & depth |
| **Tier 3** (English) | TechCrunch, The Verge, Reuters, Bloomberg, HuggingFace, TLDR | First-hand international news |
| **Tier 4** (Data) | aicpb.com, AIwatch.ai, Toolify.ai | Product data & rankings |
| **Tier 5** (Builder Feed) | follow-builders (25 AI builders' X posts, podcasts, blogs) | Builder-level real-time insights |
| **Tier 6** (Enhanced) | news-aggregator (28 sources), smart-web-fetch (anti-scrape), content-trend (validation) | Coverage boost + reliability |

### Tier 6: XiaPing Skill Enhancements (v0407)

Integrated from the [XiaPing Skill](https://xiaping.coze.site) marketplace:

| Skill | Capability | Problem Solved |
|-------|-----------|----------------|
| **News Aggregator** | Batch-fetch from 28 sources (HN, GitHub, HF Papers, AI Newsletters, etc.) | Reduces per-source scan time from 30min to 5min |
| **Smart Web Fetch** | 5-layer anti-scraping fallback | Raises fetch success rate from ~70% to ~95% |
| **Content Trend Researcher** | Cross-platform trend analysis (Google Trends, Reddit, X, YouTube) | Data-driven signal grading instead of gut feeling |

## Quick Start

### As a Mira Skill

```bash
cp -r ai-daily-report /opt/tiger/mira_nas/plugins/prod/<your_id>/skills/
# Then tell Mira: "Generate today's AI daily report"
```

### As a Standalone Prompt

Feed the contents of `ai-daily-report/SKILL.md` as a System Prompt to any tool-calling LLM (Claude / GPT-4 / Gemini) to drive the report generation workflow.

## Evaluation Results

| Test Case | Score | Grade |
|-----------|-------|-------|
| Standard Daily Report | 92 | A |
| Specific Company Focus | 90 | A |
| Multi-day Comparison | 88 | A- |
| **Mean** | **90.0** | **A** |

## License

MIT

---

<div align="center">

**Built with ❤️ for the AI community**

*Star ⭐ this repo if you find it useful!*

</div>
