#!/usr/bin/env bash
# build_mac.sh — macOS用 .app から DMG を作成する
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
APP_PATH="$PROJECT_ROOT/dist/非公式Praat日本語版.app"
DMG_PATH="$PROJECT_ROOT/dist/非公式Praat日本語版.dmg"
VOLNAME="非公式Praat日本語版"

if [ ! -d "$APP_PATH" ]; then
    echo "エラー: $APP_PATH が見つかりません。pyinstaller を先に実行してください。" >&2
    exit 1
fi

rm -f "$DMG_PATH"

if ! command -v create-dmg >/dev/null 2>&1; then
    echo "エラー: create-dmg がインストールされていません。'brew install create-dmg' を実行してください。" >&2
    exit 1
fi

create-dmg \
    --volname "$VOLNAME" \
    --window-pos 200 120 \
    --window-size 600 360 \
    --icon-size 100 \
    --icon "非公式Praat日本語版.app" 150 180 \
    --hide-extension "非公式Praat日本語版.app" \
    --app-drop-link 450 180 \
    --no-internet-enable \
    "$DMG_PATH" \
    "$APP_PATH"

echo "DMG を作成しました: $DMG_PATH"
