"""初回起動時のPraatセットアップウィザード."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from app.praat_installer import (
    PRAAT_VERSION_FALLBACK,
    download_praat,
    get_latest_praat_version,
    is_praat_installed,
)


class DownloadWorker(QObject):
    """別スレッドでPraatダウンロード処理を実行する."""

    progress = Signal(int, str)
    finished = Signal(str, str)
    failed = Signal(str)

    def run(self) -> None:
        try:
            path, version = download_praat(lambda pct, msg: self.progress.emit(pct, msg))
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(path, version)


class SetupDialog(QDialog):
    """
    初回起動時のPraatセットアップウィザード。
    QProgressBarでダウンロード進捗を表示し、QThreadでUIをブロックせずに処理する。
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("非公式Praat日本語版 (Praat JA - Unofficial) — 初回セットアップ")
        self.setModal(True)
        self.setMinimumWidth(520)
        self.praat_path: str = ""
        self.praat_version: str = ""

        self._thread: QThread | None = None
        self._worker: DownloadWorker | None = None

        self._stack = QStackedLayout()
        self._stack.addWidget(self._build_choice_page())
        self._stack.addWidget(self._build_progress_page())

        root = QVBoxLayout(self)
        root.addLayout(self._stack)

    def _build_choice_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("非公式Praat日本語版 — 初回セットアップ")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel(
            "※ 本アプリは Praat の <b>非公式</b> 日本語フロントエンドです。"
            "公式プロジェクト（Paul Boersma 他, アムステルダム大学）とは無関係です。"
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #6a6a6a; font-size: 11px;")
        layout.addWidget(subtitle)

        msg = QLabel(
            "Praat本体（GPL v3, 公式バイナリ）が見つかりませんでした。\n"
            "どちらかの方法でセットアップしてください。"
        )
        msg.setWordWrap(True)
        layout.addWidget(msg)

        layout.addSpacing(12)

        auto_btn = QPushButton(
            "自動ダウンロード（推奨）\n公式GitHubから最新版を取得します"
        )
        auto_btn.setMinimumHeight(64)
        auto_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        auto_btn.clicked.connect(self._start_download)
        layout.addWidget(auto_btn)

        manual_btn = QPushButton("手動で指定\nインストール済みのPraat実行ファイルを選択します")
        manual_btn.setMinimumHeight(64)
        manual_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        manual_btn.clicked.connect(self._select_manual)
        layout.addWidget(manual_btn)

        layout.addStretch(1)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        cancel = QPushButton("キャンセル")
        cancel.clicked.connect(self.reject)
        button_row.addWidget(cancel)
        layout.addLayout(button_row)

        return page

    def _build_progress_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Praat をダウンロードしています...")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        self._progress_label = QLabel("準備中...")
        self._progress_label.setWordWrap(True)
        layout.addWidget(self._progress_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        layout.addWidget(self._progress_bar)

        layout.addStretch(1)

        self._cancel_btn = QPushButton("キャンセル")
        self._cancel_btn.clicked.connect(self._cancel_download)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self._cancel_btn)
        layout.addLayout(row)

        return page

    def _start_download(self) -> None:
        self._stack.setCurrentIndex(1)
        self._thread = QThread(self)
        self._worker = DownloadWorker()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.start()

    def _on_progress(self, pct: int, message: str) -> None:
        self._progress_bar.setValue(pct)
        self._progress_label.setText(message)

    def _on_finished(self, path: str, version: str) -> None:
        self.praat_path = path
        self.praat_version = version
        QMessageBox.information(
            self,
            "セットアップ完了",
            f"Praat v{version} のインストールが完了しました。\n\nパス: {path}",
        )
        self.accept()

    def _on_failed(self, error: str) -> None:
        QMessageBox.critical(
            self,
            "ダウンロード失敗",
            f"Praatのダウンロードに失敗しました。\n\n{error}\n\n"
            "ネットワーク接続を確認するか、「手動で指定」をお試しください。",
        )
        self._stack.setCurrentIndex(0)

    def _cancel_download(self) -> None:
        if self._thread and self._thread.isRunning():
            self._thread.requestInterruption()
            self._thread.quit()
            self._thread.wait(2000)
        self.reject()

    def _select_manual(self) -> None:
        if sys.platform == "darwin":
            caption = "Praat.app を選択"
            filt = "アプリケーション (*.app);;すべてのファイル (*)"
            start_dir = "/Applications"
        elif sys.platform.startswith("win"):
            caption = "Praat.exe を選択"
            filt = "実行ファイル (*.exe);;すべてのファイル (*)"
            start_dir = "C:/Program Files"
        else:
            caption = "Praat実行ファイルを選択"
            filt = "すべてのファイル (*)"
            start_dir = str(Path.home())

        path, _ = QFileDialog.getOpenFileName(self, caption, start_dir, filt)
        if not path:
            return

        selected = Path(path)
        if sys.platform == "darwin" and selected.suffix == ".app":
            exe = selected / "Contents" / "MacOS" / "Praat"
            if exe.exists():
                selected = exe

        if not is_praat_installed(str(selected)):
            QMessageBox.warning(
                self,
                "無効なパス",
                "選択されたファイルはPraat実行ファイルとして認識できません。",
            )
            return

        self.praat_path = str(selected)
        self.accept()
