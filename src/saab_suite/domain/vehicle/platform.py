"""Platform / engine / transmission / drivetrain enumerations."""

from __future__ import annotations

from enum import Enum


class Platform(str, Enum):
    """Vehicle platform family."""

    GM_EPSILON = "GM_EPSILON"          # 9-3 (2003-2014), 9-5 (2010-2012)
    GM_EPSILON_II = "GM_EPSILON_II"    # later 9-5
    SAAB_GM900 = "SAAB_GM900"          # 9-5 (1997-2009), 9-3 OG
    UNKNOWN = "UNKNOWN"


class Market(str, Enum):
    """Sales market -- affects calibration and feature set."""

    NAO = "NAO"
    ROW = "ROW"
    CHINA = "CHINA"
    UNKNOWN = "UNKNOWN"


class BodyStyle(str, Enum):
    """Body style."""

    SEDAN = "SEDAN"
    SPORTCOMBI = "SPORTCOMBI"
    CONVERTIBLE = "CONVERTIBLE"
    UNKNOWN = "UNKNOWN"


class EngineCode(str, Enum):
    """Engine code.

    SAAB designations are primary (B284R for the user's 9-3 XWD Aero).
    GM corporate codes are exposed via :attr:`gm_code` for vendor lookups.
    """

    B207E = "B207E"
    B207L = "B207L"
    B207R = "B207R"
    B284R = "B284R"        # 2.8L turbo V6 -- A28NER in GM literature
    Z19DTH = "Z19DTH"
    UNKNOWN = "UNKNOWN"

    @property
    def gm_code(self) -> str:
        """GM corporate engine code used in vendor diagnostic tools."""
        return _GM_CODES.get(self, self.value)

    @property
    def displays_as(self) -> str:
        """Preferred display string in UI and reports."""
        return self.value


_GM_CODES: dict[EngineCode, str] = {
    EngineCode.B284R: "A28NER",
    EngineCode.B207R: "A20NHT",
    EngineCode.B207L: "A20NHT",
    EngineCode.B207E: "A20NHT",
    EngineCode.Z19DTH: "Z19DTH",
}


class TransmissionCode(str, Enum):
    """Transmission code."""

    F40 = "F40"
    M32 = "M32"
    AF40 = "AF40-6"
    AF33 = "AF33-5"
    UNKNOWN = "UNKNOWN"


class Drivetrain(str, Enum):
    """Drivetrain configuration."""

    FWD = "FWD"
    XWD = "XWD"
    UNKNOWN = "UNKNOWN"


class HaldexGen(str, Enum):
    """Haldex coupling generation. Only meaningful for XWD."""

    GEN3 = "GEN3"
    GEN4 = "GEN4"
    GEN5 = "GEN5"
    UNKNOWN = "UNKNOWN"
