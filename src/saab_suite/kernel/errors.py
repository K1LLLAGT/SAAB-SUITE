"""Exception hierarchy for the entire suite.

Every project exception derives from :class:`SaabSuiteError`. Each layer has
its own root so handlers can catch by layer.

Adapters MUST translate underlying library exceptions into AdapterError
subclasses before letting them cross the port boundary.
"""

from __future__ import annotations


class SaabSuiteError(Exception):
    """Root of all suite exceptions."""


class KernelError(SaabSuiteError):
    """Failure in primitive layer (clock, result, types)."""


class DomainError(SaabSuiteError):
    """Domain invariant violation. Raised at value-object construction."""


class InvalidVinError(DomainError):
    """VIN failed validation (length, charset, check digit)."""


class InvalidCanFrameError(DomainError):
    """CAN frame violates DLC/ID constraints."""


class InvalidCalibrationError(DomainError):
    """Calibration metadata malformed or internally inconsistent."""


class PortError(SaabSuiteError):
    """Port contract violated by an adapter."""


class ServiceError(SaabSuiteError):
    """Use-case failure. Carries enough context for the interface to render."""


class DiscoveryError(ServiceError):
    """Module discovery failed."""


class DiagnosticsError(ServiceError):
    """Diagnostic operation failed."""


class VinResolutionError(ServiceError):
    """VIN could not be resolved to a profile."""


class SpsError(ServiceError):
    """Base for all SPS-related failures."""


class PrecheckFailed(SpsError):
    """SPS precheck blocked the operation."""


class PlanValidationError(SpsError):
    """Flash plan failed validation."""


class InterlockFailure(SpsError):
    """A single interlock check failed. Aggregated by the validator."""


class FlashAborted(SpsError):
    """Flash session aborted (user, transport, hardware)."""


class FlashTimeout(SpsError):
    """A flash transfer step exceeded its timeout."""


class AdapterError(SaabSuiteError):
    """Base for I/O failures translated at the adapter boundary."""


class J2534Error(AdapterError):
    """J2534 device error."""


class CanBusError(AdapterError):
    """CAN bus-level failure."""


class IsoTpError(AdapterError):
    """ISO 15765-2 transport failure."""


class UdsError(AdapterError):
    """ISO 14229 / UDS protocol error."""


class NegativeResponseError(UdsError):
    """UDS server returned a negative response (0x7F + NRC)."""

    def __init__(self, service: int, nrc: int, message: str = "") -> None:
        super().__init__(message or f"NRC 0x{nrc:02X} for service 0x{service:02X}")
        self.service = service
        self.nrc = nrc


class KwpError(AdapterError):
    """ISO 14230 / KWP2000 protocol error."""


class StoreError(AdapterError):
    """Persistence failure (calibration, firmware, audit, config)."""
