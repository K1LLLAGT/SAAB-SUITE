"""Result type for fallible operations that should not raise."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeAlias, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """Successful result wrapping a value."""

    value: T

    def is_ok(self) -> bool:
        """Return whether ok."""
        return True

    def is_err(self) -> bool:
        """Return whether err."""
        return False

    def unwrap(self) -> T:
        """Unwrap."""
        return self.value


@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """Failed result wrapping an error value."""

    error: E

    def is_ok(self) -> bool:
        """Return whether ok."""
        return False

    def is_err(self) -> bool:
        """Return whether err."""
        return True

    def unwrap(self) -> object:
        """Unwrap."""
        msg = f"Called unwrap() on Err({self.error!r})"
        raise ValueError(msg)


Result: TypeAlias = Ok[T] | Err[E]
