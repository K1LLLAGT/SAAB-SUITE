"""Engine code dual-naming (B284R / A28NER)."""

from __future__ import annotations

from saab_suite.domain.vehicle.platform import EngineCode


def test_b284r_gm_code_is_a28ner() -> None:
    assert EngineCode.B284R.gm_code == "A28NER"
    assert EngineCode.B284R.displays_as == "B284R"


def test_unknown_engine_falls_back_to_value() -> None:
    assert EngineCode.UNKNOWN.gm_code == "UNKNOWN"
