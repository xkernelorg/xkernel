from __future__ import annotations

from .xkernel import XKernel, XKernelConfig
from .filament import Filament
from .fiber import Fiber
from .bundle import Bundle
from .engine import XEngine, ExtrusionSpec

__all__ = [
    "XKernel",
    "XKernelConfig",
    "Filament",
    "Fiber",
    "Bundle",
    "XEngine",
    "ExtrusionSpec",
]

__version__ = "0.3.0"

from .receipt import receipt_object, receipt_json_bytes

__all__ += [
    "receipt_object",
    "receipt_json_bytes",
]

# --- Spec: XKERNEL_INVARIANTS_kK_SPEC_V1 (integers-only) -------------------
from .kinds import StateVector, Step, Execution, Verdict
from .ops import admissible_step, apply_step, validate_execution, closed
from .canonical import canonical_json_bytes, execution_to_obj
from .hashing import sha256_hex, sha256_bytes, xk_id

__all__ += [
    "StateVector",
    "Step",
    "Execution",
    "Verdict",
    "admissible_step",
    "apply_step",
    "validate_execution",
    "closed",
    "canonical_json_bytes",
    "execution_to_obj",
    "sha256_hex",
    "sha256_bytes",
    "xk_id",
]

from .receipt import verify_receipt

__all__ += [
    "verify_receipt",
]
