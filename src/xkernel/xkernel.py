from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


# Type aliases for clarity
XVector = List[float]        # one cell: length = dim (default 6)
XField = List[XVector]       # 1-D lattice of cells


# ---------------------------------------------------------------------------
# State + config
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class XState:
    """One timestep of the X-field.

    - step: integer time index (t = 0, 1, 2, …)
    - field: list of X-vectors, each of length `dim`
    - meta: optional metadata (engine name, tags, etc.)
    """
    step: int
    field: XField
    meta: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "step": self.step,
            "field": self.field,
        }
        if self.meta is not None:
            data["meta"] = self.meta
        return data


@dataclass(frozen=True)
class XKernelConfig:
    """Configuration for the X-field kernel.

    This is the minimal “X is R^6” engine:

        X_i(t+1) = X_i(t) + eta * (A @ X_i(t)
                                   + B @ (X_{i-1}(t) + X_{i+1}(t)))

    where:
      - X_i(t) ∈ R^dim (dim = 6 by default)
      - A, B are dim×dim matrices
      - indices i form a 1-D lattice of length `size`
      - periodic boundary conditions if `periodic` is True
    """
    size: int = 64        # number of sites in the 1-D field
    dim: int = 6          # dimension of each X-vector (default: 6)
    eta: float = 0.1      # global timestep / coupling scale
    A: Optional[Sequence[Sequence[float]]] = None  # local operator
    B: Optional[Sequence[Sequence[float]]] = None  # neighbor operator
    periodic: bool = True

    def normalized(self) -> "XKernelConfig":
        """Return a config with concrete A, B matrices and basic sanity checks.

        Defaults:
          - A = -I (local damping)
          - B =  0.5 * I (neighbor coupling)
        """
        dim = self.dim
        if dim <= 0:
            raise ValueError("dim must be positive")
        if self.size <= 0:
            raise ValueError("size must be positive")

        A = self.A if self.A is not None else _identity(dim, scale=-1.0)
        B = self.B if self.B is not None else _identity(dim, scale=0.5)

        _validate_matrix(A, dim, "A")
        _validate_matrix(B, dim, "B")

        return XKernelConfig(
            size=self.size,
            dim=dim,
            eta=self.eta,
            A=A,
            B=B,
            periodic=self.periodic,
        )


class XKernel:
    """Deterministic X-field kernel.

    Given an initial XState and a config, generates a sequence of XStates
    according to the linear local update rule described in XKernelConfig.
    """

    def __init__(self, config: XKernelConfig) -> None:
        self.config = config.normalized()

    def run(self, initial: XState, steps: int) -> Iterable[XState]:
        """Run the kernel for `steps` updates, starting from `initial`.

        Yields:
          initial, then steps successive states.
        """
        if steps < 0:
            raise ValueError("steps must be non-negative")

        _check_state_shape(initial, self.config)

        current = initial
        yield current

        for _ in range(steps):
            current = self._step(current)
            yield current

    def _step(self, state: XState) -> XState:
        cfg = self.config
        size = cfg.size
        dim = cfg.dim
        A = cfg.A  # type: ignore[assignment]
        B = cfg.B  # type: ignore[assignment]
        eta = cfg.eta
        periodic = cfg.periodic

        field_next: XField = []

        for i in range(size):
            x_i = state.field[i]

            if periodic:
                left_idx = (i - 1) % size
                right_idx = (i + 1) % size
            else:
                left_idx = i - 1 if i > 0 else i
                right_idx = i + 1 if i < size - 1 else i

            x_left = state.field[left_idx]
            x_right = state.field[right_idx]

            local = _mat_vec(A, x_i, dim)
            neigh_sum = _vec_add(x_left, x_right, dim)
            neigh = _mat_vec(B, neigh_sum, dim)
            delta = _vec_add(local, neigh, dim)

            x_next = [x_i[k] + eta * delta[k] for k in range(dim)]
            field_next.append(x_next)

        return XState(
            step=state.step + 1,
            field=field_next,
            meta=state.meta,
        )


def _identity(dim: int, scale: float = 1.0) -> List[List[float]]:
    """Return a `dim` × `dim` scaled identity matrix."""
    return [
        [scale if i == j else 0.0 for j in range(dim)]
        for i in range(dim)
    ]


def _validate_matrix(M: Sequence[Sequence[float]], dim: int, name: str) -> None:
    if len(M) != dim:
        raise ValueError(f"matrix {name} must have {dim} rows, got {len(M)}")
    for r, row in enumerate(M):
        if len(row) != dim:
            raise ValueError(
                f"matrix {name} row {r} must have length {dim}, got {len(row)}"
            )


def _mat_vec(M: Sequence[Sequence[float]], v: Sequence[float], dim: int) -> List[float]:
    """Naive dense matrix–vector multiply; no external deps."""
    if len(v) != dim:
        raise ValueError(f"vector length {len(v)} != dim {dim}")
    out = [0.0] * dim
    for i in range(dim):
        s = 0.0
        row = M[i]
        for j in range(dim):
            s += row[j] * v[j]
        out[i] = s
    return out


def _vec_add(a: Sequence[float], b: Sequence[float], dim: int) -> List[float]:
    if len(a) != dim or len(b) != dim:
        raise ValueError("vector length mismatch in _vec_add")
    return [a[k] + b[k] for k in range(dim)]


def _check_state_shape(state: XState, cfg: XKernelConfig) -> None:
    if len(state.field) != cfg.size:
        raise ValueError(
            f"state.field length {len(state.field)} does not match config.size={cfg.size}"
        )
    for i, x in enumerate(state.field):
        if len(x) != cfg.dim:
            raise ValueError(
                f"state.field[{i}] length {len(x)} does not match config.dim={cfg.dim}"
            )


def seed_zero(cfg: XKernelConfig) -> XState:
    """Create a zero field: all cells = [0, 0, ..., 0] in R^dim."""
    cfg_n = cfg.normalized()
    field: XField = [[0.0] * cfg_n.dim for _ in range(cfg_n.size)]
    return XState(step=0, field=field, meta={"engine": "xkernel", "mode": "zero"})


def seed_impulse(
    cfg: XKernelConfig,
    index: int = 0,
    component: int = 0,
    amplitude: float = 1.0,
) -> XState:
    """Create a field with a single nonzero entry at (index, component)."""
    cfg_n = cfg.normalized()
    if not (0 <= index < cfg_n.size):
        raise ValueError(f"index {index} out of range for size {cfg_n.size}")
    if not (0 <= component < cfg_n.dim):
        raise ValueError(f"component {component} out of range for dim {cfg_n.dim}")

    field: XField = [[0.0] * cfg_n.dim for _ in range(cfg_n.size)]
    field[index][component] = amplitude

    return XState(
        step=0,
        field=field,
        meta={
            "engine": "xkernel",
            "mode": "impulse",
            "index": index,
            "component": component,
            "amplitude": amplitude,
        },
    )


def trace_to_dict(states: Iterable[XState]) -> Dict[str, Any]:
    """Convert a sequence of XState objects into a JSON-serializable trace."""
    states_list = [s.to_dict() for s in states]
    dim, size = _infer_trace_params(states_list)

    cfg_info: Dict[str, Any] = {}
    if states_list:
        # we don't store eta in states; callers should add it to meta if needed
        meta = states_list[0].get("meta", {}) if isinstance(states_list[0], dict) else {}
        if isinstance(meta, dict) and "eta" in meta:
            cfg_info["eta"] = meta["eta"]

    trace: Dict[str, Any] = {
        "engine": "xkernel",
        "version": "1.0.0",
        "dim": dim,
        "size": size,
        "frames": states_list,
    }
    trace.update(cfg_info)
    return trace


def _infer_trace_params(states: List[Dict[str, Any]]) -> Tuple[int, int]:
    """Best-effort inference of dim and size from a list of state dicts."""
    if not states:
        return 0, 0

    first = states[0]
    field = first.get("field", [])
    size = len(field)
    dim = len(field[0]) if size > 0 else 0
    return dim, size
