# 🤖 Claude セッション間 ナレッジ同期フォルダ

このフォルダは **PC側ローカル Claude Code** と **Claude.com/Code（クラウド版）** および **スマホ Claude.ai アプリ** の間で、re-money-lab.com の運用状況・ルール・ペルソナを共有するための同期領域です。

## 📚 ファイル一覧

| ファイル | 内容 |
|---|---|
| `project_remoney_handoff.md` | 最新セッション進捗・残タスク・次の記事候補 |
| `project_remoney_article_workflow.md` | 新記事執筆のステップ0〜10コアフロー |
| `project_remoney_writing_rules.md` | 装飾・型・H2並び順・禁止事項の詳細ルール集 |
| `feedback_eyecatch_format.md` | アイキャッチ「右側フォーマット」の完全仕様 |
| `feedback_article_principles.md` | 読者貢献最優先・捏造禁止・他大原則 |

## 🔄 更新タイミング

PC側 Claude Code（ローカル）が記事公開後・Phase 6最後に下記スクリプト実行で自動同期：

```bash
~/Library/Scripts/sync-mobile-gist.sh
```

このスクリプトが以下を実行：
1. ローカル memory → `.claude-memory/` フォルダにコピー
2. スマホ用 Gist にも同期（Gist ID: d9748ddcd020705289cfb3f908e70aff）
3. git commit + push（このフォルダも含む）

## 📱 各環境からの読み方

### PC側 Claude Code（このリポをローカルclone）
- `~/.claude/projects/.../memory/` の元データを使う（このフォルダはバックアップ＆同期源）

### Claude.com/Code（クラウド版）
- repository を自動で git clone するので、このフォルダの 5 ファイルを最初に読み込み、現状把握してください

### スマホ Claude.ai アプリ
- Gist URL（プロジェクトのカスタム指示で固定）から fetch
- Gist: https://gist.github.com/morimo335-pixel/d9748ddcd020705289cfb3f908e70aff

## ⚠️ Cloud Claude / スマホ Claude が動く時の必読事項

1. **「あとよろしく」「OK」は公開GOではない** — 明示的に「公開して」と言われるまで `git push` 禁止
2. **業界人エピソードは Satoshi 実体験のみ** — 捏造絶対禁止（2026-05-22 重大事案）
3. **「実家2巡目」等の内部設計用語は本文に流出させない**
4. **A8バナーと「あわせて読みたい」は絶対に隣接させない**
5. **結論ボックスは「💡 解決策（結論）」型で読者の悩み解決方法2-3個に絞る**

詳細は `feedback_article_principles.md` 冒頭の「重大事案」セクション参照。
