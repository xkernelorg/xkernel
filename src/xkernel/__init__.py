"""XKernel package: minimal X-field engine (X ∈ ℝ⁶)."""

from .xkernel import (
    XState,
    XKernelConfig,
    XKernel,
    seed_zero,
    seed_impulse,
    trace_to_dict,
)

__all__ = [
    "XState",
    "XKernelConfig",
    "XKernel",
    "seed_zero",
    "seed_impulse",
    "trace_to_dict",
]
