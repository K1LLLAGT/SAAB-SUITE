Write-Host "[*] Installing SAAB-SUITE (Windows)..."

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "[*] Validating directory structure..."
powershell.exe -ExecutionPolicy Bypass -File scripts\verify-tree.ps1

Write-Host "[*] Extracting packages..."
powershell.exe -ExecutionPolicy Bypass -File scripts\extract-all-packages.ps1

Write-Host "[*] Creating launcher..."
$Launcher = "$Root\scripts\saab-suite-launcher.ps1"
$BatFile = "$Root\saab.bat"
"@echo off`npowershell -ExecutionPolicy Bypass -File `"$Launcher`" %*" | Out-File $BatFile -Encoding ASCII

Write-Host "[*] Ensuring VM directories exist..."
New-Item -ItemType Directory -Force -Path "$Root\vm\WINXP-SAAB" | Out-Null
New-Item -ItemType Directory -Force -Path "$Root\vm\Win7-SAAB" | Out-Null

Write-Host "[*] Installation complete."
Write-Host "Run 'saab.bat' to launch the suite."
