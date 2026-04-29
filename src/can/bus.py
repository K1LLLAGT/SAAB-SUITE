"""
CAN bus abstraction layer.

Wraps python-can (when available) and provides a consistent interface for
transmitting and receiving CAN frames regardless of the underlying hardware
adapter (SocketCAN, Kvaser, PEAK PCAN, Vector, J2534, etc.).
"""
from __future__ import annotations

import logging
import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CAN frame
# ---------------------------------------------------------------------------

@dataclass
class CANFrame:
    """Represents a single CAN or CAN-FD frame."""

    arbitration_id: int
    data: bytes
    timestamp: float = field(default_factory=time.monotonic)
    is_extended_id: bool = False
    is_fd: bool = False
    is_remote_frame: bool = False
    channel: Optional[int] = None

    def __str__(self) -> str:
        id_str = f"0x{self.arbitration_id:08X}" if self.is_extended_id else f"0x{self.arbitration_id:03X}"
        data_str = " ".join(f"{b:02X}" for b in self.data)
        return f"[{id_str}] {data_str}"


# ---------------------------------------------------------------------------
# CAN bus
# ---------------------------------------------------------------------------

class CANBus:
    """
    High-level CAN bus interface for SAAB/GM diagnostics.

    Supports filtering, frame capture, and a callback-based receive model.

    Args:
        interface:  python-can interface name (``"socketcan"``, ``"kvaser"``,
                    ``"pcan"``, ``"vector"``, ``"ixxat"``, ``"usb2can"`` …).
        channel:    Channel identifier (e.g. ``"can0"`` for SocketCAN, or
                    channel index for hardware adapters).
        bitrate:    CAN bitrate in bits/s (default 500 kbps for SAAB/GM).
        fd_mode:    Enable CAN-FD mode (not required for most SAAB/GM ECUs).
    """

    def __init__(
        self,
        interface: str = "socketcan",
        channel: str = "can0",
        bitrate: int = 500_000,
        fd_mode: bool = False,
    ) -> None:
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate
        self.fd_mode = fd_mode

        self._bus: Optional[object] = None
        self._rx_thread: Optional[threading.Thread] = None
        self._rx_queue: queue.Queue[CANFrame] = queue.Queue(maxsize=1000)
        self._callbacks: list[Callable[[CANFrame], None]] = []
        self._filters: list[dict] = []
        self._running = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def open(self) -> None:
        """Open the CAN bus and start the receive thread."""
        if self._running:
            logger.warning("CANBus already open.")
            return
        self._bus = self._create_bus()
        self._running = True
        self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True, name="can-rx")
        self._rx_thread.start()
        logger.info("CANBus opened: %s %s @ %d bps", self.interface, self.channel, self.bitrate)

    def close(self) -> None:
        """Stop the receive thread and close the bus."""
        self._running = False
        if self._rx_thread:
            self._rx_thread.join(timeout=2.0)
        if self._bus:
            try:
                self._bus.shutdown()  # type: ignore[union-attr]
            except Exception:  # noqa: BLE001
                pass
        self._bus = None
        logger.info("CANBus closed.")

    def __enter__(self) -> "CANBus":
        self.open()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Sending
    # ------------------------------------------------------------------

    def send(self, frame: CANFrame) -> None:
        """Transmit *frame* on the bus."""
        if not self._running or self._bus is None:
            raise RuntimeError("CANBus is not open.")
        try:
            import can  # type: ignore
            msg = can.Message(
                arbitration_id=frame.arbitration_id,
                data=frame.data,
                is_extended_id=frame.is_extended_id,
                is_remote_frame=frame.is_remote_frame,
                is_fd=frame.is_fd,
            )
            self._bus.send(msg)  # type: ignore[union-attr]
        except ImportError:
            logger.debug("python-can not available; frame not transmitted: %s", frame)

    def send_raw(self, arb_id: int, data: bytes, extended: bool = False) -> None:
        """Convenience wrapper to send a raw frame."""
        self.send(CANFrame(arbitration_id=arb_id, data=data, is_extended_id=extended))

    # ------------------------------------------------------------------
    # Receiving
    # ------------------------------------------------------------------

    def recv(self, timeout: float = 1.0) -> Optional[CANFrame]:
        """
        Block and return the next received frame, or None on timeout.

        Args:
            timeout: Seconds to wait.
        """
        try:
            return self._rx_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def add_callback(self, fn: Callable[[CANFrame], None]) -> None:
        """Register *fn* to be called for every received frame."""
        self._callbacks.append(fn)

    def remove_callback(self, fn: Callable[[CANFrame], None]) -> None:
        self._callbacks.discard(fn)  # type: ignore[attr-defined]

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def set_filters(self, filters: list[dict]) -> None:
        """
        Set hardware/software acceptance filters.

        Each filter dict must have ``"can_id"`` and ``"can_mask"`` keys,
        and an optional ``"extended"`` boolean.

        Example::

            bus.set_filters([
                {"can_id": 0x7E8, "can_mask": 0x7F8, "extended": False},
            ])
        """
        self._filters = filters
        if self._bus is not None:
            try:
                self._bus.set_filters(filters)  # type: ignore[union-attr]
            except Exception:  # noqa: BLE001
                pass

    # ------------------------------------------------------------------
    # Capture / replay
    # ------------------------------------------------------------------

    def capture(self, duration: float, output_path: Optional[str] = None) -> list[CANFrame]:
        """
        Capture all frames for *duration* seconds.

        Args:
            duration:    Capture window in seconds.
            output_path: If given, write captured frames to a CSV file.

        Returns:
            List of captured :class:`CANFrame` objects.
        """
        self._require_open()
        captured: list[CANFrame] = []
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            frame = self.recv(timeout=0.1)
            if frame:
                captured.append(frame)
        logger.info("Captured %d frames in %.1fs.", len(captured), duration)

        if output_path:
            self._write_csv(captured, output_path)

        return captured

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @staticmethod
    def frame_stats(frames: list[CANFrame]) -> dict:
        """Return basic statistics about a list of captured frames."""
        if not frames:
            return {"count": 0}
        ids = [f.arbitration_id for f in frames]
        unique_ids = set(ids)
        ts = [f.timestamp for f in frames]
        duration = max(ts) - min(ts) if len(ts) > 1 else 0.0
        return {
            "count": len(frames),
            "unique_ids": len(unique_ids),
            "duration_s": round(duration, 3),
            "frames_per_second": round(len(frames) / duration, 1) if duration > 0 else 0,
            "id_histogram": {f"0x{k:03X}": ids.count(k) for k in sorted(unique_ids)},
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _create_bus(self) -> object:
        try:
            import can  # type: ignore
            return can.Bus(interface=self.interface, channel=self.channel, bitrate=self.bitrate)
        except ImportError:
            logger.warning("python-can not installed; using null bus.")
            return _NullCanBus()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not open %s/%s: %s. Using null bus.", self.interface, self.channel, exc)
            return _NullCanBus()

    def _rx_loop(self) -> None:
        """Background thread: read frames from bus and dispatch callbacks."""
        while self._running:
            if self._bus is None:
                break
            try:
                msg = self._bus.recv(timeout=0.1)  # type: ignore[union-attr]
                if msg is None:
                    continue
                frame = CANFrame(
                    arbitration_id=msg.arbitration_id,
                    data=bytes(msg.data),
                    timestamp=msg.timestamp or time.monotonic(),
                    is_extended_id=msg.is_extended_id,
                    is_fd=getattr(msg, "is_fd", False),
                    is_remote_frame=msg.is_remote_frame,
                )
                try:
                    self._rx_queue.put_nowait(frame)
                except queue.Full:
                    pass  # drop frame if queue full
                for cb in list(self._callbacks):
                    try:
                        cb(frame)
                    except Exception:  # noqa: BLE001
                        pass
            except Exception:  # noqa: BLE001
                time.sleep(0.01)

    def _require_open(self) -> None:
        if not self._running:
            raise RuntimeError("CANBus is not open. Call open() first.")

    @staticmethod
    def _write_csv(frames: list[CANFrame], path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("timestamp,arb_id,data\n")
            for f in frames:
                hex_data = " ".join(f"{b:02X}" for b in f.data)
                fh.write(f"{f.timestamp:.6f},0x{f.arbitration_id:03X},{hex_data}\n")
        logger.info("Frame capture written to %s", path)


# ---------------------------------------------------------------------------
# Null bus (no hardware)
# ---------------------------------------------------------------------------

class _NullCanBus:
    def recv(self, timeout: float = 0.1) -> None:  # noqa: ARG002
        time.sleep(timeout)
        return None

    def send(self, msg: object) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def set_filters(self, filters: list) -> None:
        pass
