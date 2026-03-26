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

## 第一阶段：信息采集（Sensor Layer）

### 搜索策略

执行 **至少 6 轮搜索**，覆盖以下维度：

1. **中文综合搜索**：`AI行业新闻 [今日日期]` / `AI 今日要闻`
2. **重点公司搜索**：针对 Tier 1 公司逐一搜索（Google/OpenAI/阿里/字节/腾讯/Meta）
3. **英文搜索**：`AI news today [date]` / `OpenAI Google Anthropic AI news [month year]`
4. **热点赛道搜索**：`AI Agent OpenClaw 龙虾 最新动态` / `大模型 开源 最新发布`
5. **初创与融资**：`AI 融资 初创公司 [月份]`
6. **海外建设者动态**：**从 follow-builders 中心化 Feed 拉取**（见下方详细说明）

每次搜索都要包含今日日期或时间标记（"今日" / "today" / 具体日期），确保采集的是当天信息。

### 信息源优先级

| 层级 | 来源 | 用途 |
|------|------|------|
| **Tier 1（必查）** | 新智元、量子位、机器之心、36Kr、Z Potentials、华尔街见闻 | 国内核心新闻源 |
| **Tier 2** | 有新Newin、AIBase、腾讯AI研究院、IT之家 | 补充与交叉验证 |
| **Tier 3（英文）** | TechCrunch、The Verge、Reuters、Bloomberg、TLDR、Product Hunt、Huggingface | 海外一手信息 |
| **Tier 4（数据型）** | aicpb.com、AIwatch.ai、Toolify.ai、Trust MRR | 产品数据与榜单 |
| **Tier 5（Builder Feed）** | follow-builders 中心化 Feed（X推文 + 播客 + 博客） | 海外建设者一手动态 |

### 原始链接采集规则

这是日报质量的硬性要求：

- **每条新闻必须附上一手信息源的具体文章页面 URL**
- 优先使用原始报道（如官方博客、一手媒体报道），而非聚合转载
- **严禁使用**：聚合平台首页、媒体号首页、频道页
- 海外建设者板块：填入 X/Twitter 原文 status 链接（`https://x.com/用户名/status/数字`），这些链接直接从 feed-x.json 中获取
- 实在找不到一手 URL 时，标注"综合报道"并在 URL 列留空

---

## 第二阶段：Watch Focus（关注焦点）

采集时优先覆盖这些公司和赛道。这些优先级来自对过去 1200+ 条 AI 日报历史数据的量化分析。

### 公司跟踪

**Tier 1 — 每日必覆盖**：
- Google/DeepMind（Gemini、搜索AI化、世界模型、NotebookLM）
- OpenAI（GPT系列、Sora、Agent平台、商业化）
- 阿里/通义（Qwen、空间智能、开源）
- 字节/豆包（飞书/Mira、Seedance、火山引擎、AI硬件）
- 腾讯/混元（微信Agent、CodeBuddy、龙虾产品）
- Meta（Llama、AI硬件/眼镜、Agent收购）

**Tier 2 — 有动态即收录**：
Anthropic、xAI、百度/文心、华为/盘古、MiniMax、月之暗面/Kimi、智谱GLM、Mistral、英伟达、微软、苹果

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
| **第三梯队** | AI编程、具身智能/机器人、AI医疗、AI安全/对齐、AI政策/监管、AI硬件/眼镜 |

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
2. **筛选高价值推文**：按以下标准从每位 Builder 的 tweets 中筛选：
   - 优先：likes > 100 或 retweets > 10 的推文
   - 优先：包含产品发布、技术洞察、行业趋势判断的内容
   - 过滤：纯转发、日常闲聊、活动推广（除非是重大会议）
   - 过滤：`isQuote: true` 且无实质评论的简单引用
3. **拉取** `feed-podcasts.json`：如有近24小时内的新集，提取关键观点（transcript 字段）
4. **拉取** `feed-blogs.json`：如有新文章，提取核心技术要点
5. **合成日报条目**：将筛选出的 3-5 条最有价值的内容写入"海外建设者"板块，直接使用 Feed 中的 `url` 字段作为原始链接

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

## 第三阶段：质量审核（5 道 QA Gate）

在完成新闻采集后、输出日报前，依次执行 5 道质量门。这套机制借鉴 Signex 工作流（Sensor → Lens → Report）的多阶段审核理念，目的是确保日报的信噪比和事实可靠性。

### Gate 1：数据源健康检查

检查各层级信息源的命中情况：
- 计算有效源命中率（成功返回有效内容的源数 / 总搜索源数）
- 要求 ≥ 70%
- 如果 Tier 1 源全部失效 → 日报末尾标注「⚠️ 信源缺失」
- 不可单一来源依赖
- **新增**：检查 follow-builders feed 是否成功拉取（`generatedAt` 时间戳应在24小时内）

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
- Tier 1 公司当日动态是否都已检查（无新闻可不收录，但必须检查过）
- 重点赛道是否覆盖
- 偏fact类 + 偏观点类 + 海外建设者 三个板块是否齐全
- 每条新闻是否都附了原始链接
- 总条目数是否在 5-15 条合理区间
- **follow-builders Feed 是否已拉取并筛选**

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

**N. [Builder名 + 核心观点]**  ⚪

[推文/播客/博客内容摘要（中文），附原始英文关键句引用]

> 来源：[[Builder名 @handle]](x.com原文链接)

---

## 📊 质量审核报告

[5道Gate的通过情况表格]

---

*日报生成时间：[时间]*
*数据采集窗口：[窗口]*
```

### 输出二：CSV 结构化数据

12列固定 schema：

```
日期,编号,板块,标题,信号等级,事实核验,关联公司,关联赛道,来源,原文URL,摘要,是否推送
```

字段规范：
- **日期**：`YYYY-MM-DD`
- **编号**：当日序号 1, 2, 3...
- **板块**：`大厂动向` / `初创公司/融资` / `生态动向` / `观点` / `海外建设者`
- **信号等级**：🔴 / 🟡 / ⚪
- **事实核验**：`双源+` / `单源` / `待验证`
- **关联公司**：涉及的主要公司名（多个用 `/` 分隔）
- **关联赛道**：所属赛道标签
- **原文URL**：一手报道的链接
- **摘要**：50字内摘要
- **是否推送**：`是` / `否`（🔴 默认推送，🟡 择优，⚪ 默认不推送，海外建设者高价值推送）

---

## 注意事项

1. **全程中文输出**（海外建设者板块的原文引用除外）
2. 不确定的信息要标注、标明来源可靠程度
3. 禁止编造新闻和链接
4. 日报字数控制在 2000-4000 字
5. 如果某日实在没有重大新闻，宁可只出 5 条高质量的，也不要凑数
6. **海外建设者板块优先从 feed-x.json 拉取，而非从头搜索——这是已经采集好的中心化数据**
