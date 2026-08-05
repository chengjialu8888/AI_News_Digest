# 飞书文档可视化插入建议

来源周报：`/Users/bytedance/Documents/New project/ai-weekly-2026-07-21-to-07-27.md`

## 插入顺序

1. `01-cover.svg`：放在飞书文档标题下方，作为整篇周报的视觉主图。
2. `02-variable-map.svg`：放在开场判断后，帮助读者先看能力、成本、分发、供给、监管、组织采用六个变量。
3. `03-trend-cards.svg`：放在趋势正文之前或之后，作为六趋势总览。
4. `04-paradigm-shifts.svg`：放在结语前，压缩成本周 from-to 迁移。
5. `05-wechat-header.svg`：公众号 HTML 头图复用版。

## 后续接入

- 飞书文档：SVG 确认后转 PNG/JPEG 上传。
- 公众号 HTML：复用 `05-wechat-header.svg` 做头图，`02/03/04` 作为正文趋势总结图。
- 日报自动化：先确认视觉方向，再接入 `stage9.py` 的 HTML/Feishu 输出步骤。
