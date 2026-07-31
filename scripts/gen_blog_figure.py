#!/usr/bin/env python3
"""
re-money-lab ブログ本文の図解を生成する。

毛皮記事(public/blog-images/kegawa/)のテイストに合わせた3ブロック構成：
  ① ヘッダー帯（紺）… その画像が付くH2/H3の見出し
  ② 本体カード（白＋金枠）… 金の番号バッジ＋小見出し＋説明文
  ③ フッター帯（紺）… その章の結論

使い方：JSONの設計ファイルを渡す。
  python3 scripts/gen_blog_figure.py figures.json
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = 1200
BG = "#FAF6EC"      # 生成り
NAVY = "#1E3A5F"    # 紺
GOLD = "#C8923A"    # 金
INK = "#333333"     # 墨
WHITE = "#FFFFFF"
LINE = "#E8E4DA"

FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc"
FONT_MED = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_REG = "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc"

# スマホで拡大せず読める下限（1200px幅に対して）
SZ_TITLE = 54
SZ_SUB = 40
SZ_BODY = 32
SZ_CONC = 36


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """日本語は文字単位で折る。「。」の後は必ず改行する。"""
    lines = []
    for para in text.split("\n"):
        buf = ""
        for ch in para:
            if draw.textlength(buf + ch, font=fnt) > max_w and buf:
                lines.append(buf)
                buf = ch
            else:
                buf += ch
            if ch == "。":               # 句点で改行（本文と同じルール）
                lines.append(buf)
                buf = ""
        if buf:
            lines.append(buf)
    return lines


def measure(spec):
    """先に高さを計算する（可変長に対応するため2パス）。"""
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    f_title, f_sub, f_body, f_conc = (
        font(FONT_BOLD, SZ_TITLE), font(FONT_BOLD, SZ_SUB),
        font(FONT_REG, SZ_BODY), font(FONT_BOLD, SZ_CONC),
    )
    pad = 48
    h = 40
    # ヘッダー
    tl = wrap(dummy, spec["title"], f_title, W - pad * 2 - 60)
    h += 40 + len(tl) * int(SZ_TITLE * 1.45) + 40 + 36
    # 本体
    h += 36
    for it in spec["items"]:
        sl = wrap(dummy, it["head"], f_sub, W - pad * 2 - 120)
        bl = wrap(dummy, it.get("body", ""), f_body, W - pad * 2 - 120)
        h += len(sl) * int(SZ_SUB * 1.4) + 12 + len(bl) * int(SZ_BODY * 1.55) + 44
    h += 20
    # フッター
    if spec.get("conclusion"):
        cl = wrap(dummy, spec["conclusion"], f_conc, W - pad * 2 - 40)
        h += 36 + len(cl) * int(SZ_CONC * 1.5) + 40 + 40
    return h + 20, (f_title, f_sub, f_body, f_conc)


def rounded(draw, box, r, fill, outline=None, width=0):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def render(spec, out_path):
    H, (f_title, f_sub, f_body, f_conc) = measure(spec)
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    pad = 48
    y = 40

    # ① ヘッダー帯（紺）
    tl = wrap(d, spec["title"], f_title, W - pad * 2 - 60)
    hh = 40 + len(tl) * int(SZ_TITLE * 1.45) + 40
    rounded(d, (pad, y, W - pad, y + hh), 16, NAVY)
    ty = y + 40
    for ln in tl:
        d.text((pad + 30, ty), ln, font=f_title, fill=WHITE)
        ty += int(SZ_TITLE * 1.45)
    y += hh + 36

    # ② 本体カード（白＋金枠）※先に白地と枠を敷いてから中身を描く
    body_top = y
    bh = 36
    for it in spec["items"]:
        bh += len(wrap(d, it["head"], f_sub, W - pad * 2 - 120)) * int(SZ_SUB * 1.4)
        bh += 12
        bh += len(wrap(d, it.get("body", ""), f_body, W - pad * 2 - 120)) * int(SZ_BODY * 1.55)
        bh += 44
    rounded(d, (pad, body_top, W - pad, body_top + bh - 20), 16, WHITE, GOLD, 3)
    yy = y + 36
    for i, it in enumerate(spec["items"], 1):
        if i > 1:
            d.line((pad + 40, yy - 22, W - pad - 40, yy - 22), fill=LINE, width=2)
        # 金の番号バッジ
        bx, by = pad + 40, yy + 4
        d.ellipse((bx, by, bx + 52, by + 52), fill=GOLD)
        num = str(i)
        nf = font(FONT_BOLD, 30)
        nw = d.textlength(num, font=nf)
        d.text((bx + 26 - nw / 2, by + 9), num, font=nf, fill=WHITE)
        # 小見出し（紺）
        tx = pad + 40 + 72
        for ln in wrap(d, it["head"], f_sub, W - pad * 2 - 120):
            d.text((tx, yy), ln, font=f_sub, fill=NAVY)
            yy += int(SZ_SUB * 1.4)
        yy += 12
        # 説明（墨）
        for ln in wrap(d, it.get("body", ""), f_body, W - pad * 2 - 120):
            d.text((tx, yy), ln, font=f_body, fill=INK)
            yy += int(SZ_BODY * 1.55)
        yy += 44
    y = body_top + bh - 20 + 36

    # ③ フッター帯（紺）
    if spec.get("conclusion"):
        cl = wrap(d, spec["conclusion"], f_conc, W - pad * 2 - 40)
        ch = 36 + len(cl) * int(SZ_CONC * 1.5) + 36
        rounded(d, (pad, y, W - pad, y + ch), 16, NAVY)
        cy = y + 36
        for ln in cl:
            d.text((pad + 30, cy), ln, font=f_conc, fill=WHITE)
            cy += int(SZ_CONC * 1.5)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "WEBP", quality=85)
    return img.size


def main():
    specs = json.load(open(sys.argv[1], encoding="utf-8"))
    for sp in specs:
        size = render(sp, sp["out"])
        print(f"  ✅ {sp['out']}  {size[0]}x{size[1]}")


if __name__ == "__main__":
    main()
