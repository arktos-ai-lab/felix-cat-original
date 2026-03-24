; MemoryServes Setup

#define BaseDir     "D:\dev\python\MemoryServes\MemoryServes"
#define AppVersion  "%(version)s"
#define SkinDir     "C:\Program Files (x86)\Codejock Software\ISSkin"

[Setup]
AppCopyright=Copyright � Ginstrom IT Solutions (GITS)
AppName=Memory Serves
AppVerName=Memory Serves version {#AppVersion}
DefaultDirName={pf}\MemoryServes
AppPublisher=Ginstrom IT Solutions (GITS)
AppPublisherURL=http://felix-cat.com/
AppSupportURL=http://felix-cat.com/
AppVersion={#AppVersion}
DefaultGroupName=Memory Serves
UninstallDisplayName=Memory Serves
ShowLanguageDialog=yes
ShowComponentSizes=yes
OutputBaseFilename=MemoryServes_Setup_{#AppVersion}
OutputDir=Setup
PrivilegesRequired=admin

[Files]
Source: {#BaseDir}\MemoryServes\*;  DestDir: {app}\;                                     Flags: ignoreversion recursesubdirs
Source: {#BaseDir}\media\*;         DestDir: {code:DefAppDataFolder}\MemoryServes\media\;      Flags: ignoreversion recursesubdirs
Source: {#BaseDir}\templates\*;     DestDir: {code:DefAppDataFolder}\MemoryServes\templates\;  Flags: ignoreversion recursesubdirs
Source: {#BaseDir}\modules\*;       DestDir: {code:DefAppDataFolder}\MemoryServes\modules\;    Flags: ignoreversion recursesubdirs
Source: {#BaseDir}\MITLicense.txt;  DestDir: {code:DefAppDataFolder}\MemoryServes\;
Source: {#BaseDir}\MITLicenseJ.txt; DestDir: {code:DefAppDataFolder}\MemoryServes\;

Source: {#BaseDir}\media\*;         DestDir: {app}\media\;  Flags: recursesubdirs
Source: {#BaseDir}\templates\*;     DestDir: {app}\templates\;  Flags: recursesubdirs

Source: {#BaseDir}\msversion.txt;  DestDir: {code:DefAppDataFolder}\MemoryServes\;
Source: {#BaseDir}\settings.cfg;   DestDir: {code:DefAppDataFolder}\MemoryServes\;

; CRT junk
Source: D:\dev\cpp\vcredist_x86.exe; DestDir: {tmp}
Source: D:\dev\cpp\vcredist_2010_x86.exe; DestDir: {tmp}

; Add the ISSkin DLL used for skinning Inno Setup installations.
Source: {#SkinDir}\ISSkin.dll; DestDir: {app}; Flags: dontcopy
Source: {#SkinDir}\Styles\Office2007.cjstyles; DestDir: {tmp}; Flags: dontcopy

[Languages]
Name: "en"; MessagesFile: "compiler:English.isl";  LicenseFile:.\MITLicense.txt
Name: "jp"; MessagesFile: "compiler:Japanese.isl"; LicenseFile:.\MITLicenseJ.txt

[Tasks]
Name: desktopicon; Description: "{cm:CreateDesktopIcon}";      GroupDescription: "{cm:IconTask}"
Name: startmenu;   Description: "{cm:CreateStartmenuIcon}";   GroupDescription: "{cm:IconTask}"

Name: common; Description: "{cm:IntallCommon}"; GroupDescription: "{cm:InstallTask}"; Flags: exclusive unchecked
Name: local;  Description: "{cm:InstallLocal}"; GroupDescription: "{cm:InstallTask}"; Flags: exclusive

[Run]
; VC Redistributables
Filename: "{tmp}\vcredist_x86.exe"; StatusMsg: {cm:Registering,VC 2008 Redistributable Files}; Parameters: "/qn"
Filename: "{tmp}\vcredist_2010_x86.exe"; StatusMsg: {cm:Registering,VC 2010 Redistributable Files}; Parameters: "/q /norestart"

Filename: "{app}\MemoryServes.exe"; WorkingDir: "{app}"; Description: "{cm:LaunchProgram,MemoryServes}"; Flags: nowait postinstall skipifsilent

[Icons]
Name: {group}\{cm:UninstallProgram,Memory Serves}; Filename: {uninstallexe};          Comment: "{cm:UninstallProgram,Memory Serves}"; WorkingDir: {app}; Tasks: startmenu
Name: {group}\Memory Serves;                       Filename: {app}\MemoryServes.exe;  Comment: "{cm:LaunchProgram,Memory Serves}";    WorkingDir: {app}; IconFilename: {app}\media\MemoryServes.ico;  IconIndex: 0; Tasks: startmenu
Name: {group}\Clear Users;                         Filename: {app}\ClearUsers.exe;    Comment: "{cm:LaunchProgram,Clear Users}";        WorkingDir: {app}; Tasks: startmenu
Name: {group}\Memory Importer;                     Filename: {app}\MemoryImporter.exe;  Comment: "{cm:LaunchProgram,Memory Importer}";        WorkingDir: {app}; Tasks: startmenu

Name: {userdesktop}\Memory Serves; Filename: {app}\MemoryServes.exe;  Comment: "{cm:LaunchProgram,Memory Serves}";    WorkingDir: {app}; IconFilename: {app}\media\MemoryServes.ico;  IconIndex: 0; Tasks: desktopicon

[Dirs]
Name: {code:DefAppDataFolder}\MemoryServes;
Name: {code:DefAppDataFolder}\MemoryServes\templates;
Name: {code:DefAppDataFolder}\MemoryServes\modules;
Name: {code:DefAppDataFolder}\MemoryServes\media;
Name: {code:DefAppDataFolder}\MemoryServes\media\manual;
Name: {code:DefAppDataFolder}\MemoryServes\data;

[Code]
// Importing LoadSkin API from ISSkin.DLL
procedure LoadSkin(lpszPath: AnsiString; lpszIniFileName: AnsiString);
external 'LoadSkin@files:isskin.dll stdcall';

// Importing UnloadSkin API from ISSkin.DLL
procedure UnloadSkin();
external 'UnloadSkin@files:isskin.dll stdcall';

// Importing ShowWindow Windows API from User32.DLL
function ShowWindow(hWnd: Integer; uType: Integer): Integer;
external 'ShowWindow@user32.dll stdcall';


function InitializeSetup(): Boolean;
begin
  ExtractTemporaryFile('Office2007.cjstyles');
  LoadSkin(ExpandConstant('{tmp}\Office2007.cjstyles'), '');
  Result := True;
end;

function DefAppDataFolder(Param: String): String;
begin
if IsTaskSelected('common') then
Result := ExpandConstant('{commonappdata}')
else
Result := ExpandConstant('{localappdata}')
end;
