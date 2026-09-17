#define MyAppName "Yornis"
#define MyAppVersion "0.15.9.2"
#define MyAppExeName "Yornis.exe"
#define MyAppPublisher "Yom Dental Análisis"
#define MyAppURL "https://yomismtz.github.io/Investigacio-analisis-cefalometricos/"
#define MyAppSupportURL "https://github.com/yomismtz/Investigacio-analisis-cefalometricos/issues"
#define MyAppUpdatesURL "https://github.com/yomismtz/Investigacio-analisis-cefalometricos/releases/latest"

[Setup]
AppId={{9EBE24F2-1F99-49D3-9D08-1DAB4A5E0150}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppSupportURL}
AppUpdatesURL={#MyAppUpdatesURL}
DefaultDirName={localappdata}\Programs\Yornis
DefaultGroupName=Yornis
DisableProgramGroupPage=yes
OutputDir=..\dist-installer-yornis
OutputBaseFilename=Yornis_Setup_v0.15.9.2_Scroll_Bird_Calls_HiDPI
SetupIconFile=assets\yornis.ico
UninstallDisplayName={#MyAppName} {#MyAppVersion}
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Instalador de Yornis · Scroll + Bird Calls · Yom Dental Análisis
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoVersion=0.15.9.2
VersionInfoCopyright=© 2026 Yom Dental Análisis

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "..\dist\Yornis\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Yornis"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Yornis"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,Yornis}"; Flags: nowait postinstall skipifsilent
