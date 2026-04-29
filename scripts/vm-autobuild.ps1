$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$VMDir = Join-Path $Root "..\vm"
$VMRun = "C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"

if (-not (Test-Path $VMRun)) {
    Write-Host "[!] vmrun not found. Install VMware Workstation Pro."
    exit
}

function Build-VM {
    param(
        [string]$Name,
        [string]$ISO
    )

    $Target = Join-Path $VMDir $Name
    New-Item -ItemType Directory -Force -Path $Target | Out-Null

    Write-Host "[*] Creating virtual disk..."
    & "C:\Program Files (x86)\VMware\VMware Workstation\vmware-vdiskmanager.exe" `
        -c -s 20GB -a lsilogic -t 1 "$Target\$Name.vmdk"

    Write-Host "[*] Writing VMX..."
    @"
.encoding = "UTF-8"
config.version = "8"
virtualHW.version = "12"
memsize = "2048"
numvcpus = "2"
displayName = "$Name"
guestOS = "windows"
ide1:0.present = "TRUE"
ide1:0.fileName = "$ISO"
ide1:0.deviceType = "cdrom-image"
scsi0.present = "TRUE"
scsi0:0.present = "TRUE"
scsi0:0.fileName = "$Name.vmdk"
sharedFolder0.present = "TRUE"
sharedFolder0.enabled = "TRUE"
sharedFolder0.hostPath = "$Root\.."
sharedFolder0.guestName = "SAAB-SUITE"
sharedFolder0.expiration = "never"
"@ | Out-File "$Target\$Name.vmx" -Encoding ASCII

    Write-Host "[*] Booting VM..."
    & $VMRun start "$Target\$Name.vmx"

    Read-Host "[*] Install Windows manually, then press Enter"

    Write-Host "[*] Installing VMware Tools..."
    & $VMRun installTools "$Target\$Name.vmx"

    Write-Host "[*] Taking baseline snapshot..."
    & $VMRun snapshot "$Target\$Name.vmx" baseline

    Write-Host "[*] VM build complete: $Name"
}

while ($true) {
    Clear-Host
    Write-Host "=============================="
    Write-Host "     VM AUTO-BUILDER (Win)    "
    Write-Host "=============================="
    Write-Host "1) Build XP SAAB VM"
    Write-Host "2) Build Win7 SAAB VM"
    Write-Host "0) Exit"
    $choice = Read-Host "Select option"

    switch ($choice) {
        "1" { Build-VM -Name "WINXP-SAAB" -ISO "$VMDir\xp.iso" }
        "2" { Build-VM -Name "WIN7-SAAB" -ISO "$VMDir\win7.iso" }
        "0" { exit }
        default { Write-Host "Invalid option" }
    }

    Read-Host "Press Enter to continue"
}
