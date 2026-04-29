"""
Tests for CAN bus and protocol modules (can.bus, can.protocols).
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from can.bus import CANBus, CANFrame, _NullCanBus
from can.protocols import ISO15765, KWP2000


# ---------------------------------------------------------------------------
# CANFrame
# ---------------------------------------------------------------------------

class TestCANFrame:
    def test_str_standard_id(self):
        f = CANFrame(arbitration_id=0x7E0, data=bytes([0x02, 0x01, 0x0D]))
        s = str(f)
        assert "7E0" in s
        assert "02 01 0D" in s

    def test_str_extended_id(self):
        f = CANFrame(arbitration_id=0x18DB33F1, data=b"\x02", is_extended_id=True)
        assert "18DB33F1" in str(f)

    def test_timestamp_defaults_to_now(self):
        before = time.monotonic()
        f = CANFrame(arbitration_id=0x100, data=b"")
        after = time.monotonic()
        assert before <= f.timestamp <= after

    def test_custom_timestamp(self):
        f = CANFrame(arbitration_id=0x100, data=b"", timestamp=1234.5)
        assert f.timestamp == pytest.approx(1234.5)


# ---------------------------------------------------------------------------
# CANBus
# ---------------------------------------------------------------------------

class TestCANBus:
    def test_open_close(self):
        bus = CANBus()
        bus.open()
        assert bus._running
        bus.close()
        assert not bus._running

    def test_context_manager(self):
        with CANBus() as bus:
            assert bus._running
        assert not bus._running

    def test_double_open_is_safe(self):
        bus = CANBus()
        bus.open()
        bus.open()  # should not raise
        bus.close()

    def test_close_when_not_open_is_safe(self):
        bus = CANBus()
        bus.close()  # should not raise

    def test_send_raises_when_not_open(self):
        bus = CANBus()
        frame = CANFrame(arbitration_id=0x7E0, data=b"\x01")
        with pytest.raises(RuntimeError):
            bus.send(frame)

    def test_recv_timeout_returns_none(self):
        bus = CANBus()
        bus.open()
        # NullCanBus.recv returns None after sleeping timeout
        frame = bus.recv(timeout=0.05)
        assert frame is None
        bus.close()

    def test_capture_returns_list(self):
        bus = CANBus()
        with bus:
            frames = bus.capture(duration=0.1)
        assert isinstance(frames, list)

    def test_frame_stats_empty(self):
        stats = CANBus.frame_stats([])
        assert stats["count"] == 0

    def test_frame_stats_populated(self):
        frames = [
            CANFrame(arbitration_id=0x100, data=b"\x01", timestamp=0.0),
            CANFrame(arbitration_id=0x100, data=b"\x02", timestamp=0.5),
            CANFrame(arbitration_id=0x200, data=b"\x03", timestamp=1.0),
        ]
        stats = CANBus.frame_stats(frames)
        assert stats["count"] == 3
        assert stats["unique_ids"] == 2
        assert stats["duration_s"] == pytest.approx(1.0)
        # 3 frames over 1 second = 3.0 fps
        assert stats["frames_per_second"] == pytest.approx(3.0)

    def test_add_callback(self):
        received = []
        bus = CANBus()
        bus.add_callback(received.append)
        assert received == []  # callback stored but not yet fired
        bus.close()


# ---------------------------------------------------------------------------
# ISO 15765-2
# ---------------------------------------------------------------------------

class TestISO15765:
    def setup_method(self):
        self.tp = ISO15765(tx_id=0x7E0, rx_id=0x7E8)

    # Encoding
    def test_single_frame_short(self):
        frames = self.tp.encode(b"\x01\x0D")
        assert len(frames) == 1
        assert frames[0][0] == 0x02  # length nibble
        assert frames[0][1] == 0x01
        assert frames[0][2] == 0x0D

    def test_single_frame_padded(self):
        frames = self.tp.encode(b"\x3E\x00")
        assert len(frames[0]) == 8  # padded to DL

    def test_multi_frame(self):
        payload = bytes(range(20))  # 20 bytes > 7 single-frame limit
        frames = self.tp.encode(payload)
        assert len(frames) > 1
        assert (frames[0][0] >> 4) == 0x1  # First Frame

    def test_consecutive_frame_sequence_numbers(self):
        payload = bytes(range(30))
        frames = self.tp.encode(payload)
        for i, frame in enumerate(frames[1:], start=1):
            sn = frame[0] & 0x0F
            assert sn == (i % 16)

    # Decoding
    def test_decode_single_frame(self):
        raw = bytes([0x02, 0x01, 0x0D, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC])
        result = self.tp.feed(raw)
        assert result == b"\x01\x0D"

    def test_decode_multi_frame(self):
        payload = bytes(range(12))
        frames = self.tp.encode(payload)
        result = None
        for frame in frames:
            r = self.tp.feed(frame)
            if r is not None:
                result = r
        assert result == payload

    def test_decode_empty_returns_none(self):
        assert self.tp.feed(b"") is None

    def test_decode_flow_control_returns_none(self):
        fc = bytes([0x30, 0x00, 0x00, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC])
        assert self.tp.feed(fc) is None

    def test_padding_disabled(self):
        tp = ISO15765(tx_id=0x7E0, rx_id=0x7E8, padding=False)
        frames = tp.encode(b"\x01\x0D")
        assert len(frames[0]) == 3  # no padding


# ---------------------------------------------------------------------------
# KWP2000
# ---------------------------------------------------------------------------

class TestKWP2000:
    def setup_method(self):
        self.kwp = KWP2000(source_addr=0xF1, target_addr=0x10)

    def test_encode_tester_present(self):
        frame = self.kwp.encode(KWP2000.SERVICE_TESTER_PRESENT)
        assert frame[-1] == sum(frame[:-1]) & 0xFF  # checksum valid

    def test_encode_read_dtc(self):
        frame = self.kwp.encode(KWP2000.SERVICE_READ_DTC_BY_STATUS, b"\xFF\xFF")
        assert len(frame) > 4
        assert frame[-1] == sum(frame[:-1]) & 0xFF

    def test_decode_valid_frame(self):
        encoded = self.kwp.encode(KWP2000.SERVICE_TESTER_PRESENT)
        decoded = self.kwp.decode(encoded)
        assert decoded is not None
        assert decoded["service_id"] == KWP2000.SERVICE_TESTER_PRESENT
        assert decoded["target"] == 0x10
        assert decoded["source"] == 0xF1

    def test_decode_bad_checksum(self):
        frame = bytearray(self.kwp.encode(KWP2000.SERVICE_TESTER_PRESENT))
        frame[-1] ^= 0xFF  # corrupt checksum
        assert self.kwp.decode(bytes(frame)) is None

    def test_decode_too_short(self):
        assert self.kwp.decode(b"\xC0\x10") is None

    def test_functional_header(self):
        kwp = KWP2000(address_mode="functional", source_addr=0xF1, target_addr=0x33)
        frame = kwp.encode(KWP2000.SERVICE_TESTER_PRESENT)
        assert frame[0] & 0xC0 == 0xC0

    def test_physical_header(self):
        kwp = KWP2000(address_mode="physical", source_addr=0xF1, target_addr=0x10)
        frame = kwp.encode(KWP2000.SERVICE_TESTER_PRESENT)
        assert frame[0] & 0xC0 == 0x80
