"""
GDS2 and Tech2Win integration helpers.

GDS2 (Global Diagnostic System 2) and Tech2Win are GM's primary dealer
diagnostic tools.  This module provides:
 - Detection of locally-installed GDS2 / Tech2Win installations.
 - Launch helpers that configure the correct J2534 device and vehicle
   identification before handing control to the OEM software.
 - A bridge class that allows SAAB-SUITE to co-operate with GDS2 while
   it is running (e.g. to capture traffic or inject custom routines).

.. note::
    GDS2 and Tech2Win must be separately licensed and installed.  This
    module does NOT redistribute or bypass any OEM software.
"""
from __future__ import annotations

import logging
import os
import platform
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# GDS2 integration
# ---------------------------------------------------------------------------

@dataclass
class GDS2Integration:
    """
    Locate and launch GDS2 with the correct device configuration.

    Args:
        install_dir: Path to the GDS2 installation directory.
                     Auto-detected if None.
        device_name: J2534 device name as registered in GDS2.
        vin:         VIN to pre-populate when launching GDS2.
    """

    install_dir: Optional[str] = None
    device_name: str = "GM MDI"
    vin: str = ""

    # Default installation paths per OS
    _DEFAULT_PATHS: dict[str, list[str]] = field(default_factory=lambda: {
        "Windows": [
            r"C:\Program Files (x86)\GM\GDS2",
            r"C:\Program Files\GM\GDS2",
            r"C:\GDS2",
        ],
        "Linux": [
            "/opt/gm/gds2",
            os.path.expanduser("~/GDS2"),
        ],
        "Darwin": [
            "/Applications/GDS2",
        ],
    }, init=False, repr=False)

    def detect_installation(self) -> Optional[Path]:
        """
        Search for a GDS2 installation on the current system.

        Returns:
            Path to the installation directory, or None if not found.
        """
        if self.install_dir:
            p = Path(self.install_dir)
            return p if p.exists() else None

        os_name = platform.system()
        for candidate in self._DEFAULT_PATHS.get(os_name, []):
            p = Path(candidate)
            if p.exists():
                logger.info("Found GDS2 at: %s", p)
                return p
        logger.warning("GDS2 installation not found.")
        return None

    def launch(self, extra_args: Optional[list[str]] = None) -> Optional[subprocess.Popen]:
        """
        Launch GDS2 as a sub-process.

        Args:
            extra_args: Additional command-line arguments for GDS2.

        Returns:
            The :class:`subprocess.Popen` object, or None if launch failed.
        """
        install_path = self.detect_installation()
        if install_path is None:
            logger.error("Cannot launch GDS2 – installation not found.")
            return None

        executable = self._find_executable(install_path)
        if executable is None:
            logger.error("GDS2 executable not found in %s", install_path)
            return None

        cmd = [str(executable)]
        if self.device_name:
            cmd += ["--device", self.device_name]
        if self.vin:
            cmd += ["--vin", self.vin]
        if extra_args:
            cmd.extend(extra_args)

        logger.info("Launching GDS2: %s", " ".join(cmd))
        try:
            return subprocess.Popen(cmd)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to launch GDS2: %s", exc)
            return None

    def get_version(self) -> Optional[str]:
        """Read the installed GDS2 version string."""
        install_path = self.detect_installation()
        if install_path is None:
            return None
        version_file = install_path / "version.txt"
        if version_file.exists():
            return version_file.read_text(encoding="utf-8").strip()
        # Try manifest / registry
        if platform.system() == "Windows":
            return self._read_registry_version()
        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_executable(install_path: Path) -> Optional[Path]:
        candidates = ["GDS2.exe", "gds2", "GDS2.sh", "launch.bat"]
        for name in candidates:
            p = install_path / name
            if p.exists():
                return p
        # Search one level deep
        for p in install_path.iterdir():
            if p.is_file() and "gds" in p.name.lower():
                return p
        return None

    @staticmethod
    def _read_registry_version() -> Optional[str]:
        try:
            import winreg  # type: ignore
            key = r"SOFTWARE\WOW6432Node\GM\GDS2"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as k:
                version, _ = winreg.QueryValueEx(k, "Version")
                return str(version)
        except Exception:  # noqa: BLE001
            return None


# ---------------------------------------------------------------------------
# Tech2Win bridge
# ---------------------------------------------------------------------------

@dataclass
class Tech2WinBridge:
    """
    Integration bridge for Tech2Win (emulates SAAB Tech2 cartridges on PC).

    Tech2Win runs inside a VMware virtual machine image provided by GM.
    This class manages the VM lifecycle and provides helpers for passing
    J2534 traffic through to Tech2Win.

    Args:
        vm_path:     Path to the Tech2Win VMware image (.vmx file).
        vmrun_path:  Path to the ``vmrun`` executable.
        j2534_device: J2534 device name to pass through to the VM.
    """

    vm_path: Optional[str] = None
    vmrun_path: str = "vmrun"
    j2534_device: str = "GM MDI"

    _DEFAULT_VM_PATHS: list[str] = field(default_factory=lambda: [
        r"C:\Program Files (x86)\GM\Tech2Win\Tech2Win.vmx",
        r"C:\Tech2Win\Tech2Win.vmx",
        os.path.expanduser("~/Tech2Win/Tech2Win.vmx"),
    ], init=False, repr=False)

    def find_vm(self) -> Optional[Path]:
        """Locate the Tech2Win VMware image file."""
        if self.vm_path:
            p = Path(self.vm_path)
            return p if p.exists() else None
        for candidate in self._DEFAULT_VM_PATHS:
            p = Path(candidate)
            if p.exists():
                return p
        logger.warning("Tech2Win VM image not found.")
        return None

    def start_vm(self, headless: bool = False) -> bool:
        """
        Start the Tech2Win virtual machine.

        Args:
            headless: Run without a GUI (not recommended for Tech2Win).

        Returns:
            True on success.
        """
        vm = self.find_vm()
        if vm is None:
            logger.error("Tech2Win VM not found – cannot start.")
            return False
        gui_flag = "nogui" if headless else "gui"
        cmd = [self.vmrun_path, "start", str(vm), gui_flag]
        logger.info("Starting Tech2Win VM: %s", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("vmrun error: %s", result.stderr.strip())
            return False
        return True

    def stop_vm(self, graceful: bool = True) -> bool:
        """Stop the Tech2Win VM."""
        vm = self.find_vm()
        if vm is None:
            return False
        stop_mode = "soft" if graceful else "hard"
        cmd = [self.vmrun_path, "stop", str(vm), stop_mode]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

    def vm_status(self) -> str:
        """Return ``"running"``, ``"stopped"``, or ``"unknown"``."""
        vm = self.find_vm()
        if vm is None:
            return "unknown"
        cmd = [self.vmrun_path, "list"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if str(vm) in result.stdout:
                return "running"
            return "stopped"
        except Exception:  # noqa: BLE001
            return "unknown"
