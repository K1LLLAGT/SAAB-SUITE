"""Ports -- abstract interfaces. Implemented by adapters, consumed by services."""

from SAAB_SUITE.ports.audit_log import IAuditLog
from SAAB_SUITE.ports.calibration_store import ICalibrationStore
from SAAB_SUITE.ports.can_sink import ICanSink
from SAAB_SUITE.ports.can_source import CanSourceStats, ICanSource
from SAAB_SUITE.ports.firmware_store import IFirmwareStore
from SAAB_SUITE.ports.flash_target import IFlashTarget
from SAAB_SUITE.ports.isotp import IIsoTpTransport
from SAAB_SUITE.ports.j2534 import IJ2534Device
from SAAB_SUITE.ports.kwp2000 import IKwpClient
from SAAB_SUITE.ports.uds import IUdsClient
from SAAB_SUITE.ports.vehicle_state import IVehicleStateProvider, VehicleState

__all__ = [
    "CanSourceStats", "IAuditLog", "ICalibrationStore", "ICanSink", "ICanSource",
    "IFirmwareStore", "IFlashTarget", "IIsoTpTransport", "IJ2534Device",
    "IKwpClient", "IUdsClient", "IVehicleStateProvider", "VehicleState",
]
