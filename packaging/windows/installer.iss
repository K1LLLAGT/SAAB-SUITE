; Inno Setup script for the Windows companion installer.
; Targets the Win7-SAAB and WinXP-SAAB VMs.

[Setup]
AppName=SAAB Suite (Companion)
AppVersion=1.0.0
AppPublisher=K1LLLAGT
DefaultDirName={pf}\SAAB_Suite
DefaultGroupName=SAAB Suite
OutputBaseFilename=Saab_Suite-v1.0.0-windows-companion
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
; Files added in Phase-2 by build_all.sh

[Icons]
Name: "{group}\SAAB Suite"; Filename: "{app}\saab.exe"

[Run]
