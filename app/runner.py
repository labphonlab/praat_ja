"""Praatスクリプトをサブプロセスとして起動するランナー."""
from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from app.platform_utils import resource_path


class PraatRunError(RuntimeError):
    """Praat実行に失敗したことを示す例外."""


def get_script_path(script_name: str) -> Path:
    """同梱scripts/<name>の絶対パスを返す."""
    path = resource_path(f"scripts/{script_name}")
    if not path.exists():
        raise PraatRunError(f"スクリプトが見つかりません: {script_name}")
    return path


def run_script(
    praat_path: str,
    script_name: str,
    args: Sequence[str] = (),
    *,
    send: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """
    Praat にスクリプトを渡して実行する。
    send=True なら --send（GUI操作可能・既存インスタンスに送る）、False なら --run。
    """
    if not praat_path:
        raise PraatRunError("Praatのパスが設定されていません。")
    if not Path(praat_path).exists():
        raise PraatRunError(f"Praat実行ファイルが存在しません: {praat_path}")

    script_path = get_script_path(script_name)
    mode_flag = "--send" if send else "--run"
    cmd = [str(praat_path), mode_flag, str(script_path), *[str(a) for a in args]]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise PraatRunError(f"Praatを起動できませんでした: {exc}") from exc
    except subprocess.TimeoutExpired as exc:
        raise PraatRunError("Praatの実行がタイムアウトしました。") from exc

    if result.returncode != 0:
        msg = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
        raise PraatRunError(f"Praatがエラー終了しました: {msg}")
    return result


def quote_command(cmd: Sequence[str]) -> str:
    """デバッグ表示用にコマンドを安全にクォートする."""
    if sys.platform.startswith("win"):
        return subprocess.list2cmdline(list(cmd))
    return " ".join(shlex.quote(c) for c in cmd)
