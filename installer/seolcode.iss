#define MyAppName "설이코드"
#define MyAppVersion "0.2.0"
#define MyAppPublisher "SEOL CODE Project"
#define MyAppExeName "SeolCode.exe"

[Setup]
AppId={{D8C11B93-61B1-4D92-94BB-7F9E35A8B027}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\SeolCode
DefaultGroupName={#MyAppName}
OutputDir=..\installer-output
OutputBaseFilename=SeolCode-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "..\dist\SeolCode.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\설이코드"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\설이코드"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "바탕 화면 바로가기 만들기"; GroupDescription: "추가 아이콘:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "설이코드 실행"; Flags: postinstall nowait skipifsilent
