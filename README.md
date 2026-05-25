# 非公式Praat日本語版 (Praat JA - Unofficial)

> ⚠️ **非公式プロジェクトです / UNOFFICIAL PROJECT**
> 本リポジトリは Praat の **非公式** 日本語GUIフロントエンドです。
> Paul Boersma・David Weenink（アムステルダム大学）および公式 Praat プロジェクトとは
> **無関係** であり、公式の承認・推奨を受けたものではありません。
>
> This is an **UNOFFICIAL** Japanese GUI frontend for Praat. It is NOT
> developed, endorsed, or sponsored by the official Praat project, Paul
> Boersma, David Weenink, or the University of Amsterdam.

---

Praat を日本語UIで気軽に操作できるデスクトップアプリです。
音声ファイルを読み込み、よく使うスクリプト（波形・スペクトログラム・ピッチ・フォルマント・TextGrid 作成など）を
ワンクリックで実行できます。

## 特長

- 日本語メニュー・日本語ダイアログ
- 初回起動時に Praat 本体を公式GitHubから自動ダウンロード（同梱しません）
- macOS（DMG）/ Windows（インストーラー）対応
- アップデート確認機能搭載

---

## ライセンスについて

| 対象 | ライセンス |
| --- | --- |
| 本プロジェクトのGUIコード（`app/`、`scripts/`、`build/` 等） | **MIT License**（[`LICENSE`](./LICENSE)） |
| Praat 本体 | **GPL v3+**（同梱せず、初回起動時に公式から取得） |

GPL v3 の全文を [`COPYING.GPL`](./COPYING.GPL) として参考同梱しています。

Praat 本体は Paul Boersma・David Weenink（アムステルダム大学）が開発した
オープンソースソフトウェアで、GPL v3 ライセンスで配布されています。
本アプリは Praat 本体を **同梱せず**、初回起動時に公式GitHubリポジトリ
(<https://github.com/praat/praat.github.io>) から自動的にダウンロードします。
ダウンロードされた Praat バイナリは GPL v3 のままユーザー環境に配置され、
本プロジェクトが再配布するものではありません。

- Praat: <https://praat.org>
- Praat GitHub: <https://github.com/praat/praat.github.io>
- Praat ライセンス: GPL v3

### 名称について

公式 Praat プロジェクトとの混同を避けるため、本アプリの正式名称は
「**非公式Praat日本語版 (Praat JA - Unofficial)**」とし、
画面・配布物・ドキュメントすべてに「非公式 / Unofficial」を明記しています。

### ソースコード

本プロジェクトのソースコードは <https://github.com/labphonlab/praat_ja>
で公開しています（MIT License）。Praat 本体のソースは
<https://github.com/praat/praat> をご参照ください。

---

## インストール

### エンドユーザー向け

ダウンロードサイト: <https://labphonlab.github.io/praat_ja/>

[Releases](https://github.com/labphonlab/praat_ja/releases) ページから
直接ダウンロードもできます。

- macOS: `非公式Praat日本語版.dmg`
- Windows: `PraatJa_Setup.exe`

### 開発者向け

```bash
cd praat_ja
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python main.py
```

---

## 初回起動フロー

1. アプリを起動すると「非公式Praat日本語版 — 初回セットアップ」ダイアログが表示されます。
2. 「自動ダウンロード（推奨）」を選ぶと、公式GitHubから Praat バイナリを取得して
   `~/Library/Application Support/PraatJa/praat/`（macOS）または
   `%APPDATA%\PraatJa\praat\`（Windows）に配置します。
3. 完了後、メインウィンドウが起動します。

「手動で指定」を選んだ場合、既にインストール済みの Praat 実行ファイルを選択できます。

---

## 使い方

1. メインウィンドウで「音声ファイルを開く...」をクリック
2. 右側のスクリプト一覧から実行したいものを選んで「選択したスクリプトを実行」

### 同梱スクリプト

| スクリプト         | 概要                                  |
| ------------------ | ------------------------------------- |
| 音声を開く         | ファイルを Objects ウィンドウへ読込    |
| 波形を表示         | View & Edit で波形表示                 |
| スペクトログラム   | Spectrogram を生成・描画               |
| ピッチ抽出         | Pitch を抽出・描画                     |
| フォルマント抽出   | Formant を抽出・描画                   |
| TextGrid 作成      | 同名 .TextGrid を作成して保存          |
| 区間抽出           | 指定区間の Sound を切り出して保存      |

---

## アップデート確認

メニュー「ヘルプ」→「アップデートを確認」で
[Praat Releases](https://github.com/praat/praat.github.io/releases) を確認し、
新バージョンがあればダウンロードを提案します。

---

## ビルド

### macOS

```bash
cd praat_ja
pip install -r requirements-dev.txt
pyinstaller build/praat_ja.spec --clean
brew install create-dmg
bash build/build_mac.sh
# → dist/非公式Praat日本語版.dmg
```

### Windows

```cmd
cd praat_ja
pip install -r requirements-dev.txt
pyinstaller build\praat_ja.spec --clean
choco install innosetup -y
build\build_win.bat
:: → dist\PraatJa_Setup.exe
```

### CI/CD

`git tag v1.0.0` をプッシュすると `.github/workflows/build.yml` が
macOS / Windows 両方のインストーラーをビルドし、自動的に Release を作成します。

---

## 設定ファイル

設定は以下のパスに `config.json` として保存されます。

- macOS: `~/Library/Application Support/PraatJa/config.json`
- Windows: `%APPDATA%\PraatJa\config.json`

```json
{
  "praat_path": "/Users/you/Library/Application Support/PraatJa/praat/Praat.app/Contents/MacOS/Praat",
  "praat_version": "6.4.65",
  "last_directory": "/Users/you/audio",
  "check_updates": true
}
```
