---
name: smart-web-fetch
description: |
  极简网页抓取工具。当传统web_fetch/web_search失败时使用。
  
  核心方法（按优先级尝试）：
  1. 在URL前加 markdown.new/ （Cloudflare网站首选）
  2. 加 defuddle.md/ （非Cloudflare网站）
  3. 加 r.jina.ai/ （终极备选）
  4. 使用Scrapling爬虫工具（终极方案）
  5. 使用Playwright动态渲染（最后手段）
  
  触发词：
  - "抓取这个网页：[URL]"
  - "读取这个链接"
  - "获取这个页面的内容"
  - "传统方法失败了，用smart-web-fetch试试"
---

# Smart Web Fetch

零配置开箱即用的网页抓取技能。当传统web_fetch/web_search方法失败时的救急方案。

## 快速开始

### 方法一：使用内置脚本（推荐）

```bash
# 基本用法
python3 scripts/fetch.py https://example.com/article

# 保存到文件
python3 scripts/fetch.py https://arxiv.org/abs/2503.12345 --output result.md

# JSON格式输出
python3 scripts/fetch.py https://github.com/user/repo --json

# 禁用特定方法
python3 scripts/fetch.py https://example.com --no-scrapling
```

### 方法二：Python API调用

```python
from scripts.fetch import smart_fetch

result = smart_fetch("https://example.com/article")
if result["success"]:
    print(f"抓取成功！使用方法: {result['method']}")
    print(result["content"])
else:
    print(f"抓取失败: {result['error']}")
```

## 核心抓取策略

### 优先级1: markdown.new/ (Cloudflare网站首选)

**适用场景**: arXiv、GitHub、Cloudflare保护的网站

```python
url = f"https://markdown.new/{original_url}"
```

**特点**:
- 专为Cloudflare网站优化
- 返回结构化Markdown
- 速度快，成功率高

### 优先级2: defuddle.md/

**适用场景**: 一般网页、博客、文档站点

```python
url = f"https://defuddle.md/{original_url}"
```

**特点**:
- 智能内容提取
- 过滤导航和广告
- 保留主要文章内容

### 优先级3: r.jina.ai/

**适用场景**: 通用备选方案

```python
clean_url = original_url.replace('https://', '').replace('http://', '')
url = f"https://r.jina.ai/http://{clean_url}"
```

**特点**:
- 通用性强
- 支持绝大多数网站
- 自动提取正文

### 优先级4: Scrapling

**适用场景**: 反爬严格、JavaScript渲染页面

```python
from scrapling import Fetcher
fetcher = Fetcher()
response = fetcher.get(url, stealth=True)
content = response.text
```

**特点**:
- 绕过反爬检测
- 模拟真实浏览器
- 支持动态内容

### 优先级5: Playwright

**适用场景**: 极度复杂的单页应用、需要完整JS执行

**特点**:
- 完整Chromium浏览器
- 执行JavaScript
- 等待页面完全加载

## 完整工作流

当用户请求抓取网页时，执行以下流程：

```
用户: "抓取 https://example.com/article"

AI:
1. 调用 scripts/fetch.py [URL]
2. 脚本按优先级自动尝试所有方法
3. 返回成功的方法和内容
4. 向用户展示结果，并说明使用了哪种方法

成功输出:
"✅ 使用 r.jina.ai 成功抓取！内容如下：..."

失败输出:
"❌ 所有方法都失败了。可能原因：
- 网站完全禁止爬虫
- 需要登录验证
- 内容需要JavaScript动态加载
建议：直接访问链接或提供其他信息来源"
```

## 快速决策表

| 网站类型 | 首选方法 | 成功率 |
|----------|----------|--------|
| arXiv论文 | markdown.new | ⭐⭐⭐⭐⭐ |
| GitHub仓库 | defuddle.md | ⭐⭐⭐⭐⭐ |
| 新闻网站 | r.jina.ai | ⭐⭐⭐⭐ |
| 博客文章 | markdown.new | ⭐⭐⭐⭐ |
| 反爬严格 | Scrapling | ⭐⭐⭐ |
| 动态JS页面 | Playwright | ⭐⭐⭐ |

## 批量抓取示例

```python
import json
from scripts.fetch import smart_fetch

urls = [
    "https://arxiv.org/abs/2503.12345",
    "https://github.com/user/repo",
    "https://example.com/blog/post-1"
]

results = []
for url in urls:
    result = smart_fetch(url)
    results.append({
        "url": url,
        "success": result["success"],
        "method": result.get("method"),
        "content_length": len(result["content"]) if result["success"] else 0
    })

print(json.dumps(results, indent=2))
```

## 脚本选项

```
usage: fetch.py [-h] [-o OUTPUT] [--no-scrapling] [--no-playwright] [--json] url

位置参数:
  url                   要抓取的URL

可选参数:
  -h, --help            显示帮助信息
  -o, --output OUTPUT   输出文件路径
  --no-scrapling        禁用Scrapling
  --no-playwright       禁用Playwright
  --json                以JSON格式输出
```

## 限制与注意事项

### ⚠️ 限制

- **登录保护**: 无法抓取需要登录的内容
- **法律限制**: 遵守目标网站的robots.txt和使用条款
- **频率限制**: 频繁请求可能导致IP暂时封禁
- **完全反爬**: 某些网站（如LinkedIn）完全禁止抓取

### ✅ 最佳实践

1. **从方法1开始**: 总是先尝试轻量级方法
2. **渐进式降级**: 失败后再尝试更强力的方法
3. **合理间隔**: 批量抓取时添加1-2秒间隔
4. **检查robots.txt**: 尊重网站的爬虫规则

## 故障排除

### 常见问题

**Q: 所有方法都失败了怎么办？**
A: 
- 检查URL是否正确
- 确认网站不需要登录
- 尝试直接访问链接
- 可能网站有严格的反爬机制

**Q: Scrapling安装失败？**
A:
- 确保Python版本 >= 3.8
- 尝试手动安装: `pip install scrapling`
- 或使用 `--no-scrapling` 跳过此方法

**Q: 内容格式混乱？**
A:
- 这是正常情况，服务返回的是原始HTML
- 使用 `scripts/extract_text.py` 进一步清理
- 或手动提取需要的部分

### 错误代码

| 退出码 | 含义 |
|--------|------|
| 0 | 抓取成功 |
| 1 | 所有方法失败 |
| 2 | 参数错误 |
| 3 | 脚本内部错误 |

## 相关资源

- **Scrapling**: https://github.com/D4Vinci/Scrapling
- **markdown.new**: https://markdown.new
- **defuddle.md**: https://defuddle.md
- **r.jina.ai**: https://r.jina.ai
