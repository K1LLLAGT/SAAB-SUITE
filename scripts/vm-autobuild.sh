#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VM_DIR="$ROOT/vm"
VMRUN="/usr/bin/vmrun"

if [ ! -x "$VMRUN" ]; then
    echo "[!] vmrun not found. Install VMware Workstation Pro."
    exit 1
fi

menu() {
    clear
    echo "=============================="
    echo "     VM AUTO-BUILDER (Linux)  "
    echo "=============================="
    echo "1) Build XP SAAB VM"
    echo "2) Build Win7 SAAB VM"
    echo "0) Exit"
    echo
    read -rp "Select option: " CHOICE
}

build_vm() {
    local NAME="$1"
    local ISO="$2"
    local TARGET="$VM_DIR/$NAME"

    echo "[*] Creating VM directory: $TARGET"
    mkdir -p "$TARGET"

    echo "[*] Creating virtual disk..."
    vmware-vdiskmanager -c -s 20GB -a lsilogic -t 1 "$TARGET/$NAME.vmdk"

    echo "[*] Writing VMX file..."
    cat > "$TARGET/$NAME.vmx" <<EOF
.encoding = "UTF-8"
config.version = "8"
virtualHW.version = "12"
memsize = "2048"
numvcpus = "2"
displayName = "$NAME"
guestOS = "windows"
ide1:0.present = "TRUE"
ide1:0.fileName = "$ISO"
ide1:0.deviceType = "cdrom-image"
scsi0.present = "TRUE"
scsi0:0.present = "TRUE"
scsi0:0.fileName = "$NAME.vmdk"
sharedFolder0.present = "TRUE"
sharedFolder0.enabled = "TRUE"
sharedFolder0.readAccess = "TRUE"
sharedFolder0.writeAccess = "TRUE"
sharedFolder0.hostPath = "$ROOT"
sharedFolder0.guestName = "SAAB-SUITE"
sharedFolder0.expiration = "never"
EOF

    echo "[*] Booting VM..."
    "$VMRUN" start "$TARGET/$NAME.vmx"

    echo "[*] Waiting for OS installation..."
    echo "    (Install Windows manually, then press Enter)"
    read -rp ""

    echo "[*] Installing VMware Tools..."
    "$VMRUN" installTools "$TARGET/$NAME.vmx"

    echo "[*] Taking baseline snapshot..."
    "$VMRUN" snapshot "$TARGET/$NAME.vmx" baseline

    echo "[*] VM build complete: $NAME"
}

while true; do
    menu
    case "$CHOICE" in
        1) build_vm "WINXP-SAAB" "$VM_DIR/xp.iso" ;;
        2) build_vm "WIN7-SAAB" "$VM_DIR/win7.iso" ;;
        0) exit 0 ;;
        *) echo "Invalid option" ;;
    esac
    read -rp "Press Enter to continue..."
done
