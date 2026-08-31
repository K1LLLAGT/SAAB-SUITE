# -*- mode: python ; coding: utf-8 -*-
# PyInstaller build spec for saab-workshop.exe.
#
# Build with:  pyinstaller saab_workshop.spec
# (run from packaging/windows/, on a Windows host with Python 3.11+ and
#  `pip install pyinstaller` -- see BUILD.md in this directory)
#
# Deliberately bundles ONLY this package's own Python source. It does NOT
# bundle, embed, or reference any GDS2/Tech2Win/GlobalTIS/WIS/EPC/J2534
# binary, driver, or ISO. Those are supplied by the user at runtime via
# `saab-workshop extract --source <folder>` and land under
# %USERPROFILE%\SaabWorkshop\vendor\. See BUILD.md and the root SECURITY
# file for the full policy.

import sys
from pathlib import Path

block_cipher = None
SPEC_DIR = Path(SPECPATH)  # noqa: F821 -- PyInstaller injects SPECPATH

a = Analysis(  # noqa: F821 -- PyInstaller injects Analysis at spec-eval time
    [str(SPEC_DIR / "entrypoint.py")],
    pathex=[str(SPEC_DIR)],
    binaries=[],
    # Only non-code assets belonging to THIS application (icon, default
    # config template). No vendor/ payload is ever listed here.
    datas=[],
    hiddenimports=["tkinter"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="saab-workshop",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
