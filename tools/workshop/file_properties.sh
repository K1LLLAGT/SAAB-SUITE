#!/usr/bin/env bash
# =============================================================================
# file_properties.sh
# SAAB_SUITE / Termux Workshop Environment -- per-file property engine
#
# Responsibilities:
#   1. Classify a discovered file into a category (via file_organization).
#   2. Compute its SHA256 hash.
#   3. Build a full property record for it (type, category, destination,
#      permissions, required/optional, size, mtime, source path).
#   4. Persist that record as one JSON line in the run's manifest file.
#
# This file is sourced by Unified_Termux_Shell_Environment_Installer.sh. It
# assumes file_organization and file_structure.sh have already been sourced
# (for CATEGORY_* / EXT_RULES / NAME_RULES and for `saab_log`).
# =============================================================================

if [ -n "${SAAB_FILE_PROPERTIES_LOADED:-}" ]; then
    return 0 2>/dev/null || exit 0
fi
SAAB_FILE_PROPERTIES_LOADED=1

# FILE_RECORDS: absolute source path -> "|"-delimited property record.
# Populated by saab_build_file_record. Acts as the in-memory manifest before
# it is flushed to JSONL.
declare -A FILE_RECORDS=()

# FILE_RECORD_COUNT: running total, used for progress logging.
FILE_RECORD_COUNT=0

# -----------------------------------------------------------------------------
# saab_hash_file <path>
# Prints the SHA256 hex digest of <path>, or "0"*64 if it cannot be read.
# -----------------------------------------------------------------------------
saab_hash_file() {
    local path="$1"
    if [ -r "$path" ]; then
        sha256sum -- "$path" 2>/dev/null | awk '{print $1}'
    else
        printf '%064d' 0
    fi
}

# -----------------------------------------------------------------------------
# saab_classify_file <path>
# Prints the category key for <path>, applying NAME_RULES (regex against
# basename, case-insensitive, first match wins) then falling back to
# EXT_RULES (extension lookup), then "unknown".
# -----------------------------------------------------------------------------
saab_classify_file() {
    local path="$1"
    local base rule pattern category ext
    base="$(basename -- "$path")"
    local base_lc
    base_lc="$(printf '%s' "$base" | tr '[:upper:]' '[:lower:]')"

    for rule in "${NAME_RULES[@]}"; do
        pattern="${rule%%|||*}"
        category="${rule##*|||}"
        if [[ "$base_lc" =~ $pattern ]]; then
            printf '%s' "$category"
            return 0
        fi
    done

    if [[ "$base" == *.* ]]; then
        ext="$(printf '%s' "${base##*.}" | tr '[:upper:]' '[:lower:]')"
        if [ -n "${EXT_RULES[$ext]:-}" ]; then
            printf '%s' "${EXT_RULES[$ext]}"
            return 0
        fi
    fi

    printf 'unknown'
}

# -----------------------------------------------------------------------------
# saab_file_type <path>
# Prints a short MIME-ish type string via `file`, falling back to "unknown".
# -----------------------------------------------------------------------------
saab_file_type() {
    local path="$1"
    if command -v file >/dev/null 2>&1 && [ -r "$path" ]; then
        file --brief --mime-type -- "$path" 2>/dev/null || printf 'application/octet-stream'
    else
        printf 'application/octet-stream'
    fi
}

# -----------------------------------------------------------------------------
# saab_json_escape <string>
# Minimal JSON string escaper (backslash, quote, control chars) -- enough for
# filesystem paths and file(1) output; avoids a hard `jq` dependency for the
# hot path even though jq is listed as a requirement for downstream tooling.
# -----------------------------------------------------------------------------
saab_json_escape() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}

# -----------------------------------------------------------------------------
# saab_build_file_record <source_path>
# Computes the full property record for <source_path> and stores it in
# FILE_RECORDS. Record fields (pipe-delimited):
#   category|dest_dir|perms|required|sha256|mime|size_bytes|mtime_epoch|source
# -----------------------------------------------------------------------------
saab_build_file_record() {
    local src="$1"
    [ -f "$src" ] || return 1

    local category dest_dir perms required sha256 mime size mtime sanitized
    category="$(saab_classify_file "$src")"
    dest_dir="${CATEGORY_DEST[$category]:-vendor/legacy_archive}"
    perms="${CATEGORY_PERMS[$category]:-640}"
    required="${CATEGORY_REQUIRED[$category]:-optional}"
    sha256="$(saab_hash_file "$src")"
    mime="$(saab_file_type "$src")"
    size="$(stat -c '%s' -- "$src" 2>/dev/null || echo 0)"
    mtime="$(stat -c '%Y' -- "$src" 2>/dev/null || echo 0)"
    sanitized="$(saab_sanitize_filename "$(basename -- "$src")")"

    FILE_RECORDS["$src"]="${category}|${dest_dir}/${sanitized}|${perms}|${required}|${sha256}|${mime}|${size}|${mtime}|${src}"
    FILE_RECORD_COUNT=$((FILE_RECORD_COUNT + 1))
    return 0
}

# -----------------------------------------------------------------------------
# saab_record_field <record> <index>
# Extracts field <index> (1-based) from a pipe-delimited record.
# -----------------------------------------------------------------------------
saab_record_field() {
    local record="$1" index="$2"
    printf '%s' "$record" | cut -d'|' -f"$index"
}

# -----------------------------------------------------------------------------
# saab_manifest_jsonl_line <source_path>
# Emits one JSONL manifest line for a source path already present in
# FILE_RECORDS.
# -----------------------------------------------------------------------------
saab_manifest_jsonl_line() {
    local src="$1"
    local record="${FILE_RECORDS[$src]:-}"
    [ -n "$record" ] || return 1

    local category dest perms required sha256 mime size mtime
    category="$(saab_record_field "$record" 1)"
    dest="$(saab_record_field "$record" 2)"
    perms="$(saab_record_field "$record" 3)"
    required="$(saab_record_field "$record" 4)"
    sha256="$(saab_record_field "$record" 5)"
    mime="$(saab_record_field "$record" 6)"
    size="$(saab_record_field "$record" 7)"
    mtime="$(saab_record_field "$record" 8)"

    printf '{"source":"%s","category":"%s","label":"%s","destination":"%s","permissions":"%s","required":"%s","sha256":"%s","mime":"%s","size_bytes":%s,"mtime_epoch":%s,"scanned_at":"%s"}\n' \
        "$(saab_json_escape "$src")" \
        "$(saab_json_escape "$category")" \
        "$(saab_json_escape "${CATEGORY_LABEL[$category]:-Unclassified}")" \
        "$(saab_json_escape "$dest")" \
        "$perms" \
        "$required" \
        "$sha256" \
        "$(saab_json_escape "$mime")" \
        "$size" \
        "$mtime" \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

# -----------------------------------------------------------------------------
# saab_flush_manifest <manifest_path>
# Writes every FILE_RECORDS entry to <manifest_path> as JSONL (one JSON
# object per line, append mode so repeated runs accumulate history), then
# also writes a companion <manifest_path>.sha256 checksum-of-the-manifest
# file so the Windows-side launcher can detect a corrupted/tampered
# manifest before trusting any per-file hash inside it.
# -----------------------------------------------------------------------------
saab_flush_manifest() {
    local manifest_path="$1"
    local src

    mkdir -p -- "$(dirname -- "$manifest_path")"
    : > "$manifest_path.tmp"

    for src in "${!FILE_RECORDS[@]}"; do
        saab_manifest_jsonl_line "$src" >> "$manifest_path.tmp"
    done

    sort -o "$manifest_path.tmp" -- "$manifest_path.tmp"
    cat -- "$manifest_path.tmp" >> "$manifest_path"
    rm -f -- "$manifest_path.tmp"

    sha256sum -- "$manifest_path" > "$manifest_path.sha256"

    saab_log INFO "manifest" "wrote ${FILE_RECORD_COUNT} record(s) to $manifest_path"
}
