# 🧊 XKernel — Minimal X-Field Engine (`X ∈ ℝ⁶`)

`xkernel.py` is a **minimal, geometry-free field engine** built around a single idea:

> **The fundamental state is a six-dimensional real vector**  
> `X ∈ ℝ⁶`, and fields are locally-coupled lattices of these vectors.

Everything else — geometry, physics, interpretation — is optional and can be layered on later.


## 1. Core Idea

- A **cell** holds one vector  

  `X = (x1, x2, x3, x4, x5, x6) ∈ ℝ⁶`

- A **field** is a 1-D lattice of `size` cells:

  ```text
  field = [ X[0], X[1], ..., X[size-1] ]
  ```

- Time is discrete: `step = 0, 1, 2, ...`.

- The **update rule** is purely local and linear by default:

  `X_i(t+1) = X_i(t) + η * (A·X_i(t) + B·(X_{i-1}(t) + X_{i+1}(t)))`

  where:

  - `X_i(t)` is the vector at site `i` and time `t`
  - `A` and `B` are `dim × dim` matrices
  - `η` is a global coupling / timestep scale
  - neighbor indices use **periodic** or **clamped** boundaries


## 2. Data Structures

### `XState`

```python
@dataclass(frozen=True)
class XState:
    step: int
    field: List[List[float]]  # [size][dim]
    meta: dict | None = None
```

Represents one **frame** of the field:

- `step` – integer timestep  
- `field` – list of cells, each a length-`dim` vector  
- `meta` – optional metadata (e.g. `{"engine": "xkernel"}`)


### `XKernelConfig`

```python
@dataclass(frozen=True)
class XKernelConfig:
    size: int = 64
    dim: int = 6
    eta: float = 0.1
    A: Sequence[Sequence[float]] | None = None
    B: Sequence[Sequence[float]] | None = None
    periodic: bool = True
```

- `size` – number of cells in the 1-D lattice  
- `dim` – dimension of each X-vector (default: 6)  
- `eta` – global timestep / coupling factor  
- `A` – local operator matrix (`dim × dim`)  
- `B` – neighbor operator matrix (`dim × dim`)  
- `periodic` – use wrap-around neighbors if `True`, clamped if `False`  

**Defaults** (if `A` or `B` are `None`):

- `A = -I` (local damping)  
- `B = 0.5 * I` (symmetric neighbor coupling)


### `XKernel`

```python
kernel = XKernel(config)
states = kernel.run(initial_state, steps=10)
```

- `run` yields `initial_state` plus `steps` successive states.  
- The kernel is **deterministic** and **pure**: same input → same trace.


## 3. Convenience Constructors

### Zero field

```python
from xkernel.xkernel import XKernelConfig, XKernel, seed_zero

cfg = XKernelConfig(size=64, dim=6, eta=0.1)
state0 = seed_zero(cfg)
kernel = XKernel(cfg)

states = list(kernel.run(state0, steps=10))
```

This creates a trace where all cells remain zero (a useful sanity check).


### Single impulse

```python
from xkernel.xkernel import XKernelConfig, XKernel, seed_impulse

cfg = XKernelConfig(size=64, dim=6, eta=0.1)

# Put an impulse of amplitude 1.0 in cell 32, component 0
state0 = seed_impulse(cfg, index=32, component=0, amplitude=1.0)

kernel = XKernel(cfg)
states = list(kernel.run(state0, steps=50))
```

This produces a simple “X-field wave”:

- the impulse spreads to neighboring cells via `B`  
- it damps locally via `A`  
- with different A/B choices you can create waves, diffusion, oscillations, etc.


## 4. Exporting a Trace to JSON

Use `trace_to_dict` to convert any iterator of `XState` into a JSON-ready dict.

```python
from xkernel.xkernel import (
    XKernelConfig,
    XKernel,
    seed_impulse,
    trace_to_dict,
)
import json

cfg = XKernelConfig(size=64, dim=6, eta=0.1)
kernel = XKernel(cfg)
state0 = seed_impulse(cfg, index=32, component=0, amplitude=1.0)

states = list(kernel.run(state0, steps=120))
trace = trace_to_dict(states)

with open("xfield_trace.json", "w") as f:
    json.dump(trace, f, indent=2)
```

The output format is:

```json
{
  "engine": "xkernel",
  "version": "1.0.0",
  "dim": 6,
  "size": 64,
  "frames": [
    { "step": 0, "field": [[...], [...], ...], "meta": {...} },
    { "step": 1, "field": [[...], [...], ...], "meta": {...} },
    ...
  ]
}
```


## 5. How This Fits “X is ℝ⁶”

`xkernel.py` is the **reference implementation** for:

- A discrete X-field on a 1-D domain  
- Local linear update with configurable operators A and B  
- Fully deterministic, purely functional evolution  
- No built-in geometry, physics, or semantics  

Everything else — CLIKR semantics, geometry, gravity, Euclidean Mechanics — can be
layered on top as *interpretations* or *derived observables*.
