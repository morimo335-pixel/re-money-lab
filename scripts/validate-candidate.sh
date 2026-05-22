#!/bin/bash
# Night Shift 候補リスト掲載前 5チェック自動検証スクリプト
# Usage:
#   ./validate-candidate.sh "<候補KW>" "<候補slugパターン>" "[A8案件IDパターン]"
#
# 例:
#   ./validate-candidate.sh "終活 何から" "shukatsu|shuukatsu" "4B1SPX+AV5TZU"
#   ./validate-candidate.sh "家族 反対 物 捨てる" "kazoku|hantai" ""
#
# 戻り値:
#   0 = 全5チェック合格（候補リスト掲載OK）
#   1 = 1つ以上NG（candidate掲載前に検討が必要）

set -uo pipefail

KW="${1:-}"
SLUG_PATTERN="${2:-}"
A8_ID_PATTERN="${3:-}"

if [ -z "$KW" ] || [ -z "$SLUG_PATTERN" ]; then
  echo "Usage: $0 \"<KW>\" \"<slug pattern>\" [A8 ID pattern]"
  exit 2
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
BLOG_DIR="$REPO_ROOT/src/content/blog"

if [ ! -d "$BLOG_DIR" ]; then
  echo "ERROR: blog directory not found: $BLOG_DIR"
  exit 2
fi

NG_COUNT=0

echo "🌙 Night Shift 候補リスト掲載前 5チェック"
echo "----------------------------------------"
echo "候補KW       : $KW"
echo "候補slug     : $SLUG_PATTERN"
echo "A8案件ID    : ${A8_ID_PATTERN:-（未指定）}"
echo "----------------------------------------"
echo ""

# ① slug 突合
echo "【①】 slug 突合"
SLUG_MATCH=$(ls "$BLOG_DIR" | grep -iE "$SLUG_PATTERN" 2>/dev/null || true)
if [ -z "$SLUG_MATCH" ]; then
  echo "  ✅ 既存slug 0件"
else
  echo "  🔴 既存slug HIT:"
  echo "$SLUG_MATCH" | sed 's/^/    /'
  NG_COUNT=$((NG_COUNT + 1))
fi
echo ""

# ② title/description 突合
echo "【②】 title/description 突合"
META_MATCH=$(cd "$BLOG_DIR" && grep -E "^title:|^description:" *.md 2>/dev/null | grep -iE "$KW" || true)
if [ -z "$META_MATCH" ]; then
  echo "  ✅ メタ突合 0件"
else
  echo "  🔴 メタ突合 HIT:"
  echo "$META_MATCH" | sed 's/^/    /' | head -10
  NG_COUNT=$((NG_COUNT + 1))
fi
echo ""

# ③ 本文部分言及度
echo "【③】 本文部分言及度"
BODY_MATCH=$(cd "$BLOG_DIR" && grep -lE "$KW" *.md 2>/dev/null || true)
if [ -z "$BODY_MATCH" ]; then
  echo "  ✅ 本文言及 0件"
else
  BODY_NG=0
  for f in $BODY_MATCH; do
    CNT=$(cd "$BLOG_DIR" && grep -c "$KW" "$f" 2>/dev/null || echo 0)
    if [ "$CNT" -le 3 ]; then
      echo "  🟡 $f: $CNT箇所 軽言及（OK）"
    else
      echo "  🔴 $f: $CNT箇所 メインテーマ被り懸念"
      BODY_NG=$((BODY_NG + 1))
    fi
  done
  if [ "$BODY_NG" -gt 0 ]; then
    NG_COUNT=$((NG_COUNT + 1))
  fi
fi
echo ""

# ④ A8案件の既存記事使用状況
echo "【④】 A8案件既存使用状況"
if [ -n "$A8_ID_PATTERN" ]; then
  A8_MATCH=$(cd "$BLOG_DIR" && grep -lE "a8mat=.*$A8_ID_PATTERN" *.md 2>/dev/null || true)
  if [ -z "$A8_MATCH" ]; then
    echo "  ✅ 同一A8案件未使用"
  else
    A8_COUNT=$(echo "$A8_MATCH" | wc -l | tr -d ' ')
    echo "  🟡 同一A8案件使用記事: ${A8_COUNT}本"
    echo "$A8_MATCH" | sed 's/^/    /' | head -5
    echo "    → 直近1-2記事と被ってないか⑤で確認"
  fi
else
  echo "  ⚠️ A8案件IDパターン未指定（要手動確認）"
fi
echo ""

# ⑤ 戦略的カニバルリスク評価（直近5本title表示）
echo "【⑤】 戦略的カニバルリスク評価"
echo "  直近5本のtitle："
cd "$BLOG_DIR" && ls -t *.md 2>/dev/null | head -5 | while read f; do
  T=$(grep "^title:" "$f" 2>/dev/null | head -1 | sed "s/^title: //; s/'//g; s/\"//g")
  echo "    - $f → $T"
done
echo "  ⚠️ 候補と直近1-2本の感情軸/解決策/A8が近すぎないか手動判断"
echo ""

echo "----------------------------------------"
if [ "$NG_COUNT" -eq 0 ]; then
  echo "🟢 5チェック合格（NG: 0 / ①②③④全パス）"
  echo "→ handoff.md 候補リストへの掲載 OK"
  echo "→ Phase 1 起動可能"
  exit 0
else
  echo "🔴 NG: $NG_COUNT 件"
  echo "→ 候補リスト掲載前に再検討必要"
  exit 1
fi
