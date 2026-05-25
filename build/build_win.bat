@echo off
REM build_win.bat — Windows用 PyInstaller one-dir + Inno Setup インストーラー
setlocal

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
pushd "%PROJECT_ROOT%"

if not exist "dist\PraatJa\PraatJa.exe" (
    echo PyInstaller のビルド成果物が見つかりません。先に "pyinstaller build\praat_ja.spec --clean" を実行してください。
    popd
    exit /b 1
)

where iscc >nul 2>nul
if errorlevel 1 (
    echo Inno Setup ^(iscc^) がパスに見つかりません。choco install innosetup でインストールしてください。
    popd
    exit /b 1
)

iscc "build\installer.iss"
if errorlevel 1 (
    echo インストーラーのビルドに失敗しました。
    popd
    exit /b 1
)

echo インストーラーを作成しました: dist\PraatJa_Setup.exe
popd
endlocal
