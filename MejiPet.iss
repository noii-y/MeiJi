; 仓鼠美叽桌宠 Inno Setup 安装脚本
#define MyAppName "仓鼠美叽桌宠"
#define MyAppShort "仓鼠美叽"
#define MyAppVersion "1.0"
#define MyAppPublisher "MejiPet"
#define MyAppExe "MejiPet.exe"

[Setup]
AppId={{B8F4A1E2-7C39-4D6A-9E21-3A7C91D20001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
; 每用户安装：装到当前用户目录，安装/卸载都不需要管理员授权(UAC)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DefaultDirName={localappdata}\Programs\MejiPet
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=MejiPet_Setup_v1.0
SetupIconFile=meji.ico
UninstallDisplayIcon={app}\{#MyAppExe}
UninstallDisplayName={#MyAppName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; 不写任何开机启动项

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "在桌面创建快捷方式"; GroupDescription: "附加图标："; Flags: checkedonce

[Files]
Source: "dist\{#MyAppExe}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppShort}"; Filename: "{app}\{#MyAppExe}"; IconFilename: "{app}\{#MyAppExe}"
Name: "{group}\卸载{#MyAppShort}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppShort}"; Filename: "{app}\{#MyAppExe}"; IconFilename: "{app}\{#MyAppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExe}"; Description: "安装完成后立即启动{#MyAppShort}"; Flags: nowait postinstall skipifsilent
