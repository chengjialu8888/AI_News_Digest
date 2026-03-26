# AI News Digest 🤖📰

**3 分钟掌握全球 AI 行业今日最值得关注的动态。**

一个 AI Agent Skill，自动搜索中英文 30+ 信源、追踪 25 位海外顶级 Builder 动态、经 5 道质量审核门把关，生成带原始链接的结构化日报。即装即用，一句话触发。

---

## Why This Exists

AI 行业每天产生数百条新闻，但真正值得你停下来看的可能不到 15 条。

手动刷 36Kr、TechCrunch、X/Twitter 至少需要 40 分钟。这个 Skill 把这 40 分钟压缩成一句 prompt：

```
跑一下今天的AI日报
```

你会得到一份经过**采集 → 去重 → 交叉验证 → 信号分级 → 事实核验**的结构化日报，每条新闻都能点进原始出处。

## What Makes It Different

| | 传统 AI 新闻聚合 | AI News Digest |
|---|---|---|
| 信源 | 单一语言，10 个左右 | 中英文 30+ 信源，5 层优先级 |
| Builder 动态 | 无 | 集成 [follow-builders](https://github.com/zarazhangrui/follow-builders)，25 人实时推文 + 播客 |
| 质量控制 | 无或人工 | 5 道自动 QA Gate（信源健康/去重/分级/核验/完整性） |
| 原始链接 | 常缺失 | 每条强制附一手 URL，禁止编造 |
| 输出格式 | 纯文本 | Markdown + CSV 12 列结构化数据 |
| Watch Focus | 泛泛覆盖 | 基于 1200+ 历史日报量化分析的公司 & 赛道优先级 |

## Quick Start

**安装（选一种）：**

```bash
# OpenClaw
clawhub install ai-daily-report.skill

# Claude Code
unzip ai-daily-report.skill -d ~/.claude/skills/

# Mira
# 将 ai-daily-report/SKILL.md 放入用户 skills 目录
```

**使用：**

```
跑一下今天的AI日报
帮我生成AI行业新闻速递，重点关注Agent和大模型
出一期日报，今天有什么值得关注的AI新闻？
```

## Output Preview

<details>
<summary>📰 点击展开示例日报（2026-03-26）</summary>

### 一句话总结
OpenAI关停Sora震动好莱坞；Arm发布首颗自研数据中心AI芯片股价飙升16%；博鳌论坛定调"2026智能体元年"。

### 偏fact类
| # | 标题 | 信号 | 来源 |
|---|------|------|------|
| 1 | OpenAI关停Sora视频平台，迪士尼10亿美元合作终止 | 🔴 | CNN / NYT / Reuters |
| 2 | Arm发布首颗自研芯片AGI CPU，Meta为首家客户 | 🔴 | TechCrunch / CNBC |
| 3 | Reflection AI洽谈25亿美元融资，估值250亿 | 🔴 | Reuters / WSJ |
| 4 | 博鳌论坛定调"2026智能体AI元年" | 🔴 | 中国新闻网 / 东方财富 |
| 5 | 快手2025年全年营收1428亿，可灵AI贡献超10亿 | 🟡 | 科创板日报 |
| 6 | Sand.ai开源三连击填补Sora真空 | 🟡 | 新浪科技 |

### 海外建设者
| Builder | 动态 |
|---------|------|
| Andrej Karpathy | "12月以来未写一行代码"，AI Agent接管80%开发 |
| Sam Altman | AI未来可能像水电一样作为公用事业出售 |

### 质量审核：5/5 Gate ✅

完整示例：[sample-output-2026-03-26.md](ai-daily-report/examples/sample-output-2026-03-26.md) · [CSV](ai-daily-report/examples/sample-output-2026-03-26.csv)

</details>

## Architecture

```
"跑一下今天的AI日报"
        │
        ▼
┌─────────────────────────────────────────────┐
│  Phase 1: Sensor Layer                      │
│  6+ rounds search × 30+ sources            │
│  + follow-builders Feed (25 KOLs)           │
│  + 5 podcasts + 2 official blogs            │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  Phase 2: Watch Focus                       │
│  Tier 1-3 Companies × Priority Tracks       │
│  (from 1200+ historical news analysis)      │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  Phase 3: Quality Audit (5 QA Gates)        │
│  Source Health → Dedup → Signal Grade       │
│  → Fact Check → Completeness                │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  Phase 4: Output                            │
│  📄 Markdown (human) + 📊 CSV 12-col (data) │
│  Every item with original source URL        │
└─────────────────────────────────────────────┘
```

## Source Tiers

| Tier | Sources | Purpose |
|------|---------|---------|
| **1 (必查)** | 新智元、量子位、机器之心、36Kr、华尔街见闻 | 国内核心 |
| **2** | AIBase、IT之家、腾讯AI研究院 | 补充验证 |
| **3 (EN)** | TechCrunch、Reuters、Bloomberg、The Verge | 海外一手 |
| **4** | aicpb.com、Toolify.ai | 产品数据 |
| **5 (Builder)** | [follow-builders](https://github.com/zarazhangrui/follow-builders) Feed | 25位 Builder 推文 + 播客 + 博客 |

## Eval Results

| Test Case | Prompt | Grade | Score |
|-----------|--------|-------|-------|
| Standard | "跑一下今天的AI日报" | **A** | 92 |
| Focused | "重点关注Agent和大模型方向" | **A** | 90 |
| Casual | "今天有什么值得关注的AI新闻？" | **A-** | 88 |

**Mean: 90.0 · Pass Rate: 3/3 (100%)**

## Project Structure

```
├── ai-daily-report.skill          # Packaged skill (install directly)
├── ai-daily-report/
│   ├── SKILL.md                   # Skill definition (316 lines)
│   ├── evals/
│   │   ├── evals.json             # Test cases
│   │   └── eval-results.json      # Eval scores
│   └── examples/
│       ├── sample-output-*.md     # Sample digest
│       └── sample-output-*.csv    # Sample CSV
└── README.md
```

## Related

- [follow-builders](https://github.com/zarazhangrui/follow-builders) — The builder feed this skill pulls from. Follow builders, not influencers.

## License

MIT
