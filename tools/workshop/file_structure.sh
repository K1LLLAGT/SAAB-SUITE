#!/usr/bin/env bash
# =============================================================================
# file_structure.sh
# SAAB_SUITE / Termux Workshop Environment -- directory tree + logging
#
# Responsibilities:
#   1. Provide saab_log(), the single logging function used by every other
#      workshop script (console + file, leveled, timestamped).
#   2. Create the full workshop directory tree (Termux-side staging areas
#      AND the git-ready layout inside the cloned/initialized repo).
#   3. Validate that tree after creation and print a structure map.
#
# Sourced by Unified_Termux_Shell_Environment_Installer.sh. Depends on
# file_organization being sourced first (for CATEGORY_DEST).
# =============================================================================

if [ -n "${SAAB_FILE_STRUCTURE_LOADED:-}" ]; then
    return 0 2>/dev/null || exit 0
fi
SAAB_FILE_STRUCTURE_LOADED=1

# -----------------------------------------------------------------------------
# saab_log <LEVEL> <component> <message...>
# LEVEL one of DEBUG|INFO|WARN|ERROR. Writes to stderr (console) and, if
# SAAB_WORKSHOP_LOGDIR/SAAB_LOG_FILE is set, appends to the run's log file.
# Honors SAAB_WORKSHOP_LOG_LEVEL (DEBUG < INFO < WARN < ERROR).
# -----------------------------------------------------------------------------
saab_log_level_rank() {
    case "$1" in
        DEBUG) echo 0 ;;
        INFO)  echo 1 ;;
        WARN)  echo 2 ;;
        ERROR) echo 3 ;;
        *)     echo 1 ;;
    esac
}

saab_log() {
    local level="$1" component="$2"; shift 2
    local msg="$*"
    local min_level="${SAAB_WORKSHOP_LOG_LEVEL:-INFO}"
    local rank min_rank ts line

    rank="$(saab_log_level_rank "$level")"
    min_rank="$(saab_log_level_rank "$min_level")"
    [ "$rank" -ge "$min_rank" ] || return 0

    ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    line="[$ts] [$level] [$component] $msg"

    case "$level" in
        ERROR) printf '\033[1;31m%s\033[0m\n' "$line" >&2 ;;
        WARN)  printf '\033[1;33m%s\033[0m\n' "$line" >&2 ;;
        INFO)  printf '\033[0;36m%s\033[0m\n' "$line" >&2 ;;
        *)     printf '%s\n' "$line" >&2 ;;
    esac

    if [ -n "${SAAB_LOG_FILE:-}" ]; then
        mkdir -p -- "$(dirname -- "$SAAB_LOG_FILE")" 2>/dev/null || true
        printf '%s\n' "$line" >> "$SAAB_LOG_FILE"
    fi
}

# -----------------------------------------------------------------------------
# saab_die <message...>
# Logs an ERROR and exits non-zero. Used by the installer's error trap paths.
# -----------------------------------------------------------------------------
saab_die() {
    saab_log ERROR "fatal" "$*"
    exit 1
}

# -----------------------------------------------------------------------------
# STAGING_TREE: Termux-side working directories, independent of the git repo.
# -----------------------------------------------------------------------------
STAGING_TREE=(
    "$HOME/saab"
    "$HOME/saab/workshop"
    "$HOME/saab/workshop/staging"
    "$HOME/saab/workshop/logs"
    "$HOME/saab/workshop/manifests"
    "$HOME/saab/workshop/state"
    "$HOME/saab/workshop/quarantine"
)

# -----------------------------------------------------------------------------
# REPO_TREE: paths created *inside* $SAAB_WORKSHOP_REPO -- the git-ready
# layout that mirrors the existing SAAB_SUITE repo conventions (vendor/,
# docs/, tools/, runtime/) so an organizer run and a `git clone` of
# k1lllagt/saab-workshop produce an identical tree.
# -----------------------------------------------------------------------------
saab_repo_tree() {
    local repo="$1"
    local -a tree=(
        "$repo"
        "$repo/vendor"
        "$repo/vendor/isos/gds2"
        "$repo/vendor/isos/tech2win"
        "$repo/vendor/isos/globaltis"
        "$repo/vendor/isos/wis"
        "$repo/vendor/isos/epc"
        "$repo/vendor/isos/misc"
        "$repo/vendor/drivers/j2534"
        "$repo/vendor/drivers/canusb"
        "$repo/vendor/drivers/tech2"
        "$repo/vendor/firmware/nao_148"
        "$repo/vendor/firmware/nao_149"
        "$repo/vendor/firmware/tech2win_pcmcia"
        "$repo/vendor/firmware/china"
        "$repo/vendor/firmware/custom"
        "$repo/vendor/deliverables"
        "$repo/vendor/legacy_archive"
        "$repo/docs/manuals"
        "$repo/tools/imported"
        "$repo/tools/workshop"
        "$repo/runtime/logs/imported"
        "$repo/runtime/backups/imported"
        "$repo/runtime/audit"
        "$repo/manifests"
    )
    printf '%s\n' "${tree[@]}"
}

# -----------------------------------------------------------------------------
# saab_create_directory_tree
# Creates STAGING_TREE and, if SAAB_WORKSHOP_REPO is set, the repo tree too.
# Idempotent: safe to re-run.
# -----------------------------------------------------------------------------
saab_create_directory_tree() {
    local d created=0 existed=0

    for d in "${STAGING_TREE[@]}"; do
        if [ -d "$d" ]; then
            existed=$((existed + 1))
        else
            mkdir -p -- "$d" || saab_die "could not create staging directory: $d"
            created=$((created + 1))
        fi
    done

    if [ -n "${SAAB_WORKSHOP_REPO:-}" ]; then
        local repo_dir
        while IFS= read -r repo_dir; do
            [ -n "$repo_dir" ] || continue
            if [ -d "$repo_dir" ]; then
                existed=$((existed + 1))
            else
                mkdir -p -- "$repo_dir" || saab_die "could not create repo directory: $repo_dir"
                created=$((created + 1))
            fi
            # Keep otherwise-empty leaf directories tracked by git.
            if [ -z "$(find "$repo_dir" -mindepth 1 -maxdepth 1 2>/dev/null)" ]; then
                : > "$repo_dir/.gitkeep"
            fi
        done < <(saab_repo_tree "$SAAB_WORKSHOP_REPO")
    fi

    saab_log INFO "structure" "directory tree ready (created=$created, existed=$existed)"
}

# -----------------------------------------------------------------------------
# saab_validate_directory_tree
# Re-checks every path from saab_create_directory_tree exists, is a
# directory, and is writable. Returns non-zero (does not exit) on the first
# failure category so the caller can decide how to react.
# -----------------------------------------------------------------------------
saab_validate_directory_tree() {
    local d bad=0

    for d in "${STAGING_TREE[@]}"; do
        if [ ! -d "$d" ]; then
            saab_log ERROR "structure" "missing staging directory: $d"
            bad=$((bad + 1))
        elif [ ! -w "$d" ]; then
            saab_log ERROR "structure" "staging directory not writable: $d"
            bad=$((bad + 1))
        fi
    done

    if [ -n "${SAAB_WORKSHOP_REPO:-}" ]; then
        local repo_dir
        while IFS= read -r repo_dir; do
            [ -n "$repo_dir" ] || continue
            if [ ! -d "$repo_dir" ]; then
                saab_log ERROR "structure" "missing repo directory: $repo_dir"
                bad=$((bad + 1))
            fi
        done < <(saab_repo_tree "$SAAB_WORKSHOP_REPO")
    fi

    if [ "$bad" -gt 0 ]; then
        saab_log ERROR "structure" "validation failed: $bad problem(s)"
        return 1
    fi

    saab_log INFO "structure" "validation passed"
    return 0
}

# -----------------------------------------------------------------------------
# saab_print_structure_map
# Human-readable tree of the workshop layout, written to the log.
# -----------------------------------------------------------------------------
saab_print_structure_map() {
    saab_log INFO "structure" "---- staging tree ----"
    local d
    for d in "${STAGING_TREE[@]}"; do
        saab_log INFO "structure" "  $d"
    done
    if [ -n "${SAAB_WORKSHOP_REPO:-}" ] && command -v tree >/dev/null 2>&1; then
        saab_log INFO "structure" "---- repo tree ($SAAB_WORKSHOP_REPO) ----"
        tree -a -I '.git' -L 3 "$SAAB_WORKSHOP_REPO" 2>/dev/null | while IFS= read -r line; do
            saab_log INFO "structure" "  $line"
        done
    fi
}
