@@SECTION01@@
## 01｜一座会变形的 Agent 屋子

本周真正的主角不是某一个模型，而是一座会工作、会记忆、会被审计的屋子。模型、上下文、harness、验证器与人，在里面共同改写任务的形状。

视觉上用房屋、门、月面和两个守门角色建立“私有神话”：AI 不是一个漂浮的聊天框，而是一个需要日常维护、需要留下证据的执行空间。

@@SECTION02@@
## 02｜上下文之门：少写命令，把门交给成熟模型

删掉 80% 以上系统提示词，不等于不要上下文。被移走的是模型读文件、看工具、跑测试就能推断的废说明；真正留下的，是偏好、参考、验证流程和判断边界。

这对应本周最重要的上下文工程变化：从“替模型想每一步”，转向给它目标、资源、边界和复盘机制。常驻 prompt 变薄，按需加载的 skills / references 变得更贵、更有价值。

@@SECTION03@@
## 03｜Agent 获得一具运行时身体

安全边界已经从发布前的一次考试，搬到运行时的身体边界。长程 Agent 需要身份、权限、网络出口、可写范围、日志、审批、回滚和人类检查点。

因此 Agent 的采购和治理单位不应只是模型。真正要看的是模型与 harness 的组合：谁在执行、能碰什么、出了错怎么停、每一步是否能复盘。

@@SECTION04@@
## 04｜仪式桌：生成不是完成，证据才是

Hyra、Cursor Agent Swarm、Google Tunix、Microsoft MagenticLite 的共同信号，是把 Agent 变成一张可复盘的工作桌：模型生成候选行动，harness 约束环境，验证器打分，轨迹把失败转成下一次行动的材料。

这也是 Kleisli arrow 式长程工作流的直觉：每一步不是把值直接交给下一步，而是把“动作 + 环境副作用 + 可验证结果”交给下一步。只有能携带证据的行动，才适合持续运行。

@@SECTION05@@
## 05｜交付物打开房门：聊天框不是终点

AI 产品正在争夺最后一扇门：Excel、Outlook、GitHub 画布、图片编辑器、设计台、知识库和内部工具。谁离真实交付物最近，谁就更容易拿到上下文、反馈和付费。

应用层的机会因此不一定长得像聊天机器人。它可能是一个 Office 插件、一块共享画布、一个图片编辑器、一个设计 Agent 或一个可协作的项目面板。

@@SECTION06@@
## 06｜真实轨迹是下一轮训练数据矿石

网页文本告诉模型“人们说过什么”；真实工作轨迹告诉模型“任务如何被完成、卡住、修正和交付”。下一轮训练数据红利，更可能来自后者。

对长程工作流而言，失败、重试、人工接管、验证通过和最终交付都不是噪音，而是高价值的过程数据。产品需要保留这些轨迹，同时做好脱敏、权限和用户体验控制。

@@SECTION07@@
## 07｜Token 不是全部账单

AI 的账本已经显出工业系统的轮廓：OpenAI 数据中心规划 3.2GW，AMD × Anthropic 计算合作涉及 2GW 产能，Nikkei 披露的五家科技巨头隐性债务约 1.65 万亿美元。

对资本市场要看全栈成本，对产品团队要看单位任务成本。一个 Agent 跑 20 分钟，如果没有缓存、路由、推测解码和评估剪枝，很快就会把毛利吃掉。

@@SECTION08@@
## 08｜把 AI 当作成熟员工管理

不是买一个更聪明的聊天框，而是引入一个会消耗预算、使用权限、留下轨迹、影响组织流程的新执行层。成熟的管理方式是授权、复盘和责任，而不是密密麻麻的禁令。

给产品团队的行动项：清理常驻上下文，把规则改成判断框架，把流程拆成按需 skills，把交付物变成测试、HTML、rubric 和真实参考。少一点噪音，多一点结构。

## 来源与事实索引

- [Anthropic：The new rules of context engineering](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
- [OpenAI：Hugging Face 模型评估安全事件](https://openai.com/index/hugging-face-model-evaluation-security-incident/)
- [AISI：Cheating behaviour in frontier model evaluations](https://www.aisi.gov.uk/blog/cheating-behaviour-in-frontier-model-evaluations)
- [UNU：Engineering and governing agent harness](https://unu.edu/publication/engineering-and-governing-agent-harness-technology-and-policy-framework-runtime-layer)
- [Cursor：Agent Swarm model economics](https://cursor.com/blog/agent-swarm-model-economics)
- [Google：Scaling agentic RL with Tunix](https://developers.googleblog.com/scaling-agentic-rl-high-throughput-agentic-training-with-tunix/)
- [Microsoft：MagenticLite](https://www.microsoft.com/en-us/research/blog/magenticlite-magenticbrain-fara1-5-an-agentic-experience-optimized-for-small-models/?lang=ja)
- [GitHub：Copilot Canvases](https://github.blog/ai-and-ml/github-copilot/how-to-build-interactive-experiences-with-canvases/)
- [OpenAI：Project Camellia](https://openai.com/index/building-ai-infrastructure-with-the-effingham-county-community/)
- [The Verge：AMD × Anthropic infrastructure deal](https://www.theverge.com/ai-artificial-intelligence/969285/amd-anthropic-ai-infrastructure-deal)
- [Nikkei：AI hidden debt](https://asia.nikkei.com/business/technology/five-us-tech-giants-hidden-debts-soar-to-1.65tn-on-opaque-ai-funding)
