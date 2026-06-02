"""Ports -- abstract interfaces. Implemented by adapters, consumed by services."""

from saab_suite.ports.audit_log import IAuditLog
from saab_suite.ports.calibration_store import ICalibrationStore
from saab_suite.ports.can_sink import ICanSink
from saab_suite.ports.can_source import CanSourceStats, ICanSource
from saab_suite.ports.firmware_store import IFirmwareStore
from saab_suite.ports.flash_target import IFlashTarget
from saab_suite.ports.isotp import IIsoTpTransport
from saab_suite.ports.j2534 import IJ2534Device
from saab_suite.ports.kwp2000 import IKwpClient
from saab_suite.ports.uds import IUdsClient
from saab_suite.ports.vehicle_state import IVehicleStateProvider, VehicleState

__all__ = [
    "CanSourceStats", "IAuditLog", "ICalibrationStore", "ICanSink", "ICanSource",
    "IFirmwareStore", "IFlashTarget", "IIsoTpTransport", "IJ2534Device",
    "IKwpClient", "IUdsClient", "IVehicleStateProvider", "VehicleState",
]
