"""プラットフォーム依存ユーティリティ — 設定ファイルとパス解決."""
from __future__ import annotations

import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

APP_NAME = "PraatJa"

DEFAULT_CONFIG: dict[str, Any] = {
    "praat_path": "",
    "praat_version": "",
    "last_directory": "",
    "check_updates": True,
}


def get_app_data_dir() -> Path:
    """アプリ用データディレクトリを返す（無ければ作成する）."""
    system = sys.platform
    if system == "darwin":
        base = Path.home() / "Library" / "Application Support" / APP_NAME
    elif system.startswith("win"):
        appdata = os.environ.get("APPDATA")
        if appdata:
            base = Path(appdata) / APP_NAME
        else:
            base = Path.home() / "AppData" / "Roaming" / APP_NAME
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME")
        base = Path(xdg) / APP_NAME if xdg else Path.home() / ".config" / APP_NAME
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_config_path() -> Path:
    """config.json のフルパスを返す."""
    return get_app_data_dir() / "config.json"


def load_config() -> dict[str, Any]:
    """config.json を読み込む。無ければデフォルトを返す."""
    path = get_config_path()
    if not path.exists():
        return dict(DEFAULT_CONFIG)
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_CONFIG)
    merged = dict(DEFAULT_CONFIG)
    merged.update(data)
    return merged


def save_config(config: dict[str, Any]) -> None:
    """config.json を保存する."""
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_platform_key() -> str:
    """ダウンロードURL選択用のプラットフォームキーを返す."""
    if sys.platform == "darwin":
        return "darwin"
    if sys.platform.startswith("win"):
        machine = platform.machine().lower()
        if machine in ("arm64", "aarch64"):
            return "win32_arm64"
        return "win32_x64"
    return sys.platform


def resource_path(relative: str) -> Path:
    """PyInstaller同梱リソースの絶対パスを返す."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base / relative
