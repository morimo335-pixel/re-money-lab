#!/usr/bin/env python3
"""raise-appraisal.md の <h3>業界人ワンポイント</h3><blockquote>...</blockquote>
をエメラルドBOXに統一する"""
import re
from pathlib import Path

target = Path("src/content/blog/raise-appraisal.md")
text = target.read_text()

# パターン: <h3>業界人ワンポイント</h3>\n<blockquote>\n(.+?)\n</blockquote>
pattern = re.compile(
    r"<h3>業界人ワンポイント</h3>\s*<blockquote>\s*(.+?)\s*</blockquote>",
    re.DOTALL,
)

def replace(match):
    inner = match.group(1).strip()
    # 先頭の <p>💡 <strong>xxx</strong></p> を取り除いて prefix にする
    # 簡単なヒューリスティック：複数pをそのまま中に入れる
    # 標準形：<div ...><strong>💡 業界人ワンポイント：</strong>テキスト</div>
    # 複数pがある場合は、最初のpをタイトル相当として<strong>に、残りをそのままpで保持

    # 最初の <p> から最後の </p> まで取得
    paragraphs = re.findall(r"<p>(.*?)</p>", inner, re.DOTALL)

    if not paragraphs:
        body = inner
    elif len(paragraphs) == 1:
        # 1段落だけ：先頭の💡や絵文字を削除して内容のみ
        body = paragraphs[0]
        body = re.sub(r"^💡\s*<strong>(.*?)</strong>\s*", r"<strong>\1</strong> ", body, count=1)
    else:
        # 複数段落：最初の段落をタイトル風に、残りはbrで連結
        first = paragraphs[0]
        first = re.sub(r"^💡\s*<strong>(.*?)</strong>\s*", r"<strong>\1</strong>", first, count=1)
        rest_html = "<br><br>".join(paragraphs[1:])
        body = f"{first}<br><br>{rest_html}"

    return (
        '<div style="background:#E0F2F1;border-left:4px solid #00695C;color:#004D40;padding:16px 22px;margin:22px 0;border-radius:4px;">\n'
        f'<strong style="color:#1E3A5F;">💡 業界人ワンポイント：</strong>{body}\n'
        '</div>'
    )


new_text, n = pattern.subn(replace, text)
print(f"変換: {n}箇所")
target.write_text(new_text)
print("保存完了")
