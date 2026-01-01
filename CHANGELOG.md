# Changelog

All notable changes to **xkernel** are documented in this file.

xkernel follows semantic versioning where **major versions represent
invariant or semantic breaks**.

---

## [2.0.0] - 2026-01-01

### Changed
- Replaced object-based kernel with invariant semantics.
- Removed `XKernel`, `XKernelConfig`, `XEngine`, and all orchestration layers.
- Kernel is no longer a runtime engine or mutable system.

### Added
- Invariant execution model with single admissible action quantum (k = 1).
- Deterministic replay validation.
- Boolean closure semantics against a target state.
- Canonical execution hashing (`xk:sha256:...`).
- Canonical receipt hashing (`xr:sha256:...`).
- Tamper-evident receipt generation and verification.
- Strict reference CLI (`validate`, `hash`, `receipt`, `verify`, `receipt-hash`).
- End-to-end test coverage for invariants, hashing stability, and tamper detection.

### Removed
- Filament, Fiber, and Bundle abstractions.
- Engine orchestration and extrusion specs.
- Demo and visualization commands.
- All backward compatibility with v1 APIs.

### Notes
- xkernel v2 is a foundational invariant kernel.
- Identity, trust, signing, aggregation, and interpretation are intentionally out of scope.
- Downstream systems are expected to consume executions and receipts as artifacts.

---

## [0.x] - Historical

Versions prior to 2.0.0 implemented an object-oriented kernel with engines,
filaments, fibers, and bundles. These concepts were removed in v2.0.0 in favor
of invariant, law-based semantics.

---

End of changelog.
