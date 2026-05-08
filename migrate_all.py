#!/usr/bin/env python3
"""
re-money-lab WP→Astro 全記事一括移管スクリプト
- WP REST API で公開済み全記事取得
- HTML をそのまま Markdown 内に埋め込み（装飾100%保持）
- インライン <style> ブロックは削除（src/styles/article.css に統合済み）
- featured_media をダウンロードして src/assets/blog/ に配置
- Markdown を src/content/blog/{slug}.md に保存
"""
import os
import re
import sys
import json
import time
import urllib.request
import urllib.parse
from html import unescape
from pathlib import Path

WP_USER = "morimo335"
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD")
if not WP_APP_PASSWORD:
    sys.exit("ERROR: WP_APP_PASSWORD not in env. Run: source ~/.zshrc && python3 migrate_all.py")

WP_BASE = "https://re-money-lab.com/wp-json/wp/v2"
ASTRO_ROOT = Path(__file__).parent
BLOG_DIR = ASTRO_ROOT / "src/content/blog"
ASSETS_DIR = ASTRO_ROOT / "src/assets/blog"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def wp_get(path: str) -> dict | list:
    """WP REST API GET."""
    url = f"{WP_BASE}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "WordPress/6.0"})
    auth = urllib.parse.quote(f"{WP_USER}:{WP_APP_PASSWORD}", safe="")
    import base64
    creds = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
    req.add_header("Authorization", f"Basic {creds}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def download_image(url: str, dest: Path) -> bool:
    """画像ダウンロード。既存ならスキップ。"""
    if dest.exists():
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            dest.write_bytes(r.read())
        return True
    except Exception as e:
        print(f"  ⚠ image download failed: {url} ({e})")
        return False


def yaml_escape(s: str) -> str:
    """YAML文字列に安全にする（シングルクォート使用）。"""
    if s is None:
        return ""
    s = str(s).replace("'", "''")
    return s


def strip_html_tags(s: str) -> str:
    """HTMLタグを除去してテキストだけにする。"""
    s = re.sub(r"<[^>]+>", "", s)
    s = unescape(s)
    return s.strip()


def convert_post_to_markdown(post: dict, image_extension_by_id: dict[int, str]) -> tuple[str, str]:
    """投稿データを Markdown 文字列に変換。(slug, markdown_content) を返す。"""
    slug = post["slug"]
    title = post["title"]["raw"] if isinstance(post["title"], dict) and "raw" in post["title"] else post["title"]["rendered"]
    title = unescape(title)

    excerpt_raw = post["excerpt"]["raw"] if isinstance(post["excerpt"], dict) and "raw" in post["excerpt"] else post["excerpt"]["rendered"]
    description = strip_html_tags(excerpt_raw)
    if not description:
        description = title

    pub_date = post["date"][:10]  # YYYY-MM-DD

    content = post["content"]["raw"] if isinstance(post["content"], dict) and "raw" in post["content"] else post["content"]["rendered"]

    # 先頭の <!-- メタ情報 --> + <style> ブロックを除去
    content = re.sub(
        r"<!--[^>]*?-->\s*<style>.*?</style>\s*",
        "",
        content,
        count=1,
        flags=re.DOTALL,
    )

    # heroImage パスを設定
    featured_id = post.get("featured_media", 0)
    hero_line = ""
    if featured_id and featured_id in image_extension_by_id:
        ext = image_extension_by_id[featured_id]
        hero_line = f"heroImage: '../../assets/blog/{slug}{ext}'\n"

    frontmatter = (
        "---\n"
        f"title: '{yaml_escape(title)}'\n"
        f"description: '{yaml_escape(description)}'\n"
        f"pubDate: '{pub_date}'\n"
        f"{hero_line}"
        "---\n\n"
        '<div class="article-content">\n\n'
        f"{content}\n\n"
        "</div>\n"
    )

    return slug, frontmatter


def main():
    print("=" * 60)
    print("re-money-lab WP→Astro 全記事一括移管")
    print("=" * 60)

    # 1. 全公開記事取得
    print("\n[1/4] 全公開記事を取得中…")
    posts = wp_get("/posts?status=publish&per_page=100&_fields=id,date,slug,title,excerpt,featured_media&context=edit")
    print(f"  → {len(posts)}件取得")

    # 2. content取得 + 画像メディア取得（並列ではなく順次）
    print("\n[2/4] 各記事の本文＋アイキャッチ情報を取得…")
    full_posts = []
    media_id_to_url = {}
    for i, p in enumerate(posts, 1):
        post_id = p["id"]
        slug = p["slug"]
        full = wp_get(f"/posts/{post_id}?context=edit")
        full_posts.append(full)
        if full.get("featured_media", 0) and full["featured_media"] not in media_id_to_url:
            try:
                media = wp_get(f"/media/{full['featured_media']}")
                media_id_to_url[full["featured_media"]] = media["source_url"]
            except Exception as e:
                print(f"  ⚠ post {post_id} ({slug}) media取得失敗: {e}")
        print(f"  [{i}/{len(posts)}] post-{post_id} {slug}")
        time.sleep(0.1)

    # 3. アイキャッチ画像ダウンロード
    print("\n[3/4] アイキャッチ画像をダウンロード…")
    image_extension_by_id = {}
    for p in full_posts:
        media_id = p.get("featured_media", 0)
        if not media_id or media_id not in media_id_to_url:
            continue
        slug = p["slug"]
        url = media_id_to_url[media_id]
        # 拡張子を取得
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or ".jpg"
        dest = ASSETS_DIR / f"{slug}{ext}"
        if download_image(url, dest):
            image_extension_by_id[media_id] = ext
            print(f"  ✓ {slug}{ext}")

    # 4. Markdown 変換＆保存
    print("\n[4/4] Markdown ファイルを生成…")
    for p in full_posts:
        slug, md = convert_post_to_markdown(p, image_extension_by_id)
        dest = BLOG_DIR / f"{slug}.md"
        dest.write_text(md, encoding="utf-8")
        print(f"  ✓ {slug}.md ({len(md):,} bytes)")

    print("\n" + "=" * 60)
    print(f"完了: {len(full_posts)} 記事を移植しました")
    print("=" * 60)


if __name__ == "__main__":
    main()
