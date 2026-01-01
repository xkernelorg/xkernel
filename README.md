[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18120560.svg)](https://doi.org/10.5281/zenodo.18120560)

# xkernel
## Invariant Deterministic Kernel (k = 1, Boolean Closure)

xkernel is a minimal, invariant execution kernel.

It defines:
- a single admissible action quantum (k = 1),
- deterministic replay semantics,
- boolean closure against a target state,
- canonical execution hashing,
- and tamper-evident receipts.

xkernel is NOT a runtime engine, simulator, or pattern system.
It has NO kernel object, NO mutable configuration, and NO hidden state.

The kernel is the law.
Executions and receipts are the artifacts.

---

## What xkernel guarantees

- Determinism
  Replaying the same execution always yields the same final state.

- Admissibility
  Any step with action != 1 is invalid.

- Closure
  Closure is a boolean: an execution either closes to a target state or it does not.

- Canonical identity
  Executions and receipts have stable, content-addressed identifiers:
  - xk:sha256:... for executions
  - xr:sha256:... for receipts

- Tamper evidence
  Any mutation of execution or receipt content changes its hash and fails verification.

---

## What xkernel does NOT do

- No engine orchestration
- No filaments, fibers, or bundles
- No pattern detection or lenses
- No identity, signing, or trust semantics
- No backward compatibility with v1

Those concerns belong in downstream systems.

---

## Installation

    pip install -e .

---

## Command-line interface

xkernel ships with a strict reference CLI.

    xkernel --help

Available commands:

- validate      Validate execution admissibility and replay
- hash          Compute execution content address (xk:sha256:...)
- receipt       Emit receipt JSON for an execution (optional target closure)
- verify        Verify receipt integrity against an execution
- receipt-hash  Compute receipt content address (xr:sha256:...)

Example:

    xkernel validate exec.json
    xkernel hash exec.json
    xkernel receipt exec.json --target target.json > receipt.json
    xkernel verify receipt.json exec.json

---

## Core model (conceptual)

    StateVector  : immutable integer coordinate vector
    Step         : delta + action (must equal k = 1)
    Execution    : init + ordered steps + final
    Closure      : boolean equality to a target under replay
    Receipt      : canonical record of execution + closure

There is no kernel instance.
Correctness is enforced structurally.

---

## Testing

    pytest

All tests assert invariants, determinism, hashing stability, and tamper detection.

---

## Versioning

v2.0.0 introduces invariant semantics and removes all v1 engine concepts.
There is no backward compatibility.

---

## License

MIT - see LICENSE.
