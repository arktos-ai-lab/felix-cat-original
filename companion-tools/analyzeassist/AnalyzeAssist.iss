#define SourceDir "C:\dev\python\AnalyzeAssist\AnalyzeAssist"
#define BaseDir "C:\dev\python\AnalyzeAssist"
#define Version "1.5"

[Setup]
AppCopyright=Copyright © 2007 Ginstrom IT Solutions (GITS)
AppName=AnalyzeAssist
AppVerName=AnalyzeAssist version {#Version}
DefaultDirName={pf}\AnalyzeAssist
AppPublisher=Ginstrom IT Solutions (GITS)
AppPublisherURL=http://www.ginstrom.com/
AppSupportURL=http://www.ginstrom.com/
AppVersion={#Version}
DefaultGroupName=AnalyzeAssist
UninstallDisplayName=AnalyzeAssist
ShowLanguageDialog=yes
ShowComponentSizes=yes
OutputBaseFilename=AnalyzeAssist_Setup_{#Version}
OutputDir=Setup

[Files]
Source: {#SourceDir}\*; DestDir: {app}\; Flags: ignoreversion recursesubdirs
Source: {#BaseDir}\help\*; DestDir:      {localappdata}\AnalyzeAssist\help\en\; Flags: ignoreversion recursesubdirs
Source: {#BaseDir}\res\*; DestDir:       {localappdata}\AnalyzeAssist\res\;
Source: {#BaseDir}\version.txt; DestDir: {localappdata}\AnalyzeAssist\;         Flags: ignoreversion;
Source: {#BaseDir}\stringres.database; DestDir: {localappdata}\AnalyzeAssist\;  Flags: ignoreversion;

[Languages]
Name: "en"; MessagesFile: "compiler:English.isl";  LicenseFile:{#BaseDir}\MITLicense.txt
Name: "jp"; MessagesFile: "compiler:Japanese.isl"; LicenseFile:{#BaseDir}\MITLicenseJ.txt

[Tasks]
Name: desktopicon; Description: "Create &desktop icons";    GroupDescription: "Icons:"
Name: startmenu;   Description: "Create &start menu icons";  GroupDescription: "Icons:"

[Run]
Filename: "{app}\AnalyzeAssist.exe"; WorkingDir: "{app}"; Description: "{cm:LaunchProgram,AnalyzeAssist}"; Flags: nowait postinstall skipifsilent

[Icons]
Name: {group}\{cm:UninstallProgram,AnalyzeAssist}; Filename: {uninstallexe};          Comment: "{cm:UninstallProgram,AnalyzeAssist}"; WorkingDir: {app}; Tasks: startmenu
Name: {group}\AnalyzeAssist;                       Filename: {app}\AnalyzeAssist.exe;  Comment: "{cm:LaunchProgram,AnalyzeAssist}";    WorkingDir: {app}; Tasks: startmenu
Name: {group}\Show Logs;                           Filename: {app}\ShowLogs.exe;  Comment: "{cm:LaunchProgram,ShowLogs}";    WorkingDir: {app}; Tasks: startmenu
Name: {userdesktop}\AnalyzeAssist;                 Filename: {app}\AnalyzeAssist.exe;  Comment: "{cm:LaunchProgram,AnalyzeAssist}";    WorkingDir: {app}; IconFilename: {app}\AnalyzeAssist.exe;  IconIndex: 0; Tasks: desktopicon

[Dirs]
Name: {localappdata}\AnalyzeAssist\;

