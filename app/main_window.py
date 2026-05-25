"""Praat 日本語版 メインウィンドウ."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Qt, QThread, QUrl, Signal
from PySide6.QtGui import QAction, QDesktopServices, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from app.platform_utils import save_config
from app.praat_installer import (
    PRAAT_VERSION_FALLBACK,
    check_for_updates,
    download_praat,
)
from app.runner import PraatRunError, run_script
from app.self_updater import check_self_update, get_current_version, get_download_page
from app.settings_dialog import SettingsDialog
from app.setup_dialog import DownloadWorker

SUPPORTED_AUDIO_EXTS = (".wav", ".mp3", ".aiff", ".aif", ".flac", ".ogg")

SCRIPTS: list[tuple[str, str, str]] = [
    ("音声を開く", "open_sound.praat", "選択ファイルを Praat の Objects ウィンドウに読み込みます"),
    ("波形を表示", "show_waveform.praat", "Sound を View & Edit で開きます"),
    ("スペクトログラム", "show_spectrogram.praat", "Spectrogram を生成して表示します"),
    ("ピッチ抽出", "show_pitch.praat", "Pitch を抽出して表示します"),
    ("フォルマント抽出", "show_formant.praat", "Formant を抽出して表示します"),
    ("TextGrid 作成", "create_textgrid.praat", "Sound と同名の TextGrid を新規作成します"),
    ("区間抽出", "extract_segment.praat", "指定区間（秒）の Sound を切り出して保存します"),
]


class UpdateCheckWorker(QObject):
    """別スレッドでアップデート確認を行うワーカー."""

    finished = Signal(bool, str)

    def __init__(self, current_version: str) -> None:
        super().__init__()
        self._current_version = current_version

    def run(self) -> None:
        has_update, version = check_for_updates(self._current_version)
        self.finished.emit(has_update, version)


class SelfUpdateWorker(QObject):
    """別スレッドでフロントエンド本体の新バージョン確認を行う."""

    finished = Signal(bool, str, str)

    def run(self) -> None:
        has, tag, url = check_self_update()
        self.finished.emit(has, tag, url)


class InstallWorker(QObject):
    """別スレッドでPraat再ダウンロードを行うワーカー."""

    progress = Signal(int, str)
    finished = Signal(str, str)
    failed = Signal(str)

    def run(self) -> None:
        try:
            path, version = download_praat(lambda p, m: self.progress.emit(p, m))
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(path, version)


class MainWindow(QMainWindow):
    """アプリのメインウィンドウ."""

    def __init__(self, praat_path: str, config: dict[str, Any]) -> None:
        super().__init__()
        self.setWindowTitle("非公式Praat日本語版 (Praat JA - Unofficial)")
        self.resize(900, 600)

        self._praat_path = praat_path
        self._config = config
        self._current_file: Path | None = None
        self._update_thread: QThread | None = None
        self._update_worker: UpdateCheckWorker | None = None
        self._install_thread: QThread | None = None
        self._install_worker: InstallWorker | None = None
        self._self_thread: QThread | None = None
        self._self_worker: SelfUpdateWorker | None = None

        self._build_ui()
        self._build_menu()
        self._build_statusbar()

        if config.get("check_updates", True):
            self._check_updates_async(silent=True)
            self._check_self_update_async(silent=True)

    # -------- UI 構築 --------
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)

        left = QVBoxLayout()
        left.addWidget(QLabel("読み込みファイル"))
        self._file_label = QLabel("（ファイル未選択）")
        self._file_label.setWordWrap(True)
        self._file_label.setStyleSheet("padding: 6px; border: 1px solid #ccc; background: #fafafa;")
        left.addWidget(self._file_label)

        open_btn = QPushButton("音声ファイルを開く...")
        open_btn.clicked.connect(self._on_open_file)
        left.addWidget(open_btn)

        left.addSpacing(12)
        left.addWidget(QLabel("実行可能なスクリプト"))

        self._script_list = QListWidget()
        for label, _name, desc in SCRIPTS:
            item = QListWidgetItem(label)
            item.setToolTip(desc)
            self._script_list.addItem(item)
        self._script_list.itemDoubleClicked.connect(lambda _i: self._on_run_script())
        left.addWidget(self._script_list, 1)

        run_btn = QPushButton("選択したスクリプトを実行")
        run_btn.clicked.connect(self._on_run_script)
        left.addWidget(run_btn)

        right = QVBoxLayout()
        right.addWidget(QLabel("スクリプトの説明"))
        self._desc_label = QLabel("左側からスクリプトを選択してください。")
        self._desc_label.setWordWrap(True)
        self._desc_label.setAlignment(Qt.AlignTop)
        self._desc_label.setStyleSheet("padding: 8px; border: 1px solid #ccc; background: #fafafa;")
        self._desc_label.setMinimumWidth(360)
        right.addWidget(self._desc_label, 1)

        self._script_list.currentRowChanged.connect(self._on_script_selected)

        root.addLayout(left, 1)
        root.addLayout(right, 1)

    def _build_menu(self) -> None:
        bar = self.menuBar()

        file_menu = bar.addMenu("ファイル(&F)")
        act_open = QAction("音声ファイルを開く...", self)
        act_open.setShortcut(QKeySequence.Open)
        act_open.triggered.connect(self._on_open_file)
        file_menu.addAction(act_open)
        file_menu.addSeparator()
        act_quit = QAction("終了", self)
        act_quit.setShortcut(QKeySequence.Quit)
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

        edit_menu = bar.addMenu("編集(&E)")
        act_settings = QAction("設定...", self)
        act_settings.triggered.connect(self._on_open_settings)
        edit_menu.addAction(act_settings)

        help_menu = bar.addMenu("ヘルプ(&H)")
        act_check = QAction("Praat のアップデートを確認", self)
        act_check.triggered.connect(lambda: self._check_updates_async(silent=False))
        help_menu.addAction(act_check)
        act_self_check = QAction("このアプリのアップデートを確認", self)
        act_self_check.triggered.connect(lambda: self._check_self_update_async(silent=False))
        help_menu.addAction(act_self_check)
        act_about_praat = QAction("Praatについて", self)
        act_about_praat.triggered.connect(self._on_about_praat)
        help_menu.addAction(act_about_praat)
        help_menu.addSeparator()
        act_about = QAction("このアプリについて", self)
        act_about.triggered.connect(self._on_about_app)
        help_menu.addAction(act_about)

    def _build_statusbar(self) -> None:
        sb = QStatusBar()
        self.setStatusBar(sb)
        sb.showMessage(f"Praat: {self._praat_path}")

    # -------- イベントハンドラ --------
    def _on_script_selected(self, row: int) -> None:
        if 0 <= row < len(SCRIPTS):
            self._desc_label.setText(SCRIPTS[row][2])

    def _on_open_file(self) -> None:
        start_dir = self._config.get("last_directory") or str(Path.home())
        exts = " ".join(f"*{e}" for e in SUPPORTED_AUDIO_EXTS)
        filt = f"音声ファイル ({exts});;すべてのファイル (*)"
        path, _ = QFileDialog.getOpenFileName(self, "音声ファイルを開く", start_dir, filt)
        if not path:
            return
        self._current_file = Path(path)
        self._file_label.setText(str(self._current_file))
        self._config["last_directory"] = str(self._current_file.parent)
        save_config(self._config)
        self.statusBar().showMessage(f"読み込み: {self._current_file.name}", 5000)

    def _on_run_script(self) -> None:
        row = self._script_list.currentRow()
        if row < 0:
            QMessageBox.information(self, "スクリプト未選択", "実行するスクリプトを選択してください。")
            return
        if self._current_file is None:
            QMessageBox.information(self, "ファイル未選択", "先に音声ファイルを開いてください。")
            return
        label, script_name, _desc = SCRIPTS[row]
        self.statusBar().showMessage(f"{label} を実行中...", 0)
        try:
            run_script(self._praat_path, script_name, [str(self._current_file)])
        except PraatRunError as exc:
            QMessageBox.critical(self, "実行エラー", str(exc))
            self.statusBar().showMessage("エラー", 5000)
            return
        self.statusBar().showMessage(f"{label} を実行しました", 5000)

    def _on_open_settings(self) -> None:
        dialog = SettingsDialog(self._config, self)
        if dialog.exec() != SettingsDialog.Accepted:
            return
        new_config = dialog.get_config()
        self._config.update(new_config)
        save_config(self._config)
        self._praat_path = self._config["praat_path"]
        self.statusBar().showMessage(f"Praat: {self._praat_path}", 5000)

    def _on_about_praat(self) -> None:
        installed = self._config.get("praat_version") or "(未取得)"
        QMessageBox.about(
            self,
            "Praatについて",
            (
                f"<h3>Praat</h3>"
                f"<p>インストール済みバージョン: <b>{installed}</b><br>"
                f"フォールバック定数: <b>{PRAAT_VERSION_FALLBACK}</b><br>"
                f"※ ダウンロード時は常に公式GitHubの<b>最新版</b>を取得します。</p>"
                f"<p>Praat は Paul Boersma・David Weenink（アムステルダム大学）が開発する"
                f"音声分析オープンソースソフトウェアで、GPL v3 ライセンスで配布されています。</p>"
                f"<p>公式サイト: <a href='https://praat.org'>https://praat.org</a><br>"
                f"GitHub: <a href='https://github.com/praat/praat.github.io'>"
                f"https://github.com/praat/praat.github.io</a><br>"
                f"ライセンス: <a href='https://www.gnu.org/licenses/gpl-3.0.html'>GPL v3</a></p>"
                f"<p>本アプリは Praat 本体を同梱しません。</p>"
            ),
        )

    def _on_about_app(self) -> None:
        QMessageBox.about(
            self,
            "このアプリについて",
            (
                "<h3>非公式Praat日本語版 (Praat JA - Unofficial)</h3>"
                "<p><b>非公式</b>の Japanese GUI frontend for Praat.</p>"
                "<p>ライセンス: MIT（フロントエンド本体）</p>"
                "<p style='color:#c8102e;'>本アプリは Praat の <b>非公式</b> 日本語フロントエンドです。"
                "Paul Boersma・David Weenink（アムステルダム大学）および公式 Praat プロジェクトとは"
                "<b>無関係</b>であり、公式の承認・推奨を受けたものではありません。</p>"
                "<p>Praat 本体は GPL v3 で配布されており、本アプリには <b>同梱されません</b>。"
                "初回起動時に公式GitHubから自動取得します。</p>"
                "<p>ソースコード: <a href='https://github.com/labphonlab/praat_ja'>"
                "https://github.com/labphonlab/praat_ja</a></p>"
            ),
        )

    # -------- アップデート確認 --------
    def _check_updates_async(self, *, silent: bool) -> None:
        if self._update_thread and self._update_thread.isRunning():
            return
        current = self._config.get("praat_version") or PRAAT_VERSION_FALLBACK
        self._update_thread = QThread(self)
        self._update_worker = UpdateCheckWorker(current)
        self._update_worker.moveToThread(self._update_thread)
        self._update_thread.started.connect(self._update_worker.run)
        self._update_worker.finished.connect(lambda has, ver: self._on_update_checked(has, ver, silent))
        self._update_worker.finished.connect(self._update_thread.quit)
        self._update_thread.finished.connect(self._update_worker.deleteLater)
        self._update_thread.start()

    def _on_update_checked(self, has_update: bool, version: str, silent: bool) -> None:
        if has_update and version:
            ret = QMessageBox.question(
                self,
                "アップデート",
                f"Praat v{version} が利用可能です。\nダウンロードしますか？",
                QMessageBox.Yes | QMessageBox.No,
            )
            if ret == QMessageBox.Yes:
                self._start_reinstall()
            return
        if not silent:
            QMessageBox.information(
                self,
                "アップデート",
                "新しいバージョンは見つかりませんでした。" if version else "アップデート情報を取得できませんでした。",
            )

    def _start_reinstall(self) -> None:
        if self._install_thread and self._install_thread.isRunning():
            return
        self.statusBar().showMessage("Praatをダウンロード中...", 0)
        self._install_thread = QThread(self)
        self._install_worker = InstallWorker()
        self._install_worker.moveToThread(self._install_thread)
        self._install_thread.started.connect(self._install_worker.run)
        self._install_worker.progress.connect(self._on_install_progress)
        self._install_worker.finished.connect(self._on_install_finished)
        self._install_worker.failed.connect(self._on_install_failed)
        self._install_worker.finished.connect(self._install_thread.quit)
        self._install_worker.failed.connect(self._install_thread.quit)
        self._install_thread.finished.connect(self._install_worker.deleteLater)
        self._install_thread.start()

    def _on_install_progress(self, pct: int, msg: str) -> None:
        self.statusBar().showMessage(f"{msg} ({pct}%)", 0)

    def _on_install_finished(self, path: str, version: str) -> None:
        self._praat_path = path
        self._config["praat_path"] = path
        self._config["praat_version"] = version
        save_config(self._config)
        self.statusBar().showMessage(f"Praat v{version} を更新しました: {path}", 5000)
        QMessageBox.information(self, "完了", f"Praat v{version} の更新が完了しました。")

    def _on_install_failed(self, error: str) -> None:
        self.statusBar().showMessage("ダウンロード失敗", 5000)
        QMessageBox.critical(self, "失敗", f"Praatの更新に失敗しました:\n\n{error}")

    # -------- フロントエンド本体のセルフアップデート確認 --------
    def _check_self_update_async(self, *, silent: bool) -> None:
        if self._self_thread and self._self_thread.isRunning():
            return
        self._self_thread = QThread(self)
        self._self_worker = SelfUpdateWorker()
        self._self_worker.moveToThread(self._self_thread)
        self._self_thread.started.connect(self._self_worker.run)
        self._self_worker.finished.connect(lambda has, tag, url: self._on_self_update(has, tag, url, silent))
        self._self_worker.finished.connect(self._self_thread.quit)
        self._self_thread.finished.connect(self._self_worker.deleteLater)
        self._self_thread.start()

    def _on_self_update(self, has_update: bool, tag: str, url: str, silent: bool) -> None:
        if has_update and tag:
            ret = QMessageBox.question(
                self,
                "アプリのアップデート",
                f"このアプリの新しいバージョン v{tag} が利用可能です。\n"
                f"現在のバージョン: v{get_current_version()}\n\n"
                f"ダウンロードページを開きますか？",
                QMessageBox.Yes | QMessageBox.No,
            )
            if ret == QMessageBox.Yes:
                target = url or get_download_page()
                QDesktopServices.openUrl(QUrl(target))
            return
        if not silent:
            QMessageBox.information(
                self,
                "アプリのアップデート",
                f"このアプリは最新です（v{get_current_version()}）。" if tag else
                "アップデート情報を取得できませんでした。",
            )
