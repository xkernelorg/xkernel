from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

__version__ = "0.1.0"
ENGINE_NAME = "xkernel"

__all__ = [
    "XState",
    "XKernelConfig",
    "XKernel",
    "seed_zero",
    "seed_impulse",
    "trace_to_dict",
]


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

XVector = List[float]     # one cell: length = dim (default 6)
XField = List[XVector]    # 1-D lattice of cells


# ---------------------------------------------------------------------------
# State + Config
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
        data = {
            "step": self.step,
            "field": self.field,
        }
        if self.meta is not None:
            data["meta"] = self.meta
        return data


@dataclass(frozen=True)
class XKernelConfig:
    """Configuration for the X-field kernel.

    Core update rule:

        X_i(t+1) = X_i(t) + eta * (A @ X_i(t)
                                   + B @ (X_{i-1}(t) + X_{i+1}(t)))

    where:
      - X_i(t) ∈ R^dim      (dim = 6 by default)
      - A, B are dim×dim   matrices
      - indices form a 1-D lattice of length `size`
      - periodic boundary conditions wrap indices
    """

    size: int = 64
    dim: int = 6
    eta: float = 0.1
    A: Optional[Sequence[Sequence[float]]] = None
    B: Optional[Sequence[Sequence[float]]] = None
    periodic: bool = True

    def normalized(self) -> "XKernelConfig":
        """Return a config with concrete A, B matrices and sanity checks."""
        if self.dim <= 0:
            raise ValueError("dim must be positive")
        if self.size <= 0:
            raise ValueError("size must be positive")

        A = self.A if self.A is not None else _identity(self.dim, scale=-1.0)
        B = self.B if self.B is not None else _identity(self.dim, scale=0.5)

        _validate_matrix(A, self.dim, "A")
        _validate_matrix(B, self.dim, "B")

        return XKernelConfig(
            size=self.size,
            dim=self.dim,
            eta=self.eta,
            A=A,
            B=B,
            periodic=self.periodic,
        )


# ---------------------------------------------------------------------------
# Kernel
# ---------------------------------------------------------------------------

class XKernel:
    """Deterministic X-field kernel."""

    def __init__(self, config: XKernelConfig) -> None:
        self.config = config.normalized()

    def run(self, initial: XState, steps: int) -> Iterable[XState]:
        """Yield `initial`, then `steps` successive states."""
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
        A = cfg.A
        B = cfg.B
        eta = cfg.eta
        periodic = cfg.periodic

        field_next: XField = []

        for i in range(size):
            x_i = state.field[i]

            # neighbor selection
            if periodic:
                left_idx = (i - 1) % size
                right_idx = (i + 1) % size
            else:
                left_idx = i - 1 if i > 0 else i
                right_idx = i + 1 if i < size - 1 else i

            x_left = state.field[left_idx]
            x_right = state.field[right_idx]

            # compute updates
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _identity(dim: int, scale: float = 1.0) -> List[List[float]]:
    """Return a scaled identity matrix."""
    return [[scale if i == j else 0.0 for j in range(dim)] for i in range(dim)]


def _validate_matrix(M: Sequence[Sequence[float]], dim: int, name: str) -> None:
    if len(M) != dim:
        raise ValueError(f"matrix {name} must have {dim} rows, got {len(M)}")
    for r, row in enumerate(M):
        if len(row) != dim:
            raise ValueError(
                f"matrix {name} row {r} must have length {dim}, got {len(row)}"
            )


def _mat_vec(M: Sequence[Sequence[float]], v: Sequence[float], dim: int) -> List[float]:
    """Dense matrix–vector multiply (no external deps)."""
    if len(v) != dim:
        raise ValueError(f"vector length {len(v)} != dim {dim}")
    out = [0.0] * dim
    for i in range(dim):
        row = M[i]
        s = 0.0
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
            f"field size {len(state.field)} does not match config.size={cfg.size}"
        )
    for i, x in enumerate(state.field):
        if len(x) != cfg.dim:
            raise ValueError(
                f"state.field[{i}] length {len(x)} != config.dim={cfg.dim}"
            )


# ---------------------------------------------------------------------------
# Seeds
# ---------------------------------------------------------------------------

def seed_zero(cfg: XKernelConfig) -> XState:
    """Create a zero field: all cells = [0, ..., 0]."""
    cfg_n = cfg.normalized()
    field = [[0.0] * cfg_n.dim for _ in range(cfg_n.size)]
    return XState(step=0, field=field, meta={"engine": ENGINE_NAME, "mode": "zero"})


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

    field = [[0.0] * cfg_n.dim for _ in range(cfg_n.size)]
    field[index][component] = amplitude

    return XState(
        step=0,
        field=field,
        meta={
            "engine": ENGINE_NAME,
            "mode": "impulse",
            "index": index,
            "component": component,
            "amplitude": amplitude,
        },
    )


# ---------------------------------------------------------------------------
# Trace export
# ---------------------------------------------------------------------------

def trace_to_dict(states: Iterable[XState]) -> Dict[str, Any]:
    """Convert a sequence of XState objects into a JSON trace."""
    states_list = [s.to_dict() for s in states]
    dim, size = _infer_trace_params(states_list)

    trace = {
        "engine": ENGINE_NAME,
        "version": __version__,
        "dim": dim,
        "size": size,
        "frames": states_list,
    }

    # propagate eta if user included it in initial meta
    if states_list:
        meta = states_list[0].get("meta", {})
        if isinstance(meta, dict) and "eta" in meta:
            trace["eta"] = meta["eta"]

    return trace


def _infer_trace_params(states: List[Dict[str, Any]]) -> Tuple[int, int]:
    """Infer (dim, size) from a list of state dictionaries."""
    if not states:
        return 0, 0
    field = states[0].get("field", [])
    size = len(field)
    dim = len(field[0]) if size > 0 else 0
    return dim, size


def main() -> None:
    # TODO: wire this to your real kernel interface
    # e.g., parse args and run a default demo
    import argparse

    parser = argparse.ArgumentParser(prog="xkernel")
    parser.add_argument("--demo", choices=["einstein", "shannon", "wave"], default="einstein")
    args = parser.parse_args()

    if args.demo == "einstein":
        print("Running Einstein lens…")
        # call your real function here
    elif args.demo == "shannon":
        print("Running Shannon lens…")
    elif args.demo == "wave":
        print("Running wave lens…")


if __name__ == "__main__":
    main()
