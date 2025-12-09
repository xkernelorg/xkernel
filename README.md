# 🌀 xkernel
### Minimal Deterministic X-Kernel with Filaments, Fibers, and Bundles

**xkernel** is a small, deterministic engine that evolves vectors with a local
rule and organizes their histories into **filaments**, **fibers**, and
**bundles**.

Out of the box, xkernel ships with a simple linear update rule in ℝ^d so the
package is:

- deterministic
- easy to test
- semantically agnostic

It does **not** define patterns or lenses. Those belong in downstream systems
that consume xkernel's data structures.

---

## Quick start

```bash
# from the repo root, in your venv
pip install -e .

# Run a demo extrusion
xkernel demo --fibers 2 --filaments 3 --steps 8 --dim 4
```

Example output:

```text
Bundle:
  fibers: 2
  filaments per fiber: 3
  steps per filament: 8
  dimension: 4
```

---

## Core concepts

```text
XKernel      : s_{t+1} = s_t + η * w
Filament     : [s_0, s_1, ..., s_T]
Fiber        : { filament_id -> Filament }
Bundle       : { fiber_id    -> Fiber }
XEngine      : orchestrator building bundles from a spec
ExtrusionSpec: small config object describing counts + dimension
```

The default rule uses a fixed weight vector so that traces are stable and
predictable. You can later replace `XKernel` with a richer rule while keeping
the same public API.

---

## Testing

```bash
pytest
```

---

## License

MIT — see `LICENSE`.
