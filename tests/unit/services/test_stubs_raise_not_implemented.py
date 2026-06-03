"""Phase-0 verification: every service stub raises NotImplementedError.

This locks the architecture: nobody can accidentally ship empty implementations.
When a service is implemented, its test is rewritten to verify behavior.
"""

from __future__ import annotations

import pytest

from SAAB_SUITE.services.diagnostics import dtc_reader
from SAAB_SUITE.services.discovery import module_discovery, module_ping
from SAAB_SUITE.services.live import autoscale, replay_engine, streaming_engine
from SAAB_SUITE.services.sps import plan_builder, plan_validator, precheck
from SAAB_SUITE.services.vin import decoder, profile_builder

STUBS = [
    (module_discovery.discover_modules, (None, None, None)),
    (module_ping.ping, (None, None)),
    (dtc_reader.read_dtcs, (None,)),
    (autoscale.compute, ([],)),
    (replay_engine.from_file, (None,)),
    (streaming_engine.stream, (None, [])),
    (plan_builder.build, (None, None, None)),
    (plan_validator.validate, (None, None)),
    (precheck.run, (None, None, None)),
    (decoder.decode, (None,)),
    (profile_builder.build, (None,)),
]


@pytest.mark.parametrize(("func", "args"), STUBS)
def test_stub_raises_not_implemented(func, args) -> None:
    with pytest.raises(NotImplementedError):
        func(*args)
