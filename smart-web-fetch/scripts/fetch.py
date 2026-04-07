#!/usr/bin/env python3
"""
Smart Web Fetch - 智能网页抓取工具
按优先级尝试多种方法抓取网页并返回Markdown格式

使用方法:
    python3 fetch.py [URL] [--output OUTPUT_FILE]
    
示例:
    python3 fetch.py https://arxiv.org/abs/2503.12345
    python3 fetch.py https://github.com/user/repo --output result.md
"""

import sys
import os
import argparse
import urllib.request
import urllib.error
import subprocess
import json
from urllib.parse import quote


def try_fetch_with_urllib(url, service_name, full_url, timeout=15):
    """使用urllib尝试抓取URL"""
    print(f"  [{service_name}] 尝试...", file=sys.stderr)
    try:
        req = urllib.request.Request(
            full_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read()
            # 处理gzip压缩
            if response.headers.get('Content-Encoding') == 'gzip':
                import gzip
                content = gzip.decompress(content)
            content = content.decode('utf-8', errors='ignore')
            if len(content) > 200:  # 有效内容检查
                return True, content
            else:
                return False, None
    except Exception as e:
        return False, str(e)


def try_scrapling(url):
    """使用Scrapling尝试抓取"""
    print("  [Scrapling] 尝试...", file=sys.stderr)
    
    # 首先尝试安装scrapling
    try:
        import scrapling
    except ImportError:
        print("    正在安装 Scrapling...", file=sys.stderr)
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'scrapling', '-q'])
            import scrapling
        except Exception as e:
            return False, f"无法安装Scrapling: {e}"
    
    try:
        from scrapling import Fetcher
        fetcher = Fetcher()
        response = fetcher.get(url, stealth=True)
        
        # 提取内容并转换为markdown风格
        title = response.find('title')
        title_text = title.text if title else ""
        
        # 尝试提取主要内容
        content = response.find('article') or response.find('main') or response.find('body')
        if content:
            text = content.text
        else:
            text = response.text
            
        # 构建markdown格式输出
        markdown = f"# {title_text}\n\n"
        markdown += text.strip()
        
        if len(markdown) > 200:
            return True, markdown
        return False, None
    except Exception as e:
        return False, str(e)


def try_playwright(url):
    """使用Playwright作为备选方案"""
    print("  [Playwright] 尝试...", file=sys.stderr)
    
    script = f'''
import asyncio
from playwright.async_api import async_playwright

async def fetch():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('{url}', wait_until='networkidle', timeout=30000)
        content = await page.content()
        await browser.close()
        print(content)

asyncio.run(fetch())
'''
    try:
        result = subprocess.run(
            [sys.executable, '-c', script],
            capture_output=True,
            text=True,
            timeout=45
        )
        if result.returncode == 0 and len(result.stdout) > 500:
            # 将HTML转换为markdown（简化版）
            from html.parser import HTMLParser
            class TextExtractor(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text = []
                    self.in_script = False
                    
                def handle_starttag(self, tag, attrs):
                    if tag in ['script', 'style']:
                        self.in_script = True
                    elif tag in ['h1', 'h2', 'h3']:
                        self.text.append('\n# ')
                    elif tag == 'p':
                        self.text.append('\n')
                    elif tag == 'br':
                        self.text.append('\n')
                        
                def handle_endtag(self, tag):
                    if tag in ['script', 'style']:
                        self.in_script = False
                    elif tag in ['h1', 'h2', 'h3', 'p']:
                        self.text.append('\n')
                        
                def handle_data(self, data):
                    if not self.in_script:
                        self.text.append(data.strip())
            
            extractor = TextExtractor()
            extractor.feed(result.stdout)
            text = ' '.join(extractor.text)
            
            if len(text) > 200:
                return True, text
        return False, None
    except Exception as e:
        return False, str(e)


def smart_fetch(url, use_scrapling=True, use_playwright=True):
    """
    智能抓取网页
    按优先级尝试：markdown.new → defuddle.md → r.jina.ai → Scrapling → Playwright
    """
    # 清理URL
    url = url.strip().strip('"\'')
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    original_url = url
    
    # 优先级1: markdown.new (Cloudflare网站首选)
    full_url = f"https://markdown.new/{original_url}"
    success, content = try_fetch_with_urllib(original_url, "markdown.new", full_url)
    if success:
        return {"success": True, "method": "markdown.new", "content": content}
    
    # 优先级2: defuddle.md (非Cloudflare)
    full_url = f"https://defuddle.md/{original_url}"
    success, content = try_fetch_with_urllib(original_url, "defuddle.md", full_url)
    if success:
        return {"success": True, "method": "defuddle.md", "content": content}
    
    # 优先级3: r.jina.ai
    clean_url = original_url.replace('https://', '').replace('http://', '')
    full_url = f"https://r.jina.ai/http://{clean_url}"
    success, content = try_fetch_with_urllib(original_url, "r.jina.ai", full_url)
    if success:
        return {"success": True, "method": "r.jina.ai", "content": content}
    
    # 优先级4: Scrapling
    if use_scrapling:
        success, content = try_scrapling(original_url)
        if success:
            return {"success": True, "method": "Scrapling", "content": content}
    
    # 优先级5: Playwright
    if use_playwright:
        success, content = try_playwright(original_url)
        if success:
            return {"success": True, "method": "Playwright", "content": content}
    
    return {
        "success": False, 
        "method": None, 
        "content": None,
        "error": "所有抓取方法都失败了"
    }


def main():
    parser = argparse.ArgumentParser(
        description='Smart Web Fetch - 智能网页抓取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python3 fetch.py https://arxiv.org/abs/2503.12345
  python3 fetch.py https://github.com/user/repo --output result.md
  python3 fetch.py example.com/article --no-scrapling
        '''
    )
    parser.add_argument('url', help='要抓取的URL')
    parser.add_argument('-o', '--output', help='输出文件路径（默认输出到stdout）')
    parser.add_argument('--no-scrapling', action='store_true', help='禁用Scrapling')
    parser.add_argument('--no-playwright', action='store_true', help='禁用Playwright')
    parser.add_argument('--json', action='store_true', help='以JSON格式输出')
    
    args = parser.parse_args()
    
    result = smart_fetch(
        args.url,
        use_scrapling=not args.no_scrapling,
        use_playwright=not args.no_playwright
    )
    
    if args.json:
        output = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        if result["success"]:
            output = result["content"]
            if not args.output:
                print(f"\n# 抓取成功 [使用 {result['method']}]\n", file=sys.stderr)
        else:
            output = f"抓取失败: {result.get('error', '未知错误')}"
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"结果已保存到: {args.output}", file=sys.stderr)
    else:
        print(output)
    
    sys.exit(0 if result["success"] else 1)


if __name__ == '__main__':
    main()
