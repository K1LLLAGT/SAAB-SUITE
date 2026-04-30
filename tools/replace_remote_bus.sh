#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="$HOME/saab-suite"

echo "Scanning $ROOT for Python files only…"

# 1. Replace import lines
find "$ROOT" -type f -name "*.py" ! -name "*.bak" | while read -r file; do
    if grep -q "from can.remote import RemoteBus" "$file"; then
        echo "Patching import in: $file"
        sed -i.bak \
            's|from can.remote import RemoteBus|from saab_suite.remote_tcp_bus import RemoteTcpBus|g' \
            "$file"
    fi
done

# 2. Replace constructor calls
find "$ROOT" -type f -name "*.py" ! -name "*.bak" | while read -r file; do
    if grep -q "RemoteBus(" "$file"; then
        echo "Patching constructor in: $file"
        sed -i.bak \
            's|RemoteBus([^)]*)|RemoteTcpBus(host="192.168.1.50", port=5000, timeout=1.0)|g' \
            "$file"
    fi
done

echo "Done. Only .py files were modified. Backups (*.bak) preserved."
