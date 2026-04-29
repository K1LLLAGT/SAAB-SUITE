"""
CAN diagnostic protocol implementations.

Provides framing, segmentation, and reassembly for:
- ISO 15765-2 (CAN transport layer, used by UDS and OBD-II on CAN)
- KWP2000 / ISO 14230 over K-line (legacy SAAB 9-3 / 9-5 pre-2003)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ISO 15765-2 (CAN transport layer)
# ---------------------------------------------------------------------------

class FrameType(int):
    SINGLE = 0x0
    FIRST = 0x1
    CONSECUTIVE = 0x2
    FLOW_CONTROL = 0x3


@dataclass
class ISO15765:
    """
    ISO 15765-2 transport layer (CAN TP) encoder / decoder.

    Handles segmentation of multi-byte UDS payloads into CAN frames and
    reassembly of consecutive frames back into PDUs.

    Args:
        tx_id:    CAN arbitration ID used for *outgoing* frames.
        rx_id:    CAN arbitration ID of *incoming* frames from the ECU.
        padding:  Fill unused bytes in the CAN data field with 0xCC.
        max_dl:   Maximum data length (8 for classic CAN, up to 64 for CAN-FD).
    """

    tx_id: int
    rx_id: int
    padding: bool = True
    max_dl: int = 8

    _rx_buffer: bytearray = field(default_factory=bytearray, init=False, repr=False)
    _expected_length: int = field(default=0, init=False, repr=False)
    _consecutive_index: int = field(default=0, init=False, repr=False)

    # ------------------------------------------------------------------
    # Encoding (PDU → CAN frames)
    # ------------------------------------------------------------------

    def encode(self, pdu: bytes) -> list[bytes]:
        """
        Segment *pdu* into one or more CAN data fields.

        Returns:
            List of 8-byte (or *max_dl*-byte) CAN data fields ready to
            be placed into CAN frames with *tx_id*.
        """
        if len(pdu) <= (self.max_dl - 1):
            return [self._single_frame(pdu)]
        frames = [self._first_frame(pdu)]
        frames.extend(self._consecutive_frames(pdu))
        return frames

    def _single_frame(self, pdu: bytes) -> bytes:
        length = len(pdu)
        data = bytes([length]) + pdu
        return self._pad(data)

    def _first_frame(self, pdu: bytes) -> bytes:
        total = len(pdu)
        first_byte = (FrameType.FIRST << 4) | ((total >> 8) & 0x0F)
        second_byte = total & 0xFF
        payload = pdu[:self.max_dl - 2]
        data = bytes([first_byte, second_byte]) + payload
        return self._pad(data)

    def _consecutive_frames(self, pdu: bytes) -> list[bytes]:
        frames = []
        idx = 1
        offset = self.max_dl - 2  # bytes already sent in FF
        while offset < len(pdu):
            sn = idx & 0x0F
            chunk = pdu[offset: offset + self.max_dl - 1]
            data = bytes([(FrameType.CONSECUTIVE << 4) | sn]) + chunk
            frames.append(self._pad(data))
            offset += self.max_dl - 1
            idx += 1
        return frames

    def _pad(self, data: bytes) -> bytes:
        if self.padding and len(data) < self.max_dl:
            data = data + bytes([0xCC] * (self.max_dl - len(data)))
        return data

    # ------------------------------------------------------------------
    # Decoding (CAN data fields → PDU)
    # ------------------------------------------------------------------

    def feed(self, data: bytes) -> Optional[bytes]:
        """
        Feed a single CAN data field into the reassembler.

        Returns:
            Reassembled PDU when complete, otherwise None.
        """
        if not data:
            return None
        frame_type = (data[0] >> 4) & 0x0F

        if frame_type == FrameType.SINGLE:
            length = data[0] & 0x0F
            return bytes(data[1: 1 + length])

        if frame_type == FrameType.FIRST:
            self._expected_length = ((data[0] & 0x0F) << 8) | data[1]
            self._rx_buffer = bytearray(data[2:])
            self._consecutive_index = 1
            return None  # wait for consecutive frames

        if frame_type == FrameType.CONSECUTIVE:
            sn = data[0] & 0x0F
            if sn != (self._consecutive_index & 0x0F):
                logger.warning("ISO15765: sequence number mismatch (expected %d, got %d)",
                               self._consecutive_index & 0x0F, sn)
                self._rx_buffer.clear()
                return None
            self._rx_buffer.extend(data[1:])
            self._consecutive_index += 1
            if len(self._rx_buffer) >= self._expected_length:
                result = bytes(self._rx_buffer[:self._expected_length])
                self._rx_buffer.clear()
                self._expected_length = 0
                return result
            return None

        if frame_type == FrameType.FLOW_CONTROL:
            # Flow control is handled transparently during encoding; log only.
            fc_flag = data[0] & 0x03
            logger.debug("ISO15765: FC flag=%d bs=%d stmin=%d", fc_flag, data[1], data[2])
            return None

        logger.warning("ISO15765: unknown frame type 0x%X", frame_type)
        return None


# ---------------------------------------------------------------------------
# KWP2000 / ISO 14230 (K-line, legacy SAAB)
# ---------------------------------------------------------------------------

@dataclass
class KWP2000:
    """
    KWP2000 (ISO 14230) protocol codec for K-line interfaces.

    Used on older SAAB 9-3 (YS3F, pre-2003) and 9-5 (YS3E) vehicles that
    do not have a CAN bus for diagnostics.

    Args:
        address_mode: ``"functional"`` (0xC0) or ``"physical"`` (0x80).
        source_addr:  Tester address (default 0xF1 for external test tool).
        target_addr:  Target ECU address.
    """

    address_mode: str = "functional"
    source_addr: int = 0xF1
    target_addr: int = 0x10

    _HEADER_FUNCTIONAL = 0xC0
    _HEADER_PHYSICAL = 0x80

    @property
    def _header_byte(self) -> int:
        return self._HEADER_FUNCTIONAL if self.address_mode == "functional" else self._HEADER_PHYSICAL

    # ------------------------------------------------------------------
    # Frame encoding
    # ------------------------------------------------------------------

    def encode(self, service_id: int, data: bytes = b"") -> bytes:
        """
        Build a KWP2000 request frame.

        Frame format (format byte mode):
          [fmt] [tgt] [src] [len] [SID] [data…] [checksum]

        Args:
            service_id: KWP2000 service identifier byte.
            data:       Service payload bytes.

        Returns:
            Complete frame bytes ready for transmission on K-line.
        """
        payload = bytes([service_id]) + data
        length = len(payload)
        fmt = self._header_byte | (length if length <= 0x3F else 0)
        if length > 0x3F:
            header = bytes([fmt, self.target_addr, self.source_addr, length])
        else:
            header = bytes([fmt, self.target_addr, self.source_addr])
        frame = header + payload
        checksum = sum(frame) & 0xFF
        return frame + bytes([checksum])

    def decode(self, frame: bytes) -> Optional[dict]:
        """
        Decode a received KWP2000 frame.

        Returns:
            Dict with keys ``source``, ``target``, ``service_id``, ``data``,
            or None if the frame fails checksum validation.
        """
        if len(frame) < 4:
            return None
        # Verify checksum
        expected = sum(frame[:-1]) & 0xFF
        if frame[-1] != expected:
            logger.warning("KWP2000: checksum mismatch (expected 0x%02X, got 0x%02X)",
                           expected, frame[-1])
            return None

        fmt = frame[0]
        length_in_fmt = fmt & 0x3F
        if length_in_fmt == 0:
            # Additional length byte present
            length = frame[3]
            data_start = 4
        else:
            length = length_in_fmt
            data_start = 3

        return {
            "source": frame[2],
            "target": frame[1],
            "service_id": frame[data_start],
            "data": bytes(frame[data_start + 1: data_start + length]),
        }

    # ------------------------------------------------------------------
    # Common KWP2000 service IDs
    # ------------------------------------------------------------------

    SERVICE_START_DIAGNOSTIC_SESSION = 0x10
    SERVICE_ECU_RESET = 0x11
    SERVICE_READ_ECU_ID = 0x1A
    SERVICE_READ_DTC_BY_STATUS = 0x18
    SERVICE_CLEAR_DIAGNOSTIC_INFO = 0x14
    SERVICE_READ_DATA_BY_LOCAL_ID = 0x21
    SERVICE_INPUT_OUTPUT_CONTROL = 0x2F
    SERVICE_START_ROUTINE_BY_LOCAL_ID = 0x31
    SERVICE_REQUEST_DOWNLOAD = 0x34
    SERVICE_TRANSFER_DATA = 0x36
    SERVICE_REQUEST_TRANSFER_EXIT = 0x37
    SERVICE_TESTER_PRESENT = 0x3E
