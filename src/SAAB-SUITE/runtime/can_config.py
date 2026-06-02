from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class CanConfig:
    mode: str          # "remote", "virtual", "mock"
    remote_host: str
    remote_port: int
    virtual_channel: str


def load_can_config() -> CanConfig:
    """Unified CAN config.

    SAAB_CAN_MODE:   remote | virtual | mock
    SAAB_CAN_REMOTE_HOST: host for remote gateway
    SAAB_CAN_REMOTE_PORT: port for remote gateway
    SAAB_CAN_VIRTUAL_CHANNEL: name for virtual bus
    """
    mode = os.getenv("SAAB_CAN_MODE", "mock").lower()

    host = os.getenv("SAAB_CAN_REMOTE_HOST", "127.0.0.1")
    port_s = os.getenv("SAAB_CAN_REMOTE_PORT", "29536")
    port = int(port_s)

    virtual_channel = os.getenv("SAAB_CAN_VIRTUAL_CHANNEL", "vcan0")

    return CanConfig(
        mode=mode,
        remote_host=host,
        remote_port=port,
        virtual_channel=virtual_channel,
    )
