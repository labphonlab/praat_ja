# PyInstaller spec — 非公式Praat日本語版 (Praat JA - Unofficial)
# 使い方: pyinstaller build/praat_ja.spec --clean

import sys
from pathlib import Path

block_cipher = None

SPEC_DIR = Path(SPECPATH).resolve()
PROJECT_ROOT = SPEC_DIR.parent

is_mac = sys.platform == "darwin"
is_win = sys.platform.startswith("win")

# 必須でないファイルは存在チェックを通して datas に入れる。
# CI 上でアイコンや LICENSE がまだ無くてもビルドが落ちないようにする。
datas = [
    (str(PROJECT_ROOT / "scripts"), "scripts"),
]
_assets_dir = PROJECT_ROOT / "assets"
if _assets_dir.exists():
    datas.append((str(_assets_dir), "assets"))

for _extra in ("LICENSE", "COPYING.GPL", "README.md"):
    _p = PROJECT_ROOT / _extra
    if _p.exists():
        datas.append((str(_p), "."))

a = Analysis(
    [str(PROJECT_ROOT / "main.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# アイコンは存在する場合のみ指定する。無ければ None を渡して OS デフォルトに任せる。
def _icon_or_none(filename: str):
    p = PROJECT_ROOT / "assets" / filename
    return str(p) if p.exists() else None

if is_mac:
    icon_path = _icon_or_none("icon.icns")
elif is_win:
    icon_path = _icon_or_none("icon.ico")
else:
    icon_path = None

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PraatJa",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="PraatJa",
)

if is_mac:
    _bundle_kwargs = dict(
        name="非公式Praat日本語版.app",
        bundle_identifier="org.labphonlab.praatja.unofficial",
        info_plist={
            "CFBundleShortVersionString": "1.0.0",
            "CFBundleVersion": "1.0.0",
            "CFBundleName": "非公式Praat日本語版",
            "CFBundleDisplayName": "非公式Praat日本語版 (Praat JA - Unofficial)",
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "11.0",
            "NSHumanReadableCopyright": (
                "Unofficial Japanese GUI frontend for Praat. "
                "Not affiliated with the official Praat project."
            ),
        },
    )
    if icon_path:
        _bundle_kwargs["icon"] = icon_path
    app = BUNDLE(coll, **_bundle_kwargs)
