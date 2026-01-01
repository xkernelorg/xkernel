"""
xkernel v2.0 — invariant execution kernel

- k = 1 (step quantum)
- closure is boolean, decided by deterministic replay
- canonical execution + receipt hashing
- receipts + verify (integrity-only)
- strict CLI in cli_kK.py
"""

from .kinds import StateVector, Step, Execution, Verdict
from .ops import admissible_step, apply_step, validate_execution, closed
from .canonical import canonical_json_bytes, execution_to_obj
from .hashing import sha256_hex, sha256_bytes, xk_id
from .receipt import receipt_object, receipt_json_bytes, verify_receipt
from .receipt_hashing import receipt_sha256_bytes, receipt_sha256_hex, receipt_id

__all__ = [
    # kinds
    "StateVector",
    "Step",
    "Execution",
    "Verdict",
    # ops
    "admissible_step",
    "apply_step",
    "validate_execution",
    "closed",
    # canonical + hashing (execution)
    "canonical_json_bytes",
    "execution_to_obj",
    "sha256_hex",
    "sha256_bytes",
    "xk_id",
    # receipts
    "receipt_object",
    "receipt_json_bytes",
    "verify_receipt",
    # receipt hashing
    "receipt_sha256_bytes",
    "receipt_sha256_hex",
    "receipt_id",
]
