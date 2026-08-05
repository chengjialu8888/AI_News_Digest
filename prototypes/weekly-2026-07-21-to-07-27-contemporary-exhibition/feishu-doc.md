# AI 周报视觉展览｜The Scaffold After the Model

> 2026 年 7 月 21 日至 7 月 27 日。把本周 AI 行业的六条趋势，重新组织成一组“展厅式”判断：模型变强之后，脚手架如何退场，Agent 如何进入运行时、真实交付和工业成本账。

本版不是把周报变成一个 dashboard，而是把每个关键判断压缩成一张 16:9 幕面。图像负责留下视觉证据，文字负责告诉读者应该看什么。

## 01｜展览入口：脚手架之后

本周的主标题不是“哪个模型又赢了”，而是：当模型本身更成熟，过去塞在 prompt、skills、harness 里的东西，哪些应该继续存在，哪些只是给弱模型写的保姆手册？

![01 / The Scaffold After the Model](frame-01.png)

## 02｜第一性原理：Agent 的价值是系统属性

用一个简化的式子看本周所有新闻：可完成任务的复杂度 × 成功率 × 可验证性，再除以上下文成本、推理成本、治理成本和集成成本。提示词变薄、运行时边界变硬、轨迹变贵、交付物变近、基础设施变重，都是在改写这个式子的某一项。

![02 / First Principles](frame-02.png)

## 03｜上下文工程：消失的脚手架

Claude Opus 5 / Claude 5 generation 的周末更新，把上下文工程从“写更多规则”推向“给更成熟的模型更多授权”。删掉 80% 以上常驻系统提示词，不意味着不要上下文；被删掉的是模型读文件、看工具、跑测试就能自行推断的废说明。留下的应该是团队偏好、真实参考、验证流程、历史包袱和判断边界。

![03 / The Disappearing Scaffold](frame-03.png)

## 04｜运行时治理：Agent 不等于 Model

OpenAI / Hugging Face 模型评估安全事件、AISI 评测作弊、Agent escape 和 AI-native SDLC 共同把安全边界从“发布前评测”推到了“运行时边界”：身份、权限、网络出口、可写范围、日志、审批、回滚和人类 checkpoint。

![04 / Agent Is Not Model](frame-04.png)

## 05｜竞争单位：模型 + Harness + Verifier + Trace

Hyra、Cursor Agent Swarm、Google Tunix、Microsoft MagenticLite 等信号说明，Agent 产品的核心不是一个聪明大脑，而是一条可复盘的工作流水线：模型生成候选行动，harness 约束环境，验证器评分，轨迹保存失败与修正。任务完成，不再等于一次回答正确。

![05 / The Competition Unit](frame-05.png)

## 06｜交付物表面：聊天框不是终点

Grok for Excel / Outlook、GitHub Copilot Canvases、Qwen-Image-3.0、Miora 和 AI 短片都在抢同一层：最终交付物表面。下一个 AI 应用未必长得像聊天机器人，更可能长得像 Office 插件、共享画布、图片编辑器、设计 Agent 或协作项目面板。

![06 / Delivery Surfaces](frame-06.png)

## 07｜工业账：Token 不是全部账单

Google 的 tokens/min、OpenAI 的数据中心电力、AMD / Anthropic 的芯片产能绑定、Nikkei 披露的 AI 隐性债务，把 AI 从软件行业拉回工业系统：电力、土地、水、芯片、租赁、债务和吞吐共同决定谁能跑得久。Agent 的商业化也要回到“完成一次任务”的全栈成本。

![07 / The Industrial Ledger](frame-07.png)

## 08｜管理注：把 AI 当成熟员工

给产品团队：清理常驻上下文，把规则变成判断框架，把流程拆成按需 skills，把交付物变成 HTML、测试、rubric 和真实参考。

给资本市场：继续看模型能力，但更要看谁能以更低的全栈成本完成更多可计费任务，谁掌握数据轨迹、算力债务和治理能力。

给 AI 数字员工管理者：你不是在买一个更聪明的聊天框，而是在引入一个会消耗预算、使用权限、留下轨迹、影响组织流程的新执行层。

![08 / Manage the Mature Employee](frame-08.png)

## 证据索引

- 原始周报：[AI 周报｜Opus 5 删掉 80% 提示词后，Agent 行业开始重估“脚手架”](../../../../ai-weekly-2026-07-21-to-07-27.md)
- Anthropic：[The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
- OpenAI：[Hugging Face model evaluation security incident](https://openai.com/index/hugging-face-model-evaluation-security-incident/)
- AISI：[Cheating behaviour in frontier model evaluations](https://www.aisi.gov.uk/blog/cheating-behaviour-in-frontier-model-evaluations)
- Cursor：[Agent Swarm: Model Economics](https://cursor.com/blog/agent-swarm-model-economics)
- Qwen：[Qwen-Image-3.0](https://qwen.ai/blog?id=qwen-image-3.0)
- OpenAI：[Building AI infrastructure with the Effingham County community](https://openai.com/index/building-ai-infrastructure-with-the-effingham-county-community/)

视觉参考：Contra Labs 的人类判断、比较评测与轨迹数据叙事方式；本版将其转译成更适合 AI 行业周报的黑 / 米白 / 酸性绿 / 红 / 蓝视觉系统。
