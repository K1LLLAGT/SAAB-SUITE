#!/usr/bin/env bash
set -euo pipefail

changed_python_files() {
  local base_ref=""
  if [[ -n "${GITHUB_BASE_REF:-}" ]] && git rev-parse --verify "origin/${GITHUB_BASE_REF}" >/dev/null 2>&1; then
    base_ref="origin/${GITHUB_BASE_REF}"
  elif git rev-parse --verify HEAD~1 >/dev/null 2>&1; then
    base_ref="HEAD~1"
  fi

  if [[ -n "${base_ref}" ]]; then
    git diff --name-only --diff-filter=ACMR "${base_ref}...HEAD" -- "*.py"
  else
    git ls-files "*.py"
  fi
}

mapfile -t targets < <(changed_python_files)
mypy_targets=()

for target in "${targets[@]}"; do
  if [[ "${target}" == src/SAAB_SUITE/* || "${target}" == packaging/windows/* ]]; then
    mypy_targets+=("${target}")
  fi
done

if [[ ${#mypy_targets[@]} -eq 0 ]]; then
  echo "No typed Python files changed; skipping mypy."
  exit 0
fi

mypy "${mypy_targets[@]}"
