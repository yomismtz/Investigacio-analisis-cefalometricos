#define MyAppName "YomCeph Desktop"
#define MyAppVersion "0.13.2 Classic · Clinical Audit"
#define MyAppExeName "YomCeph_Desktop.exe"

[Setup]
AppId={{E2ECA52A-5360-4B30-86E9-C8BA3F9D0130}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=YomCeph
DefaultDirName={autopf}\YomCeph
DefaultGroupName=YomCeph
DisableProgramGroupPage=yes
OutputDir=..\dist-installer
OutputBaseFilename=YomCeph_Desktop_Setup_v0.13.2_Classic
SetupIconFile=assets\yomceph.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\YomCeph_Desktop\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\YomCeph Desktop"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--lang={language}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\YomCeph Desktop"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--lang={language}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio / Create desktop shortcut"; GroupDescription: "Accesos directos / Shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Parameters: "--lang={language}"; Description: "Abrir YomCeph Desktop / Launch YomCeph Desktop"; Flags: nowait postinstall skipifsilent
