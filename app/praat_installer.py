"""Praat 本体の自動ダウンロード・インストール・バージョン管理.

ポリシー: ダウンロード時には必ず GitHub Releases API から最新タグを取得し、
そのタグに対応する URL を組み立てる。これにより、本アプリ側を更新せずとも
Praat の新リリースをユーザーが即座に取得できる。
ネットワーク取得に失敗した場合のみ、フォールバック定数 PRAAT_VERSION_FALLBACK
を使う。
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Callable

import requests

from app.platform_utils import get_app_data_dir, get_platform_key

# ----------------------------------------------------------------------
# フォールバック用バージョン定数（API が使えない時にだけ使う最低限の値）
# Praat の新リリースは API 経由で自動取得されるため、ここを更新しなくても
# 最新版が落ちる。これはあくまでオフライン/API障害時の保険。
# ----------------------------------------------------------------------
PRAAT_VERSION_FALLBACK = "6.4.67"
PRAAT_VERSION = PRAAT_VERSION_FALLBACK  # 後方互換のため公開

# 公式 Praat のリポジトリ。バイナリリリースはこちらに置かれている。
GITHUB_REPO = "praat/praat.github.io"
GITHUB_LATEST_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

# API レスポンスの簡易キャッシュ（プロセス内）。check と download で
# 同じバージョンを引き当てるために使う。
_latest_cache: dict[str, object] = {}

ProgressCallback = Callable[[int, str], None]


def _build_urls(version: str) -> dict[str, str]:
    """バージョン文字列からプラットフォーム別の公式ダウンロードURLを組み立てる."""
    compact = version.replace(".", "")
    base = f"https://github.com/{GITHUB_REPO}/releases/download/v{version}"
    return {
        "darwin": f"{base}/praat{compact}_mac.dmg",
        "win32_x64": f"{base}/praat{compact}_win-intel64.zip",
        "win32_arm64": f"{base}/praat{compact}_win-arm64.zip",
    }


# 後方互換: 旧コードが参照する DOWNLOAD_URLS は「フォールバック版URL」を返す
DOWNLOAD_URLS = _build_urls(PRAAT_VERSION_FALLBACK)


def get_praat_install_dir() -> Path:
    """Praat本体を管理するディレクトリを返す（無ければ作成する）."""
    install_dir = get_app_data_dir() / "praat"
    install_dir.mkdir(parents=True, exist_ok=True)
    return install_dir


def _praat_executable_name() -> str:
    if sys.platform == "darwin":
        return "Praat"
    if sys.platform.startswith("win"):
        return "Praat.exe"
    return "praat"


def get_default_praat_path() -> Path:
    """インストール先のPraat実行ファイル想定パスを返す."""
    install_dir = get_praat_install_dir()
    if sys.platform == "darwin":
        return install_dir / "Praat.app" / "Contents" / "MacOS" / "Praat"
    if sys.platform.startswith("win"):
        return install_dir / "Praat.exe"
    return install_dir / "praat"


def is_praat_installed(praat_path: str | os.PathLike[str]) -> bool:
    """指定パスにPraat実行ファイルが存在し実行可能か確認する."""
    if not praat_path:
        return False
    path = Path(praat_path)
    if not path.exists() or not path.is_file():
        return False
    if sys.platform != "win32" and not os.access(path, os.X_OK):
        return False
    return True


def get_latest_release_info(*, force_refresh: bool = False) -> dict[str, object] | None:
    """
    GitHub Releases API から最新リリース情報を取得する。
    プロセス内キャッシュを返すこともある。失敗時は None。
    """
    if not force_refresh and _latest_cache.get("data"):
        return _latest_cache["data"]  # type: ignore[return-value]
    try:
        response = requests.get(
            GITHUB_LATEST_API,
            headers={"Accept": "application/vnd.github+json"},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        _latest_cache["data"] = data
        return data
    except Exception:
        return None


def get_latest_praat_version(*, force_refresh: bool = False) -> str | None:
    """最新リリースのタグ（バージョン文字列）を返す。失敗時は None。"""
    info = get_latest_release_info(force_refresh=force_refresh)
    if not info:
        return None
    tag = str(info.get("tag_name", "")).lstrip("v").strip()
    return tag or None


def _resolve_download_url(version: str | None) -> tuple[str, str]:
    """
    バージョンが指定されていればそれを、無ければAPIで最新を引き、
    フォールバック定数で最後に保険を掛ける。
    戻り値: (使用バージョン, ダウンロードURL)
    """
    if version is None:
        version = get_latest_praat_version() or PRAAT_VERSION_FALLBACK
    urls = _build_urls(version)
    key = get_platform_key()
    if key not in urls:
        raise RuntimeError(f"このプラットフォームには対応していません: {key}")
    return version, urls[key]


def _download_file(
    url: str, dest: Path, progress_callback: ProgressCallback, base_pct: int, span_pct: int
) -> None:
    """URLからdestへチャンクダウンロード。base_pct〜base_pct+span_pctで進捗を通知する."""
    progress_callback(base_pct, f"ダウンロード開始: {url.rsplit('/', 1)[-1]}")
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()
        total = int(response.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 64 * 1024
        with dest.open("wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    pct = base_pct + int(span_pct * downloaded / total)
                    progress_callback(
                        min(pct, base_pct + span_pct),
                        f"ダウンロード中: {downloaded // (1024 * 1024)} / {total // (1024 * 1024)} MB",
                    )
                else:
                    progress_callback(base_pct, f"ダウンロード中: {downloaded // (1024 * 1024)} MB")


def _install_macos(dmg_path: Path, install_dir: Path, progress_callback: ProgressCallback) -> Path:
    """DMGをマウントしてPraat.appをinstall_dirへコピーする."""
    progress_callback(70, "DMGをマウントしています...")
    mount_point = Path(tempfile.mkdtemp(prefix="praatja_mount_"))
    try:
        subprocess.run(
            ["hdiutil", "attach", "-nobrowse", "-readonly", "-mountpoint", str(mount_point), str(dmg_path)],
            check=True,
            capture_output=True,
        )
        progress_callback(80, "Praat.app をコピーしています...")
        src_app = mount_point / "Praat.app"
        if not src_app.exists():
            candidates = list(mount_point.glob("*.app"))
            if not candidates:
                raise RuntimeError("DMG内にPraat.appが見つかりませんでした。")
            src_app = candidates[0]
        dst_app = install_dir / "Praat.app"
        if dst_app.exists():
            shutil.rmtree(dst_app)
        shutil.copytree(src_app, dst_app, symlinks=True)
    finally:
        subprocess.run(["hdiutil", "detach", str(mount_point), "-force"], capture_output=True)
        shutil.rmtree(mount_point, ignore_errors=True)

    exe = install_dir / "Praat.app" / "Contents" / "MacOS" / "Praat"
    if exe.exists():
        exe.chmod(0o755)
    return exe


def _install_windows(zip_path: Path, install_dir: Path, progress_callback: ProgressCallback) -> Path:
    """ZIPを展開し、Praat.exeのパスを返す."""
    progress_callback(80, "ZIPを展開しています...")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(install_dir)
    exe = install_dir / "Praat.exe"
    if not exe.exists():
        for found in install_dir.rglob("Praat.exe"):
            exe = found
            break
    if not exe.exists():
        raise RuntimeError("展開後にPraat.exeが見つかりませんでした。")
    return exe


def download_praat(
    progress_callback: ProgressCallback,
    *,
    version: str | None = None,
) -> tuple[str, str]:
    """
    Praatを公式GitHubから自動ダウンロードし、適切な場所に配置する。

    version=None（既定）の場合、GitHub Releases API で最新版を解決してから
    ダウンロードする。これにより本アプリを更新せずとも常に最新の Praat が
    取得できる。API失敗時のみフォールバック定数を使う。

    戻り値: (実行ファイルパス, 実際にインストールしたバージョン文字列)
    """
    install_dir = get_praat_install_dir()

    progress_callback(0, "最新版を確認しています...")
    resolved_version, url = _resolve_download_url(version)
    progress_callback(3, f"取得対象: Praat v{resolved_version}")

    with tempfile.TemporaryDirectory(prefix="praatja_dl_") as tmp:
        tmp_path = Path(tmp)
        filename = url.rsplit("/", 1)[-1]
        archive = tmp_path / filename
        _download_file(url, archive, progress_callback, base_pct=5, span_pct=60)

        if sys.platform == "darwin":
            exe = _install_macos(archive, install_dir, progress_callback)
        elif sys.platform.startswith("win"):
            exe = _install_windows(archive, install_dir, progress_callback)
        else:
            raise RuntimeError(f"未対応のプラットフォームです: {sys.platform}")

    progress_callback(100, f"インストール完了 (v{resolved_version})")
    return str(exe), resolved_version


def check_for_updates(current_version: str | None = None) -> tuple[bool, str]:
    """
    GitHub のlatestリリースを確認し、新バージョンがあれば(True, バージョン)を返す。
    current_version を渡すとそれと比較する（既定: フォールバック定数）。
    ネットワークエラー時は (False, "")。
    """
    base = current_version or PRAAT_VERSION_FALLBACK
    latest = get_latest_praat_version(force_refresh=True)
    if not latest:
        return False, ""
    if _version_tuple(latest) > _version_tuple(base):
        return True, latest
    return False, latest


def _version_tuple(v: str) -> tuple[int, ...]:
    parts = []
    for chunk in v.split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)
