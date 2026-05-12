"""
re-money-lab.com アイキャッチ ハイブリッド自動生成
- 背景＋人物：Gemini Imagen 4 で生成（中央エリアはテキストなしの空白）
- タイトル文字：Pillow で合成（日本語完全精度・色完全制御）

Usage:
    # テスト（記事30のパラメータでデフォルト生成）
    python3 scripts/generate_eyecatch_hybrid.py
    → /tmp/test_hybrid_final.jpg

    # 本番（記事のパラメータJSONから生成）
    python3 scripts/generate_eyecatch_hybrid.py prompts/tenpo-kaitori-kotsu.json src/assets/blog/tenpo-kaitori-kotsu.jpg
"""

import os
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# .env から APIキー読み込み
ROOT = Path(__file__).resolve().parent.parent
env = ROOT / ".env"
if env.exists():
    for line in env.read_text().splitlines():
        if line.startswith("GEMINI_API_KEY="):
            os.environ["GEMINI_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")

from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 日本語明朝フォント（macOS標準）
MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"

# ベースプロンプト：人物2人＋空白中央エリア（テキストなし）
BG_PROMPT = """A photorealistic 16:9 horizontal magazine cover background image (1376x768 pixels) for a high-end Japanese women's lifestyle magazine. Editorial photography style, warm and refined.

THREE-PART LAYOUT:
- LEFT 25 percent: A Japanese housewife in her early 40s, gentle but slightly anxious face, hair in a loose bun, wearing cream-beige knit sweater. She holds a small jewelry box and a brand-style leather handbag, looking down with hesitant worried expression. Half-body composition.
- CENTER 50 percent: PURE CLEAN CREAM-WHITE BACKGROUND. The center 50 percent of the image MUST BE COMPLETELY EMPTY. Absolutely NO text, NO letters, NO Japanese characters, NO numbers, NO codes, NO hashtags, NO symbols, NO objects, NO logos, NO decorations in this central area. Just empty smooth cream background.
- RIGHT 25 percent: A confident smiling Japanese woman in her 30s with neat half-up dark hair, wearing navy blouse. She holds a wooden clipboard with warm welcoming gesture. Half-body composition.

STYLE:
- Background: clean white to cream gradient, soft warm tone
- Soft natural lighting, gentle shadows
- High-end editorial magazine aesthetic
- Photorealistic, NOT cartoon

ABSOLUTELY CRITICAL: This is a BACKGROUND-ONLY image. The center 50 percent must be COMPLETELY EMPTY. Do NOT draw any text, letters, characters, numbers, color codes, or symbols anywhere in the image. Only the two figures on the left and right edges. Text will be added separately by a different process later.
"""


def generate_bg(output: Path):
    """Imagen 4 で背景（人物2人＋空白中央）を生成"""
    print("🎨 背景生成中（Imagen 4）...")
    resp = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=BG_PROMPT,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="16:9",
        ),
    )
    resp.generated_images[0].image.save(str(output))
    print(f"✅ 背景保存: {output} ({output.stat().st_size/1024:.1f} KB)")
    return output


def compose_text(
    bg_path: Path,
    output: Path,
    line1: str,
    line1_color: str,
    line2: str,
    line2_color: str,
    line3_main: str,
    line3_accent: str,
    line3_main_color: str,
    line3_accent_color: str,
    subtitle: str,
    subtitle_color: str,
    gold_line_color: str = "#D4A574",
):
    """背景画像にタイトル＋サブ＋ゴールド水平線を合成"""
    print("✏️ テキスト合成中...")
    img = Image.open(bg_path).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    # フォントサイズ（スマホ視認性最優先）
    main_size = max(72, int(H * 0.115))
    accent_size = max(86, int(H * 0.145))

    # サブタイトルは中央エリア（中央50%幅）に収まるよう自動調整
    center_area_width = int(W * 0.52)  # 人物に被らない中央エリア
    sub_size_initial = max(24, int(H * 0.034))
    font_sub = ImageFont.truetype(MINCHO, sub_size_initial)
    # 幅オーバーするなら段階的に縮小
    while draw.textlength("元業界人8年が暴く 持ち込みで損しない本音", font=font_sub) > center_area_width and sub_size_initial > 18:
        sub_size_initial -= 1
        font_sub = ImageFont.truetype(MINCHO, sub_size_initial)
    sub_size = sub_size_initial

    font_main = ImageFont.truetype(MINCHO, main_size)
    font_accent = ImageFont.truetype(MINCHO, accent_size)

    cx = W // 2
    line_spacing = int(main_size * 1.15)

    # Line 1 (全体を少し上に詰める)
    y1 = int(H * 0.07)
    w1 = draw.textlength(line1, font=font_main)
    draw.text((cx - w1 / 2, y1), line1, font=font_main, fill=line1_color)

    # Line 2
    y2 = y1 + line_spacing
    w2 = draw.textlength(line2, font=font_main)
    draw.text((cx - w2 / 2, y2), line2, font=font_main, fill=line2_color)

    # Line 3: accent (大きい黄色) + 残り (ネイビー)
    y3 = y2 + line_spacing
    rest = line3_main.replace(line3_accent, "", 1)
    accent_w = draw.textlength(line3_accent, font=font_accent)
    rest_w = draw.textlength(rest, font=font_main)
    gap = 6
    total_w = accent_w + gap + rest_w
    x_start = cx - total_w / 2
    accent_y_offset = (accent_size - main_size) // 2
    draw.text((x_start, y3 - accent_y_offset), line3_accent, font=font_accent, fill=line3_accent_color)
    draw.text((x_start + accent_w + gap, y3), rest, font=font_main, fill=line3_main_color)

    # ゴールド水平線
    y_line = y3 + line_spacing + 20
    line_width = int(W * 0.18)
    draw.line(
        [(cx - line_width // 2, y_line), (cx + line_width // 2, y_line)],
        fill=gold_line_color,
        width=3,
    )

    # サブタイトル
    y_sub = y_line + 24
    sub_w = draw.textlength(subtitle, font=font_sub)
    draw.text((cx - sub_w / 2, y_sub), subtitle, font=font_sub, fill=subtitle_color)

    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output, "JPEG", quality=92)
    print(f"✅ 最終保存: {output} ({output.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        # テストモード：記事30のパラメータ
        params = {
            "line1": "店舗買取",
            "line1_color": "#00A878",
            "line2": "買い叩かれない",
            "line2_color": "#1E3A5F",
            "line3_main": "5つのコツ",
            "line3_accent": "5つ",
            "line3_main_color": "#1E3A5F",
            "line3_accent_color": "#FFD700",
            "subtitle": "元業界人8年が暴く 持ち込みで損しない本音",
            "subtitle_color": "#D4A574",
        }
        bg = Path("/tmp/test_hybrid_bg.jpg")
        final = Path("/tmp/test_hybrid_final.jpg")
    elif len(args) == 2:
        params = json.loads(Path(args[0]).read_text())
        bg = Path("/tmp/_bg_temp.jpg")
        final = Path(args[1])
    else:
        print(__doc__)
        sys.exit(1)

    generate_bg(bg)
    compose_text(bg, final, **params)
    print(f"\n🎉 完了！→ {final}")
