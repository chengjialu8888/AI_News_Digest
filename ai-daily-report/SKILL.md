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

## 第一阶段：信息采集（信源驱动 + 搜索补充）

> **核心原则：信源逐一巡检是主线，搜索是补充。**
> 
> 过去的教训：如果只依赖搜索引擎聚合结果（"搜索驱动"），官方博客发布、微信公众号深度文、低热度高质量 Builder 推文会被系统性遗漏。必须先跑完信源巡检再搜索补充，争取一次性出完整版，避免反复让用户手动补条。

### 第一轮：信源逐一巡检（必做，不可跳过）

这一轮的目标是主动检查每一个信源，而不是等搜索引擎帮你发现新闻。按以下顺序依次执行：

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

#### 1F. 国内大厂公众号 + 子品牌扫描

> **0401教训**：即梦CLI、支付宝支付Skill等国内大厂子品牌的AI动态通过微信公众号首发，传统信源巡检全部遗漏。

国内大厂的AI产品动态大量通过微信公众号首发，必须主动扫描。执行方式：

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

#### 1G. 虾评增强信源（news-aggregator-skill 集成）

> **0407 新增**：通过虾评Skill平台安装的「全网新闻聚合助手」提供 28+ 信源的批量抓取能力，作为信源巡检的加速器。

在完成 1A-1F 的人工信源巡检后，调用 news-aggregator-skill 进行**补充扫描**，覆盖第一轮可能遗漏的信源：

```bash
# AI 深度模式：抓取 HuggingFace Papers + AI Newsletters
python3 news-aggregator-skill/scripts/fetch_news.py --source huggingface,ai_newsletters --keyword "AI,LLM,GPT,Claude,Agent,RAG,DeepSeek" --deep --no-save

# GitHub Trending 扫描
python3 news-aggregator-skill/scripts/fetch_news.py --source github --keyword "AI,LLM,agent" --no-save

# 综合扫描（Hacker News + Product Hunt + 华尔街见闻）
python3 news-aggregator-skill/scripts/fetch_news.py --source hackernews,producthunt,wallstreetcn --keyword "AI" --limit 10 --no-save
```

**整合规则**：
- news-aggregator 输出的条目与 1A-1F 已有条目做**去重**（按标题 + 公司名匹配）
- 新发现的条目补入对应板块（大厂/初创/生态/观点）
- 优先使用 news-aggregator 提供的原始 URL 链接
- HuggingFace Papers 的论文如果与当日 AI 动态高度相关，可独立收录

#### 1H. 反爬增强（smart-web-fetch 降级策略）

> 信源巡检中经常遇到部分 URL 无法正常抓取（如 TechCrunch Cloudflare 防护、arXiv 限流等）。安装 smart-web-fetch 技能后，对**所有抓取失败的 URL**自动启用 5 层降级策略：

```bash
# 当 web_builtin_fetch 失败时，自动降级
python3 smart-web-fetch/scripts/fetch.py <失败的URL> --json
```

降级优先级：
1. `markdown.new/` → 2. `defuddle.md/` → 3. `r.jina.ai/` → 4. Scrapling → 5. Playwright

**适用场景**：
- TechCrunch 文章（Cloudflare 保护）→ 优先用 `markdown.new/`
- arXiv 论文全文 → 优先用 `markdown.new/`
- 微信公众号原文（JS 渲染）→ Scrapling 或 Playwright
- GitHub 仓库 README → `defuddle.md/`


### 第二轮：搜索补充（增量发现）

第一轮信源巡检完成后，执行宽泛搜索来捕获可能遗漏的长尾新闻：

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
- 发现第一轮未覆盖的新闻
- 交叉验证第一轮发现的新闻（增加来源数）
- 发现非 Tier 列表内的突发新闻

### 第三轮：质量审核 + 一次性出稿

将第一轮和第二轮的所有发现汇总后，执行第三阶段的 5 Gate 审核，然后**一次性输出完整日报**，而不是先出"半成品"等用户补充。

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
| 华人Builder | Zhao Zhang | @zaaborean | 创投媒体、Builder文化 |

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

## 第三阶段：质量审核（5 道 QA Gate）

在完成新闻采集后、输出日报前，依次执行 5 道质量门。这套机制借鉴 Signex 工作流（Sensor → Lens → Report）的多阶段审核理念，目的是确保日报的信噪比和事实可靠性。

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
- **Tier 1 公司官方博客是否都已检查过**（无新闻可不收录，但必须确认巡检过）
- 重点赛道是否覆盖
- 偏fact类 + 偏观点类 + 海外建设者 三个板块是否齐全
- 每条新闻是否都附了原始链接
- 总条目数是否在 5-15 条合理区间（核心新闻，不含 Builder 条目）
- **follow-builders Feed 是否全量解析**（不应遗漏有价值的 Builder 推文）
- **Tier 1 中文媒体是否都已巡检**
- **Round 1F 国内公众号扫描是否已执行**（字节/阿里/腾讯/百度/蚂蚁子品牌）
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

### 🚀 初创 / 融资

**N. [标题]**  [信号等级emoji]

[新闻摘要]

> 来源：[[来源名称]](原始URL)

### 🌐 生态 / 政策

**N. [标题]**  [信号等级emoji]

[新闻摘要]

> 来源：[[来源名称]](原始URL)

---

## 💬 偏观点类

**N. [标题]**  ⚪

[观点摘要]

> 来源：[[来源名称]](原始URL)

---

## 🌍 海外建设者动态

**BN. [Builder名（@handle）：核心观点]**  [信号等级]

[推文/播客/博客内容摘要（中文），附原始英文关键句引用]

> 来源：[[Builder名 @handle]](x.com原文链接)

---

## 📊 质量审核报告

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
- **板块**：`大厂动向` / `初创公司/融资` / `生态动向` / `观点` / `海外建设者`
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

## 虾评增强技能依赖

本技能通过虾评Skill平台（xiaping.coze.site）集成了以下 3 个增强技能：

| 技能名称 | 安装路径 | 核心能力 | 何时调用 |
|----------|---------|---------|---------|
| **news-aggregator-skill** | `news-aggregator-skill/` | 28 信源批量抓取 + AI 深度模式 + 日报模板 | 第一阶段 1G 环节 |
| **smart-web-fetch** | `smart-web-fetch/` | 5 层反爬降级策略 | 任何 URL 抓取失败时 |
| **content-trend-researcher** | `content-trend-researcher/` | 跨 10+ 平台趋势分析 | 第二轮搜索补充环节 |

**安装方式**：这些技能已安装在 Mira skills 目录（`/opt/tiger/mira_nas/plugins/prod/9893703/skills/`），可直接调用其脚本或遵循其 SKILL.md 中的使用说明。

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
| 国内大厂子品牌AI动态通过微信公众号首发 | 必须执行 Round 1F 公众号扫描，不能仅依赖搜索引擎 |
| Engadget/The Verge 可替代 TechCrunch | 作为英文科技媒体的备选源，覆盖消费级AI产品动态 |
| AI安全/供应链攻击新闻出自安全研究者和专业安全媒体 | AGI Hunt、Feross(X)、StepSecurity、Wiz Blog 是关键信源 |
| TestingCatalog 是 Google 产品泄露的主要信源 | 功能泄露/内测消息通常先出现在此类小众科技博客 |

---

## 注意事项

1. **全程中文输出**（海外建设者板块的原文引用除外）
2. 不确定的信息要标注、标明来源可靠程度
3. 禁止编造新闻和链接
4. 日报字数控制在 2000-4000 字（不含海外建设者板块可适当超出）
5. 如果某日实在没有重大新闻，宁可只出 5 条高质量的，也不要凑数
6. **海外建设者板块优先从 feed-x.json 全量解析，而非从头搜索——这是已经采集好的中心化数据**
7. **一次性出完整版**——信源巡检和搜索补充都完成后再输出，避免多轮迭代让用户手动补条
