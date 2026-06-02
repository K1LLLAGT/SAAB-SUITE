"""CAN adapters.

Public API:
    CanFrame        - the frame type (defined once, in interface.py)
    CanSource       - the backend contract every source implements
    CanInterface    - python-can-backed source (socketcan / slcan / pcan / ...)
    RemoteCanInterface - TCP bridge source
    open_source     - factory that returns the configured CanSource
"""

from __future__ import annotations

from saab_suite.adapters.can.interface import CanFrame, CanInterface, CanSource
from saab_suite.adapters.can.remote_interface import RemoteCanInterface

# Backend sources — uncomment as you confirm each module's public class name:
# from saab_suite.adapters.can.mock_source import MockCanSource
# from saab_suite.adapters.can.replay_source import ReplayCanSource
# from saab_suite.adapters.can.j2534_source import J2534CanSource

__all__ = [
    "CanFrame",
    "CanSource",
    "CanInterface",
    "RemoteCanInterface",
    "open_source",
]


def open_source(mode: str | None = None) -> CanSource:
    """Return an (unopened) CanSource for the given mode.

    Modes that map to a python-can bustype (socketcan, slcan/canusb, pcan)
    are all served by CanInterface via runtime config, so they don't need a
    bespoke class. Bespoke backends (mock, replay, j2534, remote) dispatch here.
    """
    mode = (mode or "hardware").lower()
    if mode == "remote":
        return RemoteCanInterface()
    if mode in {"hardware", "socketcan", "canusb", "slcan", "pcan"}:
        return CanInterface()
    # if mode in {"mock"}:  return MockCanSource()
    # if mode in {"replay"}: return ReplayCanSource()
    # if mode in {"j2534"}:  return J2534CanSource()
    raise ValueError(f"unknown CAN mode: {mode!r}")
