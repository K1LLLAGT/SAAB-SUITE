; Inno Setup script for the Windows companion installer.
; Targets the Win7-SAAB and WinXP-SAAB VMs.

[Setup]
AppName=SAAB Suite (Companion)
AppVersion=0.1.0
AppPublisher=GWT
DefaultDirName={pf}\SAAB-Suite
DefaultGroupName=SAAB Suite
OutputBaseFilename=SAAB-Suite-0.1.0-windows-companion
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
; Files added in Phase-2 by build_all.sh

[Icons]
Name: "{group}\SAAB Suite"; Filename: "{app}\saab.exe"

[Run]
