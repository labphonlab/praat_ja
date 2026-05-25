"""Praat 日本語版 GUI フロントエンド — エントリーポイント."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from app.main_window import MainWindow
from app.platform_utils import get_config_path, load_config, save_config
from app.praat_installer import is_praat_installed
from app.setup_dialog import SetupDialog


def _asset_path(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base / "assets" / name


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("非公式Praat日本語版")
    app.setApplicationDisplayName("非公式Praat日本語版 (Praat JA - Unofficial)")
    app.setOrganizationName("PraatJa")

    icon_path = _asset_path("icon.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    config = load_config()
    praat_path = config.get("praat_path", "")

    if not praat_path or not is_praat_installed(praat_path):
        dialog = SetupDialog()
        if dialog.exec() != SetupDialog.Accepted:
            QMessageBox.information(
                None,
                "セットアップ未完了",
                "Praatのセットアップが完了していないためアプリを終了します。",
            )
            return 1
        praat_path = dialog.praat_path
        config["praat_path"] = praat_path
        if dialog.praat_version:
            config["praat_version"] = dialog.praat_version
        save_config(config)

    window = MainWindow(praat_path=praat_path, config=config)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
