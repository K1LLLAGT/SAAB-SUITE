#!/usr/bin/env bash
# =============================================================================
# file_system.sh
# SAAB_SUITE / Termux Workshop Environment -- environment + storage wiring
#
# Responsibilities:
#   1. Export every SAAB_WORKSHOP_* environment variable (with defaults from
#      tools/workshop/file_requirements.txt applied if unset).
#   2. Extend PATH with the workshop's local bin directories.
#   3. Link Termux's Android storage access (termux-setup-storage) and
#      verify/normalize ~/storage and ~/sdcard.
#   4. Provide "bind"-style access to ~/home/saab even where that literal
#      path does not exist on stock Termux, by symlinking it to the
#      workshop staging root.
#   5. Generate a JSON system-state snapshot for diagnostics and for the
#      Windows-side launcher to sanity-check what environment produced a
#      given manifest.
#
# Sourced by Unified_Termux_Shell_Environment_Installer.sh, after
# file_organization and file_structure.sh (needs saab_log).
# =============================================================================

if [ -n "${SAAB_FILE_SYSTEM_LOADED:-}" ]; then
    return 0 2>/dev/null || exit 0
fi
SAAB_FILE_SYSTEM_LOADED=1

# -----------------------------------------------------------------------------
# saab_export_env
# Exports every SAAB_WORKSHOP_* variable used across the workshop scripts,
# defaulting anything not already set in the calling shell's environment.
# -----------------------------------------------------------------------------
saab_export_env() {
    : "${SAAB_WORKSHOP_HOME:=$HOME/saab/workshop}"
    : "${SAAB_WORKSHOP_REPO:=$SAAB_WORKSHOP_HOME/repo}"
    : "${SAAB_WORKSHOP_STAGING:=$SAAB_WORKSHOP_HOME/staging}"
    : "${SAAB_WORKSHOP_LOGDIR:=$SAAB_WORKSHOP_HOME/logs}"
    : "${SAAB_WORKSHOP_MANIFEST_DIR:=$SAAB_WORKSHOP_HOME/manifests}"
    : "${SAAB_WORKSHOP_STATE_DIR:=$SAAB_WORKSHOP_HOME/state}"
    : "${SAAB_WORKSHOP_REPO_URL:=https://github.com/k1lllagt/saab-workshop.git}"
    : "${SAAB_WORKSHOP_SCAN_DIRS:=$HOME/storage:$HOME/sdcard:$HOME/saab}"
    : "${SAAB_WORKSHOP_HASH_ALGO:=sha256}"
    : "${SAAB_WORKSHOP_COPY_MODE:=copy}"
    : "${SAAB_WORKSHOP_LOG_LEVEL:=INFO}"
    : "${SAAB_WORKSHOP_BIN:=$SAAB_WORKSHOP_HOME/bin}"

    export SAAB_WORKSHOP_HOME SAAB_WORKSHOP_REPO SAAB_WORKSHOP_STAGING \
        SAAB_WORKSHOP_LOGDIR SAAB_WORKSHOP_MANIFEST_DIR SAAB_WORKSHOP_STATE_DIR \
        SAAB_WORKSHOP_REPO_URL SAAB_WORKSHOP_SCAN_DIRS SAAB_WORKSHOP_HASH_ALGO \
        SAAB_WORKSHOP_COPY_MODE SAAB_WORKSHOP_LOG_LEVEL SAAB_WORKSHOP_BIN

    SAAB_LOG_FILE="$SAAB_WORKSHOP_LOGDIR/install-$(date -u +%Y%m%dT%H%M%SZ).log"
    export SAAB_LOG_FILE

    saab_log INFO "system" "environment exported (repo=$SAAB_WORKSHOP_REPO)"
}

# -----------------------------------------------------------------------------
# saab_extend_path
# Prepends the workshop's own bin directory (once) and the standard Termux
# usr/bin, so scripts invoked from anywhere resolve workshop tooling first.
# -----------------------------------------------------------------------------
saab_extend_path() {
    mkdir -p -- "$SAAB_WORKSHOP_BIN"
    case ":$PATH:" in
        *":$SAAB_WORKSHOP_BIN:"*) ;;
        *) PATH="$SAAB_WORKSHOP_BIN:$PATH" ;;
    esac
    local termux_bin="${PREFIX:-/data/data/com.termux/files/usr}/bin"
    case ":$PATH:" in
        *":$termux_bin:"*) ;;
        *) PATH="$PATH:$termux_bin" ;;
    esac
    export PATH
    saab_log DEBUG "system" "PATH=$PATH"
}

# -----------------------------------------------------------------------------
# saab_link_storage
# Runs termux-setup-storage (if available and ~/storage is not already
# populated) and verifies the resulting symlink farm. Non-fatal if the user
# is on a non-Termux Linux box running this for testing -- falls back to
# treating ~/storage / ~/sdcard as plain directories.
# -----------------------------------------------------------------------------
saab_link_storage() {
    if [ -d "$HOME/storage" ] && [ -n "$(find "$HOME/storage" -mindepth 1 -maxdepth 1 2>/dev/null)" ]; then
        saab_log INFO "system" "~/storage already linked"
    elif command -v termux-setup-storage >/dev/null 2>&1; then
        saab_log INFO "system" "requesting Android storage permission (termux-setup-storage)"
        termux-setup-storage || saab_log WARN "system" "termux-setup-storage did not complete; continuing without it"
        # termux-setup-storage returns immediately while Android grants the
        # permission asynchronously; give it a short, bounded window.
        local waited=0
        while [ ! -d "$HOME/storage/shared" ] && [ "$waited" -lt 15 ]; do
            sleep 1
            waited=$((waited + 1))
        done
    else
        saab_log WARN "system" "termux-setup-storage not found; creating ~/storage as a plain directory (non-Termux host?)"
        mkdir -p -- "$HOME/storage"
    fi

    if [ ! -e "$HOME/sdcard" ]; then
        if [ -e "$HOME/storage/shared" ]; then
            ln -s -- "$HOME/storage/shared" "$HOME/sdcard"
        else
            mkdir -p -- "$HOME/sdcard"
        fi
    fi

    saab_log INFO "system" "storage: ~/storage=$([ -d "$HOME/storage" ] && echo present || echo missing), ~/sdcard=$([ -e "$HOME/sdcard" ] && echo present || echo missing)"
}

# -----------------------------------------------------------------------------
# saab_bind_home_saab
# The task spec refers to ~/home/saab/ as a scan root. Termux has no /home
# hierarchy, so we create $HOME/saab (already part of STAGING_TREE) and, for
# compatibility with tooling/docs that expect the literal ~/home/saab path,
# symlink $HOME/home -> $HOME (making ~/home/saab resolve to $HOME/saab).
# This is a symlink, never a real second copy -- no data duplication.
# -----------------------------------------------------------------------------
saab_bind_home_saab() {
    mkdir -p -- "$HOME/saab"
    if [ -L "$HOME/home" ]; then
        saab_log DEBUG "system" "~/home already bound"
    elif [ -e "$HOME/home" ]; then
        saab_log WARN "system" "~/home exists and is not a symlink; leaving it untouched"
    else
        ln -s -- "$HOME" "$HOME/home"
        saab_log INFO "system" "bound ~/home -> \$HOME (so ~/home/saab resolves to \$HOME/saab)"
    fi
}

# -----------------------------------------------------------------------------
# saab_generate_system_state
# Writes a JSON snapshot of the environment (Termux info, storage stats,
# resolved scan roots, exported env vars) to
# $SAAB_WORKSHOP_STATE_DIR/system_state.json. Consumed by the installer's
# post-install summary and, optionally, by the Windows launcher when
# diagnosing a manifest it was handed.
# -----------------------------------------------------------------------------
saab_generate_system_state() {
    local out="$SAAB_WORKSHOP_STATE_DIR/system_state.json"
    mkdir -p -- "$SAAB_WORKSHOP_STATE_DIR"

    local termux_version android_version arch
    termux_version="$(command -v termux-info >/dev/null 2>&1 && termux-info 2>/dev/null | head -n1 || echo unknown)"
    android_version="$(getprop ro.build.version.release 2>/dev/null || echo unknown)"
    arch="$(uname -m 2>/dev/null || echo unknown)"

    local storage_free_kb
    storage_free_kb="$(df -Pk "$HOME" 2>/dev/null | awk 'NR==2{print $4}')"
    [ -n "$storage_free_kb" ] || storage_free_kb=0

    local scan_roots_json="" root exists first=1
    IFS=':' read -r -a __scan_roots <<< "$SAAB_WORKSHOP_SCAN_DIRS"
    for root in "${__scan_roots[@]}"; do
        [ -n "$root" ] || continue
        [ -d "$root" ] && exists=true || exists=false
        if [ "$first" -eq 1 ]; then
            first=0
        else
            scan_roots_json="${scan_roots_json},"
        fi
        scan_roots_json="${scan_roots_json}
    {\"path\":\"${root//\"/\\\"}\",\"exists\":${exists}}"
    done
    unset __scan_roots

    cat > "$out" <<EOF
{
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "hostname": "$(hostname 2>/dev/null || echo termux)",
  "arch": "$arch",
  "android_release": "$android_version",
  "termux_info_summary": $(printf '%s' "$termux_version" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))' 2>/dev/null || echo '"unknown"'),
  "home_storage_free_kb": $storage_free_kb,
  "env": {
    "SAAB_WORKSHOP_HOME": "$SAAB_WORKSHOP_HOME",
    "SAAB_WORKSHOP_REPO": "$SAAB_WORKSHOP_REPO",
    "SAAB_WORKSHOP_STAGING": "$SAAB_WORKSHOP_STAGING",
    "SAAB_WORKSHOP_LOGDIR": "$SAAB_WORKSHOP_LOGDIR",
    "SAAB_WORKSHOP_MANIFEST_DIR": "$SAAB_WORKSHOP_MANIFEST_DIR",
    "SAAB_WORKSHOP_STATE_DIR": "$SAAB_WORKSHOP_STATE_DIR",
    "SAAB_WORKSHOP_REPO_URL": "$SAAB_WORKSHOP_REPO_URL",
    "SAAB_WORKSHOP_SCAN_DIRS": "$SAAB_WORKSHOP_SCAN_DIRS",
    "SAAB_WORKSHOP_HASH_ALGO": "$SAAB_WORKSHOP_HASH_ALGO",
    "SAAB_WORKSHOP_COPY_MODE": "$SAAB_WORKSHOP_COPY_MODE"
  },
  "scan_roots": [${scan_roots_json}
  ]
}
EOF

    saab_log INFO "system" "wrote system state snapshot to $out"
}
