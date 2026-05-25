# PyInstaller spec — Praat 日本語版 GUI フロントエンド
# 使い方: pyinstaller build/praat_ja.spec --clean

import sys
from pathlib import Path

block_cipher = None

SPEC_DIR = Path(SPECPATH).resolve()
PROJECT_ROOT = SPEC_DIR.parent

is_mac = sys.platform == "darwin"
is_win = sys.platform.startswith("win")

datas = [
    (str(PROJECT_ROOT / "scripts"), "scripts"),
    (str(PROJECT_ROOT / "assets"), "assets"),
    (str(PROJECT_ROOT / "LICENSE"), "."),
    (str(PROJECT_ROOT / "COPYING.GPL"), "."),
    (str(PROJECT_ROOT / "README.md"), "."),
]

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

if is_mac:
    icon_path = str(PROJECT_ROOT / "assets" / "icon.icns")
elif is_win:
    icon_path = str(PROJECT_ROOT / "assets" / "icon.ico")
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
    app = BUNDLE(
        coll,
        name="非公式Praat日本語版.app",
        icon=icon_path,
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
