# ADR-0004 -- VIN-Aware Subsystems

**Status:** Accepted

## VehicleProfile is the spine

Every subsystem accepts `VehicleProfile` and adapts:

- **Module discovery** filters its probe list to expected modules.
- **Boost model** loads engine-specific maps (B284R/A28NER differs from B207R).
- **Torque model** loads engine + transmission combined limits.
- **Haldex model** loads only if `drivetrain == XWD`.
- **Health report** sections are conditional on profile.
- **SPS** rejects deliverables not compatible with `(platform, market, engine, model_year)`.

## Engine code dual naming

The B284R engine in the user's 9-3 XWD Aero is also referred to as A28NER in
GM corporate literature. The domain holds both:

```python
class EngineCode(Enum):
    B284R = "B284R"   # SAAB designation, used in UI and docs
    @property
    def gm_code(self) -> str: ...   # A28NER for B284R
```

UI displays the SAAB code; SPS lookups against vendor deliverables use the
GM code.

## Immutability

`VehicleProfile` is immutable per session. Mutation produces a new profile
with an audit-logged delta.
