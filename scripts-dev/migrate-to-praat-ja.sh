#!/usr/bin/env bash
# migrate-to-praat-ja.sh
#
# 現在の praat_open リポジトリの praat_ja/ サブディレクトリ配下を、
# 新リポジトリ labphonlab/praat_ja のルートとしてプッシュするための
# 移行ヘルパー。
#
# 前提:
#   - GitHub 側で空の labphonlab/praat_ja リポジトリを作成済みであること
#   - gh CLI または手動で remote URL が判明していること
#
# 使い方:
#   cd <praat_open repo>
#   bash praat_ja/scripts-dev/migrate-to-praat-ja.sh \
#       /tmp/praat_ja-staging \
#       git@github.com:labphonlab/praat_ja.git
#
# 動作:
#   1. STAGING_DIR を作り、praat_ja/* + docs/ + .github/ + LICENSE + COPYING.GPL を
#      フラット構造でコピー
#   2. STAGING_DIR で git init し、空の new repo として初期化
#   3. 指定の remote を追加し、main ブランチをプッシュ
#
# プッシュ後、GitHub Settings → Pages で
# Source: Deploy from a branch / Branch: main / Folder: /docs に設定すれば
# https://labphonlab.github.io/praat_ja/ が有効になる。

set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "使い方: $0 <staging directory> [<remote URL>]" >&2
    echo "例:     $0 /tmp/praat_ja-staging git@github.com:labphonlab/praat_ja.git" >&2
    exit 1
fi

STAGING_DIR="$1"
REMOTE_URL="${2:-}"

REPO_ROOT="$(git rev-parse --show-toplevel)"
SRC="$REPO_ROOT/praat_ja"

if [ ! -d "$SRC" ]; then
    echo "エラー: $SRC が見つかりません。praat_open リポジトリのルートから実行してください。" >&2
    exit 1
fi

if [ -e "$STAGING_DIR" ]; then
    echo "エラー: $STAGING_DIR は既に存在します。空のパスを指定してください。" >&2
    exit 1
fi

echo "==> ステージングディレクトリを作成: $STAGING_DIR"
mkdir -p "$STAGING_DIR"

echo "==> praat_ja/ の中身をフラットコピー"
# ドットファイル含めてコピー
cp -a "$SRC"/. "$STAGING_DIR"/

echo "==> docs/ をコピー"
cp -a "$REPO_ROOT/docs" "$STAGING_DIR/docs"

echo "==> .github/ をコピー"
mkdir -p "$STAGING_DIR/.github"
cp -a "$REPO_ROOT/.github/workflows" "$STAGING_DIR/.github/workflows"

cd "$STAGING_DIR"

echo "==> 新しい git リポジトリを初期化"
git init -b main
git add -A
git commit -m "Initial commit — non-affiliated Japanese frontend for Praat

非公式Praat日本語版 (Praat JA - Unofficial)
Imported from labphonlab/praat_open praat_ja/ subdirectory.
"

if [ -n "$REMOTE_URL" ]; then
    echo "==> remote 'origin' を追加: $REMOTE_URL"
    git remote add origin "$REMOTE_URL"
    echo "==> プッシュ準備完了。次のコマンドを実行してください:"
    echo "       cd $STAGING_DIR && git push -u origin main"
else
    echo "==> remote URL が指定されなかったため、ローカルリポジトリの作成のみで終了します。"
    echo "    後で次のように push してください:"
    echo "       cd $STAGING_DIR"
    echo "       git remote add origin git@github.com:labphonlab/praat_ja.git"
    echo "       git push -u origin main"
fi

echo ""
echo "==> 完了。次の手順:"
echo "  1) GitHub 上で空の labphonlab/praat_ja リポジトリを作成"
echo "  2) $STAGING_DIR から main を push"
echo "  3) Settings → Pages で Source=main / Folder=/docs を設定"
echo "  4) Settings → Actions → General で Workflow permissions を 'Read and write' に"
echo "  5) watch-praat ワークフローが自動的に最初のタグ v1.0.0 を作成"
echo "  6) build ワークフローが DMG / EXE を成果物として Release に公開"
echo "  7) https://labphonlab.github.io/praat_ja/ が稼働開始"
