"""
re-money-lab.com アイキャッチ自動生成スクリプト
Gemini API (Nano Banana / Imagen 4) を呼び出して記事のアイキャッチ画像を生成する。

Usage:
    python3 scripts/generate_eyecatch.py <prompt_file> <output_path>
    python3 scripts/generate_eyecatch.py prompts/tenpo-kaitori-kotsu.txt src/assets/blog/tenpo-kaitori-kotsu.jpg

テスト用（プロンプト・出力先省略時）:
    python3 scripts/generate_eyecatch.py
    → 記事30スタイルでテスト1枚を /tmp/test_eyecatch.jpg に生成
"""

import os
import sys
import base64
from pathlib import Path

# .envからAPIキー読み込み
ROOT = Path(__file__).resolve().parent.parent
env_file = ROOT / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if line.startswith("GEMINI_API_KEY="):
            os.environ["GEMINI_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("❌ GEMINI_API_KEY が .env に設定されていません")
    sys.exit(1)

from google import genai
from google.genai import types

client = genai.Client(api_key=API_KEY)

# テスト用デフォルトプロンプト（記事30の福ちゃん出張テンプレ流用版）
DEFAULT_PROMPT = """A photorealistic 16:9 horizontal image (1376x768 pixels) for a Japanese women's lifestyle magazine featured image, in the style of LEE, ESSE, or Kurashi-no-Techo magazine.

CRITICAL: This image will be viewed primarily on SMARTPHONES (small screens, 350-400px wide when displayed). The main headline text MUST be LARGE, BOLD, and HIGH-CONTRAST so it remains perfectly readable even when scaled down. The center text area must be visually dominant.

THREE-PART COMPOSITION (left 28% / center 44% / right 28%):

LEFT 28%: A Japanese housewife in her early 40s, gentle but slightly anxious face, hair in a loose bun, wearing a white or cream-beige knit sweater. She is holding a small jewelry box and a brand-style handbag, looking down at them with a hesitant, worried expression as if she's wondering whether to take them to a buyback shop and worrying about being lowballed. Half-body composition.

CENTER 44% (TEXT-DOMINANT AREA): Large Japanese text on a clean white-cream background, in elegant Mincho (serif) font. ALL HEADLINE CHARACTERS MUST BE EXTRA LARGE, BOLD, AND THICK-STROKED.
- Main headline (in 3 lines, EXTRA BOLD Mincho serif font):
  Line 1: "店舗買取" — BRIGHT EMERALD GREEN color #00A878 (vivid, lively, NOT dark)
  Line 2: "買い叩かれない" — DEEP NAVY color #1E3A5F
  Line 3: "5つのコツ" — base DEEP NAVY #1E3A5F, BUT the first two characters "5つ" must be colored BEAUTIFUL GOLDEN YELLOW #FFD700 (bright, clear, classic gold leaf), bolder and slightly LARGER than the rest.
- A thin elegant gold horizontal line (color #D4A574) separating headline from subtitle.
- Subtitle below in smaller but readable Mincho font, GOLD color #D4A574:
  "元業界人8年が暴く 持ち込みで損しない本音"

RIGHT 28%: A confident smiling Japanese woman in her 30s with neat half-up dark hair, wearing a navy blouse. She holds a clipboard, with a warm welcoming gesture. Half-body composition.

OVERALL STYLE:
- Background: clean white to cream gradient (#FFFFFF to #FAF7F0)
- Soft natural lighting, gentle shadows
- High-end, trustworthy, calm magazine-cover aesthetic
- Mincho/serif Japanese typography

STRICTLY AVOID:
- Emoji icons of any kind
- Trademarked logos or brand monograms
- Cartoon or illustration style — keep it photorealistic
- Crowded layouts, harsh colors, commercial banner feel
- Pop, rounded gothic, or handwritten fonts — must be Mincho serif
- Garbled or random Japanese characters
- Bright warning red, panel dividers, yellow ribbon banners
- YouTube-thumbnail style

Aspect ratio: 16:9, suitable for a blog featured image at 1376x768px.
"""


def generate(prompt: str, output_path: Path, model: str = "gemini-2.5-flash-image") -> Path:
    """
    Gemini Nano Banana で画像生成して指定パスに保存。
    モデル候補:
      - gemini-2.5-flash-image  (Nano Banana・最新)
      - imagen-4.0-generate-001 (Imagen 4・高品質)
    """
    print(f"🎨 生成開始 | モデル: {model}")
    print(f"📝 プロンプト先頭: {prompt[:80]}...")

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    # 画像データを抽出
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(part.inline_data.data)
            print(f"✅ 保存完了: {output_path}")
            print(f"📦 サイズ: {output_path.stat().st_size / 1024:.1f} KB")
            return output_path

    print("❌ 画像データが返されませんでした")
    print("レスポンス:", response.candidates[0].content.parts)
    sys.exit(1)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        # テストモード
        prompt = DEFAULT_PROMPT
        output = Path("/tmp/test_eyecatch.jpg")
    elif len(args) == 2:
        prompt = Path(args[0]).read_text()
        output = Path(args[1])
    else:
        print(__doc__)
        sys.exit(1)

    generate(prompt, output)
