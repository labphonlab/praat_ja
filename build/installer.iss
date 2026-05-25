; installer.iss — Inno Setup スクリプト（非公式Praat日本語版 Windowsインストーラー）

#define MyAppName "非公式Praat日本語版"
#define MyAppNameAscii "Praat JA (Unofficial)"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "labphonlab"
#define MyAppExeName "PraatJa.exe"
#define MyAppURL "https://github.com/labphonlab/praat_ja"

[Setup]
AppId={{B2C3D4E5-6789-4ABC-9DEF-0123456789AB}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppComments=Unofficial Japanese GUI frontend for Praat. Not affiliated with the official Praat project.
DefaultDirName={autopf}\PraatJa
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=PraatJa_Setup
SetupIconFile=..\assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64 arm64
PrivilegesRequired=admin
LicenseFile=..\LICENSE
InfoBeforeFile=..\COPYING.GPL

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "デスクトップにショートカットを作成 / Create desktop shortcut"; GroupDescription: "追加アイコン / Additional icons:"

[Files]
Source: "..\dist\PraatJa\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\COPYING.GPL"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{#MyAppName} をアンインストール / Uninstall"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "今すぐ起動する / Launch now"; Flags: nowait postinstall skipifsilent
