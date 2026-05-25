# docs/ — 非公式Praat日本語版 配布サイト

GitHub Pages で **<https://labphonlab.github.io/praat_ja/>** として公開する静的サイトです。

## 公開方法

`labphonlab/praat_ja` リポジトリで:

1. **Settings → Pages**
2. **Source**: Deploy from a branch
3. **Branch**: `main`, Folder: `/docs`
4. 数分後に <https://labphonlab.github.io/praat_ja/> で公開

## ファイル構成

```
docs/
├── index.html       ← ブラウザ言語で /ja/ か /en/ に自動振り分け
├── ja/index.html    ← 日本語ページ
├── en/index.html    ← 英語ページ
├── style.css        ← 共通スタイル
└── app.js           ← GitHub Releases API から最新版取得、OS判定、言語切替
```

## 動作

- `/` にアクセスするとブラウザ言語に応じて `/ja/` または `/en/` にリダイレクト
  （`localStorage` に選択を記録）
- 各ページのヘッダー右側に言語スイッチャー（日本語 / English）
- GitHub Releases API で最新の `.dmg` / `.exe` URL とファイルサイズを取得
- Praat 本体の最新版バージョンも公式リポジトリから取得して表示
- ユーザーの OS を自動判定し、該当カードをハイライト + ヒーローの主ボタンを直リンクに
