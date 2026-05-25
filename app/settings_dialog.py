"""設定ダイアログ — Praatのパスやアップデート確認設定."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.praat_installer import is_praat_installed


class SettingsDialog(QDialog):
    """設定（Praatのパス、自動更新確認など）を編集するダイアログ."""

    def __init__(self, config: dict[str, Any], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("設定")
        self.setModal(True)
        self.setMinimumWidth(560)
        self._config = dict(config)

        layout = QVBoxLayout(self)

        form = QFormLayout()
        layout.addLayout(form)

        path_row = QHBoxLayout()
        self._path_edit = QLineEdit(self._config.get("praat_path", ""))
        browse = QPushButton("参照...")
        browse.clicked.connect(self._browse_path)
        path_row.addWidget(self._path_edit, 1)
        path_row.addWidget(browse)
        form.addRow("Praat 実行ファイル:", self._wrap_layout(path_row))

        self._version_label = QLabel(self._config.get("praat_version", "（未取得）"))
        form.addRow("Praat バージョン:", self._version_label)

        last_dir_row = QHBoxLayout()
        self._last_dir_edit = QLineEdit(self._config.get("last_directory", ""))
        last_browse = QPushButton("参照...")
        last_browse.clicked.connect(self._browse_last_dir)
        last_dir_row.addWidget(self._last_dir_edit, 1)
        last_dir_row.addWidget(last_browse)
        form.addRow("既定の作業フォルダ:", self._wrap_layout(last_dir_row))

        self._check_updates = QCheckBox("起動時にアップデートを確認する")
        self._check_updates.setChecked(bool(self._config.get("check_updates", True)))
        form.addRow("", self._check_updates)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def _wrap_layout(inner) -> QWidget:
        w = QWidget()
        w.setLayout(inner)
        return w

    def _browse_path(self) -> None:
        if sys.platform == "darwin":
            caption = "Praat.app を選択"
            filt = "アプリケーション (*.app);;すべてのファイル (*)"
            start = "/Applications"
        elif sys.platform.startswith("win"):
            caption = "Praat.exe を選択"
            filt = "実行ファイル (*.exe);;すべてのファイル (*)"
            start = "C:/Program Files"
        else:
            caption = "Praat 実行ファイルを選択"
            filt = "すべてのファイル (*)"
            start = str(Path.home())
        path, _ = QFileDialog.getOpenFileName(self, caption, start, filt)
        if not path:
            return
        selected = Path(path)
        if sys.platform == "darwin" and selected.suffix == ".app":
            inner = selected / "Contents" / "MacOS" / "Praat"
            if inner.exists():
                selected = inner
        self._path_edit.setText(str(selected))

    def _browse_last_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "既定の作業フォルダ", self._last_dir_edit.text() or str(Path.home()))
        if path:
            self._last_dir_edit.setText(path)

    def _on_accept(self) -> None:
        praat_path = self._path_edit.text().strip()
        if not is_praat_installed(praat_path):
            QMessageBox.warning(
                self,
                "無効なパス",
                "指定されたPraat実行ファイルが見つかりません。",
            )
            return
        self._config["praat_path"] = praat_path
        self._config["last_directory"] = self._last_dir_edit.text().strip()
        self._config["check_updates"] = self._check_updates.isChecked()
        self.accept()

    def get_config(self) -> dict[str, Any]:
        return dict(self._config)
