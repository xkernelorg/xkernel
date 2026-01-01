from __future__ import annotations

import json
from typing import Any, Dict, Optional

from .kinds import Execution, StateVector, Verdict
from .ops import validate_execution, closed
from .hashing import xk_id


RECEIPT_SPEC = "XKERNEL_RECEIPT_V1"
RECEIPT_VERSION = "1.0.0-draft"


def receipt_object(
    *,
    execution: Execution,
    target: Optional[StateVector] = None,
) -> Dict[str, Any]:
    """
    Build a receipt object for an execution.

    Records:
      - spec + version
      - execution content-address (xk:sha256:...)
      - validation verdict
      - optional closure result (relative to target)

    No signing, no endorsement, no authority.
    """
    verdict: Verdict = validate_execution(execution)

    receipt: Dict[str, Any] = {
        "spec": RECEIPT_SPEC,
        "version": RECEIPT_VERSION,
        "execution_id": xk_id(execution),
        "verdict": {
            "ok": verdict.ok,
            "reason": verdict.reason,
            "details": verdict.details,
        },
    }

    if target is not None:
        receipt["closure"] = {
            "target": {
                "coords": list(target.coords),
                "meta": dict(target.meta),
            },
            "closed": closed(execution, target),
        }

    return receipt


def receipt_json_bytes(receipt: Dict[str, Any]) -> bytes:
    """
    Canonical JSON bytes for a receipt:
      - UTF-8
      - sorted keys
      - no whitespace
    """
    s = json.dumps(receipt, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return s.encode("utf-8")


def verify_receipt(
    *,
    receipt: Dict[str, Any],
    execution: Execution,
) -> Verdict:
    """
    Verify that a receipt is internally consistent with an Execution.

    This is integrity checking only:
      - spec/version correct
      - execution_id matches recomputed xk_id(execution)
      - verdict matches validate_execution(execution)
      - optional closure matches recomputed closed(execution, target)

    Returns a Verdict (OK / reason / details).
    """
    if not isinstance(receipt, dict):
        return Verdict(ok=False, reason="RECEIPT_BAD_TYPE", details={"expected": "dict"})

    spec = receipt.get("spec")
    ver = receipt.get("version")
    if spec != RECEIPT_SPEC:
        return Verdict(ok=False, reason="RECEIPT_BAD_SPEC", details={"spec": spec, "expected": RECEIPT_SPEC})
    if ver != RECEIPT_VERSION:
        return Verdict(ok=False, reason="RECEIPT_BAD_VERSION", details={"version": ver, "expected": RECEIPT_VERSION})

    expected_exec_id = xk_id(execution)
    got_exec_id = receipt.get("execution_id")
    if got_exec_id != expected_exec_id:
        return Verdict(
            ok=False,
            reason="RECEIPT_EXECUTION_ID_MISMATCH",
            details={"got": got_exec_id, "expected": expected_exec_id},
        )

    # Verdict consistency
    expected_v = validate_execution(execution)
    got_v = receipt.get("verdict", {})
    if not isinstance(got_v, dict):
        return Verdict(ok=False, reason="RECEIPT_BAD_VERDICT", details={"expected": "dict"})

    if got_v.get("ok") != expected_v.ok or got_v.get("reason") != expected_v.reason:
        return Verdict(
            ok=False,
            reason="RECEIPT_VERDICT_MISMATCH",
            details={
                "got": {"ok": got_v.get("ok"), "reason": got_v.get("reason")},
                "expected": {"ok": expected_v.ok, "reason": expected_v.reason},
            },
        )

    # Optional closure consistency
    if "closure" in receipt:
        cl = receipt.get("closure")
        if not isinstance(cl, dict):
            return Verdict(ok=False, reason="RECEIPT_BAD_CLOSURE", details={"expected": "dict"})

        tgt = cl.get("target")
        if not isinstance(tgt, dict):
            return Verdict(ok=False, reason="RECEIPT_BAD_CLOSURE_TARGET", details={"expected": "dict"})

        coords = tgt.get("coords")
        meta = tgt.get("meta", {})
        if not isinstance(coords, list) or not all(isinstance(x, int) and not isinstance(x, bool) for x in coords):
            return Verdict(ok=False, reason="RECEIPT_BAD_CLOSURE_COORDS", details={"coords": coords})

        if not isinstance(meta, dict):
            return Verdict(ok=False, reason="RECEIPT_BAD_CLOSURE_META", details={"meta_type": type(meta).__name__})

        target_sv = StateVector(coords=list(coords), meta=dict(meta))

        expected_closed = closed(execution, target_sv)
        got_closed = cl.get("closed")
        if got_closed != expected_closed:
            return Verdict(
                ok=False,
                reason="RECEIPT_CLOSURE_MISMATCH",
                details={"got": got_closed, "expected": expected_closed},
            )

    return Verdict(ok=True, reason="OK", details={})
