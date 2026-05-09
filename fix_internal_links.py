#!/usr/bin/env python3
"""旧blockquote式の内部リンクプレースホルダ整理
1. 「内部リンク（公開後追加）：[xxx]」プレースホルダ → 削除
2. 「内部リンク：<a>...</a>」blockquote → 水色カード変換
"""
import re
from pathlib import Path

CONTENT = Path("src/content/blog")
total_removed = 0
total_converted = 0
total_files = 0

# パターン1: 公開後追加 のプレースホルダ全削除
placeholder_pat = re.compile(
    r"<blockquote>\s*<p>内部リンク（公開後追加）：[^<]*</p>\s*</blockquote>\s*",
    re.DOTALL,
)

# パターン2: <blockquote><p>内部リンク：<a href="...">title</a></p></blockquote>
inline_link_pat = re.compile(
    r'<blockquote>\s*<p>内部リンク：<a href="([^"]+)">([^<]+)</a></p>\s*</blockquote>',
    re.DOTALL,
)

def to_card(href: str, title: str) -> str:
    return (
        '<div style="background:#E3F2FD;border-left:5px solid #1E3A5F;padding:14px 20px;margin:22px 0;border-radius:4px;">\n'
        '▶ <strong>あわせて読みたい</strong><br>\n'
        f'<a href="{href}">{title}</a>\n'
        '</div>'
    )

for md in sorted(CONTENT.glob("*.md")):
    text = md.read_text()
    original = text

    # 1. プレースホルダ削除
    text, n_removed = placeholder_pat.subn("", text)

    # 2. インラインリンクをカードに変換
    def repl(m):
        return to_card(m.group(1), m.group(2))

    text, n_converted = inline_link_pat.subn(repl, text)

    if text != original:
        md.write_text(text)
        print(f"  {md.name}: 削除{n_removed} 変換{n_converted}")
        total_removed += n_removed
        total_converted += n_converted
        total_files += 1

print(f"\n変更: {total_files}ファイル / プレースホルダ削除{total_removed}件 / カード変換{total_converted}件")
