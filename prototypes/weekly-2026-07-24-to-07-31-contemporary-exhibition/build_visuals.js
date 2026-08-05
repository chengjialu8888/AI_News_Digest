const fs = require("fs");
const path = require("path");

const outDir = __dirname;

const C = {
  ink: "#171814",
  black: "#0E0F0D",
  paper: "#E8E5DC",
  white: "#F6F4ED",
  acid: "#D9FF3F",
  red: "#FF5B3F",
  blue: "#3159FF",
  orange: "#FFB338",
  line: "#B9B6AC",
};

const font = "'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', Arial, sans-serif";

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function textLines(lines, x, y, opts = {}) {
  const {
    size = 28,
    weight = 500,
    fill = C.ink,
    leading = Math.round(size * 1.25),
    anchor = "start",
  } = opts;
  return `<text x="${x}" y="${y}" font-family="${font}" font-size="${size}" font-weight="${weight}" fill="${fill}" text-anchor="${anchor}" letter-spacing="0">${lines
    .map((line, i) => `<tspan x="${x}" dy="${i === 0 ? 0 : leading}">${esc(line)}</tspan>`)
    .join("")}</text>`;
}

function label(t, x, y, fill = C.ink, anchor = "start") {
  return `<text x="${x}" y="${y}" font-family="${font}" font-size="17" font-weight="800" fill="${fill}" text-anchor="${anchor}" letter-spacing="0">${esc(t)}</text>`;
}

function smallText(t, x, y, opts = {}) {
  return `<text x="${x}" y="${y}" font-family="${font}" font-size="${opts.size || 15}" font-weight="${opts.weight || 700}" fill="${opts.fill || C.ink}" text-anchor="${opts.anchor || "start"}" letter-spacing="0">${esc(t)}</text>`;
}

function evidenceRail(items) {
  const w = 252;
  const gap = 18;
  const y = 660;
  return items
    .map((it, i) => {
      const x = 48 + i * (w + gap);
      return `<g transform="translate(${x} ${y})">
        <rect width="${w}" height="102" fill="${it.fill || C.white}" stroke="${it.stroke || C.line}" stroke-width="1"/>
        ${smallText(it.kicker, 14, 25, { size: 14, weight: 800, fill: it.accent || C.ink })}
        ${smallText(it.value, 14, 58, { size: 25, weight: 900, fill: it.color || C.ink })}
        ${smallText(it.note, 14, 84, { size: 15, weight: 500, fill: C.ink })}
      </g>`;
    })
    .join("");
}

function shell({ index, title, deck, stamp, body, rail }) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="810" viewBox="0 0 1440 810" role="img" aria-label="${esc(title.join(" "))}">
  <rect width="1440" height="810" fill="${C.paper}"/>
  <rect x="0" y="0" width="1440" height="6" fill="${C.black}"/>
  ${label(`第 ${String(index).padStart(2, "0")} 室 / 人工智能周报`, 48, 44)}
  ${label(stamp, 1392, 44, C.blue, "end")}
  ${textLines(title, 48, 108, { size: 56, weight: 950, leading: 58, fill: C.black })}
  ${textLines(deck, 52, 228, { size: 22, weight: 560, leading: 31, fill: C.ink })}
  <line x1="48" y1="300" x2="1392" y2="300" stroke="${C.line}" stroke-width="1"/>
  ${body}
  ${rail}
  ${smallText("信号整理自 2026 年 7 月 24 日至 7 月 31 日人工智能周报", 48, 790, { size: 13, weight: 700, fill: C.ink })}
</svg>`;
}

const visuals = [
  {
    file: "01-price-performance-ledger.svg",
    svg: shell({
      index: 1,
      stamp: "成本账",
      title: ["模型溢价", "继续下沉"],
      deck: ["系统优化直接打进价格表。", "应用层要按任务完成来证明价值。"],
      body: `
        <g transform="translate(48 330)">
          <rect width="360" height="270" fill="${C.black}"/>
          ${textLines(["成本栈"], 32, 96, { size: 72, weight: 950, fill: C.white })}
          ${textLines(["词元", "路由", "缓存", "电力", "债务"], 250, 62, { size: 24, weight: 750, leading: 42, fill: C.acid })}
        </g>
        <g transform="translate(470 330)">
          ${["接口价格", "任务路由", "缓存检索", "基建账单"].map((name, i) => {
            const y = i * 63;
            const widths = [620, 500, 420, 710];
            const colors = [C.red, C.blue, C.acid, C.orange];
            return `<g transform="translate(0 ${y})">
              ${smallText(name, 0, 21, { size: 20, weight: 850 })}
              <rect x="150" y="0" width="760" height="26" fill="${C.white}" stroke="${C.line}"/>
              <rect x="150" y="0" width="${widths[i]}" height="26" fill="${colors[i]}"/>
            </g>`;
          }).join("")}
          <path d="M150 292 C330 245 510 255 706 174 C828 124 875 72 930 26" fill="none" stroke="${C.black}" stroke-width="4"/>
          <circle cx="930" cy="26" r="13" fill="${C.red}"/>
          ${textLines(["元 / 成功任务"], 680, 305, { size: 32, weight: 900, fill: C.black })}
        </g>`,
      rail: evidenceRail([
        { kicker: "开放平台", value: "-80%", note: "月神输入价", accent: C.red },
        { kicker: "微软", value: "90%", note: "小模型任务", accent: C.blue },
        { kicker: "本地检索", value: "92-99%", note: "少读全文", accent: C.acid },
        { kicker: "算力园区", value: "1.6吉瓦", note: "电力账本", accent: C.orange },
        { kicker: "新规则", value: "元/任务", note: "替代单看词元", accent: C.black },
      ]),
    }),
  },
  {
    file: "02-open-weights-production-gauntlet.svg",
    svg: shell({
      index: 2,
      stamp: "开源与部署",
      title: ["开放权重", "还要跑通生产"],
      deck: ["下载会拉低门槛。", "部署、评测、沙箱和合规才是硬活。"],
      body: `
        <g transform="translate(50 330)">
          <rect width="360" height="270" fill="${C.blue}"/>
          ${textLines(["下载", "不等于", "上线"], 34, 76, { size: 58, weight: 950, leading: 60, fill: C.white })}
          <circle cx="326" cy="235" r="82" fill="${C.acid}" opacity="0.95"/>
        </g>
        <g transform="translate(505 320)">
          ${["权重", "量化", "服务", "评测", "沙箱", "许可", "客户"].map((t, i) => {
            const x = i * 116;
            const color = i === 0 ? C.acid : i >= 4 ? C.red : C.white;
            return `<g transform="translate(${x} 0)">
              <rect width="92" height="210" fill="${color}" stroke="${C.black}" stroke-width="2"/>
              <text transform="translate(48 188) rotate(-90)" font-family="${font}" font-size="22" font-weight="900" fill="${C.black}" text-anchor="middle" letter-spacing="0">${t}</text>
            </g>`;
          }).join("")}
          <path d="M45 250 H770" stroke="${C.black}" stroke-width="6"/>
          <path d="M770 250 l-26 -18 v36 z" fill="${C.black}"/>
          ${textLines(["生产化才是护城河"], 246, 292, { size: 34, weight: 900, fill: C.black })}
        </g>`,
      rail: evidenceRail([
        { kicker: "开放权重", value: "1200亿/200亿", note: "免费商用", accent: C.blue },
        { kicker: "月之暗面", value: "2.8万亿", note: "混合专家", accent: C.acid },
        { kicker: "长上下文", value: "100万", note: "词元窗口", accent: C.black },
        { kicker: "多模态", value: "第三代", note: "计划开放", accent: C.orange },
        { kicker: "政策", value: "立法提速", note: "开放要治理", accent: C.red },
      ]),
    }),
  },
  {
    file: "03-agent-permission-boundary.svg",
    svg: shell({
      index: 3,
      stamp: "安全边界",
      title: ["权限边界", "就是产品"],
      deck: ["安全不再停留在白皮书里。", "事故已经有系统、资产和时间线。"],
      body: `
        <g transform="translate(55 325)">
          <rect width="1235" height="280" fill="${C.white}" stroke="${C.blue}" stroke-width="5"/>
          ${["身份", "网络", "写入范围", "日志", "审批", "回滚"].map((t, i) => {
            const x = 34 + i * 196;
            return `<g transform="translate(${x} 40)">
              <rect width="155" height="170" fill="${i % 2 ? C.paper : C.white}" stroke="${C.line}"/>
              ${smallText(t, 18, 40, { size: 22, weight: 900 })}
              <line x1="16" y1="70" x2="130" y2="70" stroke="${C.line}"/>
              <circle cx="34" cy="116" r="18" fill="${i < 3 ? C.blue : C.acid}"/>
            </g>`;
          }).join("")}
          <path d="M78 242 C246 160 345 229 515 121 C650 36 790 95 920 43 C1040 -5 1135 38 1248 -38" fill="none" stroke="${C.red}" stroke-width="7"/>
          ${smallText("逃逸路径", 944, 250, { size: 38, weight: 950, fill: C.red })}
        </g>`,
      rail: evidenceRail([
        { kicker: "安全回查", value: "141006次", note: "评测记录", accent: C.red },
        { kicker: "真实入侵", value: "3起", note: "未授权访问", accent: C.red },
        { kicker: "取证日志", value: "1.7万+", note: "攻击事件", accent: C.blue },
        { kicker: "外部影响", value: "第二面", note: "客户资产", accent: C.orange },
        { kicker: "控制项", value: "关停", note: "必须默认", accent: C.black },
      ]),
    }),
  },
  {
    file: "04-harness-score-split.svg",
    svg: shell({
      index: 4,
      stamp: "运行方法",
      title: ["同一模型", "不同分数"],
      deck: ["榜单分数开始拆账。", "模型能力和运行方法要分开看。"],
      body: `
        <g transform="translate(55 330)">
          <rect width="370" height="250" fill="${C.black}"/>
          ${textLines(["模型", "未变"], 34, 92, { size: 64, weight: 950, leading: 68, fill: C.white })}
          <circle cx="312" cy="194" r="84" fill="${C.blue}"/>
        </g>
        <g transform="translate(485 324)">
          <path d="M0 128 H655" stroke="${C.black}" stroke-width="8"/>
          <path d="M655 128 l-28 -20 v40 z" fill="${C.black}"/>
          ${["记忆", "压缩", "工具", "验收"].map((t, i) => {
            const x = 56 + i * 148;
            return `<g transform="translate(${x} 62)">
              <circle r="43" fill="${[C.acid, C.blue, C.orange, C.red][i]}"/>
              ${smallText(t, 0, 7, { size: 18, weight: 900, fill: C.black, anchor: "middle" })}
            </g>`;
          }).join("")}
          ${textLines(["分数三倍", "输出降六倍"], 670, 82, { size: 42, weight: 950, leading: 50, fill: C.black })}
          <rect x="650" y="166" width="260" height="66" fill="${C.acid}" stroke="${C.black}" stroke-width="2"/>
          ${smallText("运行方法", 730, 208, { size: 28, weight: 950, fill: C.black })}
        </g>`,
      rail: evidenceRail([
        { kicker: "抽象测评", value: "三倍", note: "分数提升", accent: C.red },
        { kicker: "上下文", value: "六分之一", note: "输出减少", accent: C.blue },
        { kicker: "环境", value: "快照", note: "可恢复", accent: C.acid },
        { kicker: "深度求索", value: "82.7", note: "终端测评", accent: C.orange },
        { kicker: "蒸馏", value: "10个", note: "中间检查点", accent: C.black },
      ]),
    }),
  },
  {
    file: "05-work-surface-entry-map.svg",
    svg: shell({
      index: 5,
      stamp: "工作入口",
      title: ["工作现场", "赢走入口"],
      deck: ["聊天框退到后台。", "人工智能开始占领任务发生的地方。"],
      body: `
        <g transform="translate(60 340)">
          <rect width="260" height="220" fill="${C.black}"/>
          ${textLines(["聊天框"], 34, 122, { size: 64, weight: 950, fill: C.white })}
        </g>
        <g transform="translate(390 318)">
          ${[
            ["研究", C.blue, 40, 30],
            ["邮件", C.acid, 322, 4],
            ["搜索", C.orange, 588, 44],
            ["代码", C.white, 200, 150],
            ["音乐", C.red, 488, 165],
            ["视频", C.blue, 760, 135],
          ].map(([t, color, x, y]) => `<g transform="translate(${x} ${y})">
            <rect width="178" height="78" fill="${color}" stroke="${C.black}" stroke-width="2"/>
            ${smallText(t, 89, 50, { size: 28, weight: 950, fill: color === C.black ? C.white : C.black, anchor: "middle" })}
          </g>`).join("")}
          <path d="M-55 134 C105 50 224 95 358 46 C510 -10 612 32 716 88 C792 128 850 145 930 134" fill="none" stroke="${C.black}" stroke-width="5"/>
          <path d="M930 134 l-28 -18 v36 z" fill="${C.black}"/>
          ${textLines(["入口 + 上下文 + 权限 + 反馈"], 198, 290, { size: 30, weight: 900, fill: C.black })}
        </g>`,
      rail: evidenceRail([
        { kicker: "研究计划", value: "1万到10万", note: "学术用户", accent: C.blue },
        { kicker: "搜索入口", value: "43%", note: "概览出现率", accent: C.orange },
        { kicker: "邮箱", value: "60%", note: "草稿直发", accent: C.acid },
        { kicker: "视频", value: "30秒", note: "单次生成", accent: C.red },
        { kicker: "教育", value: "一亿美元", note: "战略投资", accent: C.black },
      ]),
    }),
  },
  {
    file: "06-china-cashout-alignment.svg",
    svg: shell({
      index: 6,
      stamp: "兑现期",
      title: ["中国人工智能", "进入兑现期"],
      deck: ["组织、资本、监管在同一周收紧。", "模型故事开始接受商业化检验。"],
      body: `
        <g transform="translate(58 326)">
          ${[
            ["组织", "飞书并入豆包 / 火山", C.blue],
            ["资本", "月之暗面融资 / 上市前", C.orange],
            ["监管", "人工智能法提速", C.red],
          ].map(([h, d, color], i) => `<g transform="translate(${i * 418} 0)">
            <rect width="365" height="250" fill="${i === 1 ? C.black : C.white}" stroke="${C.black}" stroke-width="2"/>
            <rect width="365" height="20" fill="${color}"/>
            ${smallText(h, 28, 88, { size: 58, weight: 950, fill: i === 1 ? C.white : C.black })}
            ${smallText(d, 28, 137, { size: 23, weight: 800, fill: i === 1 ? C.white : C.black })}
            <line x1="28" y1="176" x2="318" y2="176" stroke="${i === 1 ? C.white : C.line}"/>
            <circle cx="307" cy="206" r="34" fill="${color}"/>
          </g>`).join("")}
          <path d="M85 283 H1188" stroke="${C.black}" stroke-width="5"/>
          ${smallText("从发布速度转向收入质量", 530, 318, { size: 34, weight: 950, fill: C.black })}
        </g>`,
      rail: evidenceRail([
        { kicker: "字节", value: "重组", note: "飞书并入豆包", accent: C.blue },
        { kicker: "月之暗面", value: "35亿美元", note: "融资口径", accent: C.orange },
        { kicker: "估值", value: "500亿美元", note: "上市前口径", accent: C.black },
        { kicker: "发改委", value: "30%+", note: "行业增速", accent: C.red },
        { kicker: "深度求索", value: "82.7", note: "终端测评", accent: C.acid },
      ]),
    }),
  },
];

for (const item of visuals) {
  fs.writeFileSync(path.join(outDir, item.file), item.svg, "utf8");
}

const index = `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>人工智能周报趋势可视化</title>
  <style>
    body { margin: 0; background: ${C.black}; color: ${C.white}; font-family: ${font}; }
    main { max-width: 1160px; margin: 0 auto; padding: 36px 20px 80px; }
    h1 { font-size: 30px; margin: 0 0 24px; letter-spacing: 0; }
    figure { margin: 0 0 36px; }
    img { display: block; width: 100%; height: auto; background: ${C.paper}; }
    figcaption { margin-top: 10px; color: #cbc8bd; font-size: 14px; }
  </style>
</head>
<body>
<main>
  <h1>人工智能周报 / 趋势可视化</h1>
  ${visuals.map((v, i) => `<figure><img src="${v.file}" alt="趋势图 ${i + 1}"/><figcaption>${String(i + 1).padStart(2, "0")} / ${v.file}</figcaption></figure>`).join("\n  ")}
</main>
</body>
</html>`;
fs.writeFileSync(path.join(outDir, "index.html"), index, "utf8");

const readme = `# 人工智能周报趋势可视化

源文章：ai-weekly-2026-07-24-to-07-31.md

输出：六张 1440x810 SVG 趋势图，图内可见文字已中文化。

- 01-price-performance-ledger.svg
- 02-open-weights-production-gauntlet.svg
- 03-agent-permission-boundary.svg
- 04-harness-score-split.svg
- 05-work-surface-entry-map.svg
- 06-china-cashout-alignment.svg

打开 index.html 可预览。
`;
fs.writeFileSync(path.join(outDir, "README.md"), readme, "utf8");

console.log(`写入 ${visuals.length} 张中文 SVG 趋势图：${outDir}`);
