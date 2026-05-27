# 🔒 re-money-lab.com 装飾正規テンプレ（2026-05-27 Satoshi確定）

明日からの全記事で**ここのテンプレ以外のmybest風カード・プロフィール②装飾は禁止**。
独自装飾を1ミリでも入れた瞬間に再発事案扱い。

## ファイル一覧
- `mybest-card.html` — A8 mybest風カード（border:2px solid #1E3A5F・ネイビーグラデ帯・ul・黄リボン・緑グラデCTA・公式リンク・A8ピクセル）
- `profile-card-bottom.html` — 筆者プロフィール②記事末カード（横並び・flex:1;min-width:200px;必須）

## 使い方（新記事執筆時）

```bash
# 直近1記事を複製してから書き始める（コピー元はSatoshiが指定した最新成功記事）
cp src/content/blog/oya-shisetsu-nyuuyo-checklist.md src/content/blog/[NEW_SLUG].md

# frontmatter / H2 / 本文 / プレースホルダー を書き換える
# 装飾HTMLは絶対に新規書きしない・templates/ を貼り付けてプレースホルダー差替のみ
```

## 集客記事の3点A8 CTA配置（2026-05-27 Satoshi確定）

| 配置 | カード | バリエーション |
|---|---|---|
| 冒頭（リード結論BOX後） | mybest-card.html | HEADER「〇〇でお困りの方へ」LEAD「物件種別訴求」 |
| 中盤（山場H2末尾） | mybest-card.html | HEADER「〇〇でお困りの方へ」LEAD「手間ゼロ訴求」 |
| 末尾（まとめ後） | mybest-card.html | HEADER「最後の一押し」LEAD「最終後押し」 |

**3点ともmybest-card.htmlで完全同型**。冒頭・中盤・末尾でフォーマット違いは厳禁。

## チェック（公開前必須）

```bash
~/Library/Scripts/article-quality-check.sh src/content/blog/[NEW_SLUG].md
# 全項目クリア + テンプレからの逸脱なし を確認してから push
```
