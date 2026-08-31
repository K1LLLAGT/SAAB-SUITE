"""Flash target port definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from saab_suite.domain.firmware.image import FirmwareImage


class IFlashTarget(Protocol):
    """Define the programmable ECU target interface."""

    @property
    def family(self) -> str:
        """Return the target family name."""
        ...

    def enter_programming_mode(self) -> None:
        """Put the target into programming mode."""
        ...

    def authenticate(self) -> None:
        """Authenticate with the target before flashing."""
        ...

    def erase(self, region_start: int, region_end: int) -> None:
        """Erase a target memory region."""
        ...

    def transfer(self, image: FirmwareImage) -> None:
        """Transfer a firmware image to the target."""
        ...

    def verify(self, image: FirmwareImage) -> bool:
        """Verify a transferred firmware image."""
        ...

    def finalize(self) -> None:
        """Finalize the flash session."""
        ...
