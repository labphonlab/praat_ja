"""フロントエンド自身の自動アップデート確認.

GitHub Releases (labphonlab/praat_ja) を起動時に確認し、現行バージョンより
新しいタグがあれば、ユーザーへ通知してダウンロードページを開く。
PyInstaller配布バイナリ用なので、ファイルの自動置換までは行わず、
ユーザーに新インストーラーを案内する設計（権限・コード署名の問題を避ける）。
"""
from __future__ import annotations

from typing import Optional

import requests

from app import __version__ as FRONTEND_VERSION

GITHUB_REPO = "labphonlab/praat_ja"
GITHUB_LATEST_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
DOWNLOAD_PAGE = "https://labphonlab.github.io/praat_ja/"


def get_current_version() -> str:
    return FRONTEND_VERSION


def check_self_update() -> tuple[bool, str, str]:
    """
    フロントエンド本体の新バージョンが GitHub Releases に存在するか確認する。
    戻り値: (新しいバージョンがあるか, 最新タグ, リリースHTML URL)
    ネットワーク失敗時は (False, "", "")。
    """
    try:
        response = requests.get(
            GITHUB_LATEST_API,
            headers={"Accept": "application/vnd.github+json"},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except Exception:
        return False, "", ""

    tag = str(data.get("tag_name", "")).lstrip("v").strip()
    html_url = str(data.get("html_url", ""))
    if not tag:
        return False, "", html_url
    if _version_tuple(tag) > _version_tuple(FRONTEND_VERSION):
        return True, tag, html_url
    return False, tag, html_url


def get_download_page() -> str:
    return DOWNLOAD_PAGE


def _version_tuple(v: str) -> tuple[int, ...]:
    parts = []
    for chunk in v.split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)
