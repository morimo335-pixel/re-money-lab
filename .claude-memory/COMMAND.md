# 🔁 リモート命令（スマホ→PC実行）

## TIMESTAMP: 2026-05-26 14:30:00
## STATUS: idle
## COMMAND:

（ここに命令文を書いて STATUS を「pending」に変更してpushすると、PCが5分以内に検知して実行します）

---

## 📝 使い方

1. スマホのClaude.ai App or GitHub Web で本ファイル `.claude-memory/COMMAND.md` を編集
2. `## COMMAND:` の下に命令文を書く
3. `## STATUS: idle` を `## STATUS: pending` に変更
4. `## TIMESTAMP:` を現在時刻に更新
5. コミット＆push
6. **5分以内**にPC側 launchd watcher が検知→Claude Code経由で実行→結果を `RESULT.md` に書き戻し→push
7. スマホで `RESULT.md` を確認

## 🚨 制限

- 致命傷リスク作業（公開・課金・大量削除）はwatcher側で警告して止まる
- 致命傷リスクOKなら命令文に「強制実行OK」と明記
- 1回1命令（STATUS=processing中は次の命令を受け付けない）

## 🎯 命令例

- 「記事46のメタディスクリプションを以下に書き換えて push：[新メタデ]」
- 「a8-list-partnered.sh を今すぐ実行して結果報告して」
- 「handoff.md冒頭に明日の候補3本があるか確認して、無ければNight Shiftを今すぐ手動実行」
