# 移行手順 — labphonlab/praat_ja への切り出し

本プロジェクトは現在 `labphonlab/praat_open` リポジトリの `praat_ja/`
サブディレクトリで開発しています。最終的には独立したリポジトリ
**`labphonlab/praat_ja`** として配布し、ダウンロードサイトを
**<https://labphonlab.github.io/praat_ja/>** で公開する計画です。

## 移行のゴール

- 新リポジトリ `labphonlab/praat_ja` の **ルートに** 本プロジェクトを置く
  （現在の `praat_ja/` ディレクトリ階層を1段持ち上げる）
- `docs/` と `.github/workflows/` も新リポジトリのルートへ
- GitHub Pages を新リポジトリの `/docs` から配信
  → URL: `https://labphonlab.github.io/praat_ja/`

## 1. 新リポジトリを作る

GitHub Web UI で次の設定で空リポジトリを作成:

- Owner: `labphonlab`
- Name: `praat_ja`
- Visibility: Public
- **README/.gitignore/LICENSE は追加しない** (空のまま)

## 2. 移行スクリプトを実行

`praat_open` リポジトリのルートで:

```bash
bash praat_ja/scripts-dev/migrate-to-praat-ja.sh \
    /tmp/praat_ja-staging \
    git@github.com:labphonlab/praat_ja.git

cd /tmp/praat_ja-staging
git push -u origin main
```

スクリプトの動作:

1. `/tmp/praat_ja-staging/` を作成
2. `praat_ja/*` の中身をそのまま **フラットコピー** （ネストなし）
3. `docs/` をコピー
4. `.github/workflows/` をコピー
5. `git init` して初期コミット作成
6. `origin` を設定 (URL を渡した場合)

## 3. GitHub 側の設定

新リポジトリの **Settings** で以下を設定:

### Pages
- Source: **Deploy from a branch**
- Branch: **`main`**
- Folder: **`/docs`**

数分後、<https://labphonlab.github.io/praat_ja/> が稼働します。

### Actions → General
- **Workflow permissions** を **Read and write** に設定
  （`watch-praat.yml` が自動でタグを push できるようにするため）

## 4. 初回リリースの自動生成

設定が終わると、次回の `watch-praat.yml` の cron 起動（6時間ごと）で
初回タグ `v1.0.0` が自動作成されます。すぐ試したい場合:

1. リポジトリの **Actions** タブを開く
2. "Watch Praat upstream & auto-release" ワークフローを選択
3. "Run workflow" をクリック

これで `v1.0.0` タグが push され、`build.yml` が連鎖して
DMG (`非公式Praat日本語版.dmg`) と Windows インストーラー
(`PraatJa_Setup.exe`) を Release に公開します。

ダウンロードサイトの「macOS版をダウンロード」「Windows版をダウンロード」
ボタンは GitHub Releases API を介して自動的に最新の成果物にリンクされます。

## 5. 旧 praat_open リポジトリの扱い

`labphonlab/praat_open` には旧来の CLI 版 `praat_open` シェルスクリプトが
残ります。GUI プロジェクトは新リポジトリへ移行したことを README に追記し、
`praat_ja/` ディレクトリは削除するか、リンクのみ残してください。

## ワークフローの構造非依存性

`build.yml` と `watch-praat.yml` は両方の構成
（praat_ja サブディレクトリ / フラットルート）で動作するように、
`main.py` と `app/` の有無で自動判別します。そのため移行前後どちらで
実行してもエラーになりません。
