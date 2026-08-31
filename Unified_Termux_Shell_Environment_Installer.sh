#!/data/data/com.termux/files/usr/bin/bash
# =============================================================================
# Unified_Termux_Shell_Environment_Installer.sh
#
# SAAB_SUITE / Termux Workshop Environment -- unified bootstrap + organizer.
#
# Bootstraps a Saab diagnostic "workshop" environment inside Termux,
# recursively scans the device's accessible storage for Saab-related files
# the user already has (GDS2/Tech2Win/GlobalTIS installers, J2534/Mongoose
# drivers, firmware/calibration images, ISOs, scripts, docs, backups...),
# classifies them, and organizes them into a git-ready repository structure
# matching https://github.com/k1lllagt/saab-workshop -- the same shape as
# this repository's own vendor/ tree (see vendor/README.md and SECURITY).
#
# This installer never downloads, embeds, or redistributes third-party
# diagnostic software. It only organizes files that are ALREADY present on
# the device it runs on, into a structure the user (or the companion
# Windows launcher, see packaging/windows/saab_workshop/) can use locally.
# See SECURITY for the project's vendor-licensing policy.
#
# Usage:
#   ./Unified_Termux_Shell_Environment_Installer.sh [options]
#
# Options:
#   -y, --yes              Non-interactive; assume "yes" to prompts
#       --dry-run           Scan and classify, but do not copy/move/commit
#       --move               Move files instead of copying (default: copy)
#       --skip-pkg-install   Skip `pkg install` (useful outside Termux / CI)
#       --skip-storage-link  Skip termux-setup-storage
#       --scan-dirs=A:B:C    Override scan roots (colon-separated)
#       --repo-url=URL       Override target git remote
#       --repo-dir=PATH      Override local repo working tree path
#   -h, --help               Show this help and exit
# =============================================================================
set -euo pipefail
IFS=$'\n\t'

# -----------------------------------------------------------------------------
# Resolve script directory (works whether invoked via ./script.sh, bash
# script.sh, or a symlink) so the tools/workshop/*.sh libraries can always
# be found regardless of the caller's cwd.
# -----------------------------------------------------------------------------
saab_resolve_script_dir() {
    local src="${BASH_SOURCE[0]}"
    while [ -h "$src" ]; do
        local dir
        dir="$(cd -P "$(dirname -- "$src")" >/dev/null 2>&1 && pwd)"
        src="$(readlink -- "$src")"
        [[ "$src" != /* ]] && src="$dir/$src"
    done
    cd -P "$(dirname -- "$src")" >/dev/null 2>&1 && pwd
}

SCRIPT_DIR="$(saab_resolve_script_dir)"
WORKSHOP_LIB_DIR="$SCRIPT_DIR/tools/workshop"

for lib in file_organization file_structure.sh file_system.sh file_properties.sh; do
    lib_path="$WORKSHOP_LIB_DIR/$lib"
    if [ ! -f "$lib_path" ]; then
        echo "[FATAL] required library missing: $lib_path" >&2
        exit 1
    fi
    # shellcheck source=/dev/null
    source "$lib_path"
done
unset lib lib_path

# -----------------------------------------------------------------------------
# Global run state / defaults (overridable via CLI flags below)
# -----------------------------------------------------------------------------
OPT_YES=0
OPT_DRY_RUN=0
OPT_MOVE=0
OPT_SKIP_PKG_INSTALL=0
OPT_SKIP_STORAGE_LINK=0
OPT_SCAN_DIRS_OVERRIDE=""
OPT_REPO_URL_OVERRIDE=""
OPT_REPO_DIR_OVERRIDE=""

SCAN_FILES_TOTAL=0
SCAN_FILES_CLASSIFIED=0
SCAN_FILES_TRANSFERRED=0
SCAN_FILES_SKIPPED_DEDUP=0
SCAN_FILES_SKIPPED_SIZE=0
SCAN_FILES_SKIPPED_EXCLUDED=0
SCAN_FILES_FAILED=0

# -----------------------------------------------------------------------------
# saab_print_help
# -----------------------------------------------------------------------------
saab_print_help() {
    sed -n '2,33p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

# -----------------------------------------------------------------------------
# saab_parse_args
# -----------------------------------------------------------------------------
saab_parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            -y|--yes) OPT_YES=1 ;;
            --dry-run) OPT_DRY_RUN=1 ;;
            --move) OPT_MOVE=1 ;;
            --skip-pkg-install) OPT_SKIP_PKG_INSTALL=1 ;;
            --skip-storage-link) OPT_SKIP_STORAGE_LINK=1 ;;
            --scan-dirs=*) OPT_SCAN_DIRS_OVERRIDE="${1#*=}" ;;
            --repo-url=*) OPT_REPO_URL_OVERRIDE="${1#*=}" ;;
            --repo-dir=*) OPT_REPO_DIR_OVERRIDE="${1#*=}" ;;
            -h|--help) saab_print_help; exit 0 ;;
            *) echo "[FATAL] unknown option: $1" >&2; saab_print_help; exit 2 ;;
        esac
        shift
    done
}

# -----------------------------------------------------------------------------
# saab_confirm <prompt>
# Returns 0 (proceed) if OPT_YES=1 or the user answers y/Y; else returns 1.
# -----------------------------------------------------------------------------
saab_confirm() {
    local prompt="$1"
    if [ "$OPT_YES" -eq 1 ]; then
        return 0
    fi
    if [ ! -t 0 ]; then
        # Non-interactive shell with no --yes: default to proceeding, since
        # every step here is idempotent/non-destructive by design (copy
        # mode, .gitkeep-preserving mkdir -p, append-only manifest).
        return 0
    fi
    local reply
    read -r -p "$prompt [Y/n] " reply || true
    case "$reply" in
        [nN]*) return 1 ;;
        *) return 0 ;;
    esac
}

# -----------------------------------------------------------------------------
# saab_error_trap
# Installed via `trap` in main(). Logs the failing command/line before the
# shell exits under `set -e`.
# -----------------------------------------------------------------------------
saab_error_trap() {
    local exit_code=$?
    local line_no=$1
    saab_log ERROR "installer" "aborted at line $line_no (exit $exit_code)"
    exit "$exit_code"
}

# =============================================================================
# PHASE 1: bootstrap (pkg install, dependency verification)
# =============================================================================
saab_phase_bootstrap() {
    saab_log INFO "bootstrap" "phase 1/6: bootstrap"

    local req_file="$WORKSHOP_LIB_DIR/file_requirements.txt"
    [ -f "$req_file" ] || saab_die "requirements file not found: $req_file"

    if [ "$OPT_SKIP_PKG_INSTALL" -eq 1 ]; then
        saab_log WARN "bootstrap" "--skip-pkg-install set; not installing termux packages"
    elif command -v pkg >/dev/null 2>&1; then
        saab_log INFO "bootstrap" "updating package index"
        pkg update -y >>"${SAAB_LOG_FILE:-/dev/null}" 2>&1 || saab_log WARN "bootstrap" "pkg update reported a non-zero exit; continuing"

        local pkgs=()
        while IFS= read -r line; do
            [[ "$line" =~ ^pkg:(.+)$ ]] && pkgs+=("${BASH_REMATCH[1]}")
        done < "$req_file"

        if [ "${#pkgs[@]}" -gt 0 ]; then
            saab_log INFO "bootstrap" "installing ${#pkgs[@]} package(s): ${pkgs[*]}"
            pkg install -y "${pkgs[@]}" >>"${SAAB_LOG_FILE:-/dev/null}" 2>&1 \
                || saab_die "pkg install failed -- see $SAAB_LOG_FILE"
        fi
    else
        saab_log WARN "bootstrap" "'pkg' not found (not running under Termux); skipping package install"
    fi

    local missing=()
    while IFS= read -r line; do
        if [[ "$line" =~ ^bin:(.+)$ ]]; then
            local bin="${BASH_REMATCH[1]}"
            command -v "$bin" >/dev/null 2>&1 || missing+=("$bin")
        fi
    done < "$req_file"

    if [ "${#missing[@]}" -gt 0 ]; then
        saab_log WARN "bootstrap" "missing binaries after install: ${missing[*]} (continuing; some steps may be skipped)"
    else
        saab_log INFO "bootstrap" "all required binaries resolved"
    fi

    if command -v python3 >/dev/null 2>&1; then
        local pyreqs=()
        while IFS= read -r line; do
            [[ "$line" =~ ^pyreq:(.+)$ ]] && pyreqs+=("${BASH_REMATCH[1]}")
        done < "$req_file"
        if [ "${#pyreqs[@]}" -gt 0 ] && [ "$OPT_SKIP_PKG_INSTALL" -eq 0 ]; then
            saab_log INFO "bootstrap" "installing python requirements: ${pyreqs[*]}"
            python3 -m pip install --quiet --user "${pyreqs[@]}" >>"${SAAB_LOG_FILE:-/dev/null}" 2>&1 \
                || saab_log WARN "bootstrap" "pip install reported a non-zero exit; continuing"
        fi
    fi
}

# =============================================================================
# PHASE 2: environment + directory structure
# =============================================================================
saab_phase_environment() {
    saab_log INFO "environment" "phase 2/6: environment + directory structure"

    [ -n "$OPT_SCAN_DIRS_OVERRIDE" ] && export SAAB_WORKSHOP_SCAN_DIRS="$OPT_SCAN_DIRS_OVERRIDE"
    [ -n "$OPT_REPO_URL_OVERRIDE" ] && export SAAB_WORKSHOP_REPO_URL="$OPT_REPO_URL_OVERRIDE"
    [ -n "$OPT_REPO_DIR_OVERRIDE" ] && export SAAB_WORKSHOP_REPO="$OPT_REPO_DIR_OVERRIDE"
    [ "$OPT_MOVE" -eq 1 ] && export SAAB_WORKSHOP_COPY_MODE="move"

    saab_export_env
    saab_extend_path
    saab_bind_home_saab

    if [ "$OPT_SKIP_STORAGE_LINK" -eq 0 ]; then
        saab_link_storage
    else
        saab_log WARN "environment" "--skip-storage-link set; ~/storage and ~/sdcard left as-is"
    fi

    saab_create_directory_tree
    saab_validate_directory_tree || saab_die "directory structure validation failed"
    saab_generate_system_state
}

# =============================================================================
# PHASE 3: git repo initialization
# =============================================================================
saab_phase_git_init() {
    saab_log INFO "git" "phase 3/6: repository initialization"

    if [ -d "$SAAB_WORKSHOP_REPO/.git" ]; then
        saab_log INFO "git" "repo already initialized at $SAAB_WORKSHOP_REPO"
        return 0
    fi

    if ! command -v git >/dev/null 2>&1; then
        saab_log WARN "git" "git not available; skipping repo init (files will still be organized on disk)"
        return 0
    fi

    if [ "$OPT_DRY_RUN" -eq 1 ]; then
        saab_log INFO "git" "[dry-run] would initialize/clone $SAAB_WORKSHOP_REPO_URL into $SAAB_WORKSHOP_REPO"
        return 0
    fi

    if git ls-remote "$SAAB_WORKSHOP_REPO_URL" >/dev/null 2>&1; then
        saab_log INFO "git" "cloning $SAAB_WORKSHOP_REPO_URL into $SAAB_WORKSHOP_REPO"
        rmdir -- "$SAAB_WORKSHOP_REPO" 2>/dev/null || true
        git clone --quiet "$SAAB_WORKSHOP_REPO_URL" "$SAAB_WORKSHOP_REPO" \
            || saab_die "git clone failed for $SAAB_WORKSHOP_REPO_URL"
    else
        saab_log WARN "git" "remote unreachable/nonexistent; initializing local repo instead"
        mkdir -p -- "$SAAB_WORKSHOP_REPO"
        git -C "$SAAB_WORKSHOP_REPO" init --quiet
        git -C "$SAAB_WORKSHOP_REPO" remote add origin "$SAAB_WORKSHOP_REPO_URL" 2>/dev/null || true
    fi

    git -C "$SAAB_WORKSHOP_REPO" config user.name "${GIT_AUTHOR_NAME:-Saab Workshop Installer}" 2>/dev/null || true
    git -C "$SAAB_WORKSHOP_REPO" config user.email "${GIT_AUTHOR_EMAIL:-workshop-installer@localhost}" 2>/dev/null || true

    # Re-run the tree creator now that the repo exists so vendor/, docs/,
    # tools/, runtime/ all get created (and .gitkeep'd) inside it.
    saab_create_directory_tree
}

# =============================================================================
# PHASE 4: recursive scan + classification
# =============================================================================
saab_is_excluded() {
    local path="$1" pattern
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        [[ "$path" =~ $pattern ]] && return 0
    done
    return 1
}

saab_phase_scan() {
    saab_log INFO "scan" "phase 4/6: recursive scan of: $SAAB_WORKSHOP_SCAN_DIRS"

    local roots=()
    IFS=':' read -r -a roots <<< "$SAAB_WORKSHOP_SCAN_DIRS"

    local root max_bytes
    max_bytes=$(( ${SAAB_WORKSHOP_MAX_FILE_MB:-8192} * 1024 * 1024 ))

    for root in "${roots[@]}"; do
        [ -n "$root" ] || continue
        if [ ! -d "$root" ]; then
            saab_log WARN "scan" "scan root does not exist, skipping: $root"
            continue
        fi
        saab_log INFO "scan" "scanning: $root"

        while IFS= read -r -d '' file; do
            SCAN_FILES_TOTAL=$((SCAN_FILES_TOTAL + 1))

            if saab_is_excluded "$file"; then
                SCAN_FILES_SKIPPED_EXCLUDED=$((SCAN_FILES_SKIPPED_EXCLUDED + 1))
                continue
            fi

            local size
            size="$(stat -c '%s' -- "$file" 2>/dev/null || echo 0)"
            if [ "$size" -gt "$max_bytes" ]; then
                saab_log WARN "scan" "skipping oversized file ($((size / 1024 / 1024)) MB > limit): $file"
                SCAN_FILES_SKIPPED_SIZE=$((SCAN_FILES_SKIPPED_SIZE + 1))
                continue
            fi

            if saab_build_file_record "$file"; then
                SCAN_FILES_CLASSIFIED=$((SCAN_FILES_CLASSIFIED + 1))
            else
                SCAN_FILES_FAILED=$((SCAN_FILES_FAILED + 1))
            fi
        done < <(find "$root" -xdev -type f -print0 2>/dev/null || true)
    done

    saab_log INFO "scan" "scan complete: total=$SCAN_FILES_TOTAL classified=$SCAN_FILES_CLASSIFIED excluded=$SCAN_FILES_SKIPPED_EXCLUDED oversized=$SCAN_FILES_SKIPPED_SIZE failed=$SCAN_FILES_FAILED"
}

# =============================================================================
# PHASE 5: organize (transfer into repo structure) + manifest
# =============================================================================
saab_transfer_file() {
    local src="$1" dest_rel="$2" perms="$3"
    local dest_abs="$SAAB_WORKSHOP_REPO/$dest_rel"

    mkdir -p -- "$(dirname -- "$dest_abs")"

    if [ -e "$dest_abs" ] && [ "${SAAB_WORKSHOP_DEDUPLICATE:-1}" -eq 1 ]; then
        local existing_hash new_hash
        existing_hash="$(saab_hash_file "$dest_abs")"
        new_hash="$(saab_hash_file "$src")"
        if [ "$existing_hash" = "$new_hash" ]; then
            saab_log DEBUG "organize" "identical file already at destination, skipping: $dest_rel"
            SCAN_FILES_SKIPPED_DEDUP=$((SCAN_FILES_SKIPPED_DEDUP + 1))
            return 0
        fi
        # Name collision with different content: disambiguate by short hash.
        local short_hash="${new_hash:0:8}"
        dest_abs="${dest_abs%.*}.${short_hash}.${dest_abs##*.}"
    fi

    if [ "$OPT_DRY_RUN" -eq 1 ]; then
        saab_log INFO "organize" "[dry-run] would $SAAB_WORKSHOP_COPY_MODE: $src -> $dest_abs"
        return 0
    fi

    if [ "$SAAB_WORKSHOP_COPY_MODE" = "move" ]; then
        mv -- "$src" "$dest_abs"
    else
        cp -p -- "$src" "$dest_abs"
    fi
    chmod "$perms" -- "$dest_abs" 2>/dev/null || true

    if [ "${SAAB_WORKSHOP_VERIFY_BEFORE_MOVE:-1}" -eq 1 ]; then
        local src_hash dest_hash
        src_hash="$(saab_hash_file "$src")"
        # After a move, $src no longer exists; re-hash only in copy mode.
        if [ "$SAAB_WORKSHOP_COPY_MODE" != "move" ]; then
            dest_hash="$(saab_hash_file "$dest_abs")"
            if [ "$src_hash" != "$dest_hash" ]; then
                saab_log ERROR "organize" "post-transfer hash mismatch for $dest_abs (source=$src_hash dest=$dest_hash)"
                return 1
            fi
        fi
    fi

    SCAN_FILES_TRANSFERRED=$((SCAN_FILES_TRANSFERRED + 1))
    return 0
}

saab_phase_organize() {
    saab_log INFO "organize" "phase 5/6: organizing ${#FILE_RECORDS[@]} classified file(s) (mode=$SAAB_WORKSHOP_COPY_MODE, dry_run=$OPT_DRY_RUN)"

    local src record dest perms
    for src in "${!FILE_RECORDS[@]}"; do
        record="${FILE_RECORDS[$src]}"
        dest="$(saab_record_field "$record" 2)"
        perms="$(saab_record_field "$record" 3)"
        if ! saab_transfer_file "$src" "$dest" "$perms"; then
            SCAN_FILES_FAILED=$((SCAN_FILES_FAILED + 1))
        fi
    done

    local manifest_file="$SAAB_WORKSHOP_MANIFEST_DIR/manifest-$(date -u +%Y%m%dT%H%M%SZ).jsonl"
    saab_flush_manifest "$manifest_file"

    if [ -d "$SAAB_WORKSHOP_REPO/manifests" ]; then
        cp -p -- "$manifest_file" "$SAAB_WORKSHOP_REPO/manifests/" 2>/dev/null || true
        cp -p -- "$manifest_file.sha256" "$SAAB_WORKSHOP_REPO/manifests/" 2>/dev/null || true
    fi

    saab_log INFO "organize" "transferred=$SCAN_FILES_TRANSFERRED deduped=$SCAN_FILES_SKIPPED_DEDUP failed=$SCAN_FILES_FAILED"
}

# =============================================================================
# PHASE 6: git commit + validation + summary
# =============================================================================
saab_phase_finalize() {
    saab_log INFO "finalize" "phase 6/6: git staging + validation + summary"

    if [ -d "$SAAB_WORKSHOP_REPO/.git" ] && [ "$OPT_DRY_RUN" -eq 0 ] && command -v git >/dev/null 2>&1; then
        git -C "$SAAB_WORKSHOP_REPO" add -A
        if ! git -C "$SAAB_WORKSHOP_REPO" diff --cached --quiet; then
            git -C "$SAAB_WORKSHOP_REPO" commit --quiet -m "workshop: organize $SCAN_FILES_TRANSFERRED file(s) via Unified_Termux_Shell_Environment_Installer.sh"
            saab_log INFO "finalize" "committed changes locally in $SAAB_WORKSHOP_REPO"
            saab_log INFO "finalize" "push manually when ready: git -C \"$SAAB_WORKSHOP_REPO\" push -u origin HEAD"
        else
            saab_log INFO "finalize" "nothing new to commit"
        fi
    fi

    saab_validate_directory_tree || saab_log WARN "finalize" "post-run validation reported problems (see above)"
    saab_print_structure_map

    saab_log INFO "summary" "=============================================="
    saab_log INFO "summary" " SAAB WORKSHOP INSTALL SUMMARY"
    saab_log INFO "summary" "=============================================="
    saab_log INFO "summary" " scanned roots     : $SAAB_WORKSHOP_SCAN_DIRS"
    saab_log INFO "summary" " files found       : $SCAN_FILES_TOTAL"
    saab_log INFO "summary" " files classified  : $SCAN_FILES_CLASSIFIED"
    saab_log INFO "summary" " files transferred : $SCAN_FILES_TRANSFERRED"
    saab_log INFO "summary" " deduped (skipped) : $SCAN_FILES_SKIPPED_DEDUP"
    saab_log INFO "summary" " excluded          : $SCAN_FILES_SKIPPED_EXCLUDED"
    saab_log INFO "summary" " oversized skipped : $SCAN_FILES_SKIPPED_SIZE"
    saab_log INFO "summary" " failed            : $SCAN_FILES_FAILED"
    saab_log INFO "summary" " repo              : $SAAB_WORKSHOP_REPO"
    saab_log INFO "summary" " manifest dir      : $SAAB_WORKSHOP_MANIFEST_DIR"
    saab_log INFO "summary" " log file          : $SAAB_LOG_FILE"
    saab_log INFO "summary" "=============================================="
    saab_log INFO "summary" " Next steps:"
    saab_log INFO "summary" "   1. Review $SAAB_WORKSHOP_REPO before pushing anywhere."
    saab_log INFO "summary" "   2. To build the Windows companion launcher, see"
    saab_log INFO "summary" "      packaging/windows/BUILD.md in this repository."
    saab_log INFO "summary" "   3. This installer never bundles OEM software -- point"
    saab_log INFO "summary" "      the launcher at your own already-licensed vendor"
    saab_log INFO "summary" "      files. See SECURITY for the full policy."
    saab_log INFO "summary" "=============================================="
}

# =============================================================================
# main
# =============================================================================
main() {
    trap 'saab_error_trap $LINENO' ERR
    saab_parse_args "$@"

    echo "=============================================="
    echo " Unified Termux Shell Environment Installer"
    echo " SAAB_SUITE Workshop Bootstrap"
    echo "=============================================="

    if ! saab_confirm "This will bootstrap Termux packages and scan/organize files on this device. Continue?"; then
        echo "Aborted by user."
        exit 0
    fi

    saab_phase_bootstrap
    saab_phase_environment
    saab_phase_git_init
    saab_phase_scan
    saab_phase_organize
    saab_phase_finalize

    saab_log INFO "installer" "done"
}

main "$@"
