#!/usr/bin/env python3
"""旧WP記事内の wp-content 画像を全部取得して public/ 配下に配置"""
import os, re, urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
PUBLIC = ROOT / "public"
CONTENT = ROOT / "src/content/blog"

# 旧WPサーバーIP（DNSはCloudflareなので明示する必要あり）
WP_IP = "157.120.209.91"
WP_HOST = "re-money-lab.com"

# Markdown ファイルから wp-content URL を全部抽出
url_pattern = re.compile(r'https://re-money-lab\.com/(wp-content/uploads/[^"\s)]+)')
urls = set()
for md in CONTENT.glob("*.md"):
    text = md.read_text()
    for m in url_pattern.finditer(text):
        urls.add(m.group(1))  # path part: wp-content/uploads/2026/04/xxx.jpg

print(f"画像URL: {len(urls)}件")

ok = 0
ng = 0
for path in sorted(urls):
    dest = PUBLIC / path
    if dest.exists():
        ok += 1
        continue
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        # WP origin server (ConoHa) から直接取得 — Host ヘッダで判別
        url = f"https://{WP_IP}/{path}"
        req = urllib.request.Request(
            url,
            headers={
                "Host": WP_HOST,
                "User-Agent": "Mozilla/5.0",
            },
        )
        # SSL検証無視（IP直叩きなので）
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            data = r.read()
        dest.write_bytes(data)
        print(f"  ✓ {path} ({len(data):,}B)")
        ok += 1
    except Exception as e:
        print(f"  ✗ {path}: {e}")
        ng += 1

print(f"\n完了: OK={ok}, NG={ng}")
