# Developer Onboarding

## Setup

    git clone <YOUR_REPO_URL> SAAB_SUITE
    cd SAAB_SUITE
    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"

## Layout
- src/SAAB_SUITE/
- plugins/
- runtime/
- vendor/
- packaging/
- tests/

## Commands

    tools/format.sh
    tools/lint.sh
    tools/typecheck.sh
    tools/test.sh
