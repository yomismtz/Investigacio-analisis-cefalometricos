#define MyAppName "YomCeph Desktop"
#define MyAppVersion "0.14.1 Classic Research Suite"
#define MyAppExeName "YomCeph_Desktop.exe"

[Setup]
AppId={{E2ECA52A-5360-4B30-86E9-C8BA3F9D0141}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=YomCeph
DefaultDirName={autopf}\YomCeph
DefaultGroupName=YomCeph
DisableProgramGroupPage=yes
OutputDir=..\dist-installer-v0141
OutputBaseFilename=YomCeph_Desktop_Setup_v0.14.1_Classic_Research_Suite
SetupIconFile=assets\yomceph.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "..\dist\YomCeph_Desktop\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\YomCeph Desktop"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\YomCeph Desktop"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
