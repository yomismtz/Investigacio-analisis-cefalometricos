#define MyAppName "Yornis"
#define MyAppVersion "0.15.7"
#define MyAppExeName "Yornis.exe"
[Setup]
AppId={{9EBE24F2-1F99-49D3-9D08-1DAB4A5E0150}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Yom Dental Análisis
DefaultDirName={localappdata}\Programs\Yornis
DefaultGroupName=Yornis
DisableProgramGroupPage=yes
OutputDir=..\dist-installer-yornis
OutputBaseFilename=Yornis_Setup_v0.15.7_Bird_Assistant_HiDPI
SetupIconFile=assets\yornis.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
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
