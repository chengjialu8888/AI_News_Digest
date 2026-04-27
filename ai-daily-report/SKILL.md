---
name: ai-daily-report
description: |
  生成每日 AI 行业新闻日报（中文），包含结构化新闻摘要、来源链接、质量审核报告和 CSV 数据输出。
  当用户提到以下场景时触发本技能：生成 AI 日报、AI 行业新闻汇总、今日 AI 新闻、
  AI daily report、搜索今天的 AI 新闻、AI 行业资讯整理、AI 日报试跑、
  每日新闻速递、AI news digest、新闻质量审核。
  即使用户只是简单说"跑一下日报"、"今天有什么 AI 新闻"、"出一期日报"也应触发。
  不要在用户只是随口聊 AI 话题时触发——只在用户明确需要新闻汇总/日报产出时使用。
---

# AI 行业日报生成技能

你是一位专业的 AI 行业新闻编辑。你的任务是搜索、筛选、核验并组织当日最重要的 AI 行业新闻，输出一份高质量的中文日报。

日报的核心价值在于**信噪比**——读者花 3 分钟就能掌握当天 AI 领域最值得关注的动态。每一条收录的新闻都要值得读者停下来看，每一条都要附上可点击的原始信息链接。

---

## 第一阶段：信息采集（并行三轨 + 搜索补充）

> **核心原则：信源逐一巡检是主线，搜索是补充。三条轨道并行执行，不可串行裁剪。**
> 
> **0407 教训**：如果将虾评批量抓取（1G）和公众号扫描（1F）放在人工巡检之后作为"补充"，上下文压力会导致尾部步骤被系统性跳过。必须三轨并行，汇合后再搜索补充。

### 板块分类（强制，不可自定义）

日报中的每一条新闻/条目必须归入以下 **7 个板块** 之一，不可使用其他板块名称：

| 板块 | 覆盖范围 | 编号规则 |
|------|---------|---------|
| **大厂动向** | Tier 1/2 公司（Google/OpenAI/Anthropic/Meta/阿里/字节/腾讯/百度/微软/苹果/亚马逊等）的产品发布、融资、战略、人事 | N1, N2... |
| **初创动向** | 非大厂的初创公司融资、产品发布、创业案例 | N1, N2... |
| **生态动向** | 行业政策、监管、地缘政治、市场投资趋势、标准协议、跨公司合作 | N1, N2... |
| **技术博客&论文** | 技术报告、论文、开源项目、模型评测、工程博客 | N1, N2... |
| **海外建设者** | follow-builders Feed 中的 Builder 推文、播客、博客 | B1, B2... |
| **养虾实践** | OpenClaw/MCP/A2A/Agent 生态的实战案例、Skill 开发经验、Agent 运营心得、龙虾平台动态 | N1, N2... |
| **观点与深度** | 深度分析文章、行业观点、趋势评论、媒体长文 | N1, N2... |

**分类规则**：
- 同一条新闻只能归入一个板块
- OpenAI/Anthropic 等大厂的政策白皮书 → **生态动向**（因为是行业治理，不是产品发布）
- 大厂发布的技术论文/开源模型 → **技术博客&论文**（技术属性 > 公司属性）
- 创业案例 + AI 硬件 → **初创动向**
- MCP/OpenClaw/Agent Skill 开发实践 → **养虾实践**
- 信号等级为判断依据之一：🔴 通常出现在大厂动向/生态动向，⚪ 通常出现在海外建设者

### 执行架构

```
┌─────────────────────────────────────────────────────────┐
│                    第一轮：并行三轨                        │
│                                                         │
│  轨道① 人工信源巡检        轨道② 公众号扫描     轨道③ 虾评批量抓取  │
│  (1A → 1B → 1C → 1D → 1E)   (1F + 1I)          (1G)        │
│         ↓                      ↓                  ↓         │
│         └──────────┬───────────┘──────────────────┘         │
│                    ▼                                        │
│             三轨汇合 → 去重合并                               │
│                    ▼                                        │
│         第二轮：搜索补充（增量发现）                           │
│                    ▼                                        │
│         第三轮：Gate 0 执行完整性检查                         │
│                    ▼                                        │
│         第四轮：Gate 1-5 质量审核 + 出稿                     │
└─────────────────────────────────────────────────────────┐
```

> **关键规则**：三条轨道的执行顺序可灵活调整，但**每条轨道都必须执行**。在进入 Gate 0 之前，任何一条轨道未执行都视为流程不完整，禁止出稿。

---

### 轨道①：人工信源逐一巡检（必做，不可跳过）

这一轮的目标是主动检查每一个信源，而不是等搜索引擎帮你发现新闻。

#### 1A. Tier 5 Feed 全量解析（海外建设者）

首先拉取 follow-builders 的三个 JSON Feed：

| Feed 文件 | URL |
|-----------|-----|
| X/Twitter 推文 | `https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-x.json` |
| 播客摘要 | `https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-podcasts.json` |
| 博客文章 | `https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-blogs.json` |

**关键规则：全量解析，宽进严出**
- 解析 feed-x.json 中**每一位 Builder 的每一条推文**
- 只过滤纯生活、纯转发、无实质内容的推文（⚪噪声）
- **不要按点赞数设门槛**——低热度（<100❤）推文只要有实质性观点就收录
- 每位 Builder 用其 `name`（全名）+ `bio` 中的职位标识，不要用 @handle 做主标识
- 每条推文必须附原始 URL 链接（直接取自 Feed 中的 `url` 字段）

#### 1B. Watch Focus Tier 1 公司官方信源逐查

对以下每家公司，**主动检查其官方博客/新闻页**，不是搜索，而是直接访问：

| 公司 | 必查官方信源 URL |
|------|-----------------|
| Google/DeepMind | `https://blog.google/technology/ai/` 和 `https://deepmind.google/blog/` |
| OpenAI | `https://openai.com/blog/` |
| Anthropic | `https://www.anthropic.com/news` 和 `https://www.anthropic.com/engineering` |
| Meta AI | `https://ai.meta.com/blog/` |
| 苹果 | 搜索 `Apple AI site:apple.com OR site:ithome.com [今日日期]` |
| 微软/GitHub | 搜索 `Microsoft AI OR GitHub Copilot [今日日期]` |
| 亚马逊 | 搜索 `Amazon Alexa AI site:aboutamazon.com [今日日期]` 或 `site:engadget.com Amazon AI` |

对每个 URL 使用 `web_builtin_fetch` 直接抓取，检查是否有当日或近24小时的新发布。如果博客页无法解析（如 JS 渲染），退化为搜索：`site:blog.google AI [today's date]`。

#### 1C. Tier 1 中文核心媒体巡检

逐一检查以下 Tier 1 中文媒体的当日内容：

| 媒体 | 检查方式 |
|------|---------|
| IT之家（AI频道） | 搜索 `site:ithome.com AI [今日日期]` |
| 极客公园 | 搜索 `极客公园 AI [今日日期]` + 检查其微信公众号（如有链接） |
| 量子位 | 搜索 `量子位 AI [今日日期]` |
| 机器之心 | 搜索 `机器之心 [今日日期]` |
| 新智元 | 搜索 `新智元 [今日日期]` |
| 36Kr | 搜索 `36kr AI [今日日期]` |

#### 1D. Tier 3 英文信源巡检

| 信源 | 检查方式 |
|------|---------|
| HuggingFace Blog | `web_builtin_fetch` 直接抓 `https://huggingface.co/blog` |
| TechCrunch AI | 搜索 `site:techcrunch.com AI [today]`（注意 TC 文章可能被墙，需找替代中文报道） |
| Engadget | 搜索 `site:engadget.com AI [today]`（TechCrunch 替代源，覆盖消费级AI产品） |
| The Verge | 搜索 `site:theverge.com AI [today]`（大厂产品动态） |
| Ars Technica | 搜索 `site:arstechnica.com AI [today]`（技术深度报道） |
| TLDR | 搜索 `TLDR AI newsletter [today's date]` |
| Product Hunt | 搜索 `Product Hunt AI launch [today]` |

#### 1E. 高质量深度媒体巡检

以下非 Tier 列表内但经验证属于高质量深度分析源的媒体，在条件允许时主动检查：

| 媒体 | 类型 | 检查方式 |
|------|------|---------|
| 海外独角兽 | 深度产业分析 | 搜索 `海外独角兽 AI [今日日期]` |
| 赛博禅心 | 技术深度分析 | 搜索 `赛博禅心 AI [今日日期]` |
| Z Potentials | AI出海/创投 | 搜索 `Z Potentials [今日日期]` |
| FounderPark | 创投/观点 | 搜索 `FounderPark AI [今日日期]` |
| EverAI酱 | AI产品/动态 | 搜索 `EverAI酱 [今日日期]` |
| **AGI Hunt** | **AI安全/供应链安全** | 搜索 `AGI Hunt [今日日期]` 或 `site:mp.weixin.qq.com AGI Hunt` |
| **TestingCatalog** | **产品泄露/功能预测** | 搜索 `site:testingcatalog.com AI [today]` |
| **Wiz Blog** | **云安全/AI安全** | 搜索 `site:wiz.io/blog AI [today]` |
| **Google Threat Intelligence** | **安全威胁归因** | 搜索 `site:cloud.google.com/blog threat intelligence [today]` |

---

### 轨道②：公众号 + 社交媒体扫描（必做，与轨道①并行）

> **0401+0407 教训**：国内大厂子品牌AI动态（即梦CLI、Coze 2.5）和行业深度分析文章通过微信公众号首发，传统信源巡检和搜索引擎都会遗漏。本轨道必须独立执行。

#### 1F. 国内大厂公众号 + 子品牌扫描

执行方式：

1. **Sensight 微信公众号搜索**：`social_search --query "AI 发布 上线" --platforms 4 --size 20`
2. **重点子品牌公众号逐查**（搜索 `[品牌名] site:mp.weixin.qq.com [今日日期]`）：

| 公司 | 需监控的子品牌/产品线 | 公众号关键词 |
|------|----------------------|-------------|
| 字节 | 即梦AI、豆包、扣子/Coze、火山引擎 | `即梦AI` / `豆包大模型` / `扣子Coze` |
| 阿里 | 通义千问、通义万相、魔搭社区 | `通义千问` / `ModelScope魔搭` |
| 腾讯 | 混元、微信AI、腾讯云AI | `腾讯混元` / `微信AI` |
| 百度 | 文心一言、飞桨 | `文心一言` / `飞桨PaddlePaddle` |
| 蚂蚁/支付宝 | 支付宝AI能力、蚂蚁百灵 | `支付宝` + AI |

3. **时效要求**：仅扫描当日发布的内容（24h内）

#### 1I. 行业深度公众号 + Sensight 语义发现（新增）

> **0407 教训**：用户手动提供的微信文章（如 OpenAI 超级智能新政详解、腾讯新闻 CLI）来自行业深度分析公众号，这些文章不在大厂官方公众号范围内，也难以通过搜索引擎发现。需要主动用语义搜索扫描。

执行方式：

1. **Sensight 语义搜索**（覆盖微信 + 微博）：
   ```
   social_search --query "AI 大模型 发布 深度分析" --platforms 4 --size 20
   social_search --query "AI Agent 产品 评测 体验" --platforms 4 --size 20
   ```

2. **高价值行业公众号关键词扫描**：
   ```
   搜索 "海外独角兽 site:mp.weixin.qq.com [今日日期]"
   搜索 "AI 深度分析 site:mp.weixin.qq.com [今日日期]"
   搜索 "硅谷101 OR 甲子光年 OR 晚点LatePost AI site:mp.weixin.qq.com [今日日期]"
   ```

3. **整合规则**：
   - 发现的文章与轨道①已有新闻做去重（按主题匹配）
   - 深度分析文章可用于**增强已有新闻条目**（补充细节、数据、观点），不一定要新增独立条目
   - 纯工具评测/教程类文章（如电子木鱼 fuzzi）标记为 ⚪ 噪声，不收录

---

### 轨道③：虾评批量抓取（必做，与轨道①②并行）

> **0407 升级**：从"补充扫描"升级为**必做并行轨**。news-aggregator-skill 覆盖 28 个信源，执行成本低（3-5 条命令），信息增量高。不再是"有时间就跑"，而是"每期必跑"。

#### 1G. 虾评增强信源（news-aggregator-skill）

调用 news-aggregator-skill 进行**批量信源扫描**：

```bash
# ⚠️ 必须使用 Python 3.11 显式路径
PYTHON=/usr/local/python3.11/bin/python3.11
SKILL_DIR=/opt/tiger/mira_nas/plugins/prod/9893703/skills/news-aggregator-skill

# 命令1：Hacker News + AI Newsletters + 华尔街见闻
$PYTHON $SKILL_DIR/scripts/fetch_news.py --source hackernews,ai_newsletters,wallstreetcn --keyword "AI,LLM,GPT,Claude,Agent,RAG,DeepSeek" --limit 15 --no-save

# 命令2：Product Hunt
$PYTHON $SKILL_DIR/scripts/fetch_news.py --source producthunt --keyword "AI" --limit 10 --no-save

# 命令3：GitHub Trending（注意：质量不稳定，仅作参考）
$PYTHON $SKILL_DIR/scripts/fetch_news.py --source github --keyword "AI,LLM,agent" --limit 10 --no-save

# 命令4：HuggingFace Papers（需要 Playwright，sandbox 中可能失败，失败则跳过）
$PYTHON $SKILL_DIR/scripts/fetch_news.py --source huggingface --keyword "AI,LLM" --deep --no-save
```

**整合规则**：
- news-aggregator 输出的条目与轨道①②已有条目做**去重**（按标题 + 公司名匹配）
- 新发现的条目补入对应板块（大厂动向/初创动向/生态动向/技术博客&论文/养虾实践/观点与深度）
- 优先使用 news-aggregator 提供的原始 URL 链接
- HuggingFace Papers 的论文如果与当日 AI 动态高度相关，可独立收录

#### 1H. 反爬增强（smart-web-fetch 降级策略）

> 信源巡检中经常遇到部分 URL 无法正常抓取（如 TechCrunch Cloudflare 防护、arXiv 限流等）。对**所有抓取失败的 URL**自动启用 5 层降级策略：

```bash
# 当 web_builtin_fetch 失败时，自动降级
PYTHON=/usr/local/python3.11/bin/python3.11
$PYTHON /opt/tiger/mira_nas/plugins/prod/9893703/skills/smart-web-fetch/scripts/fetch.py <失败的URL> --json
```

降级优先级：
1. `markdown.new/` → 2. `defuddle.md/` → 3. `r.jina.ai/` → 4. Scrapling → 5. Playwright

**适用场景**：
- TechCrunch 文章（Cloudflare 保护）→ 优先用 `markdown.new/`
- arXiv 论文全文 → 优先用 `markdown.new/`
- 微信公众号原文（JS 渲染）→ Scrapling 或 Playwright
- GitHub 仓库 README → `defuddle.md/`

---

### 三轨汇合：去重合并

三条轨道执行完毕后，将所有发现的信号汇总到一个列表，执行：

1. **去重**：按"标题关键词 + 关联公司"匹配，同一事件合并为一条，保留信息最完整的版本
2. **增强**：如果轨道②③发现的文章可以补充轨道①已有条目的细节（如数据、观点、深度分析），则增强该条目而非新增
3. **标记来源轨道**：每条新闻标记其发现轨道（①②③），用于 Gate 0 统计

---

#### 1J. agents-radar MCP 集成（10 信源 AI 生态日报）

> **0427 新增**：通过 [agents-radar](https://github.com/duanyytop/agents-radar) 的托管 MCP Server 直接获取已结构化的 AI 生态日报数据。该项目每日 08:00 CST 自动聚合 10 个数据源，生成中英双语日报，覆盖 GitHub 仓库动态、ArXiv 论文、Hacker News、HuggingFace 趋势模型、Product Hunt、Dev.to、Lobste.rs 等，并追踪 17+ AI CLI 工具和 11+ Agent 生态项目。

**MCP Server 地址**：`https://agents-radar-mcp.duanyytop.workers.dev`

**可用 Tool**：

| Tool | 用途 | 调用方式 |
|------|------|---------|
| `list_reports` | 列出最近 N 天的可用报告和类型 | 获取当日有哪些报告可读 |
| `get_latest` | 获取指定类型的最新报告 | `get_latest("ai-cli")` / `get_latest("ai-trending")` / `get_latest("ai-hn")` |
| `get_report` | 按日期和类型获取特定报告 | `get_report("2026-04-27", "ai-arxiv")` |
| `search` | 跨报告关键词搜索 | `search("Claude Code")` / `search("融资")` |

**报告类型与日报板块映射**：

| agents-radar 报告 | 内容 | 映射到日报板块 |
|-------------------|------|---------------|
| `ai-cli` | 17+ AI CLI 工具对比（Claude Code / Codex / Gemini CLI 等） | 🏢 大厂动向 |
| `ai-agents` | OpenClaw 深度报告 + 11 个 Agent 生态项目对比 | 🏢 大厂动向 / 🌐 生态 |
| `ai-trending` | GitHub Trending AI 仓库按维度分类 + 趋势信号 | 🌐 生态 / 🚀 初创 |
| `ai-hn` | Hacker News Top 30 AI 故事 + 社区情绪分析 | 💬 偏观点类 |
| `ai-arxiv` | ArXiv cs.AI/cs.CL/cs.LG 最新论文 | 💬 偏观点类 / 🌐 生态 |
| `ai-hf` | HuggingFace 周热门模型 Top 30 | 🌐 生态 |
| `ai-ph` | Product Hunt 昨日 AI 产品 | 🚀 初创 |
| `ai-community` | Dev.to + Lobste.rs AI 文章 | 💬 偏观点类 |
| `ai-web` | Anthropic + OpenAI 官网新文章（sitemap diff 检测） | 🏢 大厂动向 |

**调用时机**：在 1A-1H 完成后、第二轮搜索补充之前调用。推荐流程：

```
1. 调用 list_reports 查看当日可用报告
2. 调用 get_latest("ai-cli") 获取 CLI 工具最新动态
3. 调用 get_latest("ai-trending") 获取 GitHub Trending AI 报告
4. 调用 get_latest("ai-hn") 获取 Hacker News AI 社区情绪
5. 调用 get_latest("ai-arxiv") 获取最新 AI 论文摘要
6. 调用 get_latest("ai-web") 获取 Anthropic/OpenAI 官网新发布
7. 将以上数据与 1A-1H 已有条目去重后，补入对应板块
```

**整合规则**：
- agents-radar 报告中的条目与已有条目按**标题 + 公司名 + URL** 三重去重
- agents-radar 提供的 GitHub 仓库数据可直接用于生态/初创板块
- Hacker News 社区情绪分析可作为**信号分级参考**（高讨论度 → 🔴/🟡）
- ArXiv 论文如与当日产业动态高度相关，可独立收录至观点类板块
- `ai-web` 报告中的 Anthropic/OpenAI 新文章与 1B 信源巡检结果交叉验证

### 第二轮：搜索补充（增量发现）

三轨汇合完成后，执行宽泛搜索来捕获可能遗漏的长尾新闻：

1. **中文综合搜索**：`AI行业新闻 [今日日期]` / `AI 今日要闻`
2. **英文综合搜索**：`AI news today [date]`
3. **热点赛道搜索**：`AI Agent OpenClaw 龙虾 最新动态` / `大模型 开源 最新发布`
4. **初创与融资**：`AI 融资 初创公司 [月份]`
5. **Tier 1 公司补充搜索**（查漏）：逐一搜索 `[公司名] AI [今日日期]`

6. **盲区补偿搜索**（覆盖历史遗漏高发区域）：
   - `npm pypi supply chain attack today`（供应链安全）
   - `AI product leak feature test [today]`（产品泄露/内测）
   - `Alexa Siri AI assistant update [today]`（AI助手产品线）
   - 对每个Tier 1公司的子品牌逐一搜索：`即梦 AI [今日日期]` / `豆包 [今日日期]` / `Coze [今日日期]` / `通义 [今日日期]` / `混元 [今日日期]`

7. **跨平台趋势分析**（content-trend-researcher 集成）：
   - 对当日已发现的核心话题，调用 content-trend-researcher 进行跨 10+ 平台趋势验证
   - 输入格式：`{"topic": "当日核心话题", "platforms": ["Google Trends", "Reddit", "X", "YouTube"], "intent_focus": "informational", "analysis_depth": "quick"}`
   - 用途：验证某条新闻是否为**真正的行业趋势**而非孤立事件，提升信号分级（🔴/🟡/⚪）准确度

搜索结果用于：
- 发现三轨未覆盖的新闻
- 交叉验证已发现的新闻（增加来源数）
- 发现非 Tier 列表内的突发新闻

---

## 信息源优先级

| 层级 | 来源 | 用途 |
|------|------|------|
| **Tier 1（必查）** | 新智元、量子位、机器之心、36Kr、Z Potentials、华尔街见闻、EverAI酱、极客公园、FounderPark | 国内核心新闻源 |
| **Tier 2** | 有新Newin、AIBase、腾讯AI研究院、IT之家、海外独角兽、赛博禅心 | 补充与交叉验证、深度分析 |
| **Tier 3（英文）** | TechCrunch、The Verge、Reuters、Bloomberg、TLDR、Product Hunt、Huggingface | 海外一手信息 |
| **Tier 4（数据型）** | aicpb.com、AIwatch.ai、Toolify.ai、Trust MRR | 产品数据与榜单 |
| **Tier 5（Builder Feed）** | follow-builders 中心化 Feed（X推文 + 播客 + 博客） | 海外建设者一手动态 |
| **Tier 6（虾评增强）** | news-aggregator-skill（28信源批量抓取）、content-trend-researcher（趋势验证）、smart-web-fetch（反爬降级） | 增强覆盖 + 趋势验证 + 抓取可靠性 |
| **Tier 7（agents-radar MCP）** | agents-radar 托管 MCP Server（10 信源 AI 生态日报：GitHub / ArXiv / HN / HF / PH / Dev.to / Lobste.rs / Anthropic / OpenAI sitemap） | 预结构化 AI 生态数据 + 跨工具对比 + 社区情绪 |
| **Tier 7（公众号/社交）** | Sensight social_search、大厂公众号、行业深度公众号 | 微信生态首发内容 |

### 原始链接采集规则

这是日报质量的硬性要求：

- **每条新闻必须附上一手信息源的具体文章页面 URL**
- 优先使用原始报道（如官方博客、一手媒体报道），而非聚合转载
- **严禁使用**：聚合平台首页、媒体号首页、频道页
- **严禁使用**低质量营销账号作为来源（已知黑名单：字母AI）
- TechCrunch 链接经常无法访问，必须同时找到中文替代来源
- 海外建设者板块：填入 X/Twitter 原文 status 链接（`https://x.com/用户名/status/数字`），这些链接直接从 feed-x.json 中获取
- 实在找不到一手 URL 时，标注"综合报道"并在 URL 列留空

---

## 第二阶段：Watch Focus（关注焦点）

采集时优先覆盖这些公司和赛道。这些优先级来自对过去 1200+ 条 AI 日报历史数据的量化分析。

### 公司跟踪

**Tier 1 — 每日必覆盖**（即使无新闻也要确认已检查过官方信源，含子品牌）：
- Google/DeepMind（Gemini、搜索AI化、世界模型、NotebookLM、**官方博客发布**）
- OpenAI（GPT系列、Sora、Agent平台、商业化）
- 阿里/通义（Qwen、通义万相、魔搭社区、空间智能、开源）
- 字节/豆包（**即梦AI/Seedance/Seedream**、飞书/Mira、扣子/Coze、火山引擎、AI硬件）
- 腾讯/混元（微信Agent、CodeBuddy、龙虾产品）
- Meta（Llama、AI硬件/眼镜、Agent收购）
- **亚马逊**（Alexa+、AWS AI/Bedrock、AGI实验室）

**Tier 2 — 有动态即收录**：
Anthropic、xAI、百度/文心、华为/盘古、MiniMax、月之暗面/Kimi、智谱GLM、Mistral、英伟达、微软、苹果、蚂蚁/支付宝

**Tier 3 — 选择性收录**：
快手、美团、小红书、京东、Stability AI、Midjourney、Runway、Pika、零一万物、阶跃星辰、商汤、科大讯飞、DeepSeek

### 行业/赛道聚焦

| 梯队 | 赛道 | 关注点 |
|------|------|--------|
| **第一梯队** | AI Agent/龙虾生态 | OpenClaw、MCP协议、A2A、Agent社交、Skill市场、大厂Agent产品 |
| **第一梯队** | 大模型迭代 | 新模型发布、基准测试、开源、MoE、推理优化 |
| **第二梯队** | 世界模型/空间智能 | 3D生成、世界模拟器、空间理解 |
| **第二梯队** | AI视频生成 | Sora、可灵、Seedance、Veo、AI短剧商业化 |
| **第二梯队** | AI社交/陪伴 | AI分身、陪伴产品、社交裂变 |
| **第二梯队** | AI芯片/算力基建 | GPU、自研芯片、数据中心投资 |
| **第二梯队** | AI安全/供应链安全 | npm/PyPI投毒、模型安全、对齐、代码泄露、Vibe Coding安全风险 |
| **第二梯队** | AI助手/消费级产品 | Alexa+、Siri、Google Assistant、AI支付集成、商业化工具 |
| **第三梯队** | AI编程、具身智能/机器人、AI医疗、AI政策/监管、AI硬件/眼镜、Harness Engineering |

### 海外建设者动态采集（follow-builders 集成）

海外建设者板块的数据来源是 **follow-builders** 项目的中心化 Feed（https://github.com/zarazhangrui/follow-builders）。该项目每日自动抓取 25 位顶级 AI Builder 的 X/Twitter 推文、5 档播客摘要和 2 个官方博客更新，已经完成了数据采集和去重。

#### 数据获取方式

**直接拉取以下 3 个 JSON Feed 文件**（无需 API Key，一次 HTTP 请求即可）：

| Feed 文件 | URL | 内容 |
|-----------|-----|------|
| **X/Twitter 推文** | `https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-x.json` | 25位 Builder 近24小时推文，含原文、likes、URL |
| **播客摘要** | `https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-podcasts.json` | 5档AI播客近72小时新集，含完整transcript |
| **博客文章** | `https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-blogs.json` | Anthropic Engineering + Claude Blog 近72小时文章 |

#### 处理流程

1. **拉取** `feed-x.json`：用 web fetch 工具获取 JSON，解析 `x[]` 数组
2. **全量解析每位 Builder 的推文**，筛选标准：
   - **收录**：包含产品发布、技术洞察、行业趋势判断、有实质性观点的内容
   - **收录**：即使点赞数低（<100❤），只要观点有价值就保留
   - **过滤**：纯转发（无评论的 retweet）、日常闲聊、活动推广（除非重大会议）
   - **过滤**：`isQuote: true` 且无实质评论的简单引用
3. **拉取** `feed-podcasts.json`：如有近24小时内的新集，提取关键观点（transcript 字段）
4. **拉取** `feed-blogs.json`：如有新文章，提取核心技术要点
5. **合成日报条目**：将所有有价值的内容写入"海外建设者"板块，直接使用 Feed 中的 `url` 字段作为原始链接

#### Feed 中覆盖的 Builder 列表（25人）

这些 Builder 已被 follow-builders 项目持续追踪，**无需逐个搜索**：

| 分类 | Builder | Handle | 关注方向 |
|------|---------|--------|----------|
| AI Lab 领袖 | Sam Altman | @sama | OpenAI 战略、产品方向 |
| AI Lab 领袖 | Andrej Karpathy | @karpathy | 技术教育、LLM实践洞察 |
| Builder/产品 | Swyx | @swyx | AI Engineer 社区、基础设施 |
| Builder/产品 | Guillermo Rauch | @rauchg | Vercel CEO、AI开发工具 |
| Builder/产品 | Amjad Masad | @amasad | Replit CEO、AI编程 |
| Builder/产品 | Peter Steinberger | @steipete | OpenClaw ClawFather、Agent生态 |
| Builder/产品 | Cat Wu | @_catwu | Claude Code、Anthropic产品 |
| Builder/产品 | Thariq | @trq212 | Claude Code、Anthropic工程 |
| Builder/产品 | Alex Albert | @alexalbert__ | Anthropic、模型评估 |
| Builder/产品 | Ryo Lu | @ryolu_ | Cursor设计、AI编程UX |
| Builder/产品 | Dan Shipper | @danshipper | Every CEO、AI产品写作 |
| Builder/产品 | Peter Yang | @petergyang | Roblox PM、AI教程 |
| Builder/产品 | Aditya Agarwal | @adityaag | South Park Commons、前Dropbox CTO |
| 投资/观察 | Garry Tan | @garrytan | YC CEO、创业投资 |
| 投资/观察 | Aaron Levie | @levie | Box CEO、企业AI |
| 投资/观察 | Matt Turck | @mattturck | FirstMark VC、MAD Landscape |
| 平台/官方 | Claude | @claudeai | Anthropic产品公告 |
| 平台/官方 | Google Labs | @googlelabs | Google AI产品实验 |
| 其他 | Josh Woodward | @JoshWoodward | Google Labs VP |
| 其他 | Kevin Weil | @kevinweil | OpenAI VP Science |
| 其他 | Nan Yu | @thenanyu | Linear产品负责人 |
| 其他 | Madhu Guru | @madhuguru_ | AI产品/工程 |
| 其他 | Amanda Askell | @amandaaskell | Anthropic、模型训练 |
| 其他 | Nikunj Kothari | @nikunj | FPV Ventures、种子投资 |
| 华人Builder | Zara Zhang | @zaaborean | 创投媒体、Builder文化 |

#### 补充搜索（仅在 Feed 不足时）

如果 feed-x.json 中当日高价值推文不足 3 条，可针对以下**不在 Feed 列表中**的 KOL 进行补充搜索：

- **Dario Amodei** (@DarioAmodei) — Anthropic CEO
- **Yann LeCun** (@ylecun) — Meta Chief AI Scientist
- **Jim Fan** (@DrJimFan) — NVIDIA 具身智能
- **Simon Willison** (@simonw) — LLM 工具链
- **Harrison Chase** (@hwchase17) — LangChain
- **Lilian Weng** (@lilianweng) — OpenAI 安全
- **Ethan Mollick** (@emollick) — 沃顿教授、AI生产力
- **Sarah Guo** (@saranormous) — Conviction、AI投资
- **Andrew Ng** (@AndrewYNg) — DeepLearning.AI
- **Fei-Fei Li** (@drfeifei) — Stanford HAI

---

## 第三阶段：质量审核（Gate 0 + 5 道 QA Gate）

在完成新闻采集后、输出日报前，依次执行 Gate 0 + 5 道质量门。

### Gate 0：执行完整性强制检查（新增，不可跳过）

> **0407 教训**：三条轨道都写在 SKILL.md 里，但实际执行时轨道②③被整体跳过，直到用户手动发现。Gate 0 的目的是在出稿前强制验证每一步是否真正执行。

**必须逐项打勾，缺任何一项则禁止进入 Gate 1-5：**

```
## Gate 0 执行完整性检查

### 轨道① 人工信源巡检
- [ ] 1A. feed-x.json 已拉取并全量解析（Builder数:___, 推文数:___）
- [ ] 1A. feed-podcasts.json 已拉取（近24h新集数:___）
- [ ] 1A. feed-blogs.json 已拉取（近24h新文数:___）
- [ ] 1B. Tier 1 公司官方博客已逐一检查（列出每家的检查结果:有/无新发布）
- [ ] 1C. Tier 1 中文媒体已逐一搜索（IT之家/极客公园/量子位/机器之心/新智元/36Kr）
- [ ] 1D. Tier 3 英文信源已搜索（HF/TC/Engadget/Verge/Ars/TLDR/PH）
- [ ] 1E. 深度媒体已扫描（至少检查3个：___/___/___）

### 轨道② 公众号 + 社交扫描
- [ ] 1F. Sensight social_search 已执行（返回条数:___）
- [ ] 1F. 大厂子品牌公众号已逐查（字节/阿里/腾讯/百度/蚂蚁：各___条）
- [ ] 1I. 行业深度公众号语义搜索已执行（返回条数:___）

### 轨道③ 虾评批量抓取
- [ ] 1G. HackerNews 已抓取（条数:___）
- [ ] 1G. AI Newsletters 已抓取（条数:___）
- [ ] 1G. WallStreetCN 已抓取（条数:___）
- [ ] 1G. ProductHunt 已抓取（条数:___）
- [ ] 1G. GitHub Trending 已抓取（条数:___，或标注失败原因:___）
- [ ] 1G. HuggingFace Papers 已抓取（条数:___，或标注失败原因:___）

### 汇合
- [ ] 三轨合并去重已完成（轨道①:___条，轨道②:___条，轨道③:___条 → 去重后:___条）
- [ ] 第二轮搜索补充已完成

⚠️ 如有任何一项未勾选，必须回头执行后再继续。
```

### Gate 1：数据源健康检查

检查各层级信息源的命中情况：
- 计算有效源命中率（成功返回有效内容的源数 / 总搜索源数）
- 要求 ≥ 70%
- 如果 Tier 1 源全部失效 → 日报末尾标注「⚠️ 信源缺失」
- 不可单一来源依赖
- **检查 follow-builders feed 是否成功拉取**（`generatedAt` 时间戳应在24小时内）
- **检查 Tier 1 公司官方博客是否都已巡检**（即使无新发布也需确认已检查）

### Gate 2：去重与交叉验证

- 多源报道同一事件 → 合并为一条，保留信息最完整的版本
- 每条新闻尽量有 ≥ 2 个独立来源交叉验证
- 单源重大消息 → 标注「⚠️ 单源」
- 记录：原始信号数 → 去重后数量
- 海外建设者板块：Feed 内推文本身已去重（state-feed.json 记录 seenTweets），但仍需与正文新闻去重

### Gate 3：信号分级与噪声过滤

| 级别 | 标准 | 处理 |
|------|------|------|
| 🔴 高信号 | 改变行业格局：重大产品发布、大额融资（>1亿美元）、关键政策法规 | 必须收录 |
| 🟡 中信号 | 有信息价值但非颠覆性：常规产品更新、中等融资、人事变动 | 择优收录 |
| ⚪ 噪声 | 营销软文、纯转载、无实质进展的传闻 | 过滤不收录 |

最终日报仅保留 🔴 和 🟡 级别的新闻。海外建设者板块可保留 ⚪ 级别的有趣洞察（如 Karpathy 的技术随想）。

### Gate 4：事实核验

- 关键数据（参数量、金额、比例、日期）必须追溯原始出处
- 多源一致 → 标记「✅ 多源交叉验证」或「✅ 双源验证」
- 仅单源 → 标记「单源」
- 信息矛盾时并列各方说法

### Gate 5：完整性自检

核对日报是否存在盲区：
- **Gate 0 所有检查项是否全部 ✅**（如果 Gate 0 有未勾选项，此处直接不通过）
- **Tier 1 公司官方博客是否都已检查过**（无新闻可不收录，但必须确认巡检过）
- 重点赛道是否覆盖
- 7个板块（大厂动向/初创动向/生态动向/技术博客&论文/海外建设者/养虾实践/观点与深度）覆盖是否充分
- 每条新闻是否都附了原始链接
- 总条目数是否在 5-15 条合理区间（核心新闻，不含 Builder 条目）
- **follow-builders Feed 是否全量解析**（不应遗漏有价值的 Builder 推文）
- **Tier 1 中文媒体是否都已巡检**
- **轨道② 公众号扫描是否已执行**（1F + 1I）
- **轨道③ 虾评批量抓取是否已执行**（1G 所有子命令）
- **AI安全/供应链安全赛道是否有当日事件**（npm/PyPI投毒、代码泄露、模型安全）
- **英文替代源（Engadget/The Verge/Ars Technica）是否已检查**（弥补TechCrunch不可用）

---

## 第四阶段：日报输出

生成 **两份输出**：Markdown 版日报（给人阅读）和 CSV 结构化数据（供后续分析）。

### 输出一：Markdown 日报

```
# 🤖 AI 行业日报 · [YYYY年M月D日]（星期X）

## 一句话总结

[用一段话概括今日2-3条最核心的动态，不超过80字]

---

## 📰 偏fact类新闻

### 🏢 大厂动向

**1. [标题]**  [信号等级emoji]

[新闻摘要（100-200字），包含关键数据和事实]

> 来源：[[来源名称]](原始URL) / [[来源名称2]](原始URL2)

### 🚀 初创动向

**N. [标题]**  [信号等级emoji]

[新闻摘要]

> 来源：[[来源名称]](原始URL)

### 🌐 生态动向

**N. [标题]**  [信号等级emoji]

[新闻摘要]

> 来源：[[来源名称]](原始URL)

### 📄 技术博客&论文

**N. [标题]**  [信号等级emoji]

[论文/博客核心要点摘要]

> 来源：[[来源名称]](原始URL)

---

## 💬 观点与深度

**N. [标题]**  ⚪

[观点摘要]

> 来源：[[来源名称]](原始URL)

---

## 🌍 海外建设者动态

**BN. [Builder名（@handle）：核心观点]**  [信号等级]

[推文/播客/博客内容摘要（中文），附原始英文关键句引用]

> 来源：[[Builder名 @handle]](x.com原文链接)

---

## 🦐 养虾实践

> 本板块记录 OpenClaw / MCP / A2A / Agent 生态的实战案例，包括 Skill 开发经验、Agent 运营心得、龙虾平台动态等。如当日无相关内容可省略。

**N. [标题]**  [信号等级emoji]

[实战经验摘要]

> 来源：[[来源名称]](原始URL)

---

## 🎙 播客监测

| 节目 | 标题 | 发布日期 |
|------|------|---------|
| [节目名] | [标题] | [YYYY-MM-DD] |

---

## 📊 质量审核报告

### Gate 0 执行完整性
[三轨执行情况汇总表]

### Gate 1-5
[5道Gate的通过情况表格]

---

*日报生成时间：[时间]*
*数据采集窗口：[窗口]*
*Follow-builders Feed 时间戳：[generatedAt]*
```

### 输出二：CSV 结构化数据

12列固定 schema：

```
日期,编号,板块,标题,信号等级,事实核验,关联公司,关联赛道,来源,原文URL,摘要,是否推送
```

字段规范：
- **日期**：`YYYY-MM-DD`
- **编号**：核心新闻用数字 1, 2, 3...；Builder 用 B1, B2, B3...
- **板块**：`大厂动向` / `初创动向` / `生态动向` / `技术博客&论文` / `海外建设者` / `养虾实践` / `观点与深度`
- **信号等级**：🔴 / 🟡 / ⚪
- **事实核验**：`多源验证` / `双源验证` / `一手信源` / `单源` / `单源(深度)`
- **关联公司**：涉及的主要公司名（多个用 `/` 分隔）
- **关联赛道**：所属赛道标签
- **原文URL**：一手报道的链接（**必填**，是日报质量底线）
- **摘要**：50字内摘要
- **是否推送**：`是` / `否`（🔴 默认推送，🟡 择优，⚪ 默认不推送，海外建设者高价值推送）

### Inline 引用格式

在日报正文中引用外部来源时，使用 `[[标题]](url)` 格式紧贴在事实陈述的句号之前。仅用于事实性声明或引用内容，不用于开头框架句、导航文本或 URL 本身即答案的场景。

---

## 增强技能与外部数据源依赖

本技能集成了以下增强技能和外部数据源：

| 技能名称 | 安装路径 | 核心能力 | 何时调用 |
|----------|---------|---------|---------|
| **news-aggregator-skill** | `news-aggregator-skill/` | 28 信源批量抓取 + AI 深度模式 + 日报模板 | 第一阶段轨道③ |
| **smart-web-fetch** | `smart-web-fetch/` | 5 层反爬降级策略 | 任何 URL 抓取失败时 |
| **content-trend-researcher** | `content-trend-researcher/` | 跨 10+ 平台趋势分析 | 第二轮搜索补充环节 |
| **agents-radar** | MCP Server: `https://agents-radar-mcp.duanyytop.workers.dev` | 10 信源 AI 生态日报（GitHub/ArXiv/HN/HF/PH 等）+ 关键词搜索 | 第一阶段 1J 环节 |

**安装方式**：这些技能已安装在 Mira skills 目录（`/opt/tiger/mira_nas/plugins/prod/9893703/skills/`），可直接调用其脚本或遵循其 SKILL.md 中的使用说明。

**Python 版本注意**：sandbox 中 `python3` 默认指向 Python 3.7（当 CWD 在 skill 目录时），必须使用 `/usr/local/python3.11/bin/python3.11` 显式路径调用 skill 脚本。

---

## 已知信源问题（经验积累）

这些是过去多期日报中发现的信源问题，避免重复踩坑：

| 问题 | 应对策略 |
|------|---------|
| TechCrunch 链接常无法访问 | 必须同时找到中文替代来源 |
| 字母AI 是低质量营销账号 | 不使用其作为来源 |
| 36Kr 个人文章页返回"数据不存在" | 使用 36Kr 列表页数据或其他媒体转载 |
| 极客公园 `/news` 页只返回 4 字符 | 跳过直接抓取，改用搜索或微信链接 |
| X.com 推文直接 fetch 返回 JS 错误页 | 使用 mira_search 搜索中文媒体报道，间接获取推文内容 |
| 飞书 CSV 上传 `upload_file_from_url_to_feishu` 返回 size:0 | 这是已知 API 行为，文件实际已上传，不需要重试 |
| 浏览器批量抓取输出 >49KB | 自动保存为 JSON 文件，需用 Python 解析 |
| `mcp__proxy___mira__web_builtin_fetch` 可用于微信文章 | 避免 captcha，比浏览器更稳定 |
| 国内大厂子品牌AI动态通过微信公众号首发 | 必须执行轨道② 1F 公众号扫描，不能仅依赖搜索引擎 |
| Engadget/The Verge 可替代 TechCrunch | 作为英文科技媒体的备选源，覆盖消费级AI产品动态 |
| AI安全/供应链攻击新闻出自安全研究者和专业安全媒体 | AGI Hunt、Feross(X)、StepSecurity、Wiz Blog 是关键信源 |
| TestingCatalog 是 Google 产品泄露的主要信源 | 功能泄露/内测消息通常先出现在此类小众科技博客 |
| HuggingFace Papers 需要 Playwright（sandbox 中可能失败） | 标注失败原因，不影响整体流程 |
| GitHub Trending 质量不稳定 | 返回 org 页面而非 repo，数据仅作参考 |
| beautifulsoup4 v4.14.3 与 Python 3.11 不兼容 | 使用 `pip3 install 'beautifulsoup4==4.12.3'` |
| sandbox CWD 在 skill 目录时 python3 指向 3.7 | 始终使用 `/usr/local/python3.11/bin/python3.11` |

---

## 注意事项

1. **全程中文输出**（海外建设者板块的原文引用除外）
2. 不确定的信息要标注、标明来源可靠程度
3. 禁止编造新闻和链接
4. 日报字数控制在 2000-4000 字（不含海外建设者板块可适当超出）
5. 如果某日实在没有重大新闻，宁可只出 5 条高质量的，也不要凑数
6. **海外建设者板块优先从 feed-x.json 全量解析，而非从头搜索——这是已经采集好的中心化数据**
7. **一次性出完整版**——三轨并行采集 + 搜索补充都完成后再输出，避免多轮迭代让用户手动补条
8. **每期必须通过 Gate 0**——没有通过 Gate 0 的日报禁止发布
