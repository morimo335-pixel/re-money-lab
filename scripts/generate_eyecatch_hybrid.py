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
# 2026-05-14 BG_PROMPT を article-aware に変更：left_holds・right_holds をJSONで上書き可能
DEFAULT_LEFT_HOLDS = "a small luxury watch case (wooden or leather, opened to show a vintage-style wristwatch with metallic bracelet inside)"
DEFAULT_RIGHT_HOLDS = "a wooden clipboard close to her chest with both hands"


def build_bg_prompt(left_holds: str = DEFAULT_LEFT_HOLDS, right_holds: str = DEFAULT_RIGHT_HOLDS) -> str:
    return f"""A photorealistic 16:9 horizontal magazine cover background image (1376x768 pixels) for a high-end Japanese women's lifestyle magazine. Editorial photography style, warm and refined.

THREE-PART LAYOUT:
- LEFT 25 percent: A Japanese housewife in her early 40s, gentle but slightly anxious face, hair in a loose bun, wearing cream-beige knit sweater. She holds {left_holds} at chest level, looking down with hesitant worried expression. Half-body composition.
- CENTER 50 percent: PURE CLEAN CREAM-WHITE BACKGROUND. The center 50 percent of the image MUST BE COMPLETELY EMPTY. Absolutely NO text, NO letters, NO Japanese characters, NO numbers, NO codes, NO hashtags, NO symbols, NO objects, NO logos, NO decorations in this central area. Just empty smooth cream background.
- RIGHT 25 percent: A confident smiling Japanese woman in her 30s with neat half-up dark hair, wearing navy blouse. She holds {right_holds}. CRITICAL: her arms and hands stay strictly within the right 25 percent zone, not extending toward the center. No outstretched hands or pointing gestures. Half-body composition.

STYLE:
- Background: clean white to cream gradient, soft warm tone
- Soft natural lighting, gentle shadows
- High-end editorial magazine aesthetic
- Photorealistic, NOT cartoon

ABSOLUTELY CRITICAL: This is a BACKGROUND-ONLY image. The center 50 percent must be COMPLETELY EMPTY. Do NOT draw any text, letters, characters, numbers, color codes, or symbols anywhere in the image. Only the two figures on the left and right edges. Text will be added separately by a different process later.
"""


def generate_bg(output: Path, left_holds: str = DEFAULT_LEFT_HOLDS, right_holds: str = DEFAULT_RIGHT_HOLDS):
    """Imagen 4 で背景（人物2人＋空白中央）を生成"""
    print("🎨 背景生成中（Imagen 4）...")
    resp = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=build_bg_prompt(left_holds, right_holds),
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
    subtitle2: str = "",
    subtitle2_color: str = "#1E3A5F",
):
    """背景画像にタイトル＋サブ＋ゴールド水平線を合成"""
    print("✏️ テキスト合成中...")
    img = Image.open(bg_path).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    # フォントサイズ（スマホ視認性最優先・2026-05-14 文字大きすぎ調整）
    main_size = max(64, int(H * 0.095))   # 旧0.115→0.095
    accent_size = max(78, int(H * 0.120)) # 旧0.145→0.120

    # サブタイトルは中央エリア（中央40%幅）に収まるよう自動調整
    # 2026-05-14 Satoshi指摘：文字が左右人物に被るので中央エリア幅を狭く（52%→40%）
    center_area_width = int(W * 0.40)  # 人物に被らない厳格中央エリア
    sub_size_initial = max(32, int(H * 0.048))  # 2026-05-14 サイズ拡大（スマホ視認性UP）
    font_sub = ImageFont.truetype(MINCHO, sub_size_initial)
    # 幅オーバーするなら段階的に縮小（実際のsubtitle文字列で判定）
    while draw.textlength(subtitle, font=font_sub) > center_area_width and sub_size_initial > 22:
        sub_size_initial -= 1
        font_sub = ImageFont.truetype(MINCHO, sub_size_initial)
    sub_size = sub_size_initial

    # 2026-05-14 Satoshi指摘：main lines も center_area_width に収まるよう自動縮小
    def fit_font(text: str, base_size: int, max_w: int) -> ImageFont.FreeTypeFont:
        size = base_size
        font = ImageFont.truetype(MINCHO, size)
        while draw.textlength(text, font=font) > max_w and size > 32:
            size -= 2
            font = ImageFont.truetype(MINCHO, size)
        return font

    font_main = fit_font(line1, main_size, center_area_width)
    font_main_l2 = fit_font(line2, main_size, center_area_width)
    font_accent = ImageFont.truetype(MINCHO, accent_size)

    cx = W // 2
    line_spacing = int(main_size * 1.15)

    # 2026-05-14 Satoshi指示：太字化（stroke）+ 文字サイズも程よく抑える
    # 旧 stroke 3/4/2 → 読みにくい（ブロック化）。1/2/1 で軽め太字
    STROKE_W_MAIN = 1
    STROKE_W_ACCENT = 2
    STROKE_W_SUB = 1

    # Line 1
    y1 = int(H * 0.07)
    w1 = draw.textlength(line1, font=font_main)
    draw.text((cx - w1 / 2, y1), line1, font=font_main, fill=line1_color, stroke_width=STROKE_W_MAIN, stroke_fill=line1_color)

    # Line 2
    y2 = y1 + line_spacing
    w2 = draw.textlength(line2, font=font_main_l2)
    draw.text((cx - w2 / 2, y2), line2, font=font_main_l2, fill=line2_color, stroke_width=STROKE_W_MAIN, stroke_fill=line2_color)

    # Line 3: 語順対応版（accent の位置を line3_main 内で検出して分割）
    y3 = y2 + line_spacing
    accent_idx = line3_main.find(line3_accent) if line3_accent in line3_main else -1
    if accent_idx == -1:
        # accent が含まれない（保険）→ 全体をmain色で描画
        before, accent_txt, after = "", line3_accent, line3_main
    else:
        before = line3_main[:accent_idx]
        accent_txt = line3_accent
        after = line3_main[accent_idx + len(line3_accent):]

    font_line3_main = fit_font(line3_main, main_size, center_area_width)
    before_w = draw.textlength(before, font=font_line3_main)
    accent_w = draw.textlength(accent_txt, font=font_accent)
    after_w = draw.textlength(after, font=font_line3_main)
    gap = 6
    gap_before = gap if before else 0
    gap_after = gap if after else 0
    total_w = before_w + gap_before + accent_w + gap_after + after_w
    x_start = cx - total_w / 2
    accent_y_offset = (accent_size - main_size) // 2

    x = x_start
    if before:
        draw.text((x, y3), before, font=font_line3_main, fill=line3_main_color, stroke_width=STROKE_W_MAIN, stroke_fill=line3_main_color)
        x += before_w + gap_before
    draw.text((x, y3 - accent_y_offset), accent_txt, font=font_accent, fill=line3_accent_color, stroke_width=STROKE_W_ACCENT, stroke_fill=line3_accent_color)
    x += accent_w + gap_after
    if after:
        draw.text((x, y3), after, font=font_line3_main, fill=line3_main_color, stroke_width=STROKE_W_MAIN, stroke_fill=line3_main_color)

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
    draw.text((cx - sub_w / 2, y_sub), subtitle, font=font_sub, fill=subtitle_color, stroke_width=STROKE_W_SUB, stroke_fill=subtitle_color)

    # 第2サブタイトル（スマホで下空白を埋めるための価格フック等）
    if subtitle2:
        sub2_size = max(34, int(H * 0.055))
        font_sub2 = ImageFont.truetype(MINCHO, sub2_size)
        # 幅オーバー時は段階縮小（中央エリア幅以内に収める）
        while draw.textlength(subtitle2, font=font_sub2) > center_area_width and sub2_size > 22:
            sub2_size -= 1
            font_sub2 = ImageFont.truetype(MINCHO, sub2_size)
        y_sub2 = y_sub + sub_size + 28
        sub2_w = draw.textlength(subtitle2, font=font_sub2)
        draw.text((cx - sub2_w / 2, y_sub2), subtitle2, font=font_sub2, fill=subtitle2_color, stroke_width=STROKE_W_SUB, stroke_fill=subtitle2_color)

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

    # left_holds / right_holds をJSONから抽出（compose_text には渡さない）
    bg_left = params.pop("bg_left_holds", DEFAULT_LEFT_HOLDS)
    bg_right = params.pop("bg_right_holds", DEFAULT_RIGHT_HOLDS)

    generate_bg(bg, left_holds=bg_left, right_holds=bg_right)
    compose_text(bg, final, **params)
    print(f"\n🎉 完了！→ {final}")
