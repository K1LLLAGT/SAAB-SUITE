"""Pydantic configuration schema."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class CanConfig(BaseModel):
    """CAN transport configuration."""

    source: str = Field("mock", description="One of: mock, replay, j2534, socketcan, canusb")
    interface: str | None = None
    bitrate: int = 500000


class SpsConfig(BaseModel):
    """SPS configuration."""

    min_battery_v: float = 12.4
    require_real_flash_env: bool = True
    audit_log_path: Path = Path("runtime/audit/audit.sqlite")


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    redact_vin: bool = False
    log_dir: Path = Path("runtime/logs")


class WebConfig(BaseModel):
    """Web UI configuration."""

    bind_host: str = "127.0.0.1"
    bind_port: int = 8765
    require_token: bool = False


class SaabSuiteConfig(BaseModel):
    """Resolved suite configuration."""

    can: CanConfig = Field(default_factory=CanConfig)
    sps: SpsConfig = Field(default_factory=SpsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    web: WebConfig = Field(default_factory=WebConfig)
