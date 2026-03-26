# AI News Digest 🤖📰

每日 AI 行业新闻日报自动生成技能（中文），基于 Mira Skill 框架。

## 功能

- **结构化日报**：偏fact类（大厂/初创/生态）+ 偏观点类 + 海外建设者动态
- **质量审核**：5 道 QA Gate（数据源健康 → 去重交叉验证 → 信号分级 → 事实核验 → 完整性自检）
- **双格式输出**：Markdown（人读）+ CSV 12列结构化数据（机器用）
- **原始链接**：每条新闻附一手信源 URL，inline citation 格式
- **海外 Builder 追踪**：集成 [follow-builders](https://github.com/zarazhangrui/follow-builders) 中心化 Feed，覆盖 25 位顶级 AI Builder

## 安装

**OpenClaw：**
```bash
clawhub install ai-daily-report.skill
```

**手动安装：**
```bash
unzip ai-daily-report.skill -d ~/.claude/skills/
```

## 使用

触发日报生成的 prompt 示例：

- "跑一下今天的AI日报"
- "帮我生成今天的 AI 行业新闻速递"
- "出一期日报，今天有什么值得关注的AI新闻？"
- "生成 AI 日报，重点关注 Agent 和大模型方向"

## 信息源体系

| 层级 | 来源 |
|------|------|
| Tier 1 | 新智元、量子位、机器之心、36Kr、华尔街见闻 |
| Tier 2 | AIBase、IT之家、腾讯AI研究院 |
| Tier 3 | TechCrunch、Reuters、Bloomberg、The Verge |
| Tier 4 | aicpb.com、Toolify.ai |
| Tier 5 | follow-builders Feed（25位 Builder 推文 + 播客 + 博客） |

## 日报示例

见 [examples/sample-output-2026-03-26.md](ai-daily-report/examples/sample-output-2026-03-26.md)

## Eval 结果

| Eval | Prompt | Grade | Score |
|------|--------|-------|-------|
| #1 | "跑一下今天的AI日报" | A | 92 |
| #2 | "重点关注Agent和大模型方向" | A | 90 |
| #3 | "今天有什么值得关注的AI新闻？" | A- | 88 |

**Mean: 90.0 · Pass Rate: 3/3 (100%)**

## 项目结构

```
├── ai-daily-report.skill       # 打包好的 .skill 文件（可直接安装）
├── ai-daily-report/
│   ├── SKILL.md                # 技能定义（316行）
│   ├── evals/
│   │   ├── evals.json          # 测试用例
│   │   └── eval-results.json   # 评测结果
│   └── examples/
│       ├── sample-output-*.md  # 示例日报
│       └── sample-output-*.csv # 示例 CSV
└── README.md
```

## License

MIT
